import common
import string
import tomli_w as tomli

class Generator:
    def preview_info_toml(self, working_dir:string=None, authors:string=None, version:string=None, additional_info:string=None):
        self.working_dir = working_dir
        self.authors = authors
        self.version = version
        self.additional_info = additional_info
        self.display_name = ""
        self.category = ""
        display_name = ""
        category = ""
        character_name = ""
        print(self.working_dir)
        
        dict_arr = common.csv_to_dict("./character_names.csv") 
        
        description = "Includes:\n"
        slots = ""
        if common.is_valid_dir(self.working_dir + "/fighter"):
            is_kirby = False
            children = common.get_all_children_in_path(self.working_dir + "/fighter")
            if len(children) > 1 and "kirby" in children:
                children.remove("kirby")
            elif len(children) <= 1 and "kirby" in children:
                is_kirby = True
                
            for child in children:
                for dict in dict_arr:
                    if child == dict['Key']:
                        character_name = dict['SourceString']
                        all_slots = common.get_all_children_in_path(self.working_dir + "/fighter/" + child + "/model/body")
                        for name in all_slots:
                            slots = slots + name
                        break
                    
            display_name += character_name + " " + slots
            
            if common.search_dir_for_keyword(self.working_dir + "/fighter", "model"):
                description = description + "Skin\n"
                
            if common.search_dir_for_keyword(self.working_dir + "/fighter", "motion"):
                description = description + "Motion\n"
            
            if is_kirby == False:
                if common.search_dir_for_keyword(self.working_dir + "/fighter", "kirby"):
                    description = description + "Kirby\n"
            
            category = "Fighter"
            
        if common.is_valid_dir(self.working_dir + "/effect"):
            for file in common.get_children_by_extension(self.working_dir + "/effect", ".eff"):
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
        
        self.display_name = display_name
        self.description = description
        self.category = category
        
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