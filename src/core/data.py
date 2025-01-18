import json
import os

import sys
import shutil

from data.cache import PATH_CONFIG
from data import PATH_CHAR_NAMES
from pathlib import Path
from os import listdir
from src.utils.file import is_valid_path, is_valid_file
from src.utils.toml import dump_toml
from src.utils.csv_helper import csv_to_dict
from src.models.settings import Settings
from src.models.mod import Mod
from src.utils.file import (
    get_parent_dir,
    get_direct_child_by_extension,
    rename_folder,
    copy_file
)
from threading import Thread, Event
import concurrent.futures

def load_config()->Settings:
    if(is_valid_file(PATH_CONFIG)):
        try:
            json_file = open(PATH_CONFIG, "r")
            data = json.loads(json_file.read())
            settings = Settings(**data)
            json_file.close()
            print("Loaded config")
            return settings
        except Exception as e:
            print(f"error: {e}")
        
    print("No saved config")
    return Settings()
    
def get_cache_directory(default_dir:str = ""):
    if not default_dir:
        config = load_config()
        default_dir = config.default_directory

    if is_valid_path(default_dir):
        preset_path = default_dir
        path = Path(default_dir)
        preset_path = os.path.join(path.parent.absolute(), "arcropolis", "config")
        
        if is_valid_path(preset_path):
            config_folders = listdir(preset_path)
            if len(config_folders) == 1:
                preset_path = os.path.join(preset_path, config_folders[0])
                config_folders = listdir(preset_path)
                if len(config_folders) == 1:
                    preset_path = os.path.join(preset_path, config_folders[0])
                    return preset_path
    return ""

def get_workspace()->str:
    config = load_config()
    return config.workspace

def get_folder_name_format()->str:
    return load_config().folder_name_format

def get_display_name_format()->str:
    return load_config().display_name_format

def get_start_w_editor()->bool:
    return load_config().start_with_editor

def remove_cache():
    project_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    folder_path = os.path.join(project_dir, 'cache', 'thumbnails')
    
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Remove file or link
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Remove directory
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

def get_characters()->list[str]:
    names = csv_to_dict(PATH_CHAR_NAMES, "Key")
    names = sorted(names)
    return names

def generate_toml(mod:Mod):
    result = False
    data = mod.to_dict()
    
    dump_toml(
        mod.path,
        data
    )

    if mod.path:
        old_dir = mod.path
        new_dir = os.path.join(get_parent_dir(mod.path), mod.folder_name) 
        result, msg = rename_folder(old_dir, new_dir)
    
    return result

def generate_batch(mods:list[Mod]):
    complete = 0
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(generate_toml, mod) for mod in mods]
        
        for future in concurrent.futures.as_completed(futures):
            if future.result() == False:
                print("generation failed")
            else:
                complete+=1

    print(f"{complete} items updated.")