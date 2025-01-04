import os
from threading import Thread
import concurrent.futures
from typing import Union
from src.utils.file import is_valid_dir, get_base_name
from src.utils.toml import load_toml
from src.utils.hash import get_hash
from src.models.mod import Mod
from src.constants.elements import *
from src.constants.categories import *
from .scanner import scan_mod

class ModLoader(Thread):
    def __init__(
        self, 
        directory:Union[str, list], 
        on_finish:callable,
        on_start:callable = None, 
        on_progress:callable = None
    ):
        super().__init__()
        self.directory = directory
        self.on_start = on_start
        self.on_progress = on_progress
        self.on_finish = on_finish
        self.daemon = True
        self.start()

    def find_mod(self, name:str, path:str):
        if not is_valid_dir(path):
            return None
        
        mod = Mod()
        mod.folder_name = name
        mod.display_name = name
        mod.category = "Misc"
        mod.wifi_safe = "Uncertain"
        mod.path = path
        mod.hash = get_hash(name)

        data = load_toml(path)
        if data is not None:
            mod.update(**data)
            mod.contains_info = True            

        mod = scan_mod(mod)
        return mod
    
    def find_mods(self, directory:Union[str, list]):
        mods = []

        if self.on_start is not None:
            self.on_start(len(os.listdir(directory)))

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            if isinstance(directory, str):
                futures = [executor.submit(self.find_mod, folder_name, os.path.join(directory, folder_name)) for folder_name in os.listdir(directory)]
            elif isinstance(directory, list):
                futures = [executor.submit(self.find_mod, get_base_name(d), d) for d in directory]
            if self.on_progress is not None:
                [future.add_done_callback(self.on_progress) for future in futures]
            for future in concurrent.futures.as_completed(futures):
                mod = future.result()
                if mod is not None:
                    mods.append(mod)

        self.on_finish(mods)

    def run(self):
        if isinstance(self.directory, str):
            if is_valid_dir(self.directory):
                self.find_mods(self.directory)
        elif isinstance(self.directory, list):
            if False not in [is_valid_dir(d) for d in self.directory]:
                self.find_mods(self.directory)