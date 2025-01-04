from data.cache import PATH_HIDDEN
from src.models.mod import Mod
from src.utils.file import read_json, get_base_name
import json

def get_hidden():
    data = read_json(PATH_HIDDEN)
    if data is not None:
        return data.get("hidden_items")
    else:
        return []

def save_hidden(hidden_items:list):
    output = {"hidden_items":hidden_items}
    with open(PATH_HIDDEN, mode='w') as o:
        o.write(json.dumps(output))

def hide_folder(directory:str):
    name = get_base_name(directory)
    if is_hidden(name):
        return
    data = get_hidden()
    data.append(name)
    save_hidden(data)

def is_hidden(folder_name:str, case_sensitive:bool=False)->bool:
    hidden = get_hidden()
    
    for d in hidden:
        if is_foldername_equal(folder_name, d):
            return True

    return False

def is_foldername_equal(a:str, b:str, case_sensitive:bool=False)->bool:
    if not case_sensitive:
        a = a.lower()
        b = b.lower()

    if a == b:
        return True
    else:
        return False

def filter_hidden(mods:list[Mod]):
    outputs = []
    hidden_items = get_hidden()
    for mod in mods:
        folder_name = get_base_name(mod.path)
        hidden = False
        for hidden_item in hidden_items:
            if is_foldername_equal(folder_name, hidden_item):
                hidden = True
                break
        if not hidden:
            outputs.append(mod)

    return outputs