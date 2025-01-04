import os
import sys
from pathlib import Path

def is_valid_path(path:str)->bool:
    return os.path.exists(path)

def is_valid_dir(dir:str)->bool:
    return is_valid_path(dir) and os.path.isdir(dir)
    
def is_valid_file(dir:str)->bool:
    return is_valid_path(dir) and Path(dir).is_file()

def get_base_name(directory:str)->str:
    return os.path.basename(directory)

def get_parent_dir(dir:str)->str:
    return Path(dir).parent

def sanitize_path(dir:str)->str:
    return os.path.normpath(dir)

def get_project_dir():
    return os.path.abspath(os.path.dirname(sys.argv[0]))

# Split the folder name into array
def split_into_arr(folder_name, split_char = '_'):
    return folder_name.split(split_char)
    
def clamp(n, smallest, largest): return max(smallest, min(n, largest))