"""
mod_loader.py: class that scans mod folders to automatically find
included elements
"""

import os
import copy
from threading import Thread
from typing import Union
from src.utils.file import (
    sanitize_path,
    is_valid_dir,
    is_valid_file,
    rename_folder,
    copy_directory_contents
)
from src.utils.string_helper import (
    remove_spacing
)
from src.utils.common import get_project_dir
from src.core.data import load_config
from src.models.mod import Mod
from src.core.mod_loader import ModLoader
from src.core.formatting import (
    group_char_name,
    format_slots,
    format_folder_name
)

ZIP_EXTENTIONS = [
    ".zip", 
    ".7z"
]

ROOT_CHILDREN = [
    "camera", 
    "effect", 
    "fighter", 
    "sound", 
    "stage", 
    "item", 
    "stream;", 
    "ui", 
    "config.json", 
    "plugin.nro", 
    "victory.toml", 
    "preview.webp", 
    "info.toml",
    "info.ini"
]

def get_mod_root(file_path:str)->str:
    """Get the root mod directory"""
    is_root = False
    path_list = os.listdir(file_path)

    if len(path_list) > 0:
        for name in path_list:
            if name in ROOT_CHILDREN:
                is_root = True
                break
        if is_root:
            return file_path
        elif is_valid_dir(os.path.join(file_path, name)):
            return get_mod_root(os.path.join(file_path, name))
        else:
            return ""
    else: 
        return ""

from pyunpack import Archive
import tempfile
        
class ModInstaller(Thread):
    """
    Adds mods to working directory in another thread
    Can add folders, zip files containing the mod.
    """
    def __init__(
        self,
        directory:Union[str, list],
        root_dir:str,
        on_finish:callable,
        on_start:callable = None,
        on_progress:callable = None,
        on_dup_error:callable = None,
        on_per_error:callable = None
    ):
        super().__init__()
        self.directory = directory
        self.root_dir = root_dir
        self.on_finish = on_finish
        self.on_start = on_start
        self.on_progress = on_progress
        self.on_dup_error = on_dup_error
        self.on_per_error = on_per_error
        self.daemon = True
        self.start()

    def run(self):
        if isinstance(self.directory, list):
            pass
        if isinstance(self.directory, str):
            if self.directory.endswith(".zip") and is_valid_file(self.directory):
                result = self.unzip_file(self.directory)
                if result:
                    ModLoader([result], self.rename_unzipped)
            else:
                self.directory = get_mod_root(self.directory)
                ModLoader([self.directory], self.add_mods)

    def add_mods(self, mods:list[Mod]):
        results = [self.add_mod(mod) for mod in mods]
        self.on_finish(results)

    def add_mod(self, mod:Mod)->str:
        if mod is None:
            return ""
    
        mod_path = mod.path
        keys, names, groups, series, slots = mod.get_character_data()

        folder_name = format_folder_name(
            remove_spacing(group_char_name(names, groups)),
            remove_spacing(format_slots(slots)),
            remove_spacing(mod.mod_name),
            remove_spacing(mod.category)
        )
        
        new_dir = os.path.join(self.root_dir, folder_name)
        new_name = folder_name

        if os.path.exists(new_dir): 
            num = 0
            while os.path.exists(new_dir): 
                num+=1
                new_name = f"{folder_name}{num}"
                new_dir = os.path.join(self.root_dir, new_name)
        try:
            copy_directory_contents(mod_path, self.root_dir, new_name)
            print("successfully added dir:", mod_path)
            return new_dir
        except PermissionError:
            print(f"PermissionError: You do not have the required permissions to copy to '{new_dir}'.")
            return ""
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return ""
        
    def unzip_file(self, input_path:str)->str:
        with tempfile.TemporaryDirectory() as temp_dir:
            Archive(input_path).extractall(temp_dir)
            files = os.listdir(temp_dir)
            if len(files) > 0:
                folder_name = files[0]    
                folder_dir = os.path.join(temp_dir, folder_name)
                folder_dir = get_mod_root(folder_dir)

                new_dir = os.path.join(self.root_dir, folder_name)
                new_name = folder_name

                if os.path.exists(new_dir): 
                    num = 0
                    while os.path.exists(new_dir): 
                        num+=1
                        new_name = f"{folder_name}{num}"
                        new_dir = os.path.join(self.root_dir, new_name)
                try:
                    copy_directory_contents(folder_dir, self.root_dir, new_name)
                    print("successfully added dir:", folder_dir)
                    return new_dir
                except PermissionError:
                    print(f"PermissionError: You do not have the required permissions to copy to '{new_dir}'.")
                    return ""
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
                    return ""

    def rename_unzipped(self, mods:list[Mod]):
        results = []
        for mod in mods:
            if mod is None:
                return
    
            mod_path = mod.path
            keys, names, groups, series, slots = mod.get_character_data()

            folder_name = format_folder_name(
                remove_spacing(group_char_name(names, groups)),
                remove_spacing(format_slots(slots)),
                remove_spacing(mod.mod_name),
                remove_spacing(mod.category)
            )
            
            new_name = folder_name
            new_dir = os.path.join(self.root_dir, new_name)
            if os.path.exists(new_dir): 
                num = 0
                while os.path.exists(new_dir): 
                    num+=1
                    new_name = f"{folder_name}{num}"
                    new_dir = os.path.join(self.root_dir, new_name)

            result, msg = rename_folder(mod_path, new_dir)
            results.append(new_dir)
        self.on_finish(results)
