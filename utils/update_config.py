import json
from cache import PATH_CONFIG
from .load_config import load_config

def update_config_directory(default_directory):
    data = load_config()
    data["default_directory"] = default_directory
    with open(PATH_CONFIG, 'w') as f:
        json.dump(data, f, indent=4)
    
    print("Config modified")