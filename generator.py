import common
import string
import tomli_w as tomli

class Generator:
    def __init__(self, working_dir:string=None, authors:string=None, version:string=None, additional_info:string=None):
        self.working_dir = working_dir
        self.authors = authors
        self.version = version
        self.additional_info = additional_info

    def generate_info_toml(self):
        display_name = ""
        category = ""
        folder_name_parts = common.split_into_arr(common.get_dir_name(self.working_dir))
        print(self.working_dir)
        if len(folder_name_parts) > 2:
            character_name = folder_name_parts[1]
            character_name = character_name.replace("[", " ").replace("]", " ")
            display_name = display_name + character_name + folder_name_parts[-1]
            category = folder_name_parts[0]
        
        description = "Includes:\n"

        if common.is_valid_dir(self.working_dir + "/fighter"):
            if common.search_dir_for_keyword(self.working_dir + "/fighter", "model"):
                description = description + "Skin\n"
                
            if common.search_dir_for_keyword(self.working_dir + "/fighter", "motion"):
                description = description + "Motion\n"
            
            if common.search_dir_for_keyword(self.working_dir + "/fighter", "kirby"):
                description = description + "Kirby\n"
            
            category = "Fighter"
            
        if common.is_valid_dir(self.working_dir + "/effect"):
            for file in common.get_children_by_extension(self.working_dir + "/effect"):
                if common.search_files_for_pattern(file, r"c\d+"):
                    description = description + "Single Effect\n"
                else:
                    description = description + "Effects\n"
            
        if common.is_valid_dir(self.working_dir + "/sound"):
            if common.search_dir_for_keyword(self.working_dir + "/sound", "fighter_voice"):
                description = description + "Voice\n"
            
            if common.search_dir_for_keyword(self.working_dir + "/sound", "narration"):
                description = description + "Narrator Voice\n"
            
        # Check if the "ui" directory exists
        if common.is_valid_dir(self.working_dir + "/ui"):
            if common.search_dir_for_keyword(self.working_dir + "/ui", "message"):
                description = description + "Custom Name\n"
            
            if common.search_dir_for_keyword(self.working_dir + "/ui", "replace"):
                description = description + "UI\n"
                
        # Get the description from the multiline Text widget
        description = description + self.additional_info

        # Create and write to the info.toml file
        with open(self.working_dir + "\info.toml", "wb") as toml_file:
            tomli.dump({
                "display_name": display_name, 
                "authors": self.authors,
                "description": description,
                "version": self.version,
                "category": category
            }, toml_file)