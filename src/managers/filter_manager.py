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
    elements: List[Element] = []
    slot_min: int = 0
    slot_max: int = 255
    wifi: List[Wifi] = []
    info: List[InfoToml] = []
    enabled: List[EnabledState] = []
    include_hidden: bool = False

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
            # Filter by mod name
            if self.params.mod_name:
                if self.params.mod_name.lower() not in mod.mod_name.lower():
                    continue
            
            # Filter by authors
            if self.params.authors:
                if self.params.authors.lower() not in mod.authors.lower():
                    continue
            
            # Filter by category (if any categories are selected)
            if self.params.category:
                if mod.category not in self.params.category:
                    continue
            
            # Filter by character (if any characters are selected)
            if self.params.character:
                mod_fighters = [Fighter(c.fighter) for c in mod.characters]
                if not any(char in mod_fighters for char in self.params.character):
                    continue
            
            # Filter by elements (if any elements are selected)
            if self.params.elements:
                mod_elements = [Element(e) for e in mod.includes]
                if not any(elem in mod_elements for elem in self.params.elements):
                    continue
            
            # Filter by slot range
            if mod.characters:
                # Check if any character has a slot in the specified range
                has_slot_in_range = False
                for char in mod.characters:
                    for slot in char.slots:
                        if self.params.slot_min <= slot <= self.params.slot_max:
                            has_slot_in_range = True
                            break
                    if has_slot_in_range:
                        break
                if not has_slot_in_range:
                    continue
            
            # Filter by wifi safety (if any wifi states are selected)
            if self.params.wifi:
                if mod.wifi_safe not in self.params.wifi:
                    continue
            
            # Filter by info.toml presence (if any info states are selected)
            if self.params.info:
                mod_info_state = InfoToml.INCLUDED if mod.contains_info else InfoToml.NOT_INCLUDED
                if mod_info_state not in self.params.info:
                    continue

            filtered.append(mod)
        return filtered 
