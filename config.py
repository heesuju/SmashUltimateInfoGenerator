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
        self.additional_elements = []
            
    def save_config(self):
        config_dict = {
            "default_directory":self.default_dir,
            "display_name_format":self.display_name_format,
            "folder_name_format":self.folder_name_format,
            "additional_elements":self.additional_elements}
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
                if len(data["additional_elements"]) > 0:
                    self.additional_elements = data["additional_elements"]
                json_file.close()
                print("Loaded config")
            except:
                self.save_config()
        else:
            print("No saved config")

    def set_default_dir(self, default_dir):
        self.default_dir = default_dir
        self.save_config()

    def set_config(self, display_name_format, folder_name_format, additional_elements):
        self.display_name_format = display_name_format
        self.folder_name_format = folder_name_format
        self.set_additional_elements(additional_elements)
        self.save_config()

    def set_additional_elements(self, in_str):
        self.additional_elements = []
        additional_elements = in_str.split(",")
        for element in additional_elements:
            trimmed_arr = element.split(" ")
            trimmed_str = ""
            for item in trimmed_arr:
                if trimmed_str: 
                    trimmed_str += " " + item
                else: 
                    trimmed_str += item
            if trimmed_str:
                self.additional_elements.append(trimmed_str)

    def get_additional_elements_as_str(self):
        out_str = ""
        for element in self.additional_elements:
            if out_str:
                out_str += ", " + element
            else:
                out_str += element
        return out_str