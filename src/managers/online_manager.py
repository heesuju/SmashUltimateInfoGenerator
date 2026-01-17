from typing import List, Callable, Dict, Optional
from src.core.web.gamebanana import Gamebanana
from src.models.mod import Mod, Character, Category, Wifi, ModItem, OnlineModItem
from src.constants.enums import Fighter, Element

from PyQt6.QtCore import QObject, pyqtSignal

class OnlineManager(QObject):
    search_complete = pyqtSignal(list)
    state_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.search_results: List[Dict] = []
        self.current_page = 1
        self.current_query = ""
        self.current_author = ""
        self.current_sort = "best_match"
        self.is_loading = False
        self.total_results = 0 # GameBanana search doesn't easily give total count, might need to infer
        
        self.selected_ids: set[str] = set()
        
        
        self.callbacks: List[Callable] = []
        # Remove on_mods_ready as we will use signal
        # self.on_mods_ready: Optional[Callable[[List[ModItem]], None]] = None
        
    def add_callback(self, callback: Callable):
        self.callbacks.append(callback)
        
    def _notify(self):
        self.state_changed.emit()
        for callback in self.callbacks:
            callback()
            
    def search(self, query: str = "", author: str = "", page: int = 1, sort: str = "best_match"):
        """Initiate a search"""
        self.current_query = query
        self.current_author = author
        self.current_page = page
        self.current_sort = sort
        self.is_loading = True
        self._notify()
        
        # Start search thread
        # Note: Gamebanana thread is fire-and-forget, calls callback when done
        Gamebanana(
            id=query,
            callback=self._on_search_complete,
            is_search=True,
            author_filter=author,
            page=page,
            sort=sort
        )
        
    def _on_search_complete(self, data: Dict):
        """Callback from Gamebanana thread"""
        self.is_loading = False
        
        # Extract metadata and records from dict response
        total_count = data.get("total_count", 0)
        records = data.get("records", [])
        self.search_results = records
        self.total_results = total_count
        
        # Convert to ModItems for UI
        mod_items = []
        for item in records:
            # We construct a minimal ModItem since we don't have full details
            # item is now the record directly, not wrapped in another dict
            
            # Extract stats from record
            likes = item.get("_nLikeCount", 0)
            posts = item.get("_nPostCount", 0)
            views = item.get("_nViewCount", 0)
            date = item.get("_tsDateModified", 0)
            ver = item.get("_sVersion", "")
            
            # Category Mapping
            cat_name = item.get("_aRootCategory", {}).get("_sName", "").lower()
            category = "Misc" # Default
            
            if cat_name == "skins":
                category = Category.FIGHTER.value
            elif cat_name == "stage mods" or cat_name == "stages":
                category = Category.STAGE.value
            elif cat_name == "effects":
                category = Category.EFFECTS.value
            elif cat_name == "ui" or cat_name == "guis":
                category = Category.UI.value
            elif cat_name == "gameplay" or cat_name == "movesets":
                category = Category.PARAM.value
            elif cat_name == "sounds" or cat_name == "voice" or cat_name == "audio":
                category = Category.AUDIO.value
            
            # Get name and ID directly from item
            id_val = item.get("_idRow", "")
            name = item.get("_sName", "Unknown")
            
            # Get thumbnail
            preview_media = item.get("_aPreviewMedia", {})
            thumbnail = ""
            if preview_media:
                images = preview_media.get("_aImages", [])
                if images:
                    image_obj = images[0]
                    base_url = image_obj.get("_sBaseUrl", "")
                    
                    file = image_obj.get("_sFile220", "")
                    if not file:
                        file = image_obj.get("_sFile530", "")
                    if not file:
                        file = image_obj.get("_sFile", "")
                        
                    if base_url and file:
                        thumbnail = f"{base_url}/{file}"
            
            # Get author
            submitter = item.get("_aSubmitter", {})
            author = submitter.get("_sName", "Unknown")
            
            mod_items.append(OnlineModItem(
                id=str(id_val),
                name=name,
                thumbnail=thumbnail,
                category=category,
                authors=author,
                slots="",
                version=ver,
                enabled=False,
                selected=False,
                favorited=False,
                hidden=False,
                character_icons=[],
                like_count=likes,
                post_count=posts,
                view_count=views,
                date_updated=date,
                url=f"https://gamebanana.com/mods/{id_val}"
            ))
            
            
        self.search_complete.emit(mod_items)
        self._notify()

    def get_results(self) -> List[Dict]:
        return self.search_results

    def next_page(self):
        self.search(self.current_query, self.current_author, self.current_page + 1)
        
    def prev_page(self):
        if self.current_page > 1:
            self.search(self.current_query, self.current_author, self.current_page - 1)

    # Selection Interface for GridList/TreeList compatibility
    def is_selected(self, mod_id: str) -> bool:
        return mod_id in self.selected_ids
        
    def set_selection(self, mod_id: str):
        self.selected_ids = {mod_id}
        self._notify()
        
    def add_selection(self, mod_id: str):
        self.selected_ids.add(mod_id)
        self._notify()
        
    def remove_selection(self, mod_id: str):
        if mod_id in self.selected_ids:
            self.selected_ids.remove(mod_id)
            self._notify()
            
    def clear_selection(self):
        self.selected_ids.clear()
        self._notify()
