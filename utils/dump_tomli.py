import tomli_w as tomli
import os
from typing import List

class TomlParams:
    def __init__(self, display_name:str = "", authors:str = "", description:str = "", version:str = "", category:str = "", 
                 url:str = "", mod_name:str = "", wifi_safe:str = "Unknown", includes:List = [], slots:List = []) -> None:
        self.display_name = display_name
        self.authors = authors 
        self.description = description 
        self.version = version
        self.category = category
        self.url = url
        self.mod_name = mod_name
        self.wifi_safe = wifi_safe
        self.includes = includes
        self.slots = slots

# Create and write to the info.toml file
def dump_toml(path, params:TomlParams):
    output_path = os.path.join(path, "info.toml")
    with open(output_path, "wb") as toml_file:
        tomli.dump({
            "display_name": params.display_name, 
            "authors": params.authors,
            "description": params.description,
            "version": params.version,
            "category": params.category,
            "url": params.url,
            "mod_name": params.mod_name,
            "wifi_safe":params.wifi_safe,
            "includes":params.includes,
            "slots": params.slots
        }, toml_file)