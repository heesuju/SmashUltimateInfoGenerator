import common
import string
import tomli_w as tomli
import defs

class Generator:
    def __init__(self):
        self.working_dir = ""
        self.authors = ""
        self.version = "1.0.0"
        self.additional_info = ""
        self.display_name = ""
        self.category = "Misc"
        self.contains_fighter = False
        self.contains_effect = False
        self.contains_ui = False
        self.contains_audio = False

    def get_slot_range(self, slots):
        ranges = []
        numbers = []
        current_idx = 0
        out_str = ""
        for s in slots:
            number = int(s[1:])  # Start from the second character to exclude the 'c'
            numbers.append(number)
        numbers.sort()
        
        start = numbers[0] 
        prev = numbers[0]
        ranges.append("C" + f"{start:02}")

        for n in range(1, len(numbers)):
            if prev + 1 == numbers[n]:
                ranges[current_idx] = "C" + f"{start:02}" + "-" + f"{numbers[n]:02}"
            else:
                current_idx+=1
                ranges.append("C" + f"{numbers[n]:02}")
                start = numbers[n]
            prev = numbers[n]

        for item in ranges:
            if not out_str:
                out_str += item
            else:
                out_str += ", " + item

        return out_str

    def get_mod_name(self):
        name = ""
        
        return name

    def get_display_name(self):
        children = common.get_all_children_in_path(self.working_dir + "/fighter")
        dict_arr = common.csv_to_dict("./character_names.csv") 
        character_name = ""                
        if len(children) > 1 and "kirby" in children:
            children.remove("kirby")
        slots = ""
        for child in children:
            for dict in dict_arr:
                if child == dict['Key']:
                    if not character_name:
                        character_name += dict['Value']
                    else:
                        character_name += ", " + dict['Value']
                    all_slots = common.get_all_children_in_path(self.working_dir + "/fighter/" + child + "/model/body")
                    slots = self.get_slot_range(all_slots)
                    break
                
        return character_name + " " + slots 
        
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
            self.display_name = self.get_display_name()
            
            if common.search_dir_for_keyword(self.working_dir + "/fighter", "model"):
                self.description += "Skin\n"
                self.contains_fighter = True

            if common.search_dir_for_keyword(self.working_dir + "/fighter", "motion"):
                self.description += "Motion\n"
            
            if "kirby" in self.display_name == False and common.search_dir_for_keyword(self.working_dir + "/fighter", "kirby"):
                self.description += "Kirby\n"
            
            
            
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
        return {"display_name":self.display_name, "description":self.description, "category":self.category}
        
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