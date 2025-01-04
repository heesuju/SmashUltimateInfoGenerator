import os
import re
import sys
import csv
from data import PATH_CHAR_NAMES

def str_to_int(s:str, start_index:int = 0)->int:
    text = str(s[start_index:]) 
    num = 0
    if text.isdigit():
        num = int(text)

    return num

def get_project_dir():
    return os.path.abspath(os.path.dirname(sys.argv[0]))

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

def csv2dict(directory:str):
    output = {}
    
    with open(directory, mode='r', newline='') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            key = row[0]
            values = row[1:]
            output[key] = values
    return output

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

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

def get_cleaned(text:str)->str:
    text = text.lower()
    text = text.replace(" ", "")
    text = text.replace(".", "")
    return text

def get_completion(text:str, values:list)->None:
    if not text:
        return ""
    elif text not in values:
        min_num = 20.0
        min_text = ""
        for cat in values:
            dist = get_edit_distance(get_cleaned(text), get_cleaned(cat))
            if dist == min_num:
                if get_cleaned(text) not in get_cleaned(min_text):
                    min_text = cat
            elif dist < min_num:
                min_num = dist
                min_text = cat
        return min_text
    else:
        return text
    
def get_edit_distance(text1:str, text2:str)->float:
    if len(text1) > len(text2):
        text1, text2 = text2, text1
    
    distances = range(len(text1) + 1)
    for idx2, char2 in enumerate(text2):
        distances_ = [idx2 + 1]
        for idx1, char1 in enumerate(text1):
            if char1 == char2:
                distances_.append(distances[idx1])
            else:
                distances_.append(1 + min((distances[idx1], distances[idx1 + 1], distances_[-1])))
        distances = distances_

    def normalize(a:str, b:str, distance:float)->float:
        max_len = max(len(a), len(b))
        return distance/max_len

    return normalize(text1, text2, distances[-1])

