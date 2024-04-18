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