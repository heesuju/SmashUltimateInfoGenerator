from enum import Enum
import os
from src.constants import Character

ICON_PATH = "assets/icons"

class NavigationMenuIcon(Enum):
    PREVIEW = "assets/icons/menu/details_32.png"
    CONFIG = "assets/icons/menu/config_32.png"
    FILTER = "assets/icons/menu/filter_32.png"
    EDIT = "assets/icons/menu/edit_32.png"

class ButtonIcons(Enum):
    SEARCH = "assets/icons/buttons/search_16.png"
    REFRESH = "assets/icons/buttons/refresh_16.png"
    CLEAR = "assets/icons/buttons/close_16.png"
    EDIT = "assets/icons/buttons/edit_16.png"
    GRID = "assets/icons/buttons/grid.png"
    LIST = "assets/icons/buttons/list.png"
    FAVORITE = "assets/icons/buttons/favorite_16.png"
    BROWSE = "assets/icons/buttons/browse_16.png"
    ENABLE = "assets/icons/buttons/on.png"
    DISABLE = "assets/icons/buttons/off.png"
    MENU = "assets/icons/buttons/ellipsis.png"

class AssetManager:
    @staticmethod
    def get_character_icon(character:Character) -> str:
        return os.path.join(ICON_PATH, "characters", f"{str(character)}.png")

    @staticmethod
    def get_character_icons(character_names: list[Character]) -> list[str]:
        return [AssetManager.get_character_icon(name) for name in character_names]
    