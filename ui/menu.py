import os
from functools import partial
import tkinter as tk
from tkinter import ttk, messagebox
from utils.scanner import Scanner
from tkinterdnd2 import DND_FILES
import threading
import queue
from PIL import Image, ImageTk
from defs import PAD_H, PAD_V
from .editor import Editor
from .config import Config, load_config, get_workspace
from .filter import Filter
from .paging import Paging
from .preview import Preview
from .preset import Preset
from . import PATH_ICON
from utils.loader import Loader
from utils.files import is_valid_dir, copy_directory_contents, is_case_sensitive, get_base_name
from .common_ui import *
from utils.hash import gen_hash_as_decimal
from utils.format import format_folder_name

class Menu:    
    def __init__(self, root, webdriver_manager) -> None:
        self.root = root
        self.webdriver_manager = webdriver_manager

        self.mods = []
        self.filtered_mods = []
        self.config = Config()
        self.loader = Loader()
        self.queue = queue.Queue()
        self.progress_count = 0
        self.progress_lock = threading.Lock()
        self.max_count = 0
        self.x = 0
        self.y = 0
       
        self.show()
        self.scan()
    
    def reset(self):
        self.treeview.selection_clear()
        self.treeview.delete(*self.treeview.get_children())
        self.preview.clear()
            
    def open_folder(self):
        selected_item = self.treeview.focus()
        if selected_item:
            item = self.treeview.item(selected_item)
            os.startfile(item['values'][-1])
        else:
            print("no item selected!")
    
    def toggle_mod(self):
        selected_item = self.treeview.focus()
        if selected_item:
            item = self.treeview.item(selected_item)
            path = item["values"][5].split("/")[-1].split("\\")[-1]
            hash = gen_hash_as_decimal(path)
            workspace = self.get_valid_workspace()
            workspace_data = self.preset.workspace_list.get(workspace)
            if workspace_data:
                enabled_mods = workspace_data["mod_list"]
            
                if hash in enabled_mods: # Disable
                    self.treeview.item(selected_item, text=" ⬜ ", tags="disabled")
                    self.preview.set_toggle_label(False)
                    self.preset.workspace_list[workspace]["mod_list"].remove(hash)
                else: # Enable
                    self.treeview.item(selected_item, text=" ✅ ", tags="enabled")
                    self.preview.set_toggle_label(True)
                    self.preset.workspace_list[workspace]["mod_list"].append(hash)

                self.preset.update_workspace_count()
            else:
                print("no workspace found")
        else:
            print("no item selected!")

    def refresh(self):
        self.filter_view.reset()
        self.paging.clear()
        clear_text(self.label_count)
        self.reset()
        self.scan()

    def populate(self, mods):
        start, end = self.paging.update(len(mods)) 
        filtered_len = len(mods)
        total = len(self.mods)
        set_text(self.label_count, f"Showing {filtered_len} of {total}" if total > filtered_len else f"Showing {total}")
        
        workspace = self.get_valid_workspace()
        for n in range(start,end):
            characters = ", ".join(sorted(mods[n]["character_names"]))
            check_mark = " ⬜ "
            tags = "disabled"
            
            enabled_mods = self.preset.workspace_list[workspace]["mod_list"] if self.preset.workspace_list.get(workspace) else []

            if mods[n]["hash"] in enabled_mods:
                check_mark = " ✅ "
                tags = "enabled"

            values = [mods[n]["category"], characters, mods[n]["slots"], mods[n]["mod_name"], mods[n]["authors"], mods[n]["path"]]

            if mods[n]["img"] == None: 
                self.treeview.insert("", tk.END, text=check_mark, values=tuple(values), tags=tags)
            else: 
                self.treeview.insert("", tk.END, text=check_mark, image=mods[n]["img"], values=tuple(values), tags=tags)

        children = self.treeview.get_children()
        if len(children) > 0:
            first_row = children[0]
            self.treeview.focus(first_row)
            self.treeview.selection_set(first_row)
        self.treeview.yview_moveto(0)

    def on_change_page(self):
        self.reset()
        self.populate(self.filtered_mods)

    def on_prev_page(self, event):
        self.paging.prev_page()

    def on_next_page(self, event):
        self.paging.next_page()

    def search(self):
        workspace = self.get_valid_workspace()
        workspace_data = self.preset.workspace_list.get(workspace)
        enabled_mods = workspace_data.get("mod_list")if workspace_data else []
        self.reset()
        self.paging.cur_page = 1
        self.filtered_mods = self.filter_view.filter_mods(self.mods, enabled_mods)
        self.populate(self.filtered_mods)

    def on_finish_edit(self, old_dir:str, new_dir:str):
        is_dir_same = True if old_dir == new_dir else False
        dir_to_update = old_dir if is_dir_same else new_dir
        Scanner([dir_to_update], callback=self.on_finish_update)

    def on_finish_update(self, mods):
        valid_mods = [mod for mod in self.mods if os.path.isdir(mod["path"])]
        case_sensitive = is_case_sensitive()

        for n in mods:
            found_match = False
            for idx, m in enumerate(valid_mods):
                new_path = get_base_name(n.get("path", ""))
                mod_path = get_base_name(m.get("path", ""))

                if not case_sensitive:
                    new_path = new_path.lower()
                    mod_path = mod_path.lower()

                if new_path == mod_path:
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

    def on_escape(self, event):
        self.preview.clear()
        if self.preview.is_shown:
            self.preview.toggle()
        elif self.preset.is_shown:
            self.preset.toggle()

    def on_item_selected(self, event):
        selected_item = self.treeview.focus()
        if not selected_item:
            return
        
        if self.x >= 20 and self.x <= 145:
            self.toggle_mod()
            self.x, self.y  = 0, 0

        item = self.treeview.item(selected_item)
        path = item['values'][-1]
        selected_mod = None
        for mod in self.mods:
            if mod.get("path") == path:
                selected_mod = mod
                break
        
        self.preview.update(item["tags"][0] == "enabled", 
                            self.loader if self.loader.load_toml(item['values'][-1]) else None,
                            selected_mod,
                            path)
                
    def on_item_clicked(self, event):
        self.x = event.x
        self.y = event.y
            
    def on_double_clicked(self, event):
        self.open_editor()

    def open_editor(self):
        selected_item = self.treeview.focus()
        if selected_item:
            item = self.treeview.item(selected_item)
            Editor(self.root, self.webdriver_manager, item['values'][-1], self.on_finish_edit)
        else:
            print("nothing selected in treeview!")

    def open_config(self):
        self.config.load()
        self.config.open_config(self.root)

    def on_enable_mod(self, event):
        self.toggle_mod()

    def on_key_press(self, event):
        self.x, self.y  = 0, 0
    
    def on_scan_start(self, max_count):
        self.max_count = max_count
        
    def scan(self):
        self.progress_count = 0
        config_data = load_config()
        if config_data is not None and config_data["default_directory"]:
            set_text(self.entry_dir, config_data["default_directory"])
            Scanner(
                config_data["default_directory"], 
                start_callback=self.on_scan_start, 
                progress_callback=self.on_scan_progress, 
                callback=self.on_scanned)
    
    def on_browse(self):
        config_data = load_config()
        if config_data is not None and config_data["default_directory"]:
            working_dir = open_file_dialog(config_data["default_directory"])
        else:
            working_dir = open_file_dialog()
        
        self.change_directory(working_dir)
    
    def on_directory_changed(self, event):
        new_directory = get_text(self.entry_dir)
        self.change_directory(new_directory)

    def change_directory(self, new_dir:str):
        if new_dir and is_valid_dir(new_dir):
            self.config.set_default_dir(new_dir)
            set_text(self.entry_dir, new_dir)
            self.preset.load_workspace()
            self.refresh()
        else:
            print("invalid directory!")

    def on_window_resize(self, event):
        selected_item = self.treeview.focus()
        if selected_item:
            item = self.treeview.item(selected_item)
            path = item["values"][-1]
            self.preview.set_image(os.path.join(path, "preview.webp"))

    def save_preset(self):
        self.preset.save_presets()
        self.preset.save_workspaces()

    def toggle_preset(self):
        if not self.preset.is_shown:
            if self.preview.is_shown:
                self.toggle_preview()
            self.btn_show_preset.config(image=self.icon_visible)
        else:
            self.btn_show_preset.config(image=self.icon_invisible)

        self.preset.toggle()

    def toggle_preview(self):
        if not self.preview.is_shown:
            if self.preset.is_shown:
                self.toggle_preset()
            self.btn_show_preview.config(image=self.icon_visible)
        else:
            self.btn_show_preview.config(image=self.icon_invisible)

        self.preview.toggle()

    def show(self):
        self.f_dir = tk.Frame(self.root)
        self.f_dir.pack(padx=PAD_H, pady=PAD_V, fill="x")
        
        self.l_dir = tk.Label(self.f_dir, text="Mod Directory")
        self.l_dir.pack(side=tk.LEFT)

        self.entry_dir = tk.Entry(self.f_dir, width=10)
        self.entry_dir.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=PAD_H)
        self.entry_dir.bind('<Return>', self.on_directory_changed)

        self.icon_browse = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'browse.png'))
        self.btn_dir = tk.Button(self.f_dir, image=self.icon_browse, relief=tk.FLAT, cursor='hand2', command=self.on_browse)
        self.btn_dir.pack(side=tk.LEFT, padx = (0, PAD_H))
        
        self.frame_content = tk.Frame(self.root)
        self.frame_content.pack(padx=PAD_H, pady=(0, PAD_V), fill="both", expand=True)

        self.frame_list = ttk.LabelFrame(self.frame_content, text="Mods")
        self.frame_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.filter_view = Filter(self.frame_list, self.search, self.refresh)

        self.workspace_frame = ttk.LabelFrame(self.frame_content, text="Preset")
        self.preset = Preset(self.workspace_frame, self.search)

        self.info_frame = ttk.LabelFrame(self.frame_content, text="Preview")
        self.info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(PAD_H, 0))
        self.info_frame.columnconfigure(0, weight=1)
        self.info_frame.rowconfigure(index=1, weight=1)
        self.info_frame.rowconfigure(index=3, weight=1)
        self.info_frame.pack_forget()

        self.label_count = tk.Label(self.frame_list, text="Showing 0", anchor=tk.W)
        self.label_count.pack(fill=tk.BOTH, padx=(PAD_H, 0))

        self.categories = ["Category", "Character", "Slot", "Mod Name", "Author", "Dir"]
        
        style = ttk.Style(self.root)
        style.configure("Treeview", rowheight=20)
        style.configure("Custom.Treeview", background="white", foreground="Black", rowheight=20)
        style.map('Custom.Treeview', background=[('selected','lightblue')],foreground=[('selected','Black')])
        style.configure("Custom1.Treeview",background="white", foreground="Black", rowheight=60)
        style.map('Custom1.Treeview', background=[('selected','lightblue')],foreground=[('selected','Black')])

        self.treeview = ttk.Treeview(self.frame_list, style="Custom1.Treeview", columns=self.categories, show=("headings", "tree"))

        def treeview_sort_column(tv, col, reverse):
            l = [(tv.set(k, col), k) for k in tv.get_children('')]
            l.sort(reverse=reverse)

            for index, (val, k) in enumerate(l):
                tv.move(k, '', index)

            tv.heading(col, command=lambda: \
                    treeview_sort_column(tv, col, not reverse))

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
        self.treeview.drop_target_register(DND_FILES)
        self.treeview.dnd_bind('<<Drop>>', lambda e: self.on_drag_drop(e.data))
        self.treeview.configure(yscrollcommand=self.scrollbar.set)
        self.treeview.bind('<<TreeviewSelect>>', self.on_item_selected)
        self.treeview.bind('<Button-1>', self.on_item_clicked)
        self.treeview.bind('<Escape>', self.on_escape)
        self.treeview.bind("<Double-1>", self.on_double_clicked)
        self.treeview.bind("<space>", self.on_enable_mod)
        self.treeview.bind("<Return>", self.on_enable_mod)
        self.treeview.bind('<Up>', self.on_key_press)
        self.treeview.bind('<Down>', self.on_key_press)

        self.scrollbar.pack(side="right", fill="y")
        
        self.paging = Paging(self.frame_list, self.on_change_page)
        self.treeview.bind('<Right>', self.on_next_page)
        self.treeview.bind('<Left>', self.on_prev_page)
        self.f_footer = tk.Frame(self.root)
        self.f_footer.pack(padx = PAD_H, pady = (0, PAD_V), fill="x")

        self.progressbar = ttk.Progressbar(self.f_footer, mode="determinate", orient="horizontal", length=200)
        self.progressbar.pack(side=tk.LEFT)
        
        self.l_progress = tk.Label(self.f_footer, text="")
        self.l_progress.pack(side=tk.LEFT)

        update_handler = partial(self.updater, self.progressbar, self.l_progress, self.queue)
        self.root.bind('<<Progress>>', update_handler)

        self.icon_save = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'save.png'))
        self.btn_save = tk.Button(self.f_footer, image=self.icon_save, text=" Save", compound=tk.LEFT, cursor='hand2', command=self.save_preset, width=100)
        self.btn_save.pack(side=tk.RIGHT)

        self.icon_visible = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'visible.png'))
        self.icon_invisible = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'invisible.png'))

        self.btn_show_preset = tk.Button(
            self.f_footer,  
            image=self.icon_invisible, 
            compound="left", 
            text=" Preset", 
            cursor='hand2', 
            command=self.toggle_preset, 
            borderwidth=0,
            relief=tk.FLAT
        )
        self.btn_show_preset.pack(
            side=tk.RIGHT,
            padx=(0, PAD_H)
        )

        self.btn_show_preview = tk.Button(
            self.f_footer,  
            image=self.icon_invisible, 
            compound="left", 
            text=" Preview", 
            cursor='hand2', 
            command=self.toggle_preview, 
            borderwidth=0,
            relief=tk.FLAT
        )
        self.btn_show_preview.pack(
            side=tk.RIGHT,
            padx=(0, PAD_H)
        )

        self.preview = Preview(self.info_frame, self.open_editor, self.open_folder, self.toggle_mod)
        self.root.bind("<Configure>", self.on_window_resize)

    def get_valid_workspace(self):
        name = get_workspace()
        workspace = self.preset.workspace_list.get(name, None)
        if workspace is None:
            return "Default"
        else:
            return name
        
    def on_drag_drop(self, dir):
        dir = dir.strip('{}')
        config = load_config()
        default_dir = config.get("default_directory")
        if is_valid_dir(default_dir) and is_valid_dir(dir):
            Scanner([dir], callback=self.on_drop_scanned)

    def on_drop_scanned(self, mods:list):
        if len(mods) <= 0: 
            return
        
        scanned_mod = mods[0]
        dir = scanned_mod.get("path")
        config = load_config()
        default_dir = config.get("default_directory")

        folder_name = format_folder_name(
            scanned_mod.get("characters"),
            scanned_mod.get("slots"),
            scanned_mod.get("mod_name"),
            scanned_mod.get("category"))
        
        new_dir = os.path.join(default_dir, folder_name)
        num = 0
        new_name = folder_name
        while os.path.exists(new_dir): 
            num+=1
            new_name = f"{folder_name}{num}"
            new_dir = os.path.join(default_dir, new_name)
        try:
            copy_directory_contents(dir, default_dir, new_name)
            print("successfully added dir:", dir)
            messagebox.showinfo("Info", "Successfully copied contents into mod directory!")
            self.on_finish_edit("", new_dir)
        except PermissionError:
            print(f"PermissionError: You do not have the required permissions to copy to '{new_dir}'.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")