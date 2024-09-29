import os
import json
from cache import PATH_CONFIG

def load_config():
    if(os.path.isfile(PATH_CONFIG)):
        try:
            json_file = open(PATH_CONFIG, "r")
            data = json.loads(json_file.read())
            json_file.close()
            print("Loaded config")
            return data
        except Exception as e:
            print(f"error: {e}")
            return None
    else:
        print("No saved config")
        return None

def update_config_directory(default_directory):
    data = load_config()
    data["default_directory"] = default_directory
    with open(PATH_CONFIG, 'w') as f:
        json.dump(data, f, indent=4)
    
    print("Config modified")