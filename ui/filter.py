import os
from tkinter import ttk
from PIL import ImageTk
import tkinter as tk
from idlelib.tooltip import Hovertip
from defs import PAD_H, PAD_V, CATEGORIES
from . import PATH_ICON
from .sorting import Sorting, sort_by_columns
from .common_ui import *
from common import get_completion
from data import PATH_CHAR_NAMES
from common import csv_to_dict
from utils.cleaner import remove_redundant_spacing
from .config import load_config

INFO_VALUES = ["All", "Included", "Not Included"]
WIFI_VALUES = ["All", "Safe", "Not Safe", "Uncertain"]

class Filter:
    def __init__(self, root, search_fn, refresh_fn) -> None:
        self.sort_view = None
        self.root = root
        self.frame = tk.Frame(root)
        self.frame.pack(padx=PAD_H, pady=PAD_V/2, fill="x")
        
        self.frame.columnconfigure(1, weight=2)
        self.frame.columnconfigure(1, minsize=100)
        self.frame.columnconfigure(3, weight=2)
        self.frame.columnconfigure(3, minsize=100)
        
        self.search_fn = search_fn
        self.refresh_fn = refresh_fn
        
        self.entry_mod_name = self.add_filter_entry(0, 0, "Mod Name")
        self.entry_author = self.add_filter_entry(0, 2, "Author", False)
        
        self.cbox_category = self.add_filter_dropdown(1, 0, "Category", ["All"] + CATEGORIES)
        label_slots = ttk.Label(self.frame, text="Slots")
        label_slots.grid(row=1, column=2, sticky=tk.EW, padx=(0,PAD_H))
        
        self.frame_slots = tk.Frame(self.frame)
        self.frame_slots.grid(row=1, column=3, sticky=tk.EW, pady=PAD_V/2)

        vcmd = (root.register(validate_slot)) 

        self.entry_slots_from = tk.Entry(self.frame_slots, width=5, validate='all', validatecommand=(vcmd, '%P'))
        self.entry_slots_from.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry_slots_from.bind("<Return>", self.on_filter_submitted)

        label_slot_n = ttk.Label(self.frame_slots, text="~")
        label_slot_n.pack(side=tk.LEFT, padx=PAD_H)
        label_slot_n.bind("<Return>", self.on_filter_submitted)

        self.entry_slots_to = tk.Entry(self.frame_slots, width=5, validate='all', validatecommand=(vcmd, '%P'))
        self.entry_slots_to.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry_slots_to.bind("<Return>", self.on_filter_submitted)

        self.series = ["All"] + sorted(csv_to_dict(PATH_CHAR_NAMES, "Series"))
        self.series = [remove_redundant_spacing(i) for i in self.series]
        self.cbox_series = self.add_filter_dropdown(2, 0, "Series", self.series)
        self.cbox_series.bind("<<ComboboxSelected>>", self.on_series_changed)

        chars = ["All"] + sorted(csv_to_dict(PATH_CHAR_NAMES, "Custom"))
        self.char_values = chars
        self.cbox_char = self.add_filter_dropdown(2, 2, "Character", chars, False)

        self.cbox_info = self.add_filter_dropdown(3, 0, "Info.toml", INFO_VALUES)
        self.cbox_wifi = self.add_filter_dropdown(3, 2, "Wifi-Safe", WIFI_VALUES, False)
        
        self.show_only_enabled = tk.IntVar()
        self.ckbox_enabled = tk.Checkbutton(self.frame, text="Show only enabled", variable=self.show_only_enabled, cursor='hand2')
        self.ckbox_enabled.grid(row=4, column=0, columnspan=2, pady=(PAD_V/2, 0), sticky=tk.W)

        self.frame_actions = tk.Frame(self.frame)
        self.frame_actions.grid(row=4, column=2, columnspan=2, pady=(PAD_V/2, 0), sticky=tk.E)

        self.icon_sort = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'config.png'))
        self.btn_sort = tk.Button(self.frame_actions, image=self.icon_sort, relief=tk.FLAT, cursor='hand2', command=self.show_sort)
        self.btn_sort.pack(side=tk.LEFT)
        sort_tip = Hovertip(self.btn_sort,'Sort Config')

        separator = ttk.Separator(self.frame_actions, orient='vertical')
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=PAD_H)

        self.icon_refresh = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'refresh.png'))
        self.btn_refresh = tk.Button(self.frame_actions, image=self.icon_refresh, relief=tk.FLAT, cursor='hand2', command=self.refresh_fn)
        self.btn_refresh.pack(side=tk.LEFT)
        refresh_tip = Hovertip(self.btn_refresh,'Refresh')
        
        separator = ttk.Separator(self.frame_actions, orient='vertical')
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=PAD_H)

        self.icon_clear = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'clear.png'))
        self.btn_clear = tk.Button(self.frame_actions, image=self.icon_clear, relief=tk.FLAT, cursor='hand2', command=self.clear)
        self.btn_clear.pack(side=tk.LEFT)
        clear_tip = Hovertip(self.btn_clear,'Clear')

        separator = ttk.Separator(self.frame_actions, orient='vertical')
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=PAD_H)

        self.icon_search = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'search.png'))
        self.btn_search = tk.Button(self.frame_actions, image=self.icon_search, relief=tk.FLAT, cursor='hand2', command=self.search_fn)
        self.btn_search.pack(side=tk.LEFT)
        search_tip = Hovertip(self.btn_search,'Search')
        
    def add_filter_entry(self, row, col, name, add_padding:bool=True):
        label = ttk.Label(self.frame, text=name)
        label.grid(row=row, column=col, sticky=tk.EW, padx=(0,PAD_H))
        entry = tk.Entry(self.frame)
        entry.grid(row=row, column=col+1, sticky=tk.EW, padx=(0,PAD_H if add_padding else 0), pady=PAD_V/2)
        entry.bind("<Return>", self.on_filter_submitted)
        return entry
    
    def add_filter_dropdown(self, row, col, name, data, add_padding:bool=True):
        label = ttk.Label(self.frame, text=name)
        label.grid(row=row, column=col, sticky=tk.EW, padx=(0,PAD_H))

        combobox = ttk.Combobox(self.frame, values=data, width=10)
        combobox.grid(row=row, column=col+1, sticky=tk.EW, padx=(0,PAD_H if add_padding else 0), pady=PAD_V/2)
        combobox.bind("<Return>", self.on_combobox_submitted)
        combobox.set(data[0])
        return combobox
    
    def on_filter_submitted(self, event):
        self.search_fn()

    def on_combobox_submitted(self, event):
        new_category = get_completion(get_text(self.cbox_category), ["All"] + CATEGORIES)
        self.cbox_category.set(new_category if new_category else "All")

        new_info = get_completion(get_text(self.cbox_info), INFO_VALUES)
        self.cbox_info.set(new_info if new_info else "All")

        new_series = get_completion(get_text(self.cbox_series), self.series)
        self.cbox_series.set(new_series if new_series else "All") 
        
        char_data = csv_to_dict(PATH_CHAR_NAMES)
        
        filtered_chars = []
        if new_series != "All":
            for c in char_data:
                if c.get("Series") == new_series:
                    filtered_chars.append(c.get("Custom"))
        else:
            filtered_chars = sorted(csv_to_dict(PATH_CHAR_NAMES, "Custom"))

        chars = ["All"] if len(filtered_chars) > 1 else []
        chars.extend(sorted(filtered_chars))
        self.char_values = chars

        new_char = get_char_completion(get_text(self.cbox_char), self.char_values)
        self.cbox_char.config(values=self.char_values)
        self.cbox_char.set(new_char if new_char else "All")

        new_wifi = get_completion(get_text(self.cbox_wifi), WIFI_VALUES)
        self.cbox_wifi.set(new_wifi if new_wifi else "All")

        self.search_fn()

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
        self.char_values = chars
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
            "slot_to": get_text(self.entry_slots_to).lower() if lowercase else get_text(self.entry_slots_to),
            "enabled_only": self.show_only_enabled.get()
        }
    
    def reset(self):
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
        self.show_only_enabled.set(False)

    def clear(self):
        self.reset()
        self.search_fn()

    def filter_mods(self, mods, enabled_list:list = []):
        filter_params = self.get_filter_params()
        outputs = []
        data = csv_to_dict(PATH_CHAR_NAMES)
        
        for mod in mods:
            if filter_params.get("enabled_only", False):
                if mod["hash"] not in enabled_list: 
                    continue

            if filter_params.get("mod_name") not in mod["mod_name"].lower(): 
                continue

            if filter_params.get("authors") not in mod["authors"].lower(): 
                continue

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

        sort_prioirty = load_config().get("sort_priority", None)
        if sort_prioirty is not None:
            return sort_by_columns(outputs, sort_prioirty)
        else:
            return outputs

    def get_series(self, character_name:str, data):
        for d in data:
            if d.get("Key") ==  character_name:
                return d.get("Series").lower()
            
    def show_sort(self):
        if self.sort_view is None:
            self.sort_view = Sorting(self.on_sorting_changed)
        self.sort_view.open(self.root)

    def on_sorting_changed(self):
        self.search_fn()

def get_char_completion(text:str, values:list)->None:
    if len(values) == 1:
        result = values[0]
    elif len(values) > 1:
        chars = csv_to_dict(PATH_CHAR_NAMES)
        options = set()
        for c in chars:
            name = c.get("Custom")
            if name in values:
                key = c.get("Key")
                org = c.get("Value")
                alt = c.get("Alt")
                if key: 
                    options.add(key)
                if org:
                    options.add(org)
                if alt:
                    options.add(alt)
                options.add(name)
        options.add("All")
        sorted_list = list(options)
        sorted_list = sorted(sorted_list)
        match = get_completion(text, sorted_list)
        
        result = "All" if "All" in values else values[0]

        for c in chars:
            name = c.get("Custom")
            key = c.get("Key")
            org = c.get("Value")
            alt = c.get("Alt")
            if match == name:
                result = name
                break
            elif match == key:
                result = name
                break
            elif match == org:
                result = name
                break
            elif match == alt:
                result = name
                break
    return result