"""
Module that contains various methods to format strings used in this application
"""

import re
from src.core.data import load_config, get_folder_name_format, get_display_name_format
from src.utils.csv_helper import csv_to_dict, csv_to_key_value
from src.utils.string_helper import (
    remove_texts,
    remove_special_chars,
    remove_non_eng,
    remove_paranthesis,
    remove_redundant_spacing,
    add_spaces_to_camel_case,
    trim_consecutive,
    SPECIAL_CHARS,
    BLACKLIST_CHARS
)

from data import PATH_CHAR_NAMES

def format_folder_name(characters:str, slots:str, mod_name:str, category:str):
    format = get_folder_name_format()
    folder_name = format.replace("{characters}", characters)
    folder_name = folder_name.replace("{slots}", slots)
    folder_name = folder_name.replace("{mod}", mod_name)
    folder_name = folder_name.replace("{category}", category)
    return clean_folder_name(folder_name)

def format_display_name(characters:str, slots:str, mod_name:str, category:str):
    format = get_display_name_format()
    display_name = format.replace("{characters}", characters)
    display_name = display_name.replace("{slots}", slots)
    display_name = display_name.replace("{mod}", mod_name)
    display_name = display_name.replace("{category}", category)
    return clean_display_name(display_name)

def format_character_names(characters:list[str]):
    return ", ".join(sorted(characters))

def format_slots(slots:list[int]):
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
    is_cap = loaded_config.is_slot_capped
    if is_cap == False:
        slot_prefix = "c"
        
    return slot_prefix + out_str

def remove_characters(text:str, characters:list[str]):
    text = text.replace("&", " ")
    arr_to_remove = []
    set_char = set()
    char_dict = csv_to_key_value(PATH_CHAR_NAMES)
    
    for key in characters:
        set_char.add(key)
        data = char_dict.get(key, None)
        if data is None: 
            continue
        
        val = data[0]
        custom = data[1]
        group = data[2]
        alt = data[4]
        gender = data[5]
        
        if alt:
            set_char.add(alt)
        
        for v in data[:2]:
            if v:
                set_char.add(v)
                if gender == "True":
                    set_char.add(v+".M")
                    set_char.add(v+".F")

        if group:
            set_char.add(group)
            set_char.add(group + val)
            set_char.add(group + custom)
            set_char.add(group + " " + val)
            set_char.add(group + " " + custom)
    
    list_char = list(set_char)
    for item in list_char:
        set_char.add(remove_special_chars(item))
        set_char.add(remove_special_chars(item).replace(" ", ""))
        set_char.add(remove_non_eng(item))
        set_char.add(remove_non_eng(item).replace(" ", ""))
    arr_to_remove = list(set_char)
    arr_to_remove = sorted(arr_to_remove, key=len, reverse=True)
    text = remove_texts(text, arr_to_remove)
    return text

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

def get_mod_name(display_name:str, character_keys:list, slots:list, category:str)->str:
    def remove_numbers(text:str, numbers:list):
        pattern = r'(?<![^\s_Cc\-])[Cc]?0*(' + '|'.join(map(str, numbers)) + r')(?![^\s_Cc\-])'
        matches = re.finditer(pattern, text)
        match_at_end = None
        for match in matches:
            if match.end() == len(text):
                match_at_end = match.group() 
                if "C"  in match_at_end or "c" in match_at_end:
                    match_at_end = None
                break 
        
        text = re.sub(pattern, '', text).strip()
        if match_at_end is not None:
            text = text + " " + match_at_end
        return text

    name = remove_texts(display_name, [category])
    name = remove_special_chars(name)
    name = remove_characters(name, character_keys)
    name = remove_texts(name, ["Even Slots", "Odd Slots", "EvenSlots", "OddSlots", "Even", "Odd"])
    name = remove_numbers(name, slots)
    name = clean_mod_name(name)
    name = remove_paranthesis(name)
    if len(name) > 4:
        name = add_spaces_to_camel_case(name)
    return name

def trim_mod_name(mod_name, ignored_list):
    words_pattern = '|'.join(re.escape(word) for word in ignored_list)
    pattern = r'\b(?:' + words_pattern + r')\b'
    return re.sub(pattern, '', mod_name)

def clean_mod_name(mod_name:str)->str:
    def substitute_characters(text:str, chars_to_substitute:list)->str:
        """
        Removes characters from string
        """
        chars_set = set(chars_to_substitute)
        result = ''.join([char if char not in chars_set else ' ' for char in text])
        return result

    pattern = r"^(.*?)\s+over\s+"
    match = re.match(pattern, mod_name)
    if match:
        mod_name = match.group(1)
    mod_name = substitute_characters(mod_name, SPECIAL_CHARS)
    mod_name = remove_redundant_spacing(mod_name)
    return mod_name

def clean_display_name(display_name:str)->str:
    """
    Returns cleaned display name
    """
    display_name = display_name.replace("[]", "")
    display_name = display_name.replace("()", "")
    display_name = display_name.replace("{}", "")

    display_name = remove_redundant_spacing(display_name)
    display_name = trim_consecutive(display_name, [",", ".", "_", "-", "~"])
    return display_name 

def clean_folder_name(folder_name:str)->str:
    """
    Returns cleaned folder name
    """
    for b in BLACKLIST_CHARS:
        folder_name = folder_name.replace(b, " ")
    folder_name = folder_name.replace("[]", "")
    folder_name = folder_name.replace("()", "")
    folder_name = folder_name.replace("{}", "")
    folder_name = folder_name.replace(" ", "")
    folder_name = trim_consecutive(folder_name, [",", ".", "_", "-", "~"])
    return folder_name

def clean_version(version:str)->str:
    """
    Returns formatted version(e.g. v1.0 -> 1.0.0)
    """
    parts = version.split('.')
    if len(parts) <= 0:
        return "1.0.0"

    numeric_parts = []
    for part in parts :
        if part:
            numbers = filter(str.isdigit, part)
            numeric_parts.append(''.join(numbers))

    diff = 3 - len(numeric_parts)
    for n in range(diff):
        numeric_parts.append('0')

    formatted_version = '.'.join(numeric_parts)
    return formatted_version

def clean_description(description:str)->str:
    description = description.strip()
    return description
