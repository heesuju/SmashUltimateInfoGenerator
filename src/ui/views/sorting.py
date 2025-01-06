import tkinter as tk
from tkinter import ttk
from src.constants.ui_params import PAD_H, PAD_V
from src.ui.base import get_text, set_text
from src.models.mod import Mod
from .config import Config

SORTING_CATEGORIES = {
    "mod_name":"Mod Name", 
    "category":"Category", 
    "authors":"Author", 
    "character":"Character", 
    "character_slots":"Slot"
}

class Sorting:
    def __init__(self, callback = None):
        self.new_window = None
        self.callback = callback

    def open(self, root):
        if self.new_window is not None:
            self.new_window.destroy()
    
        self.new_window = tk.Toplevel(root)
        self.new_window.title("Sorting")
        self.new_window.geometry("400x300")
        self.new_window.columnconfigure(1, weight=1)
        self.new_window.columnconfigure(2, weight=1)
        self.new_window.rowconfigure(6, weight=1)
        self.new_window.configure(padx=10, pady=10)
        self.new_window.lift(root)

        l_column = tk.Label(self.new_window, text="Column", justify=tk.LEFT)
        l_column.grid(row=0, column=1, sticky=tk.W)
        l_column2 = tk.Label(self.new_window, text="Order", justify=tk.LEFT)
        l_column2.grid(row=0, column=2, sticky=tk.W)

        category_values = [value for value in SORTING_CATEGORIES.values()]

        self.ddl_sort1 = self.add_filter_dropdown(1, 0, "Sort by", category_values)
        self.ddl_sort2 = self.add_filter_dropdown(2, 0, "Then by", ["None"] + category_values)
        self.ddl_sort3 = self.add_filter_dropdown(3, 0, "Then by", ["None"] + category_values)
        self.ddl_sort4 = self.add_filter_dropdown(4, 0, "Then by", ["None"] + category_values)

        self.ddl_order1 = self.add_filter_dropdown(1, 2, data=["Ascending", "Descending"])
        self.ddl_order2 = self.add_filter_dropdown(2, 2, data=["Ascending", "Descending"])
        self.ddl_order3 = self.add_filter_dropdown(3, 2, data=["Ascending", "Descending"])
        self.ddl_order4 = self.add_filter_dropdown(4, 2, data=["Ascending", "Descending"])

        self.f_actions = tk.Frame(self.new_window)
        self.f_actions.grid(row=6, column=0, columnspan=4, sticky=tk.SE)

        self.btn_restore = tk.Button(self.f_actions, text="Restore", command=lambda: self.restore())
        self.btn_restore.pack(side="left", padx=(0, PAD_H))

        self.btn_save = tk.Button(self.f_actions, text="Save", command=lambda: self.save())
        self.btn_save.pack()

        self.load()        

    def add_filter_dropdown(self, row, col, name:str = "", data:list = []):
        if name:
            label = ttk.Label(self.new_window, text=name)
            label.grid(row=row, column=col, sticky=tk.EW, padx=(0,PAD_H))

        combobox = ttk.Combobox(self.new_window, values=data, width=10)
        combobox.grid(row=row, column=col+1 if name else col, sticky=tk.EW, padx=(0,PAD_H if name else 0), pady=PAD_V/2)
        combobox.bind("<<ComboboxSelected>>", self.on_sort_changed)

        combobox.set(data[0])
        return combobox
    
    def load(self):
        self.config = Config()
        sort_priority = self.config.settings.sort_priority
        if sort_priority is not None:
            if len(sort_priority) >= 1:
                self.ddl_sort1.set(SORTING_CATEGORIES[sort_priority[0]["column"]])
                self.ddl_order1.set(sort_priority[0]["order"])
            
            if len(sort_priority) >= 2:
                self.ddl_order2.config(state="normal")
                self.ddl_sort2.set(SORTING_CATEGORIES[sort_priority[1]["column"]])
                self.ddl_order2.set(sort_priority[1]["order"])
            else:
                self.ddl_sort2.set("None")
                self.ddl_order2.config(state="disabled")
            if len(sort_priority) >= 3:
                self.ddl_order3.config(state="normal")
                self.ddl_sort3.set(SORTING_CATEGORIES[sort_priority[2]["column"]])
                self.ddl_order3.set(sort_priority[2]["order"])
            else:
                self.ddl_sort3.set("None")
                self.ddl_order3.config(state="disabled")
            if len(sort_priority) >= 4:
                self.ddl_order4.config(state="normal")
                self.ddl_sort4.set(SORTING_CATEGORIES[sort_priority[3]["column"]])
                self.ddl_order4.set(sort_priority[3]["order"])
            else:
                self.ddl_sort4.set("None")
                self.ddl_order4.config(state="disabled")

    def save(self):
        sort1 = self.get_sort_category(self.ddl_sort1)
        sort2 = self.get_sort_category(self.ddl_sort2)
        sort3 = self.get_sort_category(self.ddl_sort3)
        sort4 = self.get_sort_category(self.ddl_sort4)
        order1 = get_text(self.ddl_order1)
        order2 = get_text(self.ddl_order2)
        order3 = get_text(self.ddl_order3)
        order4 = get_text(self.ddl_order4)
        
        sort_items = []
        if sort1 != "None": 
            sort_items.append({"column":sort1, "order":order1})
        if sort2 != "None": 
            sort_items.append({"column":sort2, "order":order2})
        if sort3 != "None": 
            sort_items.append({"column":sort3, "order":order3})
        if sort4 != "None": 
            sort_items.append({"column":sort4, "order":order4})

        self.config.set_sort_priority(sort_items)
        self.callback()
        self.new_window.destroy()

    def restore(self):
        self.ddl_sort1.set("Category")
        self.ddl_sort2.set("Character")
        self.ddl_sort3.set("Slot")
        self.ddl_sort4.set("Mod Name")
        self.ddl_order1.set("Ascending")
        self.ddl_order2.set("Ascending")
        self.ddl_order3.set("Ascending")
        self.ddl_order4.set("Ascending")
        self.on_sort_changed(None)

    def get_sort_category(self, combobox):
        output = get_text(combobox)
        for key, value in SORTING_CATEGORIES.items():
            if output == value:
                return key
        return "None"

    def on_sort_changed(self, event):
        sel1 = get_text(self.ddl_sort1)
        sel2 = get_text(self.ddl_sort2)
        sel3 = get_text(self.ddl_sort3)
        sel4 = get_text(self.ddl_sort4)

        category_values = [value for value in SORTING_CATEGORIES.values() if value != sel1]
        self.ddl_sort2.config(values=["None"] + category_values)
        self.ddl_sort3.config(values=["None"] + category_values)
        self.ddl_sort4.config(values=["None"] + category_values)

        if sel2 not in category_values:
            self.ddl_sort2.set("None")
        if sel3 not in category_values:
            self.ddl_sort3.set("None")
        if sel4 not in category_values:
            self.ddl_sort4.set("None")

        category_values = [value for value in category_values if value != sel2]
        if sel3 not in category_values:
            self.ddl_sort3.set("None")
        if sel4 not in category_values:
            self.ddl_sort4.set("None")

        category_values = [value for value in category_values if value != sel3]
        if sel4 not in category_values:
            self.ddl_sort4.set("None")

        if get_text(self.ddl_sort2) == "None":
            self.ddl_order2.config(state="disabled")
        else:
            self.ddl_order2.config(state="normal")

        if get_text(self.ddl_sort3) == "None":
            self.ddl_order3.config(state="disabled")
        else:
            self.ddl_order3.config(state="normal")

        if get_text(self.ddl_sort4) == "None":
            self.ddl_order4.config(state="disabled")
        else:
            self.ddl_order4.config(state="normal")