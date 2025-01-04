import json
import os

import sys
import shutil

from data.cache import PATH_CONFIG
from pathlib import Path
from os import listdir
from src.utils.file import is_valid_path, is_valid_file

def load_config():
    if(is_valid_file(PATH_CONFIG)):
        try:
            json_file = open(PATH_CONFIG, "r")
            data = json.loads(json_file.read())
            json_file.close()
            print("Loaded config")
            return data
        except Exception as e:
            print(f"error: {e}")
            return None
    else:
        print("No saved config")
        return None
    
def get_cache_directory(default_dir:str = ""):
    if not default_dir:
        config = load_config()
        default_dir = config["default_directory"]

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

def get_workspace():
    return load_config().get("workspace", "Default")

def get_folder_name_format():
    return load_config().get("folder_name_format")

def get_display_name_format():
    return load_config().get("display_name_format")

def get_start_w_editor():
    config = load_config()
    if config:
        return config.get("start_w_editor", False)
            
    return False

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