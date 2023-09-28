import common
import string
import tomli_w as tomli
import re
import csv
import defs

class Generator:
    def __init__(self):
        self.working_dir = ""
        self.authors = ""
        self.version = "1.0.0"
        self.additional_info = ""
        self.display_name = ""
        self.char_names = []
        self.group_names = []
        self.slots = []
        self.mod_name = ""
        self.category = "Misc"
        self.contains_fighter = False
        self.contains_effect = False
        self.contains_ui = False
        self.contains_audio = False

    def get_slots(self, slots):
        numbers = []

        for s in slots:
            if s[1:].isdigit():
                number = int(s[1:])
            else:
                number = s[1:]

            numbers.append(number)
        numbers.sort()
        return numbers
    
    # trims the character name and category from the folder name to get the mod title
    def get_mod_title(self, original):
        dict_arr = common.csv_to_dict("./character_names.csv") 
        set_name = set()
        for dict in dict_arr:
            if dict['Custom'] in self.char_names:
                #set_name.add(dict['Key'])
                set_name.add(dict['Value'])
                set_name.add(dict['Custom'])
                if dict['Group']:
                    set_name.add(dict['Group'])

        # Create a regular expression pattern to match words to remove and underscore
        pattern = r'|'.join(re.escape(word) for word in defs.CATEGORIES) + r'|'
        pattern += r'|'.join(re.escape(name) for name in set_name)
        pattern += r'|_|-|&'  # Add underscore to the pattern
        
        # Use regular expression to remove unwanted parts
        return re.sub(r'(C\d+|\[.*?\]|' + pattern + ')', '', original, flags=re.I)

    def get_characters(self):
        children = common.get_all_children_in_path(self.working_dir + "/fighter")
        dict_arr = common.csv_to_dict("./character_names.csv") 
        name_arr = []        
        group_arr = []
        slot_arr = []

        if len(children) > 1 and "kirby" in children:
            children.remove("kirby")

        for child in children:
            for dict in dict_arr:
                if child == dict['Key']:
                    name_arr.append(dict['Custom'])
                    group_arr.append(dict['Group'])
                    
                    slots = []
                    if common.is_valid_dir(self.working_dir + "/fighter/" + child + "/model"):
                        models = common.get_all_children_in_path(self.working_dir + "/fighter/" + child + "/model")
                        for model in models:
                            all_slots = common.get_all_children_in_path(self.working_dir + "/fighter/" + child + "/model/" + model)
                            slots = self.get_slots(all_slots)
                            for slot in slots:
                                if slot not in slot_arr:
                                    slot_arr.append(slot)

        return slot_arr, name_arr, group_arr
        
    def set_category(self):
        if self.contains_fighter == True: return "Fighter"
        elif self.contains_effect == True: return "Effects"
        elif self.contains_ui == True: return "UI"
        elif self.contains_audio == True: return "Audio"

    def preview_info_toml(self, working_dir:string=None, authors:string=None, version:string=None, additional_info:string=None):
        self.working_dir = working_dir
        self.authors = authors
        self.version = version
        self.additional_info = additional_info
        
        self.description = "Includes:\n"

        if common.is_valid_dir(self.working_dir + "/fighter"):
            self.slots, self.char_names, self.group_names = self.get_characters()
            
            if common.search_dir_for_keyword(self.working_dir + "/fighter", "model"):
                self.description += "Skin\n"
                self.contains_fighter = True

            if common.search_dir_for_keyword(self.working_dir + "/fighter", "motion"):
                self.description += "Motion\n"
            
            if "kirby" in self.display_name == False and common.search_dir_for_keyword(self.working_dir + "/fighter", "kirby"):
                self.description += "Kirby\n"
            
        self.mod_name = self.get_mod_title(common.get_dir_name(self.working_dir)) 
            
        if common.is_valid_dir(self.working_dir + "/effect"):
            for file in common.get_children_by_extension(self.working_dir + "/effect", ".eff"):
                self.contains_effect = True
                if common.search_files_for_pattern(file, r"c\d+"):
                    self.description += "Single Effect\n"
                else:
                    self.description += "Effects\n"
            
        if common.is_valid_dir(self.working_dir + "/sound"):
            self.contains_audio = True
            if common.search_dir_for_keyword(self.working_dir + "/sound", "fighter_voice"):
                self.description += "Voice\n"

            if common.search_dir_for_keyword(self.working_dir + "/sound", "fighter"):
                self.description += "SFX\n"
            
            if common.search_dir_for_keyword(self.working_dir + "/sound", "narration"):
                self.description += "Narrator Voice\n"
            
        # Check if the "ui" directory exists
        if common.is_valid_dir(self.working_dir + "/ui"):
            self.contains_ui = True
            if common.search_dir_for_keyword(self.working_dir + "/ui", "message"):
                self.description += "Custom Name\n"
            
            if common.search_dir_for_keyword(self.working_dir + "/ui", "replace"):
                self.description += "UI\n"
                
        # Get the description from the multiline Text widget
        self.description += self.additional_info
        self.category = self.set_category()
        return {"description":self.description, 
                "category":self.category, 
                "character_names": self.char_names, 
                "mod_name":self.mod_name,
                "slots":self.slots}
        
    def generate_info_toml(self, display_name, authors, description, version, category):
        # Create and write to the info.toml file
        with open(self.working_dir + "\info.toml", "wb") as toml_file:
            tomli.dump({
                "display_name": display_name, 
                "authors": authors,
                "description": description,
                "version": version,
                "category": category
            }, toml_file)