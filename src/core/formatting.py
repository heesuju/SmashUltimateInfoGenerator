import re
from src.core.data import load_config, get_folder_name_format, get_display_name_format
from src.utils.csv_helper import csv_to_dict, csv_to_key_value
from src.utils.string_helper import (
    clean_folder_name,
    clean_display_name,
    remove_text,
    remove_special_chars,
    remove_non_eng,
    remove_numbers,
    clean_mod_name,
    remove_paranthesis,
    add_spaces_to_camel_case,
    add_spacing
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
    format = get_display_name_format
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
    if loaded_config is not None:
        is_cap = loaded_config.get("is_slot_capped")
        if is_cap == False:
            slot_prefix = "c"
            
    return slot_prefix + out_str

def remove_characters(text:str, characters:list[str]):
    text = add_spacing(text)
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
    text = remove_text(text, arr_to_remove)
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
    name = remove_text(display_name, [category])
    name = remove_special_chars(name)
    name = remove_characters(name, character_keys)
    name = remove_text(name, ["Even Slots", "Odd Slots", "EvenSlots", "OddSlots", "Even", "Odd"])
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