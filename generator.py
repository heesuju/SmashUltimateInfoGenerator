import common
import string
import tomli_w as tomli
import re
import defs

class Generator:
    def __init__(self):
        self.working_dir = ""
        self.image_dir = ""
        self.additional_info = ""
        self.category = "Misc"
        self.reset()
    
    # resets values for generator
    def reset(self):
        self.display_name = ""          # The name that shows up in the in-game mod manager
        self.mod_name = ""              # The name of the mod
        self.char_names = []            # Character names included
        self.ignore_names = []          # A set of names to ignore in the mod title
        self.group_names = []           # The name that groups Characters sharing the same slot 
        self.slots = []                 # Slots used up by the mod
        self.is_skin = False            # Whether skins are included
        self.is_motion = False          # Whether animation or physics are included
        self.is_effect = False          # Whether effects are included
        self.is_single_effect = False   # Whether single slot effects are included
        self.is_voice = False           # Whether fighter voice is included
        self.is_sfx = False             # Whether sound effects are included
        self.is_narrator = False        # Whether narrator voice is included
        self.is_custom_name = False     # Whether custom name message is included
        self.is_ui = False              # Whether css ui is included
        self.is_kirby = False           # Whether replacement for kirby's copy ability is included 

    # converts c01 to 1 if possible and sorts them in ascending order
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
        pattern += r'|_|&'  # Add underscore to the pattern
        self.ignore_names = set_name
        
        # Use regular expression to remove unwanted parts
        return re.sub(r'(C\d+|\[.*?\]|-\d+|' + pattern + ')', '', original, flags=re.I)

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
        if self.is_skin or self.is_motion:              return "Fighter"
        elif self.is_effect or self.is_single_effect:   return "Effects"
        elif self.is_voice or self.is_sfx:              return "Audio"
        elif self.is_ui:                                return "UI"
        else:                                           return "Misc"

    def preview_info_toml(self, working_dir:string=None, authors:string=None, version:string=None, additional_info:string=None):
        self.working_dir = working_dir
        self.version = version
        self.additional_info = additional_info
        
        self.description = "Includes:\n"
        self.reset()

        if common.is_valid_dir(self.working_dir + "/fighter"):
            self.slots, self.char_names, self.group_names = self.get_characters()
            
            if common.search_dir_for_keyword(self.working_dir + "/fighter", "model"):
                self.description += "Skin\n"
                self.is_skin = True

            if common.search_dir_for_keyword(self.working_dir + "/fighter", "motion"):
                             
                self.is_motion = True

            if "kirby" in self.display_name == False and common.search_dir_for_keyword(self.working_dir + "/fighter", "kirby"):
                self.is_kirby = True
            
        self.mod_name = self.get_mod_title(common.get_dir_name(self.working_dir)) 
            
        if common.is_valid_dir(self.working_dir + "/effect"):
            for file in common.get_children_by_extension(self.working_dir + "/effect", ".eff"):
                
                if common.search_files_for_pattern(file, r"c\d+"):
                    self.is_single_effect = True
                else:
                    self.is_effect = True
                break
            
        if common.is_valid_dir(self.working_dir + "/sound"):
            if common.search_dir_for_keyword(self.working_dir + "/sound", "fighter_voice"):
                self.is_voice = True

            if common.search_dir_for_keyword(self.working_dir + "/sound", "fighter"):
                self.is_sfx = True
            
            if common.search_dir_for_keyword(self.working_dir + "/sound", "narration"):
                self.is_narrator = True
            
        # Check if the "ui" directory exists
        if common.is_valid_dir(self.working_dir + "/ui"):
            if common.search_dir_for_keyword(self.working_dir + "/ui", "message"):
                self.is_custom_name = True
            
            if common.search_dir_for_keyword(self.working_dir + "/ui", "replace") or common.search_dir_for_keyword(self.working_dir + "/ui", "replace_patch"):
                self.is_ui = True
                
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