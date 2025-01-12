"""
filter.py: View containing various filters for searching mods
"""

import os
from tkinter import ttk
from PIL import ImageTk
import tkinter as tk
from idlelib.tooltip import Hovertip
from src.constants.defs import SLOT_RULE
from src.constants.ui_params import PAD_H, PAD_V
from src.constants.categories import CATEGORIES
from src.constants.elements import ELEMENTS
from src.models.filter_params import FilterParams, DEFAULT_VALUE
from src.ui.base import get_text, validate_slot, add_filter_dropdown, add_filter_entry
from src.utils.edit_distance import get_completion
from src.utils.csv_helper import csv_to_dict
from src.core.filter import get_similar_character
from data import PATH_CHAR_NAMES
from assets import ICON_PATH
from .sorting import Sorting

class SearchFilter:
    def __init__(self, root:tk.Frame, on_search:callable, on_refresh:callable) -> None:
        self.sort_view = None
        self.root = root
        self.on_search = on_search
        self.on_refresh = on_refresh
        self.params = FilterParams()
        
        self.mod_name_var = tk.StringVar()
        self.authors_var = tk.StringVar()
        self.character_var = tk.StringVar()
        self.series_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.info_toml_var = tk.StringVar()
        self.wifi_safe_var = tk.StringVar()
        self.included_var = tk.StringVar()
        self.slot_from_var = tk.StringVar()
        self.slot_to_var = tk.StringVar()
        self.enabled_only_var = tk.IntVar()
        self.include_hidden_var = tk.IntVar()
        self.slot_rule_var = tk.StringVar()

        self.set_binding()
        self.show()
        
    def set_values(self, params:FilterParams):
        """
        Sets params
        """
        self.mod_name_var.set(params.mod_name)
        self.authors_var.set(params.authors)
        self.character_var.set(params.character)
        self.series_var.set(params.series)
        self.category_var.set(params.category)
        self.info_toml_var.set(params.info_toml)
        self.wifi_safe_var.set(params.wifi_safe)
        self.included_var.set(params.included)
        self.slot_from_var.set(params.slot_from)
        self.slot_to_var.set(params.slot_to)
        self.enabled_only_var.set(params.enabled_only)
        self.include_hidden_var.set(params.include_hidden)
        self.slot_rule_var.set(params.slot_rule)

    def set_binding(self):
        """
        Binds mod object to editor
        """
        self.mod_name_var.trace_add("write", lambda *args: setattr(self.params, 'mod_name', self.mod_name_var.get()))
        self.authors_var.trace_add("write", lambda *args: setattr(self.params, 'authors', self.authors_var.get()))
        self.character_var.trace_add("write", lambda *args: setattr(self.params, 'character', self.character_var.get()))
        self.series_var.trace_add("write", lambda *args: setattr(self.params, 'series', self.series_var.get()))
        self.category_var.trace_add("write", lambda *args: setattr(self.params, 'category', self.category_var.get()))
        self.info_toml_var.trace_add("write", lambda *args: setattr(self.params, 'info_toml', self.info_toml_var.get()))
        self.wifi_safe_var.trace_add("write", lambda *args: setattr(self.params, 'wifi_safe', self.wifi_safe_var.get()))
        self.included_var.trace_add("write", lambda *args: setattr(self.params, 'included', self.included_var.get()))
        self.slot_from_var.trace_add("write", lambda *args: setattr(self.params, 'slot_from', self.slot_from_var.get()))
        self.slot_to_var.trace_add("write", lambda *args: setattr(self.params, 'slot_to', self.slot_to_var.get()))
        self.enabled_only_var.trace_add("write", lambda *args: setattr(self.params, 'enabled_only', self.enabled_only_var.get()))
        self.include_hidden_var.trace_add("write", lambda *args: setattr(self.params, 'include_hidden', self.include_hidden_var.get()))
        self.slot_rule_var.trace_add("write", lambda *args: setattr(self.params, 'slot_rule', self.slot_rule_var.get()))

    def show(self):
        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=PAD_H, pady=PAD_V/2, fill="x")
        for i in range(6):
            if i % 2 != 0:
                self.frame.columnconfigure(i, weight=2)
                self.frame.columnconfigure(i, minsize=100)
        
        self.entry_mod_name = add_filter_entry(self.frame, 0, 0, "Mod Name", self.mod_name_var, self.on_submit)
        self.entry_author = add_filter_entry(self.frame, 0, 2, "Author", self.authors_var, self.on_submit)
        label_slots = ttk.Label(self.frame, text="Slots")
        label_slots.grid(row=0, column=4, sticky=tk.EW, padx=(0,PAD_H))
        self.frame_slots = tk.Frame(self.frame)
        self.frame_slots.grid(row=0, column=5, sticky=tk.EW, pady=PAD_V/2)
        vcmd = (self.root.register(validate_slot)) 

        self.cbox_slots = ttk.Combobox(self.frame_slots, values=SLOT_RULE, width=8, textvariable=self.slot_rule_var)
        self.cbox_slots.pack(side=tk.LEFT, fill=tk.X, expand=False, padx=(0,PAD_H))
        self.cbox_slots.bind("<Return>", self.on_submit)
        self.slot_rule_var.set(SLOT_RULE[0])

        self.entry_slots_from = tk.Entry(self.frame_slots, width=3, validate='all', validatecommand=(vcmd, '%P'), textvariable=self.slot_from_var)
        self.entry_slots_from.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry_slots_from.bind("<Return>", self.on_submit)
        self.slot_from_var.set(self.params.slot_from)

        label_slot_n = ttk.Label(self.frame_slots, text="~", takefocus=False)
        label_slot_n.pack(side=tk.LEFT, padx=PAD_H/2)
        label_slot_n.bind("<Return>", self.on_submit)

        self.entry_slots_to = tk.Entry(self.frame_slots, width=3, validate='all', validatecommand=(vcmd, '%P'), textvariable=self.slot_to_var)
        self.entry_slots_to.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry_slots_to.bind("<Return>", self.on_submit)
        self.slot_to_var.set(self.params.slot_to)

        self.cbox_series = add_filter_dropdown(self.frame, 1, 0, "Series", self.params.series_list, self.series_var, self.on_submit)
        self.cbox_series.bind("<<ComboboxSelected>>", self.on_series_changed)
        self.cbox_char = add_filter_dropdown(self.frame, 1, 2, "Character", self.params.characters_list, self.character_var, self.on_submit)
        self.cbox_category = add_filter_dropdown(self.frame, 1, 4, "Category", [DEFAULT_VALUE] + CATEGORIES, self.category_var, self.on_submit, False)

        self.cbox_info = add_filter_dropdown(self.frame, 2, 0, "Info.toml", self.params.info_toml_list, self.info_toml_var, self.on_submit)
        self.cbox_wifi = add_filter_dropdown(self.frame, 2, 2, "Wifi-Safe", self.params.wifi_safe_list, self.wifi_safe_var, self.on_submit)
        self.cbox_included = add_filter_dropdown(self.frame, 2, 4, "Included", self.params.included_list, self.included_var, self.on_submit, False)
        
        self.frame_ckbox = tk.Frame(self.frame)
        self.frame_ckbox.grid(row=3, column=0, columnspan=6, pady=(PAD_V/2, 0), sticky=tk.EW)

        self.ckbox_enabled = tk.Checkbutton(self.frame_ckbox, text="Show only enabled", variable=self.enabled_only_var, cursor='hand2')
        self.ckbox_enabled.pack(side=tk.LEFT)

        self.ckbox_hidden = tk.Checkbutton(self.frame_ckbox, text="Include hidden", variable=self.include_hidden_var, cursor='hand2')
        self.ckbox_hidden.pack(side=tk.LEFT)

        self.frame_actions = tk.Frame(self.frame_ckbox)
        self.frame_actions.pack(side=tk.RIGHT)

        self.icon_sort = ImageTk.PhotoImage(file=os.path.join(ICON_PATH, 'config.png'))
        self.btn_sort = tk.Button(self.frame_actions, image=self.icon_sort, relief=tk.FLAT, cursor='hand2', command=self.show_sort)
        self.btn_sort.pack(side=tk.LEFT)
        sort_tip = Hovertip(self.btn_sort,'Sort Config')

        separator = ttk.Separator(self.frame_actions, orient='vertical')
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=PAD_H)

        self.icon_refresh = ImageTk.PhotoImage(file=os.path.join(ICON_PATH, 'refresh.png'))
        self.btn_refresh = tk.Button(self.frame_actions, image=self.icon_refresh, relief=tk.FLAT, cursor='hand2', command=self.on_refresh)
        self.btn_refresh.pack(side=tk.LEFT)
        refresh_tip = Hovertip(self.btn_refresh,'Refresh')
        
        separator = ttk.Separator(self.frame_actions, orient='vertical')
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=PAD_H)

        self.icon_clear = ImageTk.PhotoImage(file=os.path.join(ICON_PATH, 'clear.png'))
        self.btn_clear = tk.Button(self.frame_actions, image=self.icon_clear, relief=tk.FLAT, cursor='hand2', command=self.clear)
        self.btn_clear.pack(side=tk.LEFT)
        clear_tip = Hovertip(self.btn_clear,'Clear')

        separator = ttk.Separator(self.frame_actions, orient='vertical')
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=PAD_H)

        self.icon_search = ImageTk.PhotoImage(file=os.path.join(ICON_PATH, 'search.png'))
        self.btn_search = tk.Button(self.frame_actions, image=self.icon_search, relief=tk.FLAT, cursor='hand2', command=self.on_search)
        self.btn_search.pack(side=tk.LEFT)
        search_tip = Hovertip(self.btn_search,'Search')

    def on_submit(self, event):
        new_category = get_completion(self.category_var.get(), self.params.category_list)
        self.category_var.set(new_category if new_category else DEFAULT_VALUE)

        new_info = get_completion(self.info_toml_var.get(), self.params.info_toml_list)
        self.info_toml_var.set(new_info if new_info else DEFAULT_VALUE)

        new_included = get_completion(self.included_var.get(), self.params.included_list)
        self.included_var.set(new_included if new_included else DEFAULT_VALUE)

        if self.series_var.get():
            new_series = get_completion(self.series_var.get(), self.params.series_list)
        else:
            new_series = DEFAULT_VALUE

        self.series_var.set(new_series if new_series else DEFAULT_VALUE) 
        
        char_data = csv_to_dict(PATH_CHAR_NAMES)
        
        filtered_chars = []
        if new_series != DEFAULT_VALUE:
            for c in char_data:
                if c.get("Series") == new_series:
                    filtered_chars.append(c.get("Custom"))
        else:
            filtered_chars = sorted(csv_to_dict(PATH_CHAR_NAMES, "Custom"))

        chars = [DEFAULT_VALUE] if len(filtered_chars) > 1 else []
        chars.extend(sorted(filtered_chars))
        self.params.characters_list = chars

        new_char = self.character_var.get()
        if new_char:
            new_char = get_similar_character(self.character_var.get(), self.params.characters_list)
        elif DEFAULT_VALUE in chars:
            new_char = DEFAULT_VALUE
        elif len(chars) > 0:
            new_char = chars[0]
        self.cbox_char.config(values=self.params.characters_list)
        self.character_var.set(new_char if new_char else DEFAULT_VALUE)

        new_wifi = get_completion(get_text(self.cbox_wifi), self.params.wifi_safe_list)
        self.wifi_safe_var.set(new_wifi if new_wifi else DEFAULT_VALUE)

        new_slot_rule = get_completion(self.slot_rule_var.get(), SLOT_RULE)
        self.slot_rule_var.set(new_slot_rule if new_slot_rule else SLOT_RULE[0])

        self.on_search()

    def on_series_changed(self, event):
        char_data = csv_to_dict(PATH_CHAR_NAMES)
        selected_series = get_text(self.cbox_series)
        filtered_chars = []
        if selected_series != DEFAULT_VALUE:
            for c in char_data:
                if c.get("Series") == selected_series:
                    filtered_chars.append(c.get("Custom"))
        else:
            filtered_chars = sorted(csv_to_dict(PATH_CHAR_NAMES, "Custom"))

        chars = [DEFAULT_VALUE] if len(filtered_chars) > 1 else []
        chars.extend(sorted(filtered_chars))
        self.cbox_char.config(values=chars)
        self.params.characters_list = chars
        self.character_var.set(chars[0])
    
    def reset(self):
        self.params = FilterParams()
        self.set_values(self.params)
        self.cbox_char.config(values=self.params.characters_list)

    def clear(self):
        self.reset()
        self.on_search()
            
    def show_sort(self):
        if self.sort_view is None:
            self.sort_view = Sorting(self.on_sorting_changed)
        self.sort_view.open(self.root)

    def on_sorting_changed(self):
        self.on_search()