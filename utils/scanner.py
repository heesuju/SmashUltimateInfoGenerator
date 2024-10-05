import os
from threading import Thread
import concurrent.futures
from utils.loader import Loader
from utils.generator import Generator
from PIL import Image, ImageTk
import common
from .cleaner import extract_mod_name
from .format import format_slots
from .files import is_valid_dir, get_dir_name
from utils.hash import gen_hash_as_decimal
from typing import Union

class Scanner(Thread):
    def __init__(self, directory:Union[str, list], start_callback = None, progress_callback = None, callback = None):
        super().__init__()
        self.directory = directory
        self.start_callback = start_callback
        self.progress_callback = progress_callback
        self.callback = callback
        
    def find_image(self, directory, width, height, keep_ratio:bool = True):
        img = Image.open(directory)

        # Resize the image to fit the target dimensions while preserving aspect ratio
        if keep_ratio:
            aspect_ratio = img.width / img.height

            if width / aspect_ratio <= height:
                new_width = width
                new_height = int(new_width / aspect_ratio)
            else:
                new_height = height
                new_width = int(new_height * aspect_ratio)

            return ImageTk.PhotoImage(img.resize((new_width, new_height), Image.Resampling.LANCZOS))
        else:
            return ImageTk.PhotoImage(img.resize((width, height), Image.Resampling.LANCZOS))
    
    def init_mod(self, folder_name:str = ""):
        return {
            "folder_name":folder_name,
            "display_name" : folder_name,
            "authors" : "",
            "category" : "Misc",
            "version" : "",
            "characters" : "",
            "character_names" : [],
            "character_name": "",
            "slots" : "",
            "slot_list" : [],
            "mod_name" : "",
            "selected" : "",
            "path" : "",
            "wifi_safe" : "Uncertain",
            "info_toml" : False,
            "img" : None,
            "hash": "",
            "includes": []
        }

    def find_mod(self, name:str, path:str):
        if os.path.isdir(path):
            mod = self.init_mod(name)
            mod["path"] = path
            mod["hash"] = gen_hash_as_decimal(name)
            loader = Loader()
            generator = Generator()
            if loader.load_toml(path):
                mod["display_name"] = loader.display_name
                mod["authors"] = loader.authors
                mod["category"] = loader.category
                mod["version"] = loader.version
                mod["info_toml"] = True
                mod["wifi_safe"] = loader.wifi_safe
                mod["mod_name"] = loader.mod_name
            
            generator.preview_info_toml(path, "", "", "")
            mod["slots"] = format_slots(generator.slots)
            mod["slot_list"] = generator.slots
            mod["characters"] = common.group_char_name(generator.char_names, generator.group_names)  
            mod["character_names"] = generator.char_names
            mod["character_name"] = ", ".join(sorted(mod["character_names"]))
            mod["character_list"] = generator.char_keys
            mod["includes"] = generator.includes
            
            if mod["category"] == "Misc":
                mod["category"] = generator.category

            if not mod["mod_name"]:
                mod["mod_name"] = extract_mod_name(
                    mod["display_name"], 
                    generator.char_keys, 
                    mod["slot_list"], 
                    mod["category"])
                
            img_path = path + "/preview.webp"
            if os.path.exists(img_path):
                mod["img"] = self.find_image(path + "\\preview.webp", 100, 60, False)

            return mod
        return None
    
    def find_mods(self, directory:Union[str, list]):
        mods = []

        if self.start_callback is not None:
            self.start_callback(len(os.listdir(directory)))

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            if isinstance(directory, str):
                futures = [executor.submit(self.find_mod, folder_name, os.path.join(directory, folder_name)) for folder_name in os.listdir(directory)]
            elif isinstance(directory, list):
                futures = [executor.submit(self.find_mod, get_dir_name(d), d) for d in directory]
            if self.progress_callback is not None:
                [future.add_done_callback(self.progress_callback) for future in futures]
            for future in concurrent.futures.as_completed(futures):
                mod = future.result()
                if mod is not None:
                    mods.append(mod)

        sorted_mods = self.sort_mods(mods)
        self.callback(sorted_mods)

    def sort_mods(self, mods:list):
        sorted_result = []
        sorted_result = mods.copy()
        sorted_result = sorted(sorted_result, key=lambda d: d["mod_name"])
        return sorted_result

    def run(self):
        if isinstance(self.directory, str):
            if is_valid_dir(self.directory):
                self.find_mods(self.directory)
        elif isinstance(self.directory, list):
            if False not in [is_valid_dir(d) for d in self.directory]:
                self.find_mods(self.directory)