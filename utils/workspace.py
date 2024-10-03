import os, re, json
from .files import read_json, is_valid_file, is_valid_dir
from pathlib import Path
from ui.config import load_config

def extract_number_from_preset(input_str):
    match = re.search(r'_preset(\d+)$', input_str)
    if match:
        return match.group(1)
    return ""

def load_preset_mods(preset_file:str):
    preset_mods = []
    if preset_file: 
        config = load_config()
        cache_dir = config["cache_dir"]
        preset_dir = os.path.join(cache_dir, preset_file)
        if is_valid_file(preset_dir):
            preset_mods = read_json(preset_dir)
    return preset_mods

def get_workspace_lists(dir:str):
    outputs = {}
    file_dir = os.path.join(dir, "workspace_list")
    if is_valid_file(file_dir):
        workspace_list = read_json(file_dir)
        for key, value in workspace_list.items():
            outputs[key] = {"filename":value, "mod_list":load_preset_mods(value)}
    return outputs
