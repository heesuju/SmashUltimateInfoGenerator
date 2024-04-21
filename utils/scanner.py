import os
from threading import Thread
import concurrent.futures
from utils.loader import Loader
from utils.generator import Generator
from mod import Mod
from PIL import Image, ImageTk
import common

class Scanner(Thread):
    def __init__(self, directory:str, callback):
        super().__init__()
        self.directory = directory
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
    
    def find_mod(self, name:str, path:str):
        if os.path.isdir(path):
            mod = Mod(name, name, "", "", "", "", "", "", False)
            mod.path = path
            loader = Loader()
            generator = Generator()
            if loader.load_toml(path):
                mod.display_name = loader.display_name
                mod.authors = loader.authors
                mod.category = loader.category
                mod.version = loader.version
                mod.info_toml = True
            
            generator.preview_info_toml(path, "", "", "")
            mod.slots = common.slots_to_string(generator.slots)
            mod.characters = common.group_char_name(generator.char_names, generator.group_names)      
            
            mod.mod_name = mod.display_name.replace(mod.slots.lower(), "")
            mod.mod_name = mod.mod_name.replace(mod.slots.lower().replace(" ", ""), "")
            mod.mod_name = mod.mod_name.replace(mod.slots.upper(), "")
            mod.mod_name = mod.mod_name.replace(mod.slots.upper().replace(" ", ""), "")
            
            mod.mod_name = mod.mod_name.replace(mod.characters, "")
            mod.mod_name = mod.mod_name.replace(mod.category, "")
            mod.mod_name = common.trim_redundant_spaces(mod.mod_name)
            img_path = path + "/preview.webp"
            if os.path.exists(img_path):
                mod.img = self.find_image(path + "\\preview.webp", 100, 60)

            return mod
        return None
    
    def find_mods(self, directory):
        mods = []

        if os.path.isdir(directory):
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(self.find_mod, folder_name, os.path.join(directory, folder_name)) for folder_name in os.listdir(directory)]
                for future in concurrent.futures.as_completed(futures):
                    mod = future.result()
                    if mod is not None:
                        mods.append(mod)

        self.callback(mods)

    def run(self):
        self.find_mods(self.directory)