from tkinter import ttk
from ttkwidgets import CheckboxTreeview
from PIL import ImageTk
import tkinter as tk
from defs import PAD_H, PAD_V
from . import PATH_ICON
from .common_ui import get_text, set_text, set_enabled, clear_text
from utils.image_resize import ImageResize
from utils.loader import Loader
from .config import load_config
from utils.files import read_json
import os, re

COLUMNS = ["Name", "Total", "Added", "Removed"]

class Workspaces:
    def __init__(self, root, edit_callback=None, open_callback=None, toggle_callback=None) -> None:
        self.root = root
        self.workspace_list = []
        self.open()
        self.load_workspace()
        self.is_shown = False

    def on_select_all(self):
        if self.select_all.get():
            for item in self.treeview.get_children():
                self.treeview.item(item, tags='checked')
        else:
            for item in self.treeview.get_children():
                self.treeview.item(item, tags='unchecked')

    def on_row_select(self, event):
        selected_item = self.treeview.focus()
        if not selected_item:
            return
        
        selected_name = self.treeview.item(selected_item)["text"]

        for item in self.treeview.get_children():
            data = self.treeview.item(item)
            checked_state = "checked" if  "checked" in data["tags"] else "unchecked"
            if selected_name == data["text"]:
                self.treeview.item(item, tags=[checked_state, "active"])
            else:
                self.treeview.item(item, tags=[checked_state, "inactive"])

    def on_add_new_submitted(self, event):
        self.add_new()

    def add_new(self):
        new_name = get_text(self.entry_new)
        if new_name.lower() not in [key.lower() for key, value in self.workspace_list.items()]:
            self.add_workspace(new_name, 0)
            filename = self.format_workspace_filename(new_name)
            self.workspace_list[new_name] = filename
            clear_text(self.entry_new)

    def add_workspace(self, name:str, count:int):
        self.treeview.insert("", tk.END, text=name, values=tuple([count]), tags=["unchecked", "inactive"])

    def remove_workspaces(self):
        checked_items = self.treeview.get_checked()
        for item in checked_items:
            self.remove_workspace(item)

    def remove_workspace(self, item):
        data = self.treeview.item(item)
        if data["text"] != "Default":
            self.treeview.delete(item)
            self.workspace_list.pop(data["text"], None)

    def open(self):
        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=PAD_H, pady=PAD_V/2, fill="both", expand=True)
        
        self.workspace_frame = tk.Frame(self.frame)
        self.workspace_frame.pack(pady=(PAD_V/2,PAD_V), fill="x")

        label_work_dir = tk.Label(self.workspace_frame, text="Cache Dir")
        label_work_dir.pack(side=tk.LEFT, padx=(0,PAD_H), pady=(0,PAD_V), fill="x")

        self.entry_dir = tk.Entry(self.workspace_frame)
        self.entry_dir.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)

        self.icon_browse = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'browse.png'))
        self.btn_dir = tk.Button(self.workspace_frame, image=self.icon_browse, relief=tk.FLAT, cursor='hand2')
        self.btn_dir.pack(side=tk.LEFT, padx = (0, PAD_H))

        self.top_frame = tk.Frame(self.frame)
        self.top_frame.pack(pady=(PAD_V/2,PAD_V), fill="x")

        label_workspace = tk.Label(self.top_frame, text="Current Workspace")
        label_workspace.pack(side=tk.LEFT, padx=(0,PAD_H), pady=(0,PAD_V), fill="x")

        self.cbox_workspace = ttk.Combobox(self.top_frame)
        self.cbox_workspace.pack(side=tk.LEFT, padx=(0,PAD_H), pady=(0,PAD_V), fill="x", expand=tk.YES)

        self.icon_reload = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'reload.png'))
        self.btn_load = tk.Button(self.top_frame, image=self.icon_reload, compound="left", text=" Load", cursor='hand2')
        self.btn_load.pack(side=tk.LEFT, pady=(0,PAD_V), fill=tk.X)

        separator = ttk.Separator(self.frame, orient='horizontal')
        separator.pack(fill=tk.X)

        label_workspace = tk.Label(self.frame, text="Workspaces", anchor=tk.W)
        label_workspace.pack(pady=(0,PAD_V), fill="x")

        self.header = tk.Frame(self.frame)
        self.header.pack(pady=(0,PAD_V), fill="x")

        self.select_all = tk.IntVar()
        self.ckbox_all = tk.Checkbutton(self.header, text="Select All", variable=self.select_all, command=self.on_select_all, cursor='hand2')
        self.ckbox_all.pack(side=tk.LEFT)
        
        separator = ttk.Separator(self.header, orient='vertical')
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=PAD_H)

        label_new = tk.Label(self.header, text="Add New")
        label_new.pack(side=tk.LEFT, fill="x")


        self.entry_new = tk.Entry(self.header)
        self.entry_new.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)
        self.entry_new.bind('<Return>', self.on_add_new_submitted)


        self.icon_new = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'new.png'))
        self.btn_new = tk.Button(self.header, image=self.icon_new, relief=tk.FLAT, cursor='hand2', command=self.add_new)
        self.btn_new.pack(side=tk.RIGHT)
        

        style = ttk.Style(self.root)
        style.configure("Custom.Treeview", rowheight=20)
        self.treeview = CheckboxTreeview(self.frame, columns=COLUMNS, show=("headings", "tree"))
        self.treeview.tag_configure('active', background='lightblue')
        self.treeview.bind("<<TreeviewSelect>>", self.on_row_select)

        display_columns = COLUMNS
        self.treeview.column("#0", minwidth=100, width=140, stretch=tk.YES)
        
        for idx, column in enumerate(COLUMNS):
            if idx > 0:
                self.treeview.column(f"#{idx}", minwidth=70, width=70, stretch=tk.YES)
            self.treeview.heading(f"#{idx}", text=column)
        
        self.treeview["displaycolumns"]=display_columns
        self.treeview.pack(fill="both", expand=True)        
        self.scrollbar = ttk.Scrollbar(self.treeview, orient="vertical", command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        
        self.footer = tk.Frame(self.frame)
        self.footer.pack(padx=PAD_H, pady=(PAD_V, PAD_V/2), fill="x")

        self.icon_save = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'save.png'))
        self.btn_save = tk.Button(self.footer, image=self.icon_save, text=" Close", relief=tk.FLAT, compound="left", cursor='hand2')
        self.btn_save.pack(side=tk.LEFT)
        separator = ttk.Separator(self.footer, orient='vertical')
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=PAD_H)
        
        self.icon_export = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'export.png'))
        self.btn_remove = tk.Button(self.footer, image=self.icon_export, relief=tk.FLAT, compound="left", text=" Remove", cursor='hand2', command=self.remove_workspaces)
        self.btn_remove.pack(side=tk.LEFT)
        separator = ttk.Separator(self.footer, orient='vertical')
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=PAD_H)

        self.icon_reset = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'reset.png'))
        self.btn_disable = tk.Button(self.footer, image=self.icon_reset, relief=tk.FLAT, compound="left", text=" Reset", cursor='hand2')
        self.btn_disable.pack(side=tk.LEFT)

    def toggle(self):
        if self.is_shown:
            self.root.pack_forget()
        else:
            self.root.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(PAD_H, 0))

        self.is_shown = False if self.is_shown else True
   
    def load_workspace(self):
        config = load_config()
        
        set_text(self.entry_dir, config["cache_dir"])
        if config["cache_dir"]:
            self.reset_workspace()
            self.populate_workspace(config["cache_dir"])

            if config["workspace"]:
                self.cbox_workspace.set(config["workspace"])
            else:
                self.cbox_workspace.set(config["Default"])
        else:
            self.reset_workspace()
        
    def populate_workspace(self, cache_dir:str):
        self.workspace_list = read_json(os.path.join(cache_dir, "workspace_list"))
        
        workspaces = []

        for key, value in self.workspace_list.items():
            self.add_workspace(key, value)
            workspaces.append(key)

        self.cbox_workspace.config(values=workspaces)

    def reset_workspace(self):
        self.cbox_workspace.config(values=[])
        self.cbox_workspace.select_clear()
        self.cbox_workspace.set("Default")
    
    def format_workspace_filename(self, name):
        num = self.get_available_num()
        return f"{name}_preset{num + 1}"
        
    def get_available_num(self):
        available_num = 0
        for key, value in self.workspace_list.items():
            num = extract_number_from_preset(value)
            if isinstance(num, str):
                if num.isdigit():
                    if int(num) > available_num:
                        available_num = int(num)
        return available_num

def extract_number_from_preset(input_str):
    match = re.search(r'_preset(\d+)$', input_str)
    if match:
        return match.group(1)
    return ""