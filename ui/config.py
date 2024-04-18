import json
import os
import tkinter as tk
import defs
from cache import PATH_CONFIG
from utils.load_config import load_config

class Config:
    def __init__(self):
        self.new_window = None
        self.reset()
        self.load()

    def reset(self):
        self.default_dir = ""
        self.is_slot_capped = True
        self.start_with_editor = False
        self.display_name_format = "{characters} {slots} {mod}"
        self.folder_name_format = "{category}_{characters}[{slots}]_{mod}"
        self.additional_elements = []
            
    def save_config(self):
        config_dict = {
            "default_directory":self.default_dir,
            "display_name_format":self.display_name_format,
            "folder_name_format":self.folder_name_format,
            "additional_elements":self.additional_elements,
            "is_slot_capped":self.is_slot_capped,
            "start_with_editor":self.start_with_editor}
        
        with open(PATH_CONFIG, 'w') as f:
            json.dump(config_dict, f, indent=4)
            
        print("Saved config")

    def load(self):
        data = load_config()
        if data is not None:
            self.default_dir = data["default_directory"]
            if data["display_name_format"]:
                self.display_name_format = data["display_name_format"]
            if data["folder_name_format"]:
                self.folder_name_format = data["folder_name_format"]
            if len(data["additional_elements"]) > 0:
                self.additional_elements = data["additional_elements"]
            if data.get("is_slot_capped") is not None:
                self.is_slot_capped = data["is_slot_capped"]
            if data.get("start_with_editor") is not None:
                self.start_with_editor = data["start_with_editor"]
            print("Loaded config")
        else:
            print("No saved config")
            self.save_config()

    def set_default_dir(self, default_dir):
        self.default_dir = default_dir
        self.save_config()

    def set_config(self, display_name_format, folder_name_format, additional_elements, is_slot_capped=True, start_with_editor=False):
        self.display_name_format = display_name_format
        self.folder_name_format = folder_name_format
        self.set_additional_elements(additional_elements)
        self.is_slot_capped = is_slot_capped
        self.start_with_editor = start_with_editor
        self.save_config()

    def set_additional_elements(self, in_str):
        self.additional_elements = []
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
                self.additional_elements.append(trimmed_str)

    def get_additional_elements_as_str(self):
        out_str = ""
        for element in self.additional_elements:
            if out_str:
                out_str += ", " + element
            else:
                out_str += element
        return out_str

    def on_save_config(self):
        self.set_config(self.entry_display_name_format.get(), self.entry_folder_name_format.get(), self.entry_additional_elements.get(), True if self.slot_cap.get() == 1 else False, True if self.start_w_editor.get() == 1 else False)
        self.new_window.destroy()

    def on_restore_config(self):
        self.reset()
        self.entry_display_name_format.delete(0, tk.END)
        self.entry_display_name_format.insert(0, self.display_name_format)
        self.entry_folder_name_format.delete(0, tk.END)
        self.entry_folder_name_format.insert(0, self.folder_name_format)
        self.entry_additional_elements.delete(0, tk.END)
        self.slot_cap.set(1 if self.is_slot_capped else 0)
        self.start_w_editor.set(1 if self.start_with_editor else 0)

    def open_config(self, root):
        if self.new_window is not None:
            self.new_window.destroy()
    
        self.new_window = tk.Toplevel(root)
        self.new_window.title("Config")
        self.new_window.geometry("320x340")
        self.new_window.columnconfigure(0, weight=1)
        self.new_window.rowconfigure(10, weight=1)
        self.new_window.configure(padx=10, pady=10)

        self.config_label = tk.Label(self.new_window, text="Change default format for display and folder name")
        self.config_label.grid(row=0, column=0, sticky=tk.W, pady = (0, defs.PAD_H))
        self.help_label = tk.Label(self.new_window, text="*Arrange values: {characters}, {slots}, {mod}, {category}")
        self.help_label.grid(row=1, column=0, sticky=tk.W, pady = (0, defs.PAD_V * 2))

        self.label_folder_name_format = tk.Label(self.new_window, text="Folder Name Format")
        self.label_folder_name_format.grid(row=2, column=0, sticky=tk.W)

        self.entry_folder_name_format = tk.Entry(self.new_window, width=10)
        self.entry_folder_name_format.grid(row=3, column=0, sticky=tk.EW, pady = (0, defs.PAD_V))

        self.label_display_name_format = tk.Label(self.new_window, text="Display Name Format", justify='left')
        self.label_display_name_format.grid(row=4, column=0, sticky=tk.W)

        self.entry_display_name_format = tk.Entry(self.new_window, width=10)
        self.entry_display_name_format.grid(row=5, column=0, sticky=tk.EW, pady = (0, defs.PAD_V))
        
        self.label_additional_elements = tk.Label(self.new_window, text="Additional Elements(separate by \",\")", justify='left')
        self.label_additional_elements.grid(row=6, column=0, sticky=tk.W)

        self.entry_additional_elements = tk.Entry(self.new_window, width=10)
        self.entry_additional_elements.grid(row=7, column=0, sticky=tk.EW, pady = (0, defs.PAD_V))

        self.slot_cap = tk.IntVar(value = (1 if self.is_slot_capped else 0))
        self.cbox_capitalize_slots = tk.Checkbutton(self.new_window, text="Capitalize slot prefix(e.g. C02 or c02)", variable=self.slot_cap)
        self.cbox_capitalize_slots.grid(row=8, column=0, sticky=tk.W)
        
        self.start_w_editor = tk.IntVar(value = (1 if self.start_with_editor else 0))
        self.cbox_start_w_editor = tk.Checkbutton(self.new_window, text="Show editor on start", variable=self.start_w_editor)
        self.cbox_start_w_editor.grid(row=9, column=0, sticky=tk.W)

        self.frame_config = tk.Frame(self.new_window)
        self.frame_config.grid(row=10, column=0, sticky=tk.SE)

        self.btn_restore = tk.Button(self.frame_config, text="Restore", command=lambda: self.on_restore_config())
        self.btn_restore.pack(side="left", padx=(0, defs.PAD_H))

        self.btn_save = tk.Button(self.frame_config, text="Save", command=lambda: self.on_save_config())
        self.btn_save.pack()
        
        self.entry_display_name_format.delete(0, tk.END)
        self.entry_display_name_format.insert(0, self.display_name_format)
        self.entry_folder_name_format.delete(0, tk.END)
        self.entry_folder_name_format.insert(0, self.folder_name_format)
        self.entry_additional_elements.delete(0, tk.END)
        self.entry_additional_elements.insert(0, self.get_additional_elements_as_str())