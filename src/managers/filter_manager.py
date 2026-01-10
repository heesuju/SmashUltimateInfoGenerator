import os
from pydantic import BaseModel
from typing import Union, List
from src.core.mod_loader import ModLoader
from src.managers.config_manager import ConfigManager
from src.models.mod import Mod
from src.utils.logger import output_log
from src.models.mod import Mod
from data import PATH_CHAR_NAMES
from src.utils.csv_helper import csv_to_dict
from src.utils.edit_distance import get_completion
from src.core.data import load_config
from src.utils.string_helper import str_to_int
from src.constants.enums import *

class FilterParameters(BaseModel):
    mod_name: str = ""
    authors: str = ""
    category: List[Category] = []
    character: List[Fighter] = []
    elements: List[Element] = Element.list()
    slot_min: int = 0
    slot_max: int = 255
    wifi: List[Wifi] = Wifi.list()
    info: List[InfoToml] = InfoToml.list()

class FilterManager():
    def __init__(self):
        self.params = FilterParameters()
        self.callbacks = []

    def add_callback(self, callback:callable):
        self.callbacks.append(callback)
    
    def reset(self):
        self.params = FilterParameters()

    def set(self, params:FilterParameters):
        self.params = params
        self.on_change()
        
    def on_change(self):
        for callback in self.callbacks:
            callback()

    def apply_filters(self, mods:List[Mod]) -> List[Mod]:
        filtered = []
        for mod in mods:
            if self.params.mod_name:
                if self.params.mod_name.lower() not in mod.mod_name.lower():
                    continue
            if self.params.authors:
                if self.params.authors and self.params.authors.lower() not in mod.authors.lower():
                    continue
            if self.params.category:
                if mod.category not in self.params.category:
                    continue
            if self.params.character:
                if self.params.character and not any(char in [Fighter(c.fighter) for c in mod.characters] for char in self.params.character):
                    continue

            filtered.append(mod)
        return filtered 
