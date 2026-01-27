from typing import List, Callable, Dict, Optional
from src.core.gamebanana import Gamebanana, process_mod_info
from src.models.mod import Mod, Character, Category, Wifi, ModItem, OnlineModItem
from src.constants.enums import Fighter, Element

from PyQt6.QtCore import QObject, pyqtSignal

class OnlineManager(QObject):
    search_complete = pyqtSignal(list)
    state_changed = pyqtSignal()
    mod_details_ready = pyqtSignal(dict) # New signal for full mod details
    
    def __init__(self):
        super().__init__()
        self.search_results: List[Dict] = []
        self.current_page = 1
        self.current_query = ""
        self.current_author = ""
        self.current_sort = "best_match"
        self.is_loading = False
        self.total_results = 0 
        
        self.selected_ids: set[str] = set()
        self._mod_info_cache: Dict[str, Dict] = {} 
        self._mod_description_cache: Dict[str, str] = {}
        self._page_cache: Dict[tuple, Dict] = {} # Cache for search results: (query, author, sort, page) -> data
        self._focused_id = None # Track currently focused mod for preview
        
        self.callbacks: List[Callable] = []
        self.focus_callbacks: List[Callable] = []

    @property
    def focused_id(self):
        return self._focused_id

    def add_callback(self, callback: Callable):
        self.callbacks.append(callback)

    def add_focus_callback(self, callback: Callable):
        self.focus_callbacks.append(callback)
        
    def _notify(self):
        self.state_changed.emit()
        for callback in self.callbacks:
            callback()

    def set_focus(self, mod_id: str):
        """Set the focused mod (clicked item) and fetch details"""
        print(f"[OnlineManager] set_focus called with mod_id: {mod_id}")
        if self._focused_id == mod_id:
            print(f"[OnlineManager] Same mod already focused, skipping")
            return
            
        self._focused_id = mod_id
        
        # Notify focus listeners (like PreviewPanel)
        print(f"[OnlineManager] Notifying {len(self.focus_callbacks)} focus callbacks")
        for callback in self.focus_callbacks:
            callback(mod_id)
            
        # Fetch detailed info asynchronously
        self.fetch_metadata(mod_id)

    def fetch_metadata(self, mod_id: str):
        if not mod_id:
            return
            
        # Check cache first
        has_info = mod_id in self._mod_info_cache
        has_desc = mod_id in self._mod_description_cache
        
        if has_info and has_desc:
            print(f"[OnlineManager] Using fully cached details for {mod_id}")
            details = self._mod_info_cache[mod_id].copy()
            details['description'] = self._mod_description_cache[mod_id]
            self.mod_details_ready.emit(details)
            return
        
        print(f"[OnlineManager] Cache partial or missing for {mod_id} (info: {has_info}, desc: {has_desc})")
        
        # Fetch detailed info
        Gamebanana(
            id=mod_id,
            callback=self._on_metadata_complete,
            is_search=False # Direct fetch
        )

    def _on_metadata_complete(self, data: Dict):
        """Callback from Gamebanana thread for single item details"""
        # data is keyed by ID: { "12345": { ... } }
        for mod_id, details in data.items():
            details["_mod_id"] = mod_id
            description = details.pop('description', None)
            self._mod_info_cache[mod_id] = details
            if description:
                self._mod_description_cache[mod_id] = description
                details['description'] = description
            self.mod_details_ready.emit(details)

    def get_mod(self, mod_id: str) -> OnlineModItem:
        """Retrieve a mod item by ID from search results"""
        # Linear search in current results (fast enough for page size 15)
        for item in self.search_results:
            if str(item.get("_idRow", "")) == str(mod_id):
                # Construct OnlineModItem again (or cache them)
                pass
        pass 
        
        record = None
        for r in self.search_results:
            if str(r.get("_idRow")) == str(mod_id):
                record = r
                break
        
        if record:
             # Create temp item
            id_val = record.get("_idRow", "")
            preview_media = record.get("_aPreviewMedia", {})
            thumbnail = ""
            if preview_media:
                 images = preview_media.get("_aImages", [])
                 if images:
                     image_obj = images[0]
                     base_url = image_obj.get("_sBaseUrl", "")
                     file_name = image_obj.get("_sFile220", "") or image_obj.get("_sFile", "")
                     if base_url and file_name:
                         thumbnail = f"{base_url}/{file_name}"

            return OnlineModItem(
                id=str(id_val),
                name=record.get("_sName", "Unknown"),
                thumbnail=thumbnail,
                category="Misc", # Simplified
                authors=record.get("_aSubmitter", {}).get("_sName", "Unknown"),
                slots="",
                version=record.get("_sVersion", ""),
                enabled=False,
                selected=False,
                favorited=False,
                hidden=False,
                character_icons=[],
                url=f"https://gamebanana.com/mods/{id_val}"
            )
        return None

    def search(self, query: str = "", author: str = "", page: int = 1, sort: str = "best_match", force_refresh: bool = False):
        """Initiate a search"""
        self.current_query = query
        self.current_author = author
        self.current_page = page
        self.current_sort = sort
        self.is_loading = True
        self._notify()
        
        # Check cache
        cache_key = (query, author, sort, page)
        if not force_refresh and cache_key in self._page_cache:
            print(f"[OnlineManager] Using cached page results for {cache_key}")
            self._on_search_complete(self._page_cache[cache_key])
            return

        is_new = False
        if not query:
            is_new = True

        # Start search thread
        Gamebanana(
            id=query,
            callback=self._on_search_complete,
            is_search=not is_new,
            is_new=is_new,
            author_filter=author,
            page=page,
            sort=sort
        )
        
    def _on_search_complete(self, data: Dict):
        """Callback from Gamebanana thread"""
        self.is_loading = False
        
        # Cache the page results
        cache_key = (self.current_query, self.current_author, self.current_sort, self.current_page)
        self._page_cache[cache_key] = data
        
        # Extract metadata and records from dict response
        total_count = data.get("total_count", 0)
        records = data.get("records", [])
        self.search_results = records
        self.total_results = total_count
        
        for item in records:
            try:
                if "_idRow" in item:
                    mid, details = process_mod_info(item)
                    details["_mod_id"] = str(mid)
                    self._mod_info_cache[str(mid)] = details
            except Exception as e:
                pass

        # Convert to ModItems for UI
        mod_items = []
        for item in records:
            # Extract stats from record
            likes = item.get("_nLikeCount", 0)
            posts = item.get("_nPostCount", 0)
            views = item.get("_nViewCount", 0)
            date = item.get("_tsDateModified", 0)
            ver = item.get("_sVersion", "")
            root_cat = item.get("_aRootCategory", {})
            # Category Mapping
            cat_name = root_cat.get("_sName", "").lower() if root_cat else ""
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
