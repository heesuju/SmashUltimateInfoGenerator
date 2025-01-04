import os
import json
import csv
from pathlib import Path
import shutil
import random
import string
import tempfile
import re

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

def generate_unique_name(base_name: str) -> str:
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{base_name}_{random_suffix}"

def is_folder_locked(folder_path):
    try:
        os.rename(folder_path, folder_path)
        return False
    except OSError:
        return True 
    
def rename_folder(old_dir:str, new_dir:str):
    result = False
    msg = ""
    old_dir = sanitize_path(old_dir)
    new_dir = sanitize_path(new_dir)
    
    if is_valid_dir(old_dir):
        if is_folder_locked(old_dir):
            msg = "Folder is currently locked.\nPlease close any open File Explorer windows and try again."
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
            except PermissionError as e:
                msg = f"Failed to rename folder due to file access privilege"
            except FileExistsError as e:
                msg = "Another folder with the same name already exists.\nPlease change the folder name and try again."
            except Exception as e:
                msg = "Unknown error occurred"
    else:
        msg = f"Invalid directory"
    
    return result, msg

def is_case_sensitive():
    tmphandle, tmppath = tempfile.mkstemp()
    if os.path.exists(tmppath.upper()):
        return False
    else:
        return True

def read_json(json_path:str):
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
    finally:
        return result

def copy_directory_contents(source_dir:str, new_dir_parent:str, new_dir_name:str):
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
    child_folders = []
    if is_valid_dir(directory):
        all_items = os.listdir(directory)
        # Filter out only the subdirectories
        child_folders = [item for item in all_items if os.path.isdir(os.path.join(directory, item))]
    return child_folders

def search_dir_by_keyword(directory, keyword):
    for root, dirs, files in os.walk(directory):
        if keyword in dirs:
            return True
    return False

def csv_to_dict(directory, col_name:str = ""):
    data_list = []
    
    with open(directory, mode='r', newline='') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            if col_name:
                item = str(row.get(col_name, ""))
                if item not in data_list:
                    data_list.append(item)
            else:
                data_list.append(row)
    
    return data_list

def get_direct_child_by_extension(directory, extension):
    list = []
    for filename in os.listdir(directory):
        if filename.endswith(extension) and os.path.isfile(os.path.join(directory, filename)):
            list.append(filename)
    return list

def get_children_by_extension(directory, extension):
    list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                list.append(file)
    return list

def search_files_for_pattern(file, pattern):
    if re.search(pattern, file):
        return True
    return False