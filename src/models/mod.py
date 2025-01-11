"""
mod.py: model class for each mod
"""

from .character import Character

EXCLUDED_KEYS = {"folder_name", "path", "thumbnail", "hash", "contains_info", "is_selected"}

class Mod:
    def __init__(self, **kwargs):
        """
        Init default values for mod
        """
        self.display_name:str = ""
        self.description:str = ""
        self.authors:str = ""
        self.category:str = ""
        self.version:str = ""
        self.mod_name:str = ""
        self.url:str = ""
        self.wifi_safe:str = ""
        self.folder_name:str = ""
        self.path:str = ""
        self.thumbnail:str = ""
        self.hash:str = ""
        self.characters:list[Character] = []
        self.includes:list[str] = []
        self.stage_slots:list[int] = []
        self.contains_info:bool = False
        self.is_selected:bool = False
        self.update(**kwargs)

    def update(self, **kwargs):
        """
        Updates attribute values with dict
        Usage:
            mod = Mod(**dict)
            or
            mod = Mod()
            mod.update(**dict)
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                try:
                    if key == "characters":
                        setattr(self, key, [Character(**char) for char in value])
                    else:
                        setattr(self, key, value)
                except TypeError:
                    print("type mismatch error")

    def add_to_included(self, element:str)->None:
        if element not in self.includes:
            self.includes.append(element)

    def get_character_data(self)->tuple[list[str], list[str], list[str], list[str]]:
        keys, names, groups, series, slots = [], [], [], [], []
        for ch in self.characters:
            keys.append(ch.key)
            names.append(ch.custom)
            groups.append(ch.group)
            series.append(ch.series)
            for slot in ch.slots:
                if slot not in slots:
                    slots.append(slot)
            for slot in ch.slots:
                if slot not in slots:
                    slots.append(slot)
        return keys, names, groups, series, slots

    def to_dict(self):
        def convert(obj):
            if isinstance(obj, list):
                return [convert(item) for item in obj]
            elif hasattr(obj, "__dict__"):
                return {key: convert(value) for key, value in obj.__dict__.items() if key not in EXCLUDED_KEYS}
            else:
                return obj

        return convert(self)