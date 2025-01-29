"""
mod_loader.py: class that scans mod folders to automatically find
included elements
"""

import os
import copy
from PyQt6.QtCore import QThread, pyqtSignal
from concurrent.futures import ThreadPoolExecutor
from typing import Union
from src.utils.file import is_valid_dir, get_base_name
from src.utils.toml import load_toml
from src.utils.hash import get_hash
from src.models.mod import Mod
from .scanner import scan_mod

class ModLoader():
    """
    Mod Loader Class loads mod(s) in multi-thread
    Mod directories will be scanned for info.tomls and other info
    such as skins, which slots they use, and other elements.
    """
    def __init__(self, directory):
        super().__init__()
        self.directory = directory

    def find_mod(self, name:str, path:str)->Mod:
        """
        Finds the mod in the designated path
        Args:
            name: the name of the mod
            path: the directory where the mod is located in
        Returns the scanned mod
        """
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

    def find_mods(self, directory:Union[str, list[str]])->None:
        """
        Scans multiple mod directories in multiple threads to save time
        Args: 
            directory (str or list): the directory(-ies) containing mods that needs to be scanned

        Returns None since scanned mods will be sent through a callback function
        """
        mods = []
        
        for folder_name in os.listdir(directory):
            dir = os.path.join(directory, folder_name)
            mod = self.find_mod(get_base_name(dir), dir)
            if mod is not None:
                mods.append(mod)

        # self.finished.emit(mods)  # Notify when done
        return mods

    def run(self):
        """
        Runs the thread
        """
        if isinstance(self.directory, str):
            if is_valid_dir(self.directory):
                return self.find_mods(self.directory)
