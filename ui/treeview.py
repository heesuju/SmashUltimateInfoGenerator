import os
from functools import partial
import tkinter as tk
from tkinter import ttk
from utils.scanner import Scanner
import math
import common
import threading
import queue
from PIL import Image, ImageTk
from defs import PAD_H, PAD_V
from .editor import Editor
from .config import Config
from .filter import Filter
from .paging import Paging
from utils.loader import Loader
from utils.preset_manager import PresetManager
from utils.image_resize import ImageResize
from utils import load_config
from utils.update_config import update_config_directory
from . import PATH_ICON
from .common_ui import *

class Menu:    
    def __init__(self, root) -> None:
        self.root = root
        self.mods = []
        self.filtered_mods = []
        self.config = Config(self.on_config_changed)
        self.editor = Editor(self.on_finish_edit)
        self.loader = Loader()
        self.queue = queue.Queue()
        self.enabled_mods = []
        self.preset_cache = []
        self.preset_manager = PresetManager()
        self.progress_count = 0
        self.progress_lock = threading.Lock()
        self.max_count = 0
        self.show()
        self.scan()
    
    def reset(self):
        self.treeview.selection_clear()
        self.treeview.delete(*self.treeview.get_children())
        set_enabled(self.l_desc_v)
        clear_text(self.l_desc_v)
        set_enabled(self.l_desc_v, False)
        self.label_img.image = ""
        clear_text(self.l_ver)
        clear_text(self.l_author)
            
    def open_folder(self):
        selected_item = self.treeview.focus()
        if selected_item:
            item = self.treeview.item(selected_item)
            os.startfile(item['values'][-1])
        else:
            print("no item selected!")
    
    def enable_mod(self):
        selected_item = self.treeview.focus()
        if selected_item:
            item = self.treeview.item(selected_item)
            path = item["values"][5].split("/")[-1].split("\\")[-1]
            if item["tags"][0] == "enabled": # disable mod
                self.treeview.item(selected_item, text=" ⬜ ", tags="disabled")
                self.enabled_mods.remove(path)
                self.btn_enable.config(text="Enable")
            else: # enable mod
                self.treeview.item(selected_item, text=" ✅ ", tags="enabled")
                self.enabled_mods.append(path)
                self.btn_enable.config(text="Disable")
            for mod in self.mods:
                if mod["folder_name"] == path:
                    mod["enabled"] = mod["folder_name"] in self.enabled_mods
                    break
        else:
            print("no item selected!")

    def refresh(self):
        self.filter_view.reset()
        self.reset()
        self.scan()

    def populate(self, mods):
        start, end = self.paging.update(len(mods)) 

        for n in range(start,end):
            characters = ", ".join(sorted(mods[n]["character_names"]))
            enabled = " ✅ " if mods[n]["enabled"] else " ⬜ "
            tags = "enabled" if mods[n]["enabled"] else "disabled"
            values = [mods[n]["category"], characters, mods[n]["slots"], mods[n]["mod_name"], mods[n]["authors"], mods[n]["path"]]

            if mods[n]["img"] == None: 
                self.treeview.insert("", tk.END, text=enabled, values=tuple(values), tags=tags)
            else: 
                self.treeview.insert("", tk.END, text=enabled, image=mods[n]["img"], values=tuple(values), tags=tags)

    def on_change_page(self):
        self.reset()
        self.populate(self.filtered_mods)

    def search(self):
        self.reset()
        self.paging.cur_page = 1
        self.filtered_mods = self.filter_view.filter_mods(self.mods)    
        self.populate(self.filtered_mods)

    def on_config_changed(self, dir:str):
        if dir:
            self.refresh()

    def on_finish_edit(self, old_dir:str, new_dir:str):
        is_dir_same = True if old_dir == new_dir else False
        dir_to_update = old_dir if is_dir_same else new_dir
        scan_thread = Scanner([dir_to_update], callback=self.on_finish_update)
        scan_thread.start()

    def on_finish_update(self, mods):
        valid_mods = [mod for mod in self.mods if os.path.isdir(mod["path"])]

        for n in mods:
            found_match = False
            for idx, m in enumerate(valid_mods):
                if n["path"] == m["path"]:
                    valid_mods[idx] = n
                    found_match = True
                    print("updated dir:", n["path"])
                    break
            if found_match == False:
                valid_mods.append(n)
                print("added dir:", n["path"])
        self.mods = valid_mods
        self.search()

    def on_scan_progress(self, future):
        with self.progress_lock:
            self.progress_count += 1
        self.queue.put(self.progress_count)
        self.root.event_generate('<<Progress>>')

    def updater(self, pb:ttk.Progressbar, label:ttk.Label, q:queue, event):
        perc = round(q.get()/self.max_count, 2) * 100.0
        if perc <= 100.0:
            pb['value'] = perc
            formatted_number = "{:.2f}%".format(perc)
            set_text(label, formatted_number)

    def on_scanned(self, mods):
        self.mods = mods
        self.enabled_mods = []
        for mod in self.mods:
            if mod["enabled"]:
                self.enabled_mods.append(mod["folder_name"])
                self.preset_cache.append(mod["hash"])
        self.filtered_mods = mods
        if len(mods) > 0:
            self.search()
        
    def on_img_resized(self, image):
        self.label_img.config(image=image, width=10, height=10)
        self.label_img.image = image  # Keep a reference to prevent garbage collection

    def on_item_selected(self, event):
        selected_item = self.treeview.focus()
        if not selected_item:
            return
        
        item = self.treeview.item(selected_item)
        self.l_desc_v.config(state="normal")
        self.l_desc_v.delete(1.0, tk.END)
        self.btn_enable.config(text="Enable" if item["tags"][0] == "disabled" else "Disable")
        
        if self.loader.load_toml(item['values'][-1]): 
            set_text(self.l_desc_v, self.loader.description)
            self.l_ver.config(text=self.loader.version, width=5)
            self.l_author.config(text=self.loader.authors, width=1)
        else: 
            set_text(self.l_desc_v, "No info.toml found")
        self.l_desc_v.config(state="disabled")
        img_preview = os.path.join(item['values'][-1], "preview.webp")
        if os.path.exists(img_preview):
            resize_thread = ImageResize(img_preview, self.label_img.winfo_width(), self.label_img.winfo_height(), self.on_img_resized)
            resize_thread.start()
        else:
            self.label_img.image = ""
            self.l_ver.config(text="")
            self.l_author.config(text="")
            
    def on_double_clicked(self, event):
        self.open_editor()

    def open_editor(self):
        selected_item = self.treeview.focus()
        if selected_item:
            item = self.treeview.item(selected_item)
            self.editor.open(self.root, item['values'][-1])
        else:
            print("nothing selected in treeview!")

    def open_config(self):
        self.config.load()
        self.config.open_config(self.root)

    def on_enable_mod(self, event):
        self.enable_mod()
    
    def on_scan_start(self, max_count):
        self.max_count = max_count
        
    def scan(self):
        self.progress_count = 0
        config_data = load_config()
        if config_data is not None and config_data["default_directory"]:
            set_text(self.entry_dir, config_data["default_directory"])
            preset_cache = self.preset_manager.load_preset()
            scan_thread = Scanner(config_data["default_directory"], start_callback=self.on_scan_start, progress_callback=self.on_scan_progress, callback=self.on_scanned, preset=preset_cache)
            scan_thread.start()
        # else:
        #     print("no default directory")
        #     self.open_config()
    
    def change_working_directory(self):
        config_data = load_config()
        if config_data is not None and config_data["default_directory"]:
            working_dir = open_file_dialog(config_data["default_directory"])
        else:
            working_dir = open_file_dialog()

        if not working_dir:
            return
        
        if is_valid_dir(working_dir):
            update_config_directory(working_dir)
            set_text(self.entry_dir, working_dir)
            self.refresh()
    
    def on_directory_changed(self, event):
        new_directory = get_text(self.entry_dir)
        if is_valid_dir(new_directory):
            update_config_directory(new_directory)
            self.refresh()
        else:
            print("invalid directory!")

    def save_preset(self):
        self.preset_cache = self.preset_manager.save_preset(self.enabled_mods)

    def disable_all(self):
        self.enabled_mods = []
        for mod in self.mods:
            mod["enabled"] = False
        print("disabled every mod")
        self.reset()
        self.filtered_mods = self.filter_view.filter_mods(self.mods)    
        self.populate(self.filtered_mods)

    def reload_preset(self):
        self.enabled_mods = []
        for mod in self.mods:
            if mod["hash"] in self.preset_cache:
                mod["enabled"] = True
                self.enabled_mods.append(mod["folder_name"])
            else:
                mod["enabled"] = False
        print("reloaded preset")
        self.reset()
        self.filtered_mods = self.filter_view.filter_mods(self.mods)    
        self.populate(self.filtered_mods)

    def show(self):
        self.f_dir = tk.Frame(self.root)
        self.f_dir.pack(padx=PAD_H, pady=PAD_V, fill="x")
        
        self.l_dir = tk.Label(self.f_dir, text="Mod Directory")
        self.l_dir.pack(side=tk.LEFT)

        self.entry_dir = tk.Entry(self.f_dir, width=10)
        self.entry_dir.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=PAD_H)
        self.entry_dir.bind('<Return>', self.on_directory_changed)

        self.icon_browse = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'browse.png'))

        self.btn_dir = tk.Button(self.f_dir, image=self.icon_browse, relief=tk.FLAT, cursor='hand2', command=self.change_working_directory)
        self.btn_dir.pack(side=tk.LEFT, padx = (0, PAD_H))
        
        self.frame_content = tk.Frame(self.root)
        self.frame_content.pack(padx=PAD_H, pady=(0, PAD_V), fill="both", expand=True)

        self.frame_list = ttk.LabelFrame(self.frame_content, text="Mods")
        self.frame_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,PAD_H))
        self.filter_view = Filter(self.frame_list, self.search, self.refresh)

        self.info_frame = ttk.LabelFrame(self.frame_content, text="Details")
        self.info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.info_frame.columnconfigure(0, weight=1)     

        self.categories = ["Category", "Character", "Slot", "Mod Name", "Author", "Dir"]
        
        self.treeview = ttk.Treeview(self.frame_list, columns=self.categories, show=("headings", "tree"))

        def treeview_sort_column(tv, col, reverse):
            l = [(tv.set(k, col), k) for k in tv.get_children('')]
            l.sort(reverse=reverse)

            for index, (val, k) in enumerate(l):
                tv.move(k, '', index)

            tv.heading(col, command=lambda: \
                    treeview_sort_column(tv, col, not reverse))

        style = ttk.Style(self.root)
        
        style.configure("Treeview", rowheight=60)

        display_columns = []
        self.treeview.column("#0", minwidth=150, width=150, stretch=tk.NO)
        self.treeview.column("Category", minwidth=70, width=70, stretch=tk.NO)
        self.treeview.column("Character", minwidth=70, width=70, stretch=tk.YES)
        self.treeview.column("Slot", minwidth=30, width=30, stretch=tk.YES)
        self.treeview.column("Mod Name", minwidth=100, width=100, stretch=tk.YES)
        self.treeview.column("Author", minwidth=70, width=70, stretch=tk.YES)     
        self.treeview.heading("#0", text="Thumbnail")

        for col, category in enumerate(self.categories):
            if col < len(self.categories)-1:
                display_columns.append(category)
            self.treeview.heading(category, text=category, command=lambda _col=col: \
                                  treeview_sort_column(self.treeview, _col, False))
        self.treeview["displaycolumns"]=display_columns
        self.treeview.pack(padx=10, pady=(PAD_V,0), fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(self.treeview, orient="vertical", command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=self.scrollbar.set)
        self.treeview.bind('<<TreeviewSelect>>', self.on_item_selected)
        self.treeview.bind("<Double-1>", self.on_double_clicked)
        self.treeview.bind("<space>", self.on_enable_mod)
        self.treeview.bind("<Return>", self.on_enable_mod)

        self.scrollbar.pack(side="right", fill="y")
        
        self.paging = Paging(self.frame_list, self.on_change_page)
        
        self.f_footer = tk.Frame(self.root)
        self.f_footer.pack(padx = PAD_H, pady = (0, PAD_V), fill="x")

        self.progressbar = ttk.Progressbar(self.f_footer, mode="determinate", orient="horizontal", length=200)
        self.progressbar.pack(side=tk.LEFT)
        
        self.l_progress = tk.Label(self.f_footer, text="")
        self.l_progress.pack(side=tk.LEFT)

        update_handler = partial(self.updater, self.progressbar, self.l_progress, self.queue)
        self.root.bind('<<Progress>>', update_handler)

        self.btn_save = tk.Button(self.f_footer, text="Overwrite Preset", cursor='hand2', command=self.save_preset)
        self.btn_save.pack(side=tk.RIGHT)

        self.btn_disable = tk.Button(self.f_footer, text="Disable All", cursor='hand2', command=self.disable_all)
        self.btn_disable.pack(side=tk.RIGHT, padx=(0, PAD_H))

        self.btn_load = tk.Button(self.f_footer, text="Reload Preset", cursor='hand2', command=self.reload_preset)
        self.btn_load.pack(side=tk.RIGHT, padx=(0, PAD_H))

        self.info_frame.rowconfigure(index=0, weight=1)
        self.info_frame.rowconfigure(index=3, weight=1)

        self.label_img = tk.Label(self.info_frame, bg="black")
        self.label_img.grid(row=0, padx=PAD_H, pady=(PAD_V, 0), sticky=tk.NSEW)

        self.ver_auth_frame = tk.Frame(self.info_frame)
        self.ver_auth_frame.grid(row=1, padx=PAD_H, pady=(0, PAD_V), sticky=tk.NSEW)

        self.l_ver = tk.Label(self.ver_auth_frame, anchor="w", justify="left")
        self.l_ver.pack(side=tk.LEFT)

        self.l_author = tk.Label(self.ver_auth_frame, anchor="e", justify="right", width=1)
        self.l_author.pack(side=tk.RIGHT, fill="x", expand=True)

        l_desc = tk.Label(self.info_frame, text="Description", anchor="w", justify="left")
        l_desc.grid(row=2, padx=PAD_H, sticky=tk.W)

        self.l_desc_v = tk.Text(self.info_frame, height=1, width=10, state="disabled")
        self.l_desc_v.grid(row=3, padx=PAD_H, pady=(0, PAD_V), sticky=tk.NSEW)

        self.f_selected_mod = tk.Frame(self.info_frame)
        self.f_selected_mod.grid(row=4, padx=PAD_H, pady=(0, PAD_V), sticky=tk.EW)
        self.f_selected_mod.columnconfigure(index=0, weight=1, uniform="equal")
        self.f_selected_mod.columnconfigure(index=1, weight=1, uniform="equal")
        self.f_selected_mod.columnconfigure(index=2, weight=1, uniform="equal")
        self.f_selected_mod.rowconfigure(index=0, weight=1)

        self.btn_edit = tk.Button(self.f_selected_mod, text="Edit", cursor='hand2', command=self.open_editor)
        self.btn_edit.grid(row=0, column=0, sticky=tk.EW, padx=(0, PAD_H/2))
        
        self.btn_open_folder = tk.Button(self.f_selected_mod, text="Open", cursor='hand2', command=self.open_folder)
        self.btn_open_folder.grid(row=0, column=1, sticky=tk.EW, padx=PAD_H/2)

        self.btn_enable = tk.Button(self.f_selected_mod, text="Enable", cursor='hand2', width=2, command=self.enable_mod)
        self.btn_enable.grid(row=0, column=2, sticky=tk.EW, padx=(PAD_H/2, 0))