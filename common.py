import os
import re
import sys
import csv
import math
from data import PATH_CHAR_NAMES
from utils.load_config import load_config

def get_project_dir():
    return os.path.abspath(os.path.dirname(sys.argv[0]))

def trim_url(url:str)->str:
    parts = url.split("/")
    return parts[-1]

# Split the folder name into array
def split_into_arr(folder_name, split_char = '_'):
    return folder_name.split(split_char)

def trim_redundant_spaces(input, split_char = ' '):
    arr = input.split(split_char)
    result = ""
    
    for it in arr:
        if result:
            result += " " + it
        else:
            result += it
    
    return result

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

def is_valid_dir(directory:str)->bool:
    if directory:
        return os.path.exists(directory) and os.path.isdir(directory)
    else:
        return False

def get_children_by_extension(directory, extension):
    list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                list.append(file)
    return list

def get_direct_child_by_extension(directory, extension):
    list = []
    for filename in os.listdir(directory):
        if filename.endswith(extension) and os.path.isfile(os.path.join(directory, filename)):
            list.append(filename)
    return list

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

def get_all_children_in_path(directory):
    all_items = os.listdir(directory)
    # Filter out only the subdirectories
    child_folders = [item for item in all_items if os.path.isdir(os.path.join(directory, item))]
    return child_folders

def slots_to_string(slots):
    if len(slots) <= 0:
        return ""
    
    ranges = []
    current_idx = 0
    out_str = ""
    start = slots[0] 
    prev = slots[0]
    if not isinstance(start,int):
        ranges.append(start)
    else:
        ranges.append(f"{start:02}")

        for n in range(1, len(slots)):
            if prev + 1 == slots[n]:
                ranges[current_idx] = f"{start:02}" + "-" + f"{slots[n]:02}"
            else:
                current_idx+=1
                ranges.append(f"{slots[n]:02}")
                start = slots[n]
            prev = slots[n]

    for item in ranges:
        if not out_str:
            out_str += item
        else:
            out_str += "," + item
    
    slot_prefix = "C"
    loaded_config = load_config()
    if loaded_config is not None:
        is_cap = loaded_config.get("is_slot_capped")
        if is_cap == False:
            slot_prefix = "c"
            
    return slot_prefix + out_str

def trim_mod_name(mod_name, ignored_list):
    words_pattern = '|'.join(re.escape(word) for word in ignored_list)
    pattern = r'\b(?:' + words_pattern + r')\b'
    return re.sub(pattern, '', mod_name)

def is_valid_url(url):
    pattern = r'https://gamebanana\.com/.*/\d+'
    
    if re.match(pattern, url):
        print("Valid url")
        return True
    else:
        print("Invalid url")
        return False
    
def group_char_name(char_names, group_names):
    outstr = ""
    names_by_group = {}
    for n in range(len(char_names)):
        if group_names[n] in names_by_group.keys():
            arr = names_by_group[group_names[n]]
        else:
            arr = []
        arr.append(char_names[n])
        names_by_group.update({group_names[n]: arr})

    for key, value in names_by_group.items():
        names = ""
        if key: names += key

        if len(value) < get_group_count(key): # skip other names if everything is included
            for n in range(len(value)):
                if n > 0: names +=  " & " + value[n]
                elif key: names += " " + value[n]
                else: names += value[n]
        
        if outstr: outstr += " & " + names
        else: outstr += names
            
    return outstr

def get_group_count(group_name):
    dict_arr = csv_to_dict(PATH_CHAR_NAMES) 
    count = 0

    for dict in dict_arr:
        if group_name == dict['Group']:
            count+=1

    return count

def add_spaces_to_camel_case(input_string):
    result = [input_string[0]]
    
    for i in range(1, len(input_string)):
        char = input_string[i]
        prev_char = input_string[i - 1]
        
        if char.isupper() and prev_char.islower():
            result.append(' ')
        result.append(char)
    
    return ''.join(result)

def get_formatted_elements(format, str):
    escaped_input = re.escape(format)
    #regex_pattern = escaped_input.replace(r'\{', r'(?P<').replace(r'\}', r'>\w+)')
    regex_pattern = escaped_input.replace(r'\{', r'(?P<').replace(r'\}', r'>.+)')
    match = re.match(regex_pattern, str)

    if match:
        print("String matched!")
        return match.groupdict()
    else:
        slot_removed = format
        slot_removed = slot_removed.replace("[{slots}]", "")
        escaped_input = re.escape(slot_removed)
        #regex_pattern = escaped_input.replace(r'\{', r'(?P<').replace(r'\}', r'>\w+)')
        regex_pattern = escaped_input.replace(r'\{', r'(?P<').replace(r'\}', r'>.+)')
        match = re.match(regex_pattern, str)
        if match: 
            print("String matched!")
            return match.groupdict()
        print("String did not match the pattern.")
        return None
    
# trims the character name and category from the folder name to get the mod title
def get_mod_title(original, char_names, folder_name_format):
    dict_elements = get_formatted_elements(folder_name_format, original)
    if dict_elements is not None:
        return dict_elements["mod"]
    else:
        dict_arr = csv_to_dict(PATH_CHAR_NAMES)
        set_name = set()
        for dict in dict_arr:
            if dict['Custom'] in char_names:
                #set_name.add(dict['Key'])
                set_name.add(dict['Value'])
                set_name.add(dict['Custom'])
                if dict['Group']:
                    set_name.add(dict['Group'])

        # Create a regular expression pattern to match words to remove and underscore
        pattern = r'|'.join(re.escape(name) for name in set_name) + r'|'
        pattern += r'|_|&'  # Add underscore to the pattern
        
        name = re.sub(r'(C\d+|\[.*?\]|' + pattern + ')', '', original, flags=re.I)

        #Remove spaces
        trimmed_arr = name.split(' ')
        out_str=""
        for trimmed in trimmed_arr:
            if out_str: 
                out_str += ' '
            out_str += trimmed
        
        return out_str
    
def clamp(n, smallest, largest): return max(smallest, min(n, largest))

def get_pages(current_page=1, total_pages=1, max_size=5):
    out_arr = []
    half = math.floor(max_size/2)
    min = clamp(current_page-half, 1, total_pages)
    max = clamp(current_page+half, 1, total_pages)
    if current_page-half < 1:
        max -= (current_page-half - 1)
    elif current_page+half > total_pages:
        min -= (current_page+half - total_pages)

    if total_pages < max_size:
        min = 1
        max = total_pages
        
    for n in range(min, max+1):
        out_arr.append(n) 
    
    if 1 not in out_arr:
        out_arr.append(1)
    
    if total_pages not in out_arr:
        out_arr.append(total_pages)
    
    out_arr.sort()
    return out_arr

def get_completion(text:str, values:list)->None:
    if not text:
        return ""
    elif text not in values:
        for cat in values:
            if text.lower() in cat.lower():
                return cat
        return ""
    else:
        return text
    
def get_edit_distance(text1:str, text2:str)->float: