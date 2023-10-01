import json
import os

class Config:
    def __init__(self):
        self.reset()
        self.load_config()

    def reset(self):
        self.default_dir = ""
        self.display_name_format = "{characters} {slots} {mod}"
        self.folder_name_format = "{category}_{characters}[{slots}]_{mod}"
            
    def save_config(self):
        config_dict = {
            "default_directory":self.default_dir,
            "display_name_format":self.display_name_format,
            "folder_name_format":self.folder_name_format}
        json_str = json.dumps(config_dict)
        json_file = open("config.json", "w")
        json_file.write(json_str)
        json_file.close()
        print("Saved config")

    def load_config(self):
        if(os.path.isfile("config.json")):
            try:
                json_file = open("config.json", "r")
                data = json.loads(json_file.read())
                self.default_dir = data["default_directory"]
                if data["display_name_format"]:
                    self.display_name_format = data["display_name_format"]
                if data["folder_name_format"]:
                    self.folder_name_format = data["folder_name_format"]
                json_file.close()
                print("Loaded config")
            except:
                self.save_config()
        else:
            print("No saved config")

    def set_default_dir(self, default_dir):
        self.default_dir = default_dir
        self.save_config()

    def set_format(self, display_name_format, folder_name_format):
        self.display_name_format = display_name_format
        self.folder_name_format = folder_name_format
        self.save_config()