from typing import List
from enum import Enum
import os
from src.constants.enums import Fighter
from src.utils.csv_helper import csv_to_dict, get_columns_by_key

ICON_PATH = "assets/icons"
CHARACTER_DATA_PATH = "data/character_data.csv"

class NavigationMenuIcon(Enum):
    PREVIEW = "assets/icons/menu/details_32.png"
    CONFIG = "assets/icons/menu/config_32.png"
    FILTER = "assets/icons/menu/filter_32.png"
    SORT = "assets/icons/menu/sort_32.png"
    EDIT = "assets/icons/menu/edit_32.png"
    BATCH = "assets/icons/menu/batch_32.svg"
    WORKSPACE = "assets/icons/menu/workspace_32.png"
    DOWNLOAD = "assets/icons/menu/download_32.png"
    NONE = ""

class ButtonIcons(Enum):
    SEARCH = "assets/icons/buttons/search_16.png"
    REFRESH = "assets/icons/buttons/refresh_16.png"
    CLEAR = "assets/icons/buttons/close_16.png"
    EDIT = "assets/icons/buttons/edit_16.png"
    GRID = "assets/icons/buttons/grid.png"
    LIST = "assets/icons/buttons/list.png"
    FAV_ON = "assets/icons/buttons/fav_on_16.png"
    FAV_OFF = "assets/icons/buttons/fav_off_16.png"
    HIDE_ON = "assets/icons/buttons/vis_off_16.png"
    HIDE_OFF = "assets/icons/buttons/vis_on_16.png"
    HIDE = "assets/icons/buttons/favorite_16.png"
    BROWSE = "assets/icons/buttons/browse_16.png"
    ENABLE = "assets/icons/buttons/on.png"
    DISABLE = "assets/icons/buttons/off.png"
    MENU = "assets/icons/buttons/menu_16.png"
    SORT_ASC = "assets/icons/buttons/sort_asc_16.png"
    SORT_DESC = "assets/icons/buttons/sort_desc_16.png"
    WEB = "assets/icons/buttons/web_16.png"
    DOWNLOAD = "assets/icons/buttons/download_16.png"

class DataManager:
    _data_list_cache = None
    _key_map_cache = None

    @staticmethod
    def _init_cache():
        if DataManager._data_list_cache is None:
            DataManager._data_list_cache = csv_to_dict(CHARACTER_DATA_PATH)
        if DataManager._key_map_cache is None:
            DataManager._key_map_cache = get_columns_by_key(CHARACTER_DATA_PATH)

    @staticmethod
    def get_character_keys()-> list[str]:
        data = Fighter.list()
        return data
    
    @staticmethod
    def get_character_data(character:Fighter=None, column:str = ""):
        DataManager._init_cache()
        if character is not None:
            # Emulate get_columns_by_key behavior which relies on Key being first column
            char_key = str(character)
            # Find in list cache for read efficiency
            target_row = None
            for row in DataManager._data_list_cache:
                if row.get("Key") == char_key:
                    target_row = row
                    break
            
            if not target_row:
                return "" if column else {}
                
            if column:
                return target_row.get(column, "")
            else:
                # Return dict excluding the Key (to match get_columns_by_key behavior)
                return {k: v for k, v in target_row.items() if k != "Key"}
        else:
            if column:
                # Return list of values for column (unique)
                values = []
                seen = set()
                for row in DataManager._data_list_cache:
                    val = row.get(column, "")
                    if val and val not in seen:
                        values.append(val)
                        seen.add(val)
                return values
            return DataManager._data_list_cache
        
    @staticmethod
    def get_character_by_key():
        DataManager._init_cache()
        return DataManager._key_map_cache
        
    @staticmethod
    def get_character_series(character:Fighter=None)-> list[str]:
        return DataManager.get_character_data(character, "Series")    
    
    @staticmethod
    def get_character_names(character:Fighter=None)-> list[str]:
        return DataManager.get_character_data(character, "Custom")    
    
    @staticmethod
    def get_character_by_custom(character:str)-> Fighter:
        data = DataManager.get_character_data()    
        for d in data:
            if d.get("Custom") == character:
                return Fighter(d.get("Key"))
    
    @staticmethod
    def get_character_groups(character:Fighter=None)-> list[str]:
        return DataManager.get_character_data(character, "Group")    
    
    @staticmethod
    def get_group_characters(group_name:str)-> list[str]:
        output = []
        data = DataManager.get_character_data()
        for d in data:
            if d.get("Group") == group_name:
                output.append(d.get("Key"))
        return output
    
    @staticmethod
    def get_characters_by_series(series_name:str)-> list[str]:
        """Get list of character custom names that belong to a specific series"""
        output = []
        data = DataManager.get_character_data()
        for d in data:
            if d.get("Series") == series_name:
                output.append(d.get("Custom"))
        return output

    @staticmethod
    def get_character_icon(character:str) -> str:
        return os.path.join(ICON_PATH, "characters", f"{str(character)}.png")

    @staticmethod
    def get_character_icons(character_names: list[Fighter]) -> list[str]:
        return [DataManager.get_character_icon(name) for name in character_names]

