import os
from threading import Thread
from loader import Loader
from generator import Generator
from mod import Mod
from PIL import Image, ImageTk
from image_resize import ImageResize
import common

class Scanner(Thread):
    def __init__(self, directory:str, callback):
        super().__init__()
        self.directory = directory
        self.loader = Loader()
        self.generator = Generator()
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
    
    def find_mods(self, directory):
        mods = []

        if os.path.isdir(directory):
            for folder_name in os.listdir(directory):
                
                folder_path = os.path.join(directory, folder_name)
                if os.path.isdir(folder_path):
                    mod = Mod(folder_name, folder_name, "", "", "", "", "", "", False)
                    mods.append(mod)
                    mod.path = folder_path

                    if self.loader.load_toml(folder_path):
                        mod.display_name = self.loader.display_name
                        mod.authors = self.loader.authors
                        mod.category = self.loader.category
                        mod.version = self.loader.version
                        mod.info_toml = True
                    
                    self.generator.preview_info_toml(folder_path, "", "", "")
                    mod.slots = common.slots_to_string(self.generator.slots)
                    mod.characters = common.group_char_name(self.generator.char_names, self.generator.group_names)      
                    
                    mod.mod_name = mod.display_name.replace(mod.slots, "")
                    mod.mod_name = mod.display_name.replace(mod.slots.replace(" ", ""), "")
                    mod.mod_name = mod.mod_name.replace(mod.characters, "")
                    mod.mod_name = mod.mod_name.replace(mod.category, "")
                    mod.mod_name = common.trim_redundant_spaces(mod.mod_name)
                    img_path = folder_path + "/preview.webp"
                    if os.path.exists(img_path):
                        mod.img = self.find_image(folder_path + "\\preview.webp", 100, 60)

        self.callback(mods)

    def run(self):
        self.find_mods(self.directory)