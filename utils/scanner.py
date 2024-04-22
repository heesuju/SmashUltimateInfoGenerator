import os
from threading import Thread
import concurrent.futures
from utils.loader import Loader
from utils.generator import Generator
from PIL import Image, ImageTk
import common

class Scanner(Thread):
    def __init__(self, directory:str, start_callback = None, progress_callback = None, callback = None):
        super().__init__()
        self.directory = directory
        self.start_callback = start_callback
        self.progress_callback = progress_callback
        self.callback = callback
        
    def find_image(self, directory, width, height):
        img = Image.open(directory)
        aspect_ratio = img.width / img.height
        
        # Resize the image to fit the target dimensions while preserving aspect ratio
        if width / aspect_ratio <= height:
            new_width = width
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = height
            new_width = int(new_height * aspect_ratio)

        return ImageTk.PhotoImage(img.resize((new_width, new_height), Image.Resampling.LANCZOS))
    
    def init_mod(self, folder_name:str = ""):
        return {
            "folder_name":folder_name,
            "display_name" : folder_name,
            "authors" : "",
            "category" : "",
            "version" : "",
            "characters" : "",
            "slots" : "",
            "mod_name" : "",
            "selected" : "",
            "path" : "",
            "info_toml" : False,
            "img" : None
        }

    def find_mod(self, name:str, path:str):
        if os.path.isdir(path):
            mod = self.init_mod(name)
            mod["path"] = path
            loader = Loader()
            generator = Generator()
            if loader.load_toml(path):
                mod["display_name"] = loader.display_name
                mod["authors"] = loader.authors
                mod["category"] = loader.category
                mod["version"] = loader.version
                mod["info_toml"] = True
            
            generator.preview_info_toml(path, "", "", "")
            mod["slots"] = common.slots_to_string(generator.slots)
            mod["characters"] = common.group_char_name(generator.char_names, generator.group_names)      
            
            mod["mod_name"] = mod["display_name"].replace(mod["slots"].lower(), "")
            mod["mod_name"] = mod["mod_name"].replace(mod["slots"].lower().replace(" ", ""), "")
            mod["mod_name"] = mod["mod_name"].replace(mod["slots"].upper(), "")
            mod["mod_name"] = mod["mod_name"].replace(mod["slots"].upper().replace(" ", ""), "")
            
            mod["mod_name"] = mod["mod_name"].replace(mod["characters"], "")
            mod["mod_name"] = mod["mod_name"].replace(mod["category"], "")
            mod["mod_name"] = common.trim_redundant_spaces(mod["mod_name"])
            img_path = path + "/preview.webp"
            if os.path.exists(img_path):
                mod["img"] = self.find_image(path + "\\preview.webp", 100, 60)

            return mod
        return None
    
    def find_mods(self, directory):
        mods = []

        if os.path.isdir(directory):
            self.start_callback(len(os.listdir(directory)))
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(self.find_mod, folder_name, os.path.join(directory, folder_name)) for folder_name in os.listdir(directory)]
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
        self.find_mods(self.directory)