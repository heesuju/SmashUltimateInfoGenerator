import json
import os

class Config:
    def __init__(self):
        self.default_dir = ""
        self.load_config()
        
    def save_config(self):
        config_dict = {"default_directory":self.default_dir}
        json_str = json.dumps(config_dict)
        json_file = open("config.json", "w")
        json_file.write(json_str)
        json_file.close()
        print("Saved default dir " + self.default_dir)

    def load_config(self):
        if(os.path.isfile("config.json")):
            try:
                json_file = open("config.json", "r")
                data = json.loads(json_file.read())
                self.default_dir = data["default_directory"]
                json_file.close()
            except:
                print("Loaded default dir")
        else:
            print("No saved dir")

    def set_default_dir(self, default_dir):
        self.default_dir = default_dir
        self.save_config()