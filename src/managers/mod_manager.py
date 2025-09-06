import os
from typing import Union, List
from src.core.mod_loader import ModLoader
from src.managers.config_manager import ConfigManager
from src.models.mod import Mod
from src.utils.logger import output_log

class ModManager():
    def __init__(self, config_manager:ConfigManager):
        self.config_manager = config_manager
        self.mods = []

    def scan(self, scan_target:Union[str, List[str]], callback:callable=None ):
        self.callback = callback
        loader = ModLoader(scan_target)
        loader.load_mods(self.on_progress, self.on_complete)

    def scan_all(self, callback:callable=None ):
        self.mods = []
        self.callback = callback
        root_dir = self.config_manager.config.root_dir
        mod_folders = [os.path.join(root_dir, name) for name in os.listdir(root_dir)]
        self.scan(mod_folders, callback)

    def on_progress(self, mod:Mod):
        self.mods.append(mod)

    def on_complete(self):
        if self.callback:
            self.callback(self.mods)