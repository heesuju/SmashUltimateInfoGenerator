import json
import os

import sys
import shutil

from data.cache import PATH_CONFIG
from pathlib import Path
from os import listdir
from src.utils.file import is_valid_path, is_valid_file
from src.models.settings import Settings

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