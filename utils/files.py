import os

def is_valid_dir(directory:str)->bool:
    if directory:
        return os.path.exists(directory) and os.path.isdir(directory)
    else:
        return False
    
def get_dir_name(directory):
    return os.path.basename(directory)

def rename_if_valid(dir:str, new_folder_name:str):
    output = ""
    
    old_dir = dir
    dir_name = get_dir_name(old_dir)
    new_dir = old_dir[0:-len(dir_name)]
    new_dir = os.path.join(new_dir, new_folder_name)
    
    if is_valid_dir(old_dir):
        if rename_folder(old_dir, new_dir):
            output = new_dir
    
    return output

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