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

def get_direct_child_by_extension(directory, extension):
    list = []
    for filename in os.listdir(directory):
        if filename.endswith(extension) and os.path.isfile(os.path.join(directory, filename)):
            list.append(filename)
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

# returns formatted version(e.g. 1.0 -> 1.0.0) 
def format_version(input_str):
    segments = input_str.split('.')
    
    while len(segments) < 3:
        segments.append('0')

    formatted_version = '.'.join(segments)
    return formatted_version

def slots_to_string(slots):
    ranges = []
    current_idx = 0
    out_str = ""
    start = slots[0] 
    prev = slots[0]
    if not isinstance(start,int):
        ranges.append("C" + start)
    else:
        ranges.append("C" + f"{start:02}")

        for n in range(1, len(slots)):
            if prev + 1 == slots[n]:
                ranges[current_idx] = "C" + f"{start:02}" + "-" + f"{slots[n]:02}"
            else:
                current_idx+=1
                ranges.append("C" + f"{slots[n]:02}")
                start = slots[n]
            prev = slots[n]

    for item in ranges:
        if not out_str:
            out_str += item
        else:
            out_str += ", " + item
    
    return out_str

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
    dict_arr = csv_to_dict("./character_names.csv") 
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
        dict_arr = csv_to_dict("./character_names.csv")
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