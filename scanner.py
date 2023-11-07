import os
from threading import Thread
from loader import Loader
from mod import Mod

class Scanner(Thread):
    def __init__(self, directory:str, callback):
        super().__init__()
        self.directory = directory
        self.loader = Loader()
        self.callback = callback

    def find_mods(self, directory):
        mods = []

        if os.path.isdir(directory):
            for folder_name in os.listdir(directory):
                
                folder_path = os.path.join(directory, folder_name)
                if os.path.isdir(folder_path):
                    mod = Mod(folder_name, folder_name, False, None)
                    mods.append(mod)
                    if self.loader.load_toml(folder_path):
                        mod.display_name = self.loader.display_name
        
        self.callback(mods)

    def run(self):
        self.find_mods(self.directory)