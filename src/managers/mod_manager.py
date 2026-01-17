import os
from typing import Union, List
from src.core.mod_loader import ModLoader
from src.managers.config_manager import ConfigManager
from src.models.mod import Mod
from src.utils.logger import output_log

class ModManager():
    def __init__(self, config_manager:ConfigManager):
        self.config_manager = config_manager
        self.mods = {}
        self.focused_id = ""
        self.selected_ids = []
        self.callback = None
        self.focus_callbacks = []
        self.hidden_ids = []
        self.enabled_ids = []
        self.workspace = "Default"

    @property
    def favorite_ids(self):
        return self.config_manager.config.favorites

    def set_callback(self, callback:callable):
        self.callback = callback

    def add_focus_callback(self, callback:callable):
        self.focus_callbacks.append(callback)

    def add_favorite_callback(self, callback:callable):
        if not hasattr(self, 'favorite_callbacks'):
            self.favorite_callbacks = []
        self.favorite_callbacks.append(callback)
    
    def _notify_favorite_changed(self, mod_id:str, is_favorite:bool):
        if hasattr(self, 'favorite_callbacks'):
            for callback in self.favorite_callbacks:
                callback(mod_id, is_favorite)

    def scan(self, scan_target:Union[str, List[str]]):
        loader = ModLoader(scan_target)
        loader.load_mods(self.on_progress, self.on_complete)

    def scan_all(self):
        self.mods = {}
        root_dir = self.config_manager.config.root_dir
        
        if not root_dir:
            return 
        
        mod_folders = [os.path.join(root_dir, name) for name in os.listdir(root_dir)]
        self.scan(mod_folders)

    def on_progress(self, mod:Mod):
        self.mods[str(mod.hash)] = mod

    def on_complete(self):
        if self.callback:
            self.callback()

    def set_selection(self, id:str):
        self.focused_id = id
        if len(self.focus_callbacks) > 0:
            for callback in self.focus_callbacks:
                callback(id)

    def get_mods(self)->List[Mod]:
        return self.mods.values()
    
    def get_mod(self, id:str)->Mod:
        return self.mods.get(id, None)
    
    def add_favorite(self, id:str):
        id = str(id) # Ensure ID is string
        if id not in self.favorite_ids:
            self.favorite_ids.append(id)
            self.config_manager.save()
            self._notify_favorite_changed(id, True)

    def remove_favorite(self, id:str):
        id = str(id) # Ensure ID is string
        if id in self.favorite_ids:
            self.favorite_ids.remove(id)
            self.config_manager.save()
            self._notify_favorite_changed(id, False)

    def add_enabled(self, id:str):
        if id not in self.enabled_ids:
            self.enabled_ids.append(id)

    def remove_enabled(self, id:str):
        if id in self.enabled_ids:
            self.enabled_ids.remove(id)

    def add_hidden(self, id:str):
        if id not in self.hidden_ids:
            self.hidden_ids.append(id)

    def remove_hidden(self, id:str):
        if id in self.hidden_ids:
            self.hidden_ids.remove(id)
    
    # Selection management methods
    def toggle_selection(self, id:str):
        """Toggle selection state of a mod"""
        if id in self.selected_ids:
            self.selected_ids.remove(id)
        else:
            self.selected_ids.append(id)
    
    def add_selection(self, id:str):
        """Add a mod to selection"""
        if id not in self.selected_ids:
            self.selected_ids.append(id)
    
    def remove_selection(self, id:str):
        """Remove a mod from selection"""
        if id in self.selected_ids:
            self.selected_ids.remove(id)
    
    def clear_selection(self):
        """Clear all selections"""
        self.selected_ids = []
    
    def is_selected(self, id:str)->bool:
        """Check if a mod is selected"""
        return id in self.selected_ids
    
    def are_all_selected(self, ids:List[str])->bool:
        """Check if all provided IDs are selected"""
        return all(id in self.selected_ids for id in ids)
    
    def get_selected_ids(self)->List[str]:
        """Get all selected mod IDs"""
        return self.selected_ids