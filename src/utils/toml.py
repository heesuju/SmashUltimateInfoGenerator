import os
from .file import is_valid_file
import tomli as tomli
import tomli_w as tomli_w

INFO_TOML = "info.toml"

def load_toml(dir:str) -> dict:
    file_path = os.path.join(dir, INFO_TOML)
    if not is_valid_file(file_path):    
        return None
    try:
        with open(file_path, "rb") as toml_file:
            return tomli.load(toml_file)
    except Exception as e:
        print(f"error while reading file: {e}")

def dump_toml(path, data:dict):
    output_path = os.path.join(path, INFO_TOML)
    with open(output_path, "wb") as toml_file:
        tomli_w.dump(data, toml_file)