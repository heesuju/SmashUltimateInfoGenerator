import json
import os
from pathlib import Path
from utils.hash import gen_hash_as_decimal

OUTPUT_FILE = "cache/presets"

class PresetManager():
    def __init__(self)->None:
        self.preset_file = "cache/presets"
        self.enabled = []

    def load_preset(self):
        preset_dir = "cache"
        if not os.path.exists(preset_dir):
            os.makedirs(preset_dir)
        file = Path(os.path.join(preset_dir, "presets"))
        if file.is_file():
            with open(file, mode='r', encoding='utf-8') as f:
                self.enabled = json.loads(f.read())
        return self.enabled
    
    def save_preset(self, mods:list):
        outputs = []
        preset_dir = "cache"
        if not os.path.exists(preset_dir):
            os.makedirs(preset_dir)

        for mod in mods:
            outputs.append(gen_hash_as_decimal(mod))
        
        with open(OUTPUT_FILE, mode='w', encoding='utf-8') as o:
            o.write(json.dumps(outputs, separators=(',', ':')))

        print("enabled mods:", len(outputs))
        self.enabled = outputs
        return outputs
    
    def is_preset_valid(self)->bool:
        preset_dir = "cache"
        if not os.path.exists(preset_dir):
            os.makedirs(preset_dir)
        file = Path(os.path.join(preset_dir, "presets"))
        if file.is_file():
            return True
        else:
            return False
