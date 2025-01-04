"""
filter.py: contains methods for filter/sorting
"""

from src.models.mod import Mod
from data import PATH_CHAR_NAMES
from src.utils.csv_helper import csv_to_dict
from src.utils.edit_distance import get_completion

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
