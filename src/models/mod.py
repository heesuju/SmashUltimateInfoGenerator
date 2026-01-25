"""
mod.py: model class for each mod
"""

from pydantic import BaseModel
from typing import List
from enum import Enum
from src.constants.enums import Fighter, Category, Wifi, Element, Stage, StageSlot
from src.managers.data_manager import DataManager

EXCLUDED_KEYS = {"folder_name", "path", "thumbnail", "hash", "contains_info", "is_selected"}

class ModItem(BaseModel):
    id:str = ""
    thumbnail:str = ""
    name:str = ""
    category:str = ""
    authors:str = ""
    slots:str = ""
    version:str = "1.0.0"
    enabled:bool = False
    selected:bool = False
    favorited:bool = False
    hidden:bool = False
    character_icons:List[str] = []

class OnlineModItem(ModItem):
    like_count: int = 0
    post_count: int = 0
    view_count: int = 0
    date_updated: int = 0
    url: str = ""

class Character(BaseModel):    
    fighter:Fighter = None
    slots:list[int] = []

class Stage(BaseModel):    
    stage:Stage = None
    slots:list[StageSlot] = []

class Mod(BaseModel):
    display_name:str = ""
    description:str = ""
    authors:str = ""
    category:Category = Category.MISC
    version:str = "1.0.0"
    mod_name:str = ""
    url:str = ""
    wifi_safe:Wifi = Wifi.UNCERTAIN
    folder_name:str = ""
    path:str = ""
    thumbnail:str = ""
    hash:str = ""
    characters:list[Character] = []
    stages:list[Stage] = []
    includes:list[Element] = []
    contains_info:bool = False
    is_selected:bool = False

    def add_to_included(self, element:Element)->None:
        if element not in self.includes:
            self.includes.append(element)

    def to_dict(self):
        def convert(obj):
            if isinstance(obj, Enum):
                return obj.value
            elif isinstance(obj, list):
                return [convert(item) for item in obj]
            elif hasattr(obj, "__dict__"):
                return {key: convert(value) for key, value in obj.__dict__.items() if key not in EXCLUDED_KEYS}
            else:
                return obj

        return convert(self)

    def get_character_keys(self) -> list[str]:
        return [str(character.fighter) for character in self.characters]
    
    def get_character_slots(self)->list[int]:
        slots = []
        for character in self.characters:
            slots.extend(character.slots)
        slots = list(set(slots))
        return slots

    def get_grouped_character_keys(self)->list[str]:
        keys = self.get_character_keys()
        
        groups = set()
        for key in keys:
            if key:
                groups.add(DataManager.get_character_groups(Fighter(key)))
        if len(groups) >= 1:
            for group in list(groups):
                group_items = DataManager.get_group_characters(group)
                included = True
                for item in group_items:
                    if item not in keys:
                        included = False
                        break
                if included:
                    for item in group_items:
                        keys.remove(item)

                    keys.append(group)
                    
        return keys