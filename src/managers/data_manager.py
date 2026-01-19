from typing import List
from enum import Enum
import os
from src.constants.enums import Fighter
from src.utils.csv_helper import csv_to_dict, get_columns_by_key

ICON_PATH = "assets/icons"
CHARACTER_DATA_PATH = "data/character_data.csv"

class NavigationMenuIcon(Enum):
    PREVIEW = os.path.join(ICON_PATH, "menu/details_32.svg")
    CONFIG = os.path.join(ICON_PATH, "menu/config_32.svg")
    FILTER = os.path.join(ICON_PATH, "menu/filter_32.svg")
    SORT = os.path.join(ICON_PATH, "menu/sort_32.svg")
    EDIT = os.path.join(ICON_PATH, "menu/edit_32.svg")
    BATCH = os.path.join(ICON_PATH, "menu/batch_32.svg")
    WORKSPACE = os.path.join(ICON_PATH, "menu/workspace_32.svg")
    DOWNLOAD = os.path.join(ICON_PATH, "menu/download_32.svg")
    NONE = ""

class ButtonIcons(Enum):
    EDIT = os.path.join(ICON_PATH, "buttons/edit_16.svg")
    GRID = os.path.join(ICON_PATH, "buttons/grid_16.svg")
    LIST = os.path.join(ICON_PATH, "buttons/list_16.svg")
    FAV_ON = os.path.join(ICON_PATH, "buttons/fav_on_16.svg")
    FAV_OFF = os.path.join(ICON_PATH, "buttons/fav_off_16.svg")
    HIDE_ON = os.path.join(ICON_PATH, "buttons/vis_off_16.svg")
    HIDE_OFF = os.path.join(ICON_PATH, "buttons/vis_on_16.svg")
    BROWSE = os.path.join(ICON_PATH, "buttons/browse_16.svg")
    ENABLE = os.path.join(ICON_PATH, "buttons/on_16.svg")
    DISABLE = os.path.join(ICON_PATH, "buttons/off_16.svg")
    SORT_ASC = os.path.join(ICON_PATH, "buttons/sort_asc_16.svg")
    SORT_DESC = os.path.join(ICON_PATH, "buttons/sort_desc_16.svg")
    WEB = os.path.join(ICON_PATH, "buttons/web_16.svg")
    DOWNLOAD = os.path.join(ICON_PATH, "buttons/download_16.svg")
    BATCH_GENERATE = os.path.join(ICON_PATH, "buttons/generate_16.svg")
    BATCH_ENABLE = os.path.join(ICON_PATH, "buttons/check_16.svg")
    BATCH_DISABLE = os.path.join(ICON_PATH, "buttons/block_16.svg")
    BATCH_REMOVE = os.path.join(ICON_PATH, "buttons/trash_16.svg")
    ADD = os.path.join(ICON_PATH, "buttons/add_16.svg")
    DESELECT = os.path.join(ICON_PATH, "buttons/deselect_16.svg")
    MORE = os.path.join(ICON_PATH, "buttons/more_16.svg")
    REFRESH = os.path.join(ICON_PATH, "buttons/refresh_16.svg")
    SEARCH = os.path.join(ICON_PATH, "buttons/search_16.svg")
    CLEAR = os.path.join(ICON_PATH, "buttons/clear_16.svg")
    SAVE = os.path.join(ICON_PATH, "buttons/save_16.svg")
    RESTORE = os.path.join(ICON_PATH, "buttons/restore_16.svg")
    EXPORT = os.path.join(ICON_PATH, "buttons/export_16.svg")

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

