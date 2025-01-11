"""
filter.py: contains methods for filter/sorting
"""

from src.models.mod import Mod
from data import PATH_CHAR_NAMES
from src.constants.defs import SLOT_RULE
from src.utils.csv_helper import csv_to_dict
from src.utils.edit_distance import get_completion
from src.core.data import load_config
from src.models.filter_params import FilterParams

def sort_by_columns(data:list[Mod], sort_config:list[dict]):
    """
    Sorts a list of objects by specified columns and orders.
    
    Parameters:
        data (list): List of objects to be sorted.
        sort_config (list): List of dictionaries specifying 'column' and 'order'.
    
    Returns:
        list: Sorted list of objects.
    """

    def get_nested_attr(obj, attr):
        """Helper function to get nested attributes."""
        for part in attr.split('.'):
            if isinstance(obj, list):
                obj = [getattr(item, part) for item in obj]
            else:
                obj = getattr(obj, part)
        return obj
    
    columns = [sort.get("column") for sort in sort_config]
    orders = [sort.get("order") for sort in sort_config]

    data_sorted = sorted(
        data,
        key=lambda x: tuple(
            (get_nested_attr(x, col), -1 if order == 'Descending' else 1)
            for col, order in zip(columns, orders)
        )
    )

    for i in reversed(range(len(columns))):
        reverse = orders[i] == 'Descending'
        data_sorted.sort(
            key=lambda x: get_nested_attr(x, columns[i]),
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

def filter_mods(mods:list[Mod], filter_params:FilterParams, enabled_list:list = []):
    """
    Filters and sorts the list of mods to show
    """
    outputs = []

    for mod in mods:
        if filter_params.enabled_only:
            if mod.hash not in enabled_list: 
                continue

        if filter_params.mod_name.lower() not in mod.mod_name.lower(): 
            continue

        if filter_params.authors.lower() not in mod.authors.lower(): 
            continue
        
        keys, names, groups, series, slots = mod.get_character_data()

        if filter_params.character.lower() != "all":
            found_match = False
            for ch in names:
                if ch.lower() == filter_params.character.lower():
                    found_match = True
                    break

            if  found_match == False: 
                continue

        if filter_params.series.lower() != "all":
            should_include = False
            for serie in series:
                if filter_params.series.lower() == serie.lower():
                    should_include = True

            if should_include == False:
                continue

        if filter_params.category.lower() != "all":
            if filter_params.category.lower() != mod.category.lower():
                continue

        if filter_params.info_toml.lower() != "all":
            if filter_params.info_toml.lower() == "included" and mod.contains_info == False:
                continue

            elif filter_params.info_toml.lower() == "not included" and mod.contains_info == True:
                continue

        if filter_params.wifi_safe.lower() != "all":
            if filter_params.wifi_safe.lower() != mod.wifi_safe.lower():
                continue

        if filter_params.slot_from.lower() or filter_params.slot_to.lower():
            contains_slot = False
            min_slot = int(filter_params.slot_from.lower() if filter_params.slot_from.lower() else 0)
            max_slot = int(filter_params.slot_to.lower() if filter_params.slot_to.lower() else 255)
            
            if max_slot >= min_slot:
                if filter_params.slot_rule == SLOT_RULE[0]:
                    for slot in slots:
                        if slot >= min_slot and slot <= max_slot:
                            contains_slot = True
                            break
                else:
                    contains_slot = True
                    for slot in slots:
                        if slot < min_slot or slot > max_slot:
                            contains_slot = False

            if contains_slot == False:
                continue
        
        if filter_params.included.lower() != "all":
            if filter_params.included not in mod.includes: 
                continue

        outputs.append(mod)

    sort_priority = load_config().sort_priority
    if sort_priority is not None:
        return sort_by_columns(outputs, sort_priority)
    else:
        return outputs
