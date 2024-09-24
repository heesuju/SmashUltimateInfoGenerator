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
import tkinter.font as font
from defs import PAD_H, PAD_V
from .editor import Editor
from .config import Config
from .filter import Filter
from utils.loader import Loader
from utils.image_resize import ImageResize
from utils import load_config
from utils.update_config import update_config_directory
from . import PATH_ICON
from .common_ui import *
from utils.sort import sort_by_priority

class Menu:    
    def __init__(self, root) -> None:
        self.root = root
        self.mods = []
        self.filtered_mods = []
        self.cur_page = 1
        self.total_pages = 1
        self.page_size = 30
        self.config = Config(self.on_config_changed)
        self.editor = Editor(self.on_finish_edit)
        self.loader = Loader()
        self.queue = queue.Queue()
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

    def refresh(self):
        self.filter_view.clear()
        self.reset()
        self.scan()

    def populate(self, mods):
        self.total_pages = math.ceil(len(mods)/self.page_size)
        print(f"found {len(mods)} items")
        self.show_paging()
        start = (self.cur_page-1) * self.page_size
        end = common.clamp(self.cur_page * self.page_size, start, len(mods))
        for n in range(start,end):
            characters = ", ".join(sorted(mods[n]["character_names"]))
            if mods[n]["img"] == None: self.treeview.insert("", tk.END, values=(mods[n]["mod_name"], mods[n]["category"], mods[n]["authors"], characters, mods[n]["slots"], mods[n]["path"]), tags=('enabled'))
            else: self.treeview.insert("", tk.END, image=mods[n]["img"], values=(mods[n]["mod_name"], mods[n]["category"], mods[n]["authors"], characters, mods[n]["slots"], mods[n]["path"]))
        self.treeview.tag_configure('enabled', background='lightgrey')
        n_count = end - start
        self.l_page.config(text=f"{n_count} of {len(mods)}")

    def search(self):
        self.reset()
        self.cur_page = 1        
        self.filtered_mods = self.filter_view.filter_mods(self.mods)    
        self.filtered_mods = sort_by_priority(self.filtered_mods, load_config()["sort_priority"])
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
        self.filtered_mods = mods
        if len(mods) > 0:
            self.search()
        # else:
        #     self.open_config()
    
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
    
    def on_scan_start(self, max_count):
        self.max_count = max_count
        
    def scan(self):
        self.progress_count = 0
        config_data = load_config()
        if config_data is not None and config_data["default_directory"]:
            set_text(self.entry_dir, config_data["default_directory"])
            scan_thread = Scanner(config_data["default_directory"], start_callback=self.on_scan_start, progress_callback=self.on_scan_progress, callback=self.on_scanned)
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
        for child in self.frame_paging.winfo_children():
            child.destroy()

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


        # self.entry_work_dir.bind("<KeyRelease>", self.on_update_directory)
        
        
        self.frame_content = tk.Frame(self.root)
        self.frame_content.pack(padx=PAD_H, pady=(0, PAD_V), fill="both", expand=True)

        self.frame_list = ttk.LabelFrame(self.frame_content, text="Mods")
        self.frame_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,PAD_H))
        self.filter_view = Filter(self.frame_list, self.search, self.refresh)

        self.info_frame = ttk.LabelFrame(self.frame_content, text="Details")
        self.info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.info_frame.columnconfigure(0, weight=1)     

        self.categories = ["Mod Name", "Category", "Author", "Char", "Slot", "Dir"]
        
        self.treeview = ttk.Treeview(self.frame_list, columns=self.categories, show=("headings", "tree"))
        
        style = ttk.Style(self.root)
        #style.map("Checkbox.Treeview", background=[("disabled", "#E6E6E6"), ("selected", "#E6E6E6")])
        style.configure("Treeview", rowheight=60)
        # style.map('Treeview', background=[('selected', '#BFBFBF')])

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
        
        self.f_footer = tk.Frame(self.root)
        self.f_footer.pack(padx = PAD_H, pady = (0, PAD_V), fill="x")
        self.f_footer.columnconfigure(index=0, weight=1, uniform="equal")
        self.f_footer.columnconfigure(index=1, weight=1, uniform="equal")
        self.f_footer.columnconfigure(index=2, weight=1, uniform="equal")

        icon_left = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'left.png'))
        icon_right = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'right.png'))

        self.f_left = tk.Frame(self.f_footer)
        self.f_left.grid(row=0, column=0, sticky=tk.EW)

        self.btn_left = tk.Button(self.f_left, image=icon_left, relief=tk.FLAT, cursor='hand2', command=self.prev_page)
        self.btn_left.image = icon_left
        self.btn_left.pack(side=tk.RIGHT)

        self.progressbar = ttk.Progressbar(self.f_left, mode="determinate", orient="horizontal", length=200)
        self.progressbar.pack(side=tk.LEFT)
        
        self.l_progress = tk.Label(self.f_left, text="")
        self.l_progress.pack(side=tk.LEFT)

        update_handler = partial(self.updater, self.progressbar, self.l_progress, self.queue)
        self.root.bind('<<Progress>>', update_handler)
        
        self.f_right = tk.Frame(self.f_footer)
        self.f_right.grid(row=0, column=2, sticky=tk.EW)

        self.btn_right = tk.Button(self.f_right, image = icon_right, relief=tk.FLAT, cursor='hand2', command=self.next_page)
        self.btn_right.image = icon_right
        self.btn_right.pack(side=tk.LEFT)

        self.frame_paging = tk.Frame(self.f_footer)
        self.frame_paging.grid(row=0, column=1)
        
        self.l_page = tk.Label(self.f_right, text="")
        self.l_page.pack(side=tk.RIGHT)
        
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
        self.f_selected_mod.rowconfigure(index=0, weight=1)

        self.btn_edit = tk.Button(self.f_selected_mod, text="Edit", cursor='hand2', command=self.open_editor)
        self.btn_edit.grid(row=0, column=0, sticky=tk.EW, padx=(0, PAD_H/2))
        
        self.btn_open_folder = tk.Button(self.f_selected_mod, text="Open", cursor='hand2', command=self.open_folder)
        self.btn_open_folder.grid(row=0, column=1, sticky=tk.EW, padx=(PAD_H/2, 0))