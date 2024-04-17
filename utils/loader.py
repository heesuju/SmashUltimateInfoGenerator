import tomli as tomli
import os 

class Loader:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.display_name = ""
        self.description = ""
        self.authors = ""
        self.category = ""
        self.version = ""

    def load_toml(self, dir:str):
        self.reset()
        if not os.path.exists(dir + "/info.toml"):
            return False
        with open(dir + "/info.toml", "rb") as toml_file:
            loaded_dict = tomli.load(toml_file)
            if loaded_dict:
                if "display_name" in loaded_dict: self.display_name = loaded_dict["display_name"]
                if "description" in loaded_dict: self.description = loaded_dict["description"]
                if "authors" in loaded_dict: self.authors = loaded_dict["authors"]
                if "category" in loaded_dict: self.category = loaded_dict["category"]
                if "version" in loaded_dict: self.version = loaded_dict["version"]
            
                print("successfully loaded info.toml in working directory")
                return True
            else:
                return False