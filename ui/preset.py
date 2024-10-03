import os, json
from tkinter import ttk
from PIL import ImageTk
import tkinter as tk
from defs import PAD_H, PAD_V
from . import PATH_ICON
from .common_ui import get_text, set_text, set_enabled, clear_text, open_file_dialog
from .config import load_config, Config
from utils.files import is_valid_dir
from utils.workspace import extract_number_from_preset, get_workspace_lists, load_preset_mods

COLUMNS = ["Workspace Name", "Total Enabled"]

class Preset:
    def __init__(self, root, callback=None) -> None:
        self.root = root
        self.callback = callback
        self.workspace_list = {}
        self.open()
        self.load_workspace()
        self.is_shown = False
        self.x = 0

    def on_select_all(self):
        self.set_select_all(self.select_all.get())

    def set_select_all(self, is_selected:bool):
        for item in self.treeview.get_children():
            self.set_row_checked(item, is_selected)

    def on_workspace_selected(self, event):
        config = Config()
        config.workspace = self.cbox_workspace.get()
        config.save_config()
        self.callback()

    def on_add_new_submitted(self, event):
        self.add_new()
    
    def on_row_select(self, event):
        selected_item = self.treeview.focus()
        if not selected_item or self.x == 0:
            return
        self.x = 0
        selected_data = self.treeview.item(selected_item)
        is_checked = "checked" in selected_data.get("tags")
        self.set_row_checked(selected_item, False if is_checked else True)

    def on_row_selected(self, event):
        selected_item = self.treeview.focus()
        if not selected_item:
            return
        self.x = 0
        selected_data = self.treeview.item(selected_item)
        is_checked = "checked" in selected_data.get("tags")
        self.set_row_checked(selected_item, False if is_checked else True)

    def on_item_clicked(self, event):
        self.x = 1
    
    def on_key_press(self, event):
        self.x = 0

    def add_new(self):
        new_name = get_text(self.entry_new)
        
        if not new_name:
            return
        
        if new_name.lower() not in [key.lower() for key, value in self.workspace_list.items()]:
            self.add_workspace(new_name, 0)
            filename = self.format_workspace_filename(new_name)
            self.workspace_list[new_name] = {"filename":filename, "mod_list":[]}
            self.update_workspace_dropdown()
            clear_text(self.entry_new)

    def update_workspace_dropdown(self):
        workspaces = [key for key, value in self.workspace_list.items()]
        selected_workspace = self.cbox_workspace.get()
        self.cbox_workspace.config(values=workspaces)
        if selected_workspace not in workspaces:
            self.cbox_workspace.set("Default")
            config = Config()
            config.workspace = "Default"
            config.save_config()
            self.callback()

    def add_workspace(self, name:str, count:int, checked:bool = False):
        tags = "checked" if checked else "unchecked"
        check_mark = "✅ " if checked else "⬜ "
        self.treeview.insert("", tk.END, text=check_mark + " " + name, values=tuple([count]), tags=[tags])

    def remove_workspaces(self):
        checked_items = self.get_checked()
        for item in checked_items:
            self.remove_workspace(item)
        self.set_select_all(False)

    def remove_workspace(self, item):
        name = self.get_row_text(item)
        if name != "Default":
            self.treeview.delete(item)
            self.workspace_list.pop(name, None)
            self.update_workspace_dropdown()

    def restore_workspaces(self):
        checked_items = self.get_checked()
        for item in checked_items:
            self.restore_workspace(item)
        self.set_select_all(False)
        self.callback()

    def restore_workspace(self, item):
        config = load_config()
        config["cache_dir"]
        name = self.get_row_text(item)
        path = os.path.join(config["cache_dir"], self.workspace_list[name]["filename"])
        self.workspace_list[name]["mod_list"] = load_preset_mods(path)
        self.update_workspace_count()

    def disable_workspaces(self):
        checked_items = self.get_checked()
        for item in checked_items:
            self.disable_workspace(item)
        self.set_select_all(False)
        self.callback()

    def disable_workspace(self, item):
        name = self.get_row_text(item)
        self.workspace_list[name]["mod_list"] = []
        self.update_workspace_count()

    def update_workspace_count(self):        
        for item_id in self.treeview.get_children():
            name = self.get_row_text(item_id)
            self.treeview.item(item_id, values=tuple([len(self.workspace_list[name]["mod_list"])]))

    def open(self):
        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=PAD_H, pady=PAD_V/2, fill="both", expand=True)
        
        self.workspace_frame = tk.Frame(self.frame)
        self.workspace_frame.pack(pady=(PAD_V/2,PAD_V), fill="x")

        label_work_dir = tk.Label(self.workspace_frame, text="Cache Dir")
        label_work_dir.pack(side=tk.LEFT, padx=(0,PAD_H), fill="x")

        self.entry_dir = tk.Entry(self.workspace_frame)
        self.entry_dir.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES, padx = (0, PAD_H))
        self.entry_dir.bind('<Return>', self.on_dir_submitted)

        self.icon_browse = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'browse.png'))
        self.btn_dir = tk.Button(self.workspace_frame, image=self.icon_browse, relief=tk.FLAT, cursor='hand2', command=self.get_cache_dir)
        self.btn_dir.pack(side=tk.LEFT)

        self.top_frame = tk.Frame(self.frame)
        self.top_frame.pack(pady=(0,PAD_V), fill=tk.X)

        label_workspace = tk.Label(self.top_frame, text="Selected")
        label_workspace.pack(side=tk.LEFT, padx=(0,PAD_H), fill="x")

        self.cbox_workspace = ttk.Combobox(self.top_frame)
        self.cbox_workspace.pack(side=tk.LEFT, padx=(0,PAD_H), fill="x", expand=tk.YES)
        self.cbox_workspace.bind("<<ComboboxSelected>>", self.on_workspace_selected)

        separator = ttk.Separator(self.frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=PAD_V)

        label_workspace = tk.Label(self.frame, text="Workspaces", anchor=tk.W)
        label_workspace.pack(pady=(0,PAD_V), fill="x")

        self.header = tk.Frame(self.frame)
        self.header.pack(pady=(0,PAD_V), fill="x")

        self.select_all = tk.IntVar()
        self.ckbox_all = tk.Checkbutton(self.header, text="Select All", variable=self.select_all, command=self.on_select_all, cursor='hand2')
        self.ckbox_all.pack(side=tk.LEFT)
        
        separator = ttk.Separator(self.header, orient='vertical')
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=PAD_H)

        label_new = tk.Label(self.header, text="New")
        label_new.pack(side=tk.LEFT, fill="x", padx=(0, PAD_H))

        self.entry_new = tk.Entry(self.header)
        self.entry_new.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES, padx=(0, PAD_H))
        self.entry_new.bind('<Return>', self.on_add_new_submitted)

        self.icon_new = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'new.png'))
        self.btn_new = tk.Button(self.header, image=self.icon_new, relief=tk.FLAT, cursor='hand2', command=self.add_new)
        self.btn_new.pack(side=tk.RIGHT)        

        style = ttk.Style(self.root)
        style.configure("Custom.Treeview", rowheight=20)
        self.treeview = ttk.Treeview(self.frame, columns=COLUMNS, show=("headings", "tree"))
        self.treeview.tag_configure('active', background='lightblue')
        self.treeview.bind('<Button-1>', self.on_item_clicked)
        self.treeview.bind("<<TreeviewSelect>>", self.on_row_select)
        self.treeview.bind('<Up>', self.on_key_press)
        self.treeview.bind('<Down>', self.on_key_press)
        self.treeview.bind("<space>", self.on_row_selected)
        self.treeview.bind("<Return>", self.on_row_selected)

        display_columns = COLUMNS
        self.treeview.column("#0", minwidth=140, width=200, stretch=tk.YES)
        
        for idx, column in enumerate(COLUMNS):
            if idx > 0:
                self.treeview.column(f"#{idx}", minwidth=140, width=160, stretch=tk.YES)
            self.treeview.heading(f"#{idx}", text=column)
        
        self.treeview["displaycolumns"]=display_columns
        self.treeview.pack(fill="both", expand=True)        
        self.scrollbar = ttk.Scrollbar(self.treeview, orient="vertical", command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        
        self.footer = tk.Frame(self.frame)
        self.footer.pack(pady=(PAD_V, PAD_V/2), fill="x")

        self.icon_export = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'close.png'))
        self.btn_remove = tk.Button(self.footer, image=self.icon_export, relief=tk.FLAT, compound="left", text=" Remove", cursor='hand2', command=self.remove_workspaces)
        self.btn_remove.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)

        separator = ttk.Separator(self.footer, orient='vertical')
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=PAD_H)

        self.icon_reset = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'reload.png'))
        self.btn_restore = tk.Button(self.footer, image=self.icon_reset, relief=tk.FLAT, compound="left", text=" Restore", cursor='hand2', command = self.restore_workspaces)
        self.btn_restore.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)

        separator = ttk.Separator(self.footer, orient='vertical')
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=PAD_H)

        self.icon_disable = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'reset.png'))
        self.btn_disable = tk.Button(self.footer, image=self.icon_disable, relief=tk.FLAT, compound="left", text=" Disable All", cursor='hand2', command = self.disable_workspaces)
        self.btn_disable.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)

    def toggle(self):
        if self.is_shown:
            self.root.pack_forget()
        else:
            self.root.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(PAD_H, 0))

        self.is_shown = False if self.is_shown else True
    
    def on_dir_submitted(self, event):
        new_dir = get_text(self.entry_dir)
        if is_valid_dir(new_dir):
            config = Config()
            config.cache_dir = new_dir
            config.save_config()
            self.load_workspace()
            self.callback()

    def get_cache_dir(self):
        config_data = load_config()
        if config_data is not None and config_data["cache_dir"]:
            working_dir = open_file_dialog(config_data["cache_dir"])
        else:
            working_dir = open_file_dialog()
        
        if is_valid_dir(working_dir):
            config = Config()
            config.cache_dir = working_dir
            config.save_config()
            self.load_workspace()
            self.callback()

    def load_workspace(self):
        config = load_config()
        
        set_text(self.entry_dir, config["cache_dir"])
        if config["cache_dir"]:
            self.reset_workspace()
            self.populate(config["cache_dir"])

            if config["workspace"]:
                self.cbox_workspace.set(config["workspace"])
            else:
                self.cbox_workspace.set(config["Default"])
        else:
            self.reset_workspace()
        
    def populate(self, cache_dir:str):
        self.workspace_list = get_workspace_lists(cache_dir)
        workspaces = []

        for key, value in self.workspace_list.items():
            self.add_workspace(key, len(value["mod_list"]))
            workspaces.append(key)

        self.cbox_workspace.config(values=workspaces)

    def reset_workspace(self):
        self.cbox_workspace.config(values=[])
        self.cbox_workspace.select_clear()
        self.cbox_workspace.set("Default")
        for item in self.treeview.get_children():
            self.treeview.delete(item)
    
    def format_workspace_filename(self, name):
        num = self.get_available_num()
        return f"{name}_preset{num + 1}"
    
    def get_available_num(self):
        available_num = 0
        for key, value in self.workspace_list.items():
            num = extract_number_from_preset(value["filename"])
            if isinstance(num, str):
                if num.isdigit():
                    if int(num) > available_num:
                        available_num = int(num)
        return available_num

    def save_presets(self): # Saves all workspace presets
        results = []
        for key, value in self.workspace_list.items():
            results.append(self.save_preset(value["filename"], value["mod_list"]))
        if False not in results:
            print("Successfully saved all presets")

    def save_preset(self, filename:str, enabled_mods:list)->bool: # Saves to workspace preset
        config = load_config()
        cache_dir = config["cache_dir"]
        result = False
        try:
            if is_valid_dir(cache_dir):
                with open(os.path.join(cache_dir, filename), mode='w') as output:
                    output.write(json.dumps(enabled_mods))
                    result = True
        except Exception as e:
            print("Error occurred while writing to preset file:", e)
        finally:
            return result

    def save_workspaces(self): # Saves to workspace_list and workspace in config directory
        config = load_config()
        cache_dir = config["cache_dir"]
        result = False
        workspaces = {}
        for key, value in self.workspace_list.items():
            workspaces[key] = value["filename"]
        try:
            with open(os.path.join(cache_dir, "workspace_list"), mode='w') as output:
                output.write(json.dumps(workspaces))
            
            with open(os.path.join(cache_dir, "workspace"), mode='w') as output:
                output.write(config["workspace"] if config["workspace"] else "Default")

            result = True
        except Exception as e:
            print("Error occurred while writing to workspace_list file:", e)
        finally:
            return result
        
    def get_checked(self):
        outputs = []
        for item in self.treeview.get_children():
            data = self.treeview.item(item)
            if "checked" in data.get("tags"):
                outputs.append(item)
        return outputs
    
    def set_row_checked(self, item, is_checked:bool=True):
        name = self.get_row_text(item)
        if is_checked:
            self.treeview.item(item, tags=["checked"], text="✅  " + name)
        else:
            self.treeview.item(item, tags=["unchecked"], text="⬜  " + name)

    def get_row_text(self, item):
        data = self.treeview.item(item)
        text = data["text"]
        if "✅  " in text:
            split = text.split("✅  ")
            text = split[-1]
        elif "⬜  " in text:
            split = text.split("⬜  ")
            text = split[-1]
        
        return text