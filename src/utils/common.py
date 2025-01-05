"""
common.py: contains shared utility methods
"""

import os
import sys
from pathlib import Path

def is_valid_path(path:str)->bool:
    """
    Check whether the path exists
    """
    return os.path.exists(path)

def is_valid_dir(directory:str)->bool:
    """
    Check whether the path is a valid directory
    """
    return is_valid_path(directory) and os.path.isdir(directory)

def is_valid_file(directory:str)->bool:
    """
    Check whether the directory is a valid file
    """
    return is_valid_path(directory) and Path(directory).is_file()

def get_base_name(directory:str)->str:
    """
    get the file name from the directory
    """
    return os.path.basename(directory)

def get_parent_dir(directory:str)->str:
    """
    get the parent directory
    """
    return Path(directory).parent

def sanitize_path(directory:str)->str:
    """
    gets the sanitized path
    """
    return os.path.normpath(directory)

def get_project_dir():
    """
    get the project root directory
    """
    return os.path.abspath(os.path.dirname(sys.argv[0]))

def split_into_arr(folder_name, split_char = '_'):
    """
    Split the folder name into array
    """
    return folder_name.split(split_char)

def clamp(n, smallest, largest):
    """
    limits number between smallest and largest
    """
    return max(smallest, min(n, largest))
