"""
filter.py: contains methods for filter/sorting
"""

from src.models.mod import Mod
from data import PATH_CHAR_NAMES
from src.utils.csv_helper import csv_to_dict
from src.utils.edit_distance import get_completion
from src.core.data import load_config

def sort_by_columns(data:list[Mod], sort_config:list):
    """
    Sorts a list of objects by specified columns and orders.
    
    Parameters:
        data (list): List of objects to be sorted.
        sort_config (list): List of dictionaries specifying 'column' and 'order'.
    
    Returns:
        list: Sorted list of objects.
    """

    columns = [s["column"] for s in sort_config]
    orders = [s["order"] for s in sort_config]

    data_sorted = sorted(
        data,
        key=lambda x: tuple(
            (getattr(x, col), -1 if order == 'Descending' else 1)
            for col, order in zip(columns, orders)
        )
    )

    for i in reversed(range(len(columns))):
        reverse = orders[i] == 'Descending'
        data_sorted.sort(
            key=lambda x: getattr(x, columns[i]),
            reverse=reverse
        )

    return data_sorted

def get_similar_character(text:str, values:list)->None:
    result = ""
    if len(values) == 1:
        result = values[0]
    elif len(values) > 1:
        chars = csv_to_dict(PATH_CHAR_NAMES)
        options = set()
        for c in chars:
            name = c.get("Custom")
            if name in values:
                key = c.get("Key")
                org = c.get("Value")
                alt = c.get("Alt")
                if key: 
                    options.add(key)
                if org:
                    options.add(org)
                if alt:
                    options.add(alt)
                options.add(name)
        options.add("All")
        sorted_list = list(options)
        sorted_list = sorted(sorted_list)
        match = get_completion(text, sorted_list)
        
        result = "All" if "All" in values else values[0]

        for c in chars:
            name = c.get("Custom")
            key = c.get("Key")
            org = c.get("Value")
            alt = c.get("Alt")
            if match == name:
                result = name
                break
            elif match == key:
                result = name
                break
            elif match == org:
                result = name
                break
            elif match == alt:
                result = name
                break
    return result

def get_series(character_key:str):
    """
    Get series by the character key
    """
    data = csv_to_dict(PATH_CHAR_NAMES)
    for d in data:
        if d.get("Key") ==  character_key:
            return d.get("Series").lower()

def filter_mods(mods:list[Mod], filter_params:dict, enabled_list:list = []):
    """
    Filters and sorts the list of mods to show
    """
    outputs = []

    for mod in mods:
        if filter_params.get("enabled_only", False):
            if mod.hash not in enabled_list: 
                continue

        if filter_params.get("mod_name") not in mod.mod_name.lower(): 
            continue

        if filter_params.get("authors") not in mod.authors.lower(): 
            continue

        if filter_params.get("characters") != "all":
            found_match = False
            for ch in mod.character_names:
                if ch.lower() == filter_params.get("characters"):
                    found_match = True
                    break

            if  found_match == False: 
                continue

        if filter_params.get("series") != "all":
            should_include = False
            for char_name in mod.character_keys:
                if filter_params.get("series") == get_series(char_name):
                    should_include = True

            if should_include == False:
                continue

        if filter_params.get("category") != "all":
            if filter_params.get("category") != mod.category.lower():
                continue

        if filter_params.get("info_toml") != "all":
            if filter_params.get("info_toml") == "included" and mod.contains_info == False:
                continue

            elif filter_params.get("info_toml") == "not included" and mod.contains_info == True:
                continue

        if filter_params.get("wifi_safe") != "all":
            if filter_params.get("wifi_safe") != mod.wifi_safe.lower():
                continue

        if filter_params.get("slot_from") or filter_params.get("slot_to"):
            contains_slot = False
            min_slot = int(filter_params.get("slot_from") if filter_params.get("slot_from") else 0)
            max_slot = int(filter_params.get("slot_to") if filter_params.get("slot_to") else 255)

            if max_slot >= min_slot:
                for slot in mod.character_slots:
                    if slot >= min_slot and slot <= max_slot:
                        contains_slot = True
                        break

            if contains_slot == False:
                continue

        outputs.append(mod)

    sort_prioirty = load_config().get("sort_priority", None)
    if sort_prioirty is not None:
        return sort_by_columns(outputs, sort_prioirty)
    else:
        return outputs
