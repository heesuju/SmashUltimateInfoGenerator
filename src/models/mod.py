"""
mod.py: model class for each mod
"""

from pydantic import BaseModel

from src.constants.enums import Fighter, Category, Wifi
from src.managers.data_manager import DataManager

EXCLUDED_KEYS = {"folder_name", "path", "thumbnail", "hash", "contains_info", "is_selected"}

class Character(BaseModel):    
    fighter:Fighter = None
    slots:list[int] = []

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
    includes:list[str] = []
    contains_info:bool = False
    is_selected:bool = False

    def add_to_included(self, element:str)->None:
        if element not in self.includes:
            self.includes.append(element)

    def to_dict(self):
        def convert(obj):
            if isinstance(obj, list):
                return [convert(item) for item in obj]
            elif hasattr(obj, "__dict__"):
                return {key: convert(value) for key, value in obj.__dict__.items() if key not in EXCLUDED_KEYS}
            else:
                return obj

        return convert(self)

    def get_character_keys(self) -> list[str]:
        return [str(character.fighter) for character in self.characters]
    
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