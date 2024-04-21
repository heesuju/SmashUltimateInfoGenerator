import os
import tkinter as tk
from tkinter import ttk
from utils.scanner import Scanner
import math
import common
from PIL import Image, ImageTk
import tkinter.font as font
import defs
from .editor import Editor
from .config import Config
from utils.loader import Loader
from utils.image_resize import ImageResize
from utils import load_config
from . import PATH_ICON

class Menu:    
    def __init__(self, root) -> None:
        self.root = root
        self.mods = []
        self.filtered_mods = []
        self.cur_page = 1
        self.total_pages = 1
        self.page_size = 12
        self.config = Config(self.on_config_changed)
        self.editor = Editor()
        self.loader = Loader()
        self.show()
        self.scan()
    
    def reset(self):
        self.treeview.selection_clear()
        self.treeview.delete(*self.treeview.get_children())

    def refresh(self):
        self.reset()
        self.scan()

    def populate(self, mods):
        self.total_pages = math.ceil(len(mods)/self.page_size)
        print(f"found {len(mods)} items")
        
        self.show_paging()
        start = (self.cur_page-1) * self.page_size
        end = common.clamp(self.cur_page * self.page_size, start, len(mods))
        for n in range(start,end):
            if mods[n].img == None: self.treeview.insert("", tk.END, values=(mods[n].mod_name, mods[n].category, mods[n].authors, mods[n].characters, mods[n].slots, mods[n].path))
            else: self.treeview.insert("", tk.END, image=mods[n].img, values=(mods[n].mod_name, mods[n].category, mods[n].authors, mods[n].characters, mods[n].slots, mods[n].path))

    def on_filter_submitted(self, event):
        self.search()

    def search(self):
        self.reset()
        self.cur_page = 1
        mod_name = self.entry_mod_name.get()
        author = self.entry_author.get()
        category = ""
        character = self.entry_character.get()
        self.filtered_mods = []
        for mod in self.mods:
            if mod_name.lower() not in mod.mod_name.lower(): continue
            if author.lower() not in mod.authors.lower(): continue
            if character.lower() not in mod.characters.lower(): continue
            
            self.filtered_mods.append(mod)
            
        self.populate(self.filtered_mods)

    def clear_filter(self):
        self.entry_mod_name.delete(0, tk.END)
        self.entry_author.delete(0, tk.END)
        self.entry_character.delete(0, tk.END)
        self.search()

    def on_config_changed(self):
        self.refresh()

    def on_scanned(self, mods):
        self.mods = mods
        self.filtered_mods = mods
        self.populate(self.mods)
    
    def on_img_resized(self, image):
        self.label_img.config(image=image, width=10, height=10)
        self.label_img.image = image  # Keep a reference to prevent garbage collection

    def on_item_selected(self, event):
        selected_item = self.treeview.focus()
        item = self.treeview.item(selected_item)
        self.l_desc_v.config(state="normal")
        self.l_desc_v.delete(1.0, tk.END)
        if self.loader.load_toml(item['values'][-1]): 
            self.l_desc_v.insert(tk.END, self.loader.description)
            self.l_ver.config(text=self.loader.version, width=5)
            self.l_author.config(text=self.loader.authors, width=1)
        else: self.l_desc_v.insert(tk.END, "No info.toml found")
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

    def on_space_pressed(self, event):
        selected_item = self.treeview.focus()
        item = self.treeview.item(selected_item)
        if item["tags"][0] == "checked":
            self.treeview.change_state(item=selected_item, state="unchecked")
        else:
            self.treeview.change_state(item=selected_item, state="checked")

    def scan(self):
        config_data = load_config()
        if config_data is not None and config_data["default_directory"]:
            scan_thread = Scanner(config_data["default_directory"], self.on_scanned)
            scan_thread.start()
        else:
            print("no default directory")
            self.open_config()

    def add_filter_item(self, row, col, name):
        label = ttk.Label(self.frame_filter, text=name)
        label.grid(row=row, column=col, sticky=tk.W, padx=5)
        entry = tk.Entry(self.frame_filter)
        entry.grid(row=row, column=col+1)
        entry.bind("<Return>", self.on_filter_submitted)
        return entry
    
    def change_page(self, number):
        self.cur_page = number
        self.reset()
        self.populate(self.filtered_mods)

    def next_page(self):
        self.cur_page = common.clamp(self.cur_page+1, 1, self.total_pages)
        self.change_page(self.cur_page)

    def prev_page(self):
        self.cur_page = common.clamp(self.cur_page-1, 1, self.total_pages)
        self.change_page(self.cur_page)

    def show_paging(self):
        icon_left = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'left.png'))
        icon_right = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'right.png'))
        for child in self.frame_paging.winfo_children():
            child.destroy()

        self.btn_left = tk.Button(self.frame_paging, image=icon_left, relief=tk.FLAT, cursor='hand2', command=self.prev_page)
        self.btn_left.image = icon_left
        self.btn_left.grid(row=0, column=0)
        
        prev = 0
        for index, n in enumerate(common.get_pages(self.cur_page, self.total_pages)):
            if index > 0 and prev+1 != n:
                label = tk.Label(self.frame_paging, text="...", width=2)
                label.grid(row=0, column=n-1)    
            
            btn = tk.Button(self.frame_paging, text=n, relief=tk.FLAT, cursor='hand2', command=lambda number=n: self.change_page(number), width=2)
            if self.cur_page == n:
                btn["font"]= font.Font(weight="bold")
                btn["fg"]= "#6563FF"
            btn.grid(row=0, column=n)
            prev = n

        self.btn_right = tk.Button(self.frame_paging, image = icon_right, relief=tk.FLAT, cursor='hand2', command=self.next_page)
        self.btn_right.image = icon_right
        self.btn_right.grid(row=0, column=self.total_pages + 1)

    def show(self):
        self.frame_filter = ttk.LabelFrame(self.root, text="Filter")
        self.frame_filter.pack(padx=defs.PAD_H, pady=defs.PAD_V, fill="x")
        
        self.frame_content = tk.Frame(self.root)
        self.frame_content.pack(padx=defs.PAD_H, pady=(0, defs.PAD_V), fill="both", expand=True)
        self.frame_content.columnconfigure(0, weight=2)
        self.frame_content.columnconfigure(1, weight=1)
        self.frame_content.rowconfigure(0, weight=1)

        self.frame_list = ttk.LabelFrame(self.frame_content, text="Mods")
        self.frame_list.grid(row=0, column=0, padx=(0, defs.PAD_H/2), sticky=tk.NSEW)

        self.info_frame = ttk.LabelFrame(self.frame_content, text="Details")
        self.info_frame.grid(row=0, column=1, padx=(defs.PAD_H/2, 0), sticky=tk.NSEW)
        self.info_frame.columnconfigure(0, weight=1)

        self.entry_mod_name = self.add_filter_item(0, 0, "Mod Name")
        self.entry_author = self.add_filter_item(1, 0, "Author")
        self.entry_character = self.add_filter_item(2, 0, "Character")
        
        self.f_filter_actions = tk.Frame(self.frame_filter)
        self.f_filter_actions.grid(row=3, column=0, columnspan=2, padx=(defs.PAD_H, 0), pady=(defs.PAD_V/2), sticky=tk.NSEW)
        
        self.btn_search = tk.Button(self.f_filter_actions, text="Search", cursor='hand2', command=self.search)
        self.btn_search.pack(side=tk.LEFT, padx=(0, defs.PAD_H))
        self.btn_clear = tk.Button(self.f_filter_actions, text="Clear", cursor='hand2', command=self.clear_filter)
        self.btn_clear.pack(side=tk.LEFT, padx=(0, defs.PAD_H))

        self.btn_refresh = tk.Button(self.f_filter_actions, text="Refresh", cursor='hand2', command=self.refresh)
        self.btn_refresh.pack(side=tk.LEFT, padx=(0, defs.PAD_H))

        self.categories = ["Mod Name", "Category", "Author", "Char", "Slot", "Dir"]
        
        self.treeview = ttk.Treeview(self.frame_list, columns=self.categories, show=("headings", "tree"))
        
        style = ttk.Style(self.root)
        #style.map("Checkbox.Treeview", background=[("disabled", "#E6E6E6"), ("selected", "#E6E6E6")])
        style.configure("Treeview", rowheight=60)
        display_columns = []
        self.treeview.column("#0", minwidth=140, width=140, stretch=tk.NO)
        self.treeview.column("Mod Name", minwidth=100, width=100, stretch=tk.NO)
        self.treeview.column("Category", minwidth=30, width=50)
        self.treeview.column("Author", minwidth=30, width=50)
        self.treeview.column("Char", minwidth=30, width=50)
        self.treeview.column("Slot", minwidth=30, width=50)

        for col, category in enumerate(self.categories):
            if col < len(self.categories)-1:
                display_columns.append(category)
            self.treeview.heading(category, text=category)
        self.treeview["displaycolumns"]=display_columns
        self.treeview.pack(padx=10, pady=10, fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(self.treeview, orient="vertical", command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=self.scrollbar.set)
        self.treeview.bind('<<TreeviewSelect>>', self.on_item_selected)
        self.treeview.bind("<Double-1>", self.on_double_clicked)
        self.treeview.bind("<space>", self.on_space_pressed)
        self.scrollbar.pack(side="right", fill="y")
        
        self.frame_paging = tk.Frame(self.root)
        self.frame_paging.pack(pady = (0, defs.PAD_V))
        
        self.info_frame.rowconfigure(index=0, weight=1)
        self.info_frame.rowconfigure(index=3, weight=1)

        self.label_img = tk.Label(self.info_frame, bg="black")
        self.label_img.grid(row=0, padx=defs.PAD_H, pady=(defs.PAD_V, 0), sticky=tk.NSEW)

        self.ver_auth_frame = tk.Frame(self.info_frame)
        self.ver_auth_frame.grid(row=1, padx=defs.PAD_H, pady=(0, defs.PAD_V), sticky=tk.NSEW)

        self.l_ver = tk.Label(self.ver_auth_frame, anchor="w", justify="left")
        self.l_ver.pack(side=tk.LEFT)

        self.l_author = tk.Label(self.ver_auth_frame, anchor="e", justify="right", width=1)
        self.l_author.pack(side=tk.RIGHT, fill="x", expand=True)

        l_desc = tk.Label(self.info_frame, text="Description", anchor="w", justify="left")
        l_desc.grid(row=2, padx=defs.PAD_H, sticky=tk.W)

        self.l_desc_v = tk.Text(self.info_frame, height=1, width=10, state="disabled")
        self.l_desc_v.grid(row=3, padx=defs.PAD_H, pady=(0, defs.PAD_V), sticky=tk.NSEW)

        self.btn_edit = tk.Button(self.info_frame, text="Edit", cursor='hand2', command=self.open_editor)
        self.btn_edit.grid(row=4, padx=defs.PAD_H, pady=(0, defs.PAD_V), sticky=tk.EW)