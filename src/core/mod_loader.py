"""
mod_loader.py: class that scans mod folders to automatically find
included elements
"""

import os
import copy
from threading import Thread
import concurrent.futures
from typing import Union
from src.utils.file import is_valid_dir, get_base_name
from src.utils.toml import load_toml
from src.utils.hash import get_hash
from src.models.mod import Mod
from .scanner import scan_mod

class ModLoader(Thread):
    """
    Mod Loader Class loads mod(s) in multi-thread
    Mod directories will be scanned for info.tomls and other info
    such as skins, which slots they use, and other elements.
    """
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

        tmp_includes = copy.copy(mod.includes)
        mod = scan_mod(mod)
        if len(tmp_includes) > 0:
            mod.includes = tmp_includes

        return mod

    def find_mods(self, directory:Union[str, list[str]])->None:
        """
        Scans multiple mod directories in multiple threads to save time
        Args: 
            directory (str or list): the directory(-ies) containing mods that needs to be scanned

        Returns None since scanned mods will be sent through a callback function
        """
        mods = []

        if self.on_start is not None:
            self.on_start(len(os.listdir(directory)))

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            if isinstance(directory, str):
                for folder_name in os.listdir(directory):
                    futures.append(executor.submit(
                            self.find_mod,
                            folder_name,
                            os.path.join(directory, folder_name)
                        )
                    )
            elif isinstance(directory, list):
                futures = [executor.submit(self.find_mod, get_base_name(d), d) for d in directory]
            if self.on_progress is not None:
                for future in futures:
                    future.add_done_callback(self.on_progress)
            for future in concurrent.futures.as_completed(futures):
                mod = future.result()
                if mod is not None:
                    mods.append(mod)

        self.on_finish(mods)

    def run(self):
        """
        Runs the thread
        """
        if isinstance(self.directory, str):
            if is_valid_dir(self.directory):
                self.find_mods(self.directory)
        elif isinstance(self.directory, list):
            if False not in [is_valid_dir(d) for d in self.directory]:
                self.find_mods(self.directory)
