"""
config.py: The view where various settings can be changed
"""

import json
import tkinter as tk
from src.constants.ui_params import PAD_H, PAD_V
from src.core.data import get_cache_directory
from src.core.data import load_config
from src.models.settings import Settings
from data.cache import PATH_CONFIG

class Config:
    def __init__(self, callback = None):
        self.new_window = None
        self.callback = callback
        self.settings = None
        self.load()

    def reset(self):
        self.settings = Settings()

    def load(self):
        self.settings = load_config()
            
    def save_config(self):
        with open(PATH_CONFIG, 'w') as f:
            json.dump(self.settings.__dict__, f, indent=4)
        
        if self.callback is not None:
            self.callback(self.settings.default_directory)
        
        print("Saved config")

    def set_close_on_apply(self, close_on_apply:bool):
        self.settings.close_on_apply = close_on_apply
        self.save_config()

    def set_sort_priority(self, priorities:list[dict]):
        self.settings.sort_priority = priorities
        self.save_config()

    def set_default_dir(self, default_dir):
        self.settings.default_directory = default_dir
        self.settings.cache_dir = get_cache_directory(default_dir)
        self.save_config()

    def set_cache_dir(self, cache_dir:str):
        self.settings.cache_dir = cache_dir
        self.save_config()

    def set_config(self, default_dir, display_name_format, folder_name_format, additional_elements, is_slot_capped=True, start_with_editor=False):
        self.settings.default_directory = default_dir
        self.settings.display_name_format = display_name_format
        self.settings.folder_name_format = folder_name_format
        self.set_additional_elements(additional_elements)
        self.settings.is_slot_capped = is_slot_capped
        self.settings.start_with_editor = start_with_editor
        self.save_config()

    def set_additional_elements(self, in_str):
        self.settings.additional_elements = []
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
                self.settings.additional_elements.append(trimmed_str)

    def get_additional_elements_as_str(self):
        out_str = ""
        for element in self.settings.additional_elements:
            if out_str:
                out_str += ", " + element
            else:
                out_str += element
        return out_str

    def on_save_config(self):
        self.set_config(self.e_mod_dir.get(), self.entry_display_name_format.get(), self.entry_folder_name_format.get(), self.entry_additional_elements.get(), True if self.slot_cap.get() == 1 else False, True if self.start_w_editor.get() == 1 else False)
        self.new_window.destroy()

    def on_restore_config(self):
        self.reset()
        self.entry_display_name_format.delete(0, tk.END)
        self.entry_display_name_format.insert(0, self.settings.display_name_format)
        self.entry_folder_name_format.delete(0, tk.END)
        self.entry_folder_name_format.insert(0, self.settings.folder_name_format)
        self.entry_additional_elements.delete(0, tk.END)
        self.slot_cap.set(1 if self.settings.is_slot_capped else 0)
        self.start_w_editor.set(1 if self.settings.start_with_editor else 0)

    def open_config(self, root):
        if self.new_window is not None:
            self.new_window.destroy()
    
        self.new_window = tk.Toplevel(root)
        self.new_window.title("Config")
        self.new_window.geometry("400x400")
        self.new_window.columnconfigure(0, weight=1)
        self.new_window.rowconfigure(12, weight=1)
        self.new_window.configure(padx=10, pady=10)
        self.new_window.lift(root)
        
        self.l_mod_dir = tk.Label(self.new_window, text="Mod Directory(required)")
        self.l_mod_dir.grid(row=0, column=0, sticky=tk.W)
        
        self.e_mod_dir = tk.Entry(self.new_window, width=10)
        self.e_mod_dir.grid(row=1, column=0, sticky=tk.EW, pady = (0, PAD_V))
        
        self.config_label = tk.Label(self.new_window, text="Change default format for display and folder name")
        self.config_label.grid(row=2, column=0, sticky=tk.W, pady = (0, PAD_H))
        self.help_label = tk.Label(self.new_window, text="*Arrange values: {characters}, {slots}, {mod}, {category}")
        self.help_label.grid(row=3, column=0, sticky=tk.W, pady = (0, PAD_V * 2))

        self.label_folder_name_format = tk.Label(self.new_window, text="Folder Name Format")
        self.label_folder_name_format.grid(row=4, column=0, sticky=tk.W)

        self.entry_folder_name_format = tk.Entry(self.new_window, width=10)
        self.entry_folder_name_format.grid(row=5, column=0, sticky=tk.EW, pady = (0, PAD_V))

        self.label_display_name_format = tk.Label(self.new_window, text="Display Name Format", justify='left')
        self.label_display_name_format.grid(row=6, column=0, sticky=tk.W)

        self.entry_display_name_format = tk.Entry(self.new_window, width=10)
        self.entry_display_name_format.grid(row=7, column=0, sticky=tk.EW, pady = (0, PAD_V))
        
        self.label_additional_elements = tk.Label(self.new_window, text="Additional Elements(separate by \",\")", justify='left')
        self.label_additional_elements.grid(row=8, column=0, sticky=tk.W)

        self.entry_additional_elements = tk.Entry(self.new_window, width=10)
        self.entry_additional_elements.grid(row=9, column=0, sticky=tk.EW, pady = (0, PAD_V))

        self.slot_cap = tk.IntVar(value = (1 if self.settings.is_slot_capped else 0))
        self.cbox_capitalize_slots = tk.Checkbutton(self.new_window, text="Capitalize slot prefix(e.g. C02 or c02)", variable=self.slot_cap)
        self.cbox_capitalize_slots.grid(row=10, column=0, sticky=tk.W)
        
        self.start_w_editor = tk.IntVar(value = (1 if self.settings.start_with_editor else 0))
        self.cbox_start_w_editor = tk.Checkbutton(self.new_window, text="Show editor on start", variable=self.start_w_editor)
        self.cbox_start_w_editor.grid(row=11, column=0, sticky=tk.W)

        self.frame_config = tk.Frame(self.new_window)
        self.frame_config.grid(row=12, column=0, sticky=tk.SE)

        self.btn_restore = tk.Button(self.frame_config, text="Restore", command=lambda: self.on_restore_config())
        self.btn_restore.pack(side="left", padx=(0, PAD_H))

        self.btn_save = tk.Button(self.frame_config, text="Save", command=lambda: self.on_save_config())
        self.btn_save.pack()
        
        self.e_mod_dir.delete(0, tk.END)
        self.e_mod_dir.insert(0, self.settings.default_directory)
        self.entry_display_name_format.delete(0, tk.END)
        self.entry_display_name_format.insert(0, self.settings.display_name_format)
        self.entry_folder_name_format.delete(0, tk.END)
        self.entry_folder_name_format.insert(0, self.settings.folder_name_format)
        self.entry_additional_elements.delete(0, tk.END)
        self.entry_additional_elements.insert(0, self.get_additional_elements_as_str())
