from tkinter import ttk
import tkinter as tk
from defs import PAD_H, PAD_V, CATEGORIES
from .common_ui import *
from data import PATH_CHAR_NAMES
from common import csv_to_dict
from utils.cleaner import remove_redundant_spacing

class Filter:
    def __init__(self, root, search_fn, refresh_fn) -> None:
        self.frame = tk.Frame(root)
        self.frame.pack(padx=PAD_H, pady=PAD_V/2, fill="x")
        
        self.frame.columnconfigure(1, weight=2)
        self.frame.columnconfigure(1, minsize=100)
        self.frame.columnconfigure(3, weight=2)
        self.frame.columnconfigure(3, minsize=100)
        
        self.search_fn = search_fn
        self.refresh_fn = refresh_fn
        
        self.entry_mod_name = self.add_filter_entry(0, 0, "Mod Name")
        self.entry_author = self.add_filter_entry(0, 2, "Author")
        
        self.cbox_category = self.add_filter_dropdown(1, 0, "Category", ["All"] + CATEGORIES)
        label_slots = ttk.Label(self.frame, text="Slots")
        label_slots.grid(row=1, column=2, sticky=tk.EW, padx=(0,PAD_H))
        
        self.frame_slots = tk.Frame(self.frame)
        self.frame_slots.grid(row=1, column=3, sticky=tk.EW, padx=(0,PAD_H), pady=PAD_V/2)

        vcmd = (root.register(self.callback)) 

        self.entry_slots_from = tk.Entry(self.frame_slots, width=5, validate='all', validatecommand=(vcmd, '%P'))
        self.entry_slots_from.pack(side=tk.LEFT, fill=tk.X, expand=True)

        label_slot_n = ttk.Label(self.frame_slots, text="~")
        label_slot_n.pack(side=tk.LEFT, padx=PAD_H)

        self.entry_slots_to = tk.Entry(self.frame_slots, width=5, validate='all', validatecommand=(vcmd, '%P'))
        self.entry_slots_to.pack(side=tk.LEFT, fill=tk.X, expand=True)

        series = ["All"] + sorted(csv_to_dict(PATH_CHAR_NAMES, "Series"))
        series = [remove_redundant_spacing(i) for i in series]
        self.cbox_series = self.add_filter_dropdown(2, 0, "Series", series)
        self.cbox_series.bind("<<ComboboxSelected>>", self.on_series_changed)

        chars = ["All"] + sorted(csv_to_dict(PATH_CHAR_NAMES, "Custom"))
        self.cbox_char = self.add_filter_dropdown(2, 2, "Character", chars)

        self.cbox_info = self.add_filter_dropdown(3, 0, "Info.toml", ["All", "Included", "Not Included"])
        self.cbox_wifi = self.add_filter_dropdown(3, 2, "Wifi-Safe", ["All", "Safe", "Not Safe", "Uncertain"])
        
        self.frame_actions = tk.Frame(self.frame)
        self.frame_actions.grid(row=4, column=0, columnspan=4, pady=(PAD_V/2, 0), sticky=tk.E)
        
        self.btn_search = tk.Button(self.frame_actions, text="Search", cursor='hand2', command=self.search_fn)
        self.btn_search.pack(side=tk.LEFT, padx=(0, PAD_H))

        self.btn_clear = tk.Button(self.frame_actions, text="Clear", cursor='hand2', command=self.clear)
        self.btn_clear.pack(side=tk.LEFT, padx=(0, PAD_H))

        self.btn_refresh = tk.Button(self.frame_actions, text="Refresh", cursor='hand2', command=self.refresh_fn)
        self.btn_refresh.pack(side=tk.LEFT, padx=(0, PAD_H))
    
    def callback(self, P):
        if (str.isdigit(P) and len(P) <= 3) or P == "":
            return True
        else:
            return False
        
    def add_filter_entry(self, row, col, name):
        label = ttk.Label(self.frame, text=name)
        label.grid(row=row, column=col, sticky=tk.EW, padx=(0,PAD_H))
        entry = tk.Entry(self.frame)
        entry.grid(row=row, column=col+1, sticky=tk.EW, padx=(0,PAD_H), pady=PAD_V/2)
        entry.bind("<Return>", self.on_filter_submitted)
        return entry
    
    def add_filter_dropdown(self, row, col, name, data):
        label = ttk.Label(self.frame, text=name)
        label.grid(row=row, column=col, sticky=tk.EW, padx=(0,PAD_H))

        combobox = ttk.Combobox(self.frame, values=data, width=10)
        combobox.grid(row=row, column=col+1, sticky=tk.EW, padx=(0,PAD_H), pady=PAD_V/2)
        combobox.bind("<<ComboboxSelected>>", self.on_combobox_selected)
        combobox.set(data[0])
        return combobox
    
    def on_filter_submitted(self, event):
        self.search_fn()

    def on_combobox_selected(self, event):
        pass

    def on_series_changed(self, event):
        char_data = csv_to_dict(PATH_CHAR_NAMES)
        selected_series = get_text(self.cbox_series)
        filtered_chars = []
        if selected_series != "All":
            for c in char_data:
                if c.get("Series") == selected_series:
                    filtered_chars.append(c.get("Custom"))
        else:
            filtered_chars = sorted(csv_to_dict(PATH_CHAR_NAMES, "Custom"))

        chars = ["All"] if len(filtered_chars) > 1 else []
        chars.extend(sorted(filtered_chars))
        self.cbox_char.config(values=chars)
        self.cbox_char.set(chars[0])

    def get_filter_params(self, lowercase:bool = True):
        return {
            "mod_name": get_text(self.entry_mod_name).lower() if lowercase else get_text(self.entry_mod_name),
            "authors": get_text(self.entry_author).lower() if lowercase else get_text(self.entry_author),
            "characters": get_text(self.cbox_char).lower() if lowercase else get_text(self.cbox_char),
            "series": get_text(self.cbox_series).lower() if lowercase else get_text(self.cbox_series),
            "category": get_text(self.cbox_category).lower() if lowercase else get_text(self.cbox_category),
            "info_toml": get_text(self.cbox_info).lower() if lowercase else get_text(self.cbox_info),
            "wifi_safe": get_text(self.cbox_wifi).lower() if lowercase else get_text(self.cbox_wifi),
            "slot_from": get_text(self.entry_slots_from).lower() if lowercase else get_text(self.entry_slots_from),
            "slot_to": get_text(self.entry_slots_to).lower() if lowercase else get_text(self.entry_slots_to)
        }
    
    def clear(self):
        clear_text(self.entry_mod_name)
        clear_text(self.entry_author)
        chars = ["All"] + sorted(csv_to_dict(PATH_CHAR_NAMES, "Custom"))
        self.cbox_char.config(values=chars)
        self.cbox_char.set("All")
        self.cbox_series.set("All")
        self.cbox_category.set("All")
        self.cbox_info.set("All")
        self.cbox_wifi.set("All")
        clear_text(self.entry_slots_from)
        clear_text(self.entry_slots_to)
        self.search_fn()

    def filter_mods(self, mods):
        filter_params = self.get_filter_params()
        outputs = []
        data = csv_to_dict(PATH_CHAR_NAMES)
        
        for mod in mods:
            if filter_params.get("mod_name") not in mod["mod_name"].lower(): continue
            if filter_params.get("authors") not in mod["authors"].lower(): continue
            if filter_params.get("characters") != "all":
                found_match = False
                for ch in mod["character_names"]:
                    if ch.lower() == filter_params.get("characters"):
                        found_match = True
                        break

                if  found_match == False: 
                    continue
                
            if filter_params.get("series") != "all":
                should_include = False
                for char_name in mod["character_list"]:
                    if filter_params.get("series") == self.get_series(char_name, data):
                        should_include = True
                
                if should_include == False:
                    continue
            
            if filter_params.get("category") != "all":
                if filter_params.get("category") != mod["category"].lower():
                    continue
            
            if filter_params.get("info_toml") != "all":
                if filter_params.get("info_toml") == "included" and mod["info_toml"] == False:
                    continue
                elif filter_params.get("info_toml") == "not included" and mod["info_toml"] == True:
                    continue

            if filter_params.get("wifi_safe") != "all":
                if filter_params.get("wifi_safe") != mod["wifi_safe"].lower():
                    continue

            if filter_params.get("slot_from") or filter_params.get("slot_to"):
                contains_slot = False
                min_slot = int(filter_params.get("slot_from") if filter_params.get("slot_from") else 0)
                max_slot = int(filter_params.get("slot_to") if filter_params.get("slot_to") else 255)
                
                if max_slot >= min_slot:
                    for slot in mod["slot_list"]:
                        if slot >= min_slot and slot <= max_slot:
                            contains_slot = True
                            break
                
                if contains_slot == False:
                    continue
                
            outputs.append(mod)
        
        return outputs

    def get_series(self, character_name:str, data):
        for d in data:
            if d.get("Key") ==  character_name:
                return d.get("Series").lower()