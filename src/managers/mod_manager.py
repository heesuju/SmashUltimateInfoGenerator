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
        self.favorite_ids = []
        self.enabled_ids = []
        self.workspace = "Default"

    def set_callback(self, callback:callable):
        self.callback = callback

    def add_focus_callback(self, callback:callable):
        self.focus_callbacks.append(callback)

    def scan(self, scan_target:Union[str, List[str]]):
        loader = ModLoader(scan_target)
        loader.load_mods(self.on_progress, self.on_complete)

    def scan_all(self):
        self.mods = {}
        root_dir = self.config_manager.config.root_dir
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
        if id not in self.favorite_ids:
            self.favorite_ids.append(id)

    def remove_favorite(self, id:str):
        if id in self.favorite_ids:
            self.favorite_ids.remove(id)

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