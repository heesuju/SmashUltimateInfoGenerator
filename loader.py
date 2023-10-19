import tomli as tomli

class Loader:
    def __init__(self):
        self.display_name = ""
        self.description = ""
        self.authors = ""
        self.category = ""
        self.version = ""
    
    def load_toml(self, dir):
        with open(dir + "\info.toml", "rb") as toml_file:
            loaded_dict = tomli.load(toml_file)
            if loaded_dict:
                self.display_name = loaded_dict["display_name"]
                self.description = loaded_dict["description"]
                self.authors = loaded_dict["authors"]
                self.category = loaded_dict["category"]
                self.version = loaded_dict["version"]
            
                print("successfully loaded info.toml in working directory")
                return True
            else:
                return False