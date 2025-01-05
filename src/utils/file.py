"""
file.py: contains various methods for handling file related tasks
"""

import os
import json
import shutil
import random
import string
import tempfile
import re
from .common import *

def generate_unique_name(base_name: str) -> str:
    """
    Generates a unique random string for temporary files
    """
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{base_name}_{random_suffix}"

def is_folder_locked(folder_path)->bool:
    """
    Checks whether the folder is locked or not due to existing processes
    """
    try:
        os.rename(folder_path, folder_path)
        return False
    except OSError:
        return True

def rename_folder(old_dir:str, new_dir:str):
    """
    renames a folder
    """
    result = False
    msg = ""
    old_dir = sanitize_path(old_dir)
    new_dir = sanitize_path(new_dir)

    if is_valid_dir(old_dir):
        if is_folder_locked(old_dir):
            msg = """Folder is currently locked.
            Please close file processes and try again."""
        else:
            try:
                if old_dir != new_dir:
                    tmp_name = old_dir
                    if old_dir.lower() == new_dir.lower():
                        tmp_name = generate_unique_name(old_dir)
                        os.rename(old_dir, tmp_name)
                    os.rename(tmp_name, new_dir)
                    msg = f"Applied changes to {get_base_name(new_dir)}"
                else:
                    msg = f"Applied changes to {get_base_name(old_dir)}"
                result = True
            except PermissionError:
                msg = "Failed to rename folder due to file access privilege"
            except FileExistsError:
                msg = """Another folder with the same name already exists.
                Please change the folder name and try again."""
            except Exception:
                msg = "Unknown error occurred"
    else:
        msg = "Invalid directory"

    return result, msg

def is_case_sensitive()->bool:
    """
    Returns whether os is case sensitive or not
    """
    tmphandle, tmppath = tempfile.mkstemp()
    if os.path.exists(tmppath.upper()):
        return False
    else:
        return True

def read_json(json_path:str):
    """
    reads json as dict
    """
    result = None
    try:
        with open(json_path, mode='r', encoding='utf-8') as f:
            result = json.loads(f.read())
    except FileNotFoundError:
        print(f"Error: The file '{json_path}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file '{json_path}' is not a valid JSON.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return result

def copy_directory_contents(source_dir:str, new_dir_parent:str, new_dir_name:str):
    """
    copies all contents to another directory
    """
    new_dir_path = os.path.join(new_dir_parent, new_dir_name)
    os.makedirs(new_dir_path, exist_ok=True)

    # Copy all contents from the old directory to the new directory
    for item in os.listdir(source_dir):
        source_item = os.path.join(source_dir, item)
        destination_item = os.path.join(new_dir_path, item)

        if os.path.isfile(source_item):
            # If it's a file, copy it
            shutil.copyfile(source_item, destination_item)
        elif os.path.isdir(source_item):
            # If it's a directory, create it and copy its contents recursively
            os.makedirs(destination_item, exist_ok=True)
            # Recursively call this function to copy contents of the directory
            copy_directory_contents(source_item, new_dir_path, item)

def get_children(directory:str):
    """
    Returns child folders in the specified directory
    """
    child_folders = []
    if is_valid_dir(directory):
        all_items = os.listdir(directory)
        # Filter out only the subdirectories
        child_folders = [item for item in all_items if os.path.isdir(os.path.join(directory, item))]
    return child_folders

def search_dir_by_keyword(directory, keyword)->bool:
    """
    Scans subdirectories and returns whether children contain the specified keyword
    """
    for root, dirs, files in os.walk(directory):
        if keyword in dirs:
            return True
    return False

def get_direct_child_by_extension(directory, extension)->list:
    """
    Finds children with specified extension type
    Subdirectories are not scanned
    """
    children = []
    for filename in os.listdir(directory):
        if filename.endswith(extension) and os.path.isfile(os.path.join(directory, filename)):
            children.append(filename)
    return children

def get_children_by_extension(directory, extension)->list:
    """
    Finds children with specified extension type
    All subdirectories are scanned
    """
    children = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                children.append(file)
    return children

def search_files_for_pattern(file:str, pattern)->bool:
    """
    Returns whether the file name contains the specified pattern
    """
    if re.search(pattern, file):
        return True
    return False
