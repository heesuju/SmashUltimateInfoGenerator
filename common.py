import os
import re
import csv

# Split the folder name into array
def split_into_arr(folder_name, split_char = '_'):
    return folder_name.split(split_char)

def search_dir_for_keyword(directory, keyword):
    for root, dirs, files in os.walk(directory):
        if keyword in dirs:
            return True
    return False
    
def search_files_for_pattern(file, pattern):
    if re.search(pattern, file):
        return True
    return False

def get_dir_name(directory):
    return os.path.basename(directory)

def is_valid_dir(directory):
    return os.path.exists(directory) and os.path.isdir(directory)

def get_children_by_extension(directory, extension):
    list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                list.append(file)
    return list

def csv_to_dict(directory):
    data_list = []
    
    with open(directory, mode='r', newline='') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            data_list.append(row)
    
    return data_list

def get_all_children_in_path(directory):
    all_items = os.listdir(directory)
    # Filter out only the subdirectories
    child_folders = [item for item in all_items if os.path.isdir(os.path.join(directory, item))]
    return child_folders