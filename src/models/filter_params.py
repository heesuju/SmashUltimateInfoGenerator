from src.constants.defs import INFO_VALUES, WIFI_TYPES, SLOT_RULE
from src.constants.elements import ELEMENTS
from src.constants.categories import CATEGORIES
from data import PATH_CHAR_NAMES
from src.utils.csv_helper import csv_to_dict
from src.utils.string_helper import remove_redundant_spacing

DEFAULT_VALUE = "All"

class FilterParams():
    def __init__(self):
        self.mod_name = ""
        self.authors = ""
        self.character = DEFAULT_VALUE
        self.series = DEFAULT_VALUE
        self.category = DEFAULT_VALUE
        self.info_toml = DEFAULT_VALUE
        self.wifi_safe = DEFAULT_VALUE
        self.included = DEFAULT_VALUE
        self.slot_rule = SLOT_RULE[0]
        self.slot_from = ""
        self.slot_to = ""
        self.enabled_only = False
        self.include_hidden = False
        self.characters_list = [DEFAULT_VALUE] + sorted(csv_to_dict(PATH_CHAR_NAMES, "Custom"))
        self.series_list = [DEFAULT_VALUE] + sorted(csv_to_dict(PATH_CHAR_NAMES, "Series"))
        self.series_list = [remove_redundant_spacing(i) for i in self.series_list]
        self.info_toml_list = [DEFAULT_VALUE] + INFO_VALUES
        self.wifi_safe_list = [DEFAULT_VALUE] + WIFI_TYPES
        self.included_list = [DEFAULT_VALUE] + ELEMENTS
        self.category_list = [DEFAULT_VALUE] + CATEGORIES
