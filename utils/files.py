import os
import json
from pathlib import Path
import shutil

def is_valid_dir(directory:str)->bool:
    if directory:
        return os.path.exists(directory) and os.path.isdir(directory)
    else:
        return False
    
def is_valid_file(directory:str)->bool:
    file = Path(directory)
    return file.is_file()
    
def get_dir_name(directory):
    return os.path.basename(directory)

def rename_if_valid(dir:str, new_folder_name:str):
    output = ""
    msg = ""

    old_dir = dir
    dir_name = get_dir_name(old_dir)
    new_dir = old_dir[0:-len(dir_name)]
    new_dir = os.path.join(new_dir, new_folder_name)
    
    if is_valid_dir(old_dir):
        if is_valid_dir(new_dir) == False:
            if rename_folder(old_dir, new_dir):
                output = new_dir
                msg = f"Applied changes to {new_folder_name}"
        else:
            msg = f"File name {new_folder_name} already exists."
    else:
        msg = f"Cannot find {dir}"
    
    return output, msg

def rename_folder(old_dir:str, new_dir:str):
    result = False
    if is_folder_locked(old_dir):
        print("Folder is currently in use. Please close any open windows and try again.")
        return result
    try:
        os.rename(old_dir, new_dir)
        print(f"Successfully renamed folder {old_dir} to {new_dir}")
        result = True
    except PermissionError as e:
        print(f"Failed to rename folder due to permission error: {e}")
    except FileExistsError as e:
        print(f"Existing folder with the same name: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        return result

def is_folder_locked(folder_path):
    try:
        os.rename(folder_path, folder_path)
        return False
    except OSError:
        return True 
    
def read_json(json_path:str):
    with open(json_path, mode='r', encoding='utf-8') as f:
        return json.loads(f.read())

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