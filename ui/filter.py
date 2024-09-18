from tkinter import ttk
import tkinter as tk
from defs import PAD_H, PAD_V
from .common_ui import *
from data import PATH_CHAR_NAMES
from common import csv_to_dict
from utils.cleaner import remove_redundant_spacing

class Filter:
    def __init__(self, root, search_fn, refresh_fn) -> None:
        self.frame = ttk.LabelFrame(root, text="Filter")
        self.frame.pack(padx=PAD_H, pady=PAD_V, fill="x")
        self.search_fn = search_fn
        self.refresh_fn = refresh_fn
        
        self.entry_mod_name = self.add_filter_entry(0, 0, "Mod Name")
        self.entry_author = self.add_filter_entry(0, 2, "Author")
        self.entry_character = self.add_filter_entry(0, 4, "Character")
        
        data = ["All"]
        series = sorted(csv_to_dict(PATH_CHAR_NAMES, "Series"))
        data.extend(series)
        data = [remove_redundant_spacing(i) for i in data]
        self.cbox_series = self.add_filter_dropdown(1, 0, "Series", data)

        self.frame_actions = tk.Frame(self.frame)
        self.frame_actions.grid(row=3, column=0, columnspan=2, padx=(PAD_H, 0), pady=(PAD_V/2), sticky=tk.NSEW)
        
        self.btn_search = tk.Button(self.frame_actions, text="Search", cursor='hand2', command=self.search_fn)
        self.btn_search.pack(side=tk.LEFT, padx=(0, PAD_H))

        self.btn_clear = tk.Button(self.frame_actions, text="Clear", cursor='hand2', command=self.clear)
        self.btn_clear.pack(side=tk.LEFT, padx=(0, PAD_H))

        self.btn_refresh = tk.Button(self.frame_actions, text="Refresh", cursor='hand2', command=self.refresh_fn)
        self.btn_refresh.pack(side=tk.LEFT, padx=(0, PAD_H))

    def add_filter_entry(self, row, col, name):
        label = ttk.Label(self.frame, text=name)
        label.grid(row=row, column=col, sticky=tk.W, padx=5)
        entry = tk.Entry(self.frame)
        entry.grid(row=row, column=col+1)
        entry.bind("<Return>", self.on_filter_submitted)
        return entry
    
    def add_filter_dropdown(self, row, col, name, data):
        label = ttk.Label(self.frame, text=name)
        label.grid(row=row, column=col, sticky=tk.W, padx=5)

        combobox = ttk.Combobox(self.frame, values=data, width=10)
        combobox.grid(row=row, column=col+1, sticky=tk.EW)
        combobox.bind("<<ComboboxSelected>>", self.on_combobox_selected)
        combobox.set(data[0])
        return combobox
    
    def on_filter_submitted(self, event):
        self.search_fn()

    def on_combobox_selected(self, event):
        pass

    def get_filter_params(self, lowercase:bool = True):
        return {
            "mod_name": get_text(self.entry_mod_name).lower() if lowercase else get_text(self.entry_mod_name),
            "authors": get_text(self.entry_author).lower() if lowercase else get_text(self.entry_author),
            "characters": get_text(self.entry_character).lower() if lowercase else get_text(self.entry_character),
            "series": get_text(self.cbox_series).lower() if lowercase else get_text(self.cbox_series)
        }
    
    def clear(self):
        clear_text(self.entry_mod_name)
        clear_text(self.entry_author)
        clear_text(self.entry_character)
        self.cbox_series.set("All")
        self.search_fn()

    def filter_mods(self, mods):
        filter_params = self.get_filter_params()
        outputs = []
        data = csv_to_dict(PATH_CHAR_NAMES)
        
        for mod in mods:
            if filter_params.get("mod_name") not in mod["mod_name"].lower(): continue
            if filter_params.get("authors") not in mod["authors"].lower(): continue
            if filter_params.get("characters") not in mod["characters"].lower(): continue
            if filter_params.get("series") != "all":
                should_include = False
                for char_name in mod["character_list"]:
                    if filter_params.get("series") == self.get_series(char_name, data):
                        should_include = True
                
                if should_include == False:
                    continue
            
            outputs.append(mod)
        
        return outputs

    def get_series(self, character_name:str, data):
        for d in data:
            if d.get("Key") ==  character_name:
                return d.get("Series").lower()