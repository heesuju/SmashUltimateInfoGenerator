"""
editor.py: The editor view from which info.toml parameters can be modified manually
"""

import os
import sys
import copy
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from src.constants.elements import ELEMENTS
from src.constants.ui_params import PAD_H, PAD_V
from src.constants.defs import IMAGE_TYPES, WIFI_TYPES
from src.constants.categories import CATEGORIES
from src.core.data import remove_cache
from src.core.mod_loader import ModLoader
from src.core.web.static_scraper import Extractor
from src.core.web.scraper_thread import ScraperThread
from src.core.formatting import (
    format_folder_name,
    format_display_name,
    clean_mod_name,
    clean_version,
    group_char_name,
    format_slots
)
from src.models.mod import Mod
from src.utils.web import (
    trim_url,
    open_page,
    is_valid_url
)
from src.utils.string_helper import remove_spacing
from src.utils.downloader import Downloader
from src.utils.image_handler import ImageHandler
from src.utils.file import (
    get_parent_dir,
    get_direct_child_by_extension,
    rename_folder,
    copy_file
)
from src.utils.toml import dump_toml
from src.utils.common import get_project_dir, is_valid_file
from src.ui.base import (
    get_text,
    set_text,
    set_enabled,
    open_file_dialog,
    get_icon
)
from src.ui.components.checkbox_treeview import Treeview
from data import PATH_CACHE
from .comparison import Comparison
from .config import Config

class Editor:
    """
    Tkinter UI class for modifying info.toml
    """
    def __init__(self, root, webdriver_manager, directory:str="", callback=None) -> None:
        self.root = root
        self.webdriver_manager = webdriver_manager
        self.mod = None
        self.org_mod = None
        self.new_window = None
        self.config = Config()
        self.comparison = Comparison()
        self.img_urls = []
        self.img_descriptions = []
        self.is_running = True
        self.callback = callback
        self.directory = directory
        self.icon_browse = get_icon('browse')
        self.icon_config = get_icon('config')
        self.icon_download = get_icon('download')

        self.desc_text = None

        self.dir_var = tk.StringVar()
        self.url_var = tk.StringVar()
        self.mod_name_var = tk.StringVar()
        self.authors_var = tk.StringVar()
        self.version_var = tk.StringVar()
        self.char_var = tk.StringVar()
        self.slot_var = tk.StringVar()
        self.folder_var = tk.StringVar()
        self.display_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.wifi_var = tk.StringVar()
        self.desc_var = tk.StringVar()

        self.set_binding()

        if self.mod is None:
            ModLoader(
                [self.directory],
                self.on_scanned
            )

    def set_values(self, mod:Mod):
        """
        Sets mod values
        """
        self.dir_var.set(mod.path)
        self.url_var.set(mod.url)
        self.mod_name_var.set(mod.mod_name)
        self.authors_var.set(mod.authors)
        self.version_var.set(mod.version)
        keys, names, groups, series, slots = mod.get_character_data()
        self.char_var.set(group_char_name(names, groups))
        self.slot_var.set(format_slots(slots))
        self.folder_var.set(mod.folder_name)
        self.display_var.set(mod.display_name)
        self.category_var.set(mod.category)
        self.wifi_var.set(mod.wifi_safe)
        self.desc_var.set(mod.description)

    def set_binding(self):
        """
        Binds mod object to editor
        """
        self.dir_var.trace_add("write", lambda *args: setattr(self.mod, 'path', self.dir_var.get()))
        self.url_var.trace_add("write", lambda *args: setattr(self.mod, 'url', self.url_var.get()))
        self.mod_name_var.trace_add("write", lambda *args: setattr(self.mod, 'mod_name', self.mod_name_var.get()))
        self.mod_name_var.trace_add("write", lambda *args: self.on_name_changed())
        self.authors_var.trace_add("write", lambda *args: setattr(self.mod, 'authors', self.authors_var.get()))
        self.version_var.trace_add("write", lambda *args: setattr(self.mod, 'version', self.version_var.get()))
        self.char_var.trace_add("write", lambda *args: setattr(self.mod, 'characters_grouped', self.char_var.get()))
        self.char_var.trace_add("write", lambda *args: self.on_name_changed())
        self.slot_var.trace_add("write", lambda *args: setattr(self.mod, 'character_slots_grouped', self.slot_var.get()))
        self.slot_var.trace_add("write", lambda *args: self.on_name_changed())
        self.category_var.trace_add("write", lambda *args: setattr(self.mod, 'category', self.category_var.get()))
        self.category_var.trace_add("write", lambda *args: self.on_name_changed())
        self.folder_var.trace_add("write", lambda *args: setattr(self.mod, 'folder_name', self.folder_var.get()))
        self.display_var.trace_add("write", lambda *args: setattr(self.mod, 'display_name', self.display_var.get()))
        self.wifi_var.trace_add("write", lambda *args: setattr(self.mod, 'wifi_safe', self.wifi_var.get()))
        self.desc_var.trace_add("write", lambda *args: self.on_desc_changed())

    def on_close(self):
        """
        Clean-up function called before closing window
        """
        self.is_running = False
        self.new_window.destroy()

    def on_img_resized(self, image):
        if self.is_running:
            self.label_img.config(image=image, width=10, height=10)
            self.label_img.image = image  # Keep a reference to prevent garbage collection

    def download_img(self):
        download_data = []
        download_dir = os.path.join(PATH_CACHE, "thumbnails")
        os.makedirs(download_dir, exist_ok=True)
        remove_cache()

        for img_url in self.img_urls:
            file_name = trim_url(img_url)
            download_data.append((img_url, os.path.join(download_dir, file_name)))
        
        threads = []
        for img_url, working_dir in download_data:
            downloader_thread = Downloader(img_url, working_dir)
            downloader_thread.start()  # Start each thread
            threads.append(downloader_thread)  # Keep track of threads

        for thread in threads:
            thread.join()

        self.label_output.config(text="Downloaded image")
        
    def on_bs4_result(self, mod_title:str, authors:str, is_moveset:bool):
        if mod_title:
            self.mod_name_var.set(clean_mod_name(mod_title))
            
        if authors:
            self.authors_var.set(authors)

        if is_moveset:
            self.mod.contains_moveset = True

    def on_selenium_result(self, version, img_urls, img_descriptions, wifi_safe:str):
        self.img_urls = img_urls
        self.img_descriptions = img_descriptions
        set_text(self.label_output, "Fetched elements")
        
        self.version_var.set(clean_version(version))
        self.wifi_var.set(wifi_safe)

        if len(self.img_urls) > 0:
            self.label_output.config(text="Downloading thumbnails...")
            self.download_img()
            if self.replace_img_state.get():
                self.mod.thumbnail = self.img_urls[0]
                download_dir = os.path.join(get_project_dir(), "cache/thumbnails")
                self.set_image(os.path.join(download_dir, trim_url(self.img_urls[0])))
            else:
                self.set_img_cbox(self.img_descriptions, self.img_descriptions[0])
                set_enabled(self.ckbox_replace_img)
                set_enabled(self.cbox_img)
        else:
            self.mod.thumbnail = ""
            self.set_img_cbox()
            set_enabled(self.ckbox_replace_img, False)
            set_enabled(self.cbox_img, False)
        set_enabled(self.btn_fetch_data)

    def get_data_from_url(self):
        if not self.entry_url.get() or not is_valid_url(self.entry_url.get()):
            return
        
        self.btn_fetch_data.config(state="disabled")
        set_text(self.label_output, "Fetching elements...")
        set_enabled(self.ckbox_replace_img, False)
        self.cbox_img.config(state="disabled")
        self.replace_img_state.set(False)
        bs4_thread = Extractor(self.entry_url.get(), self.on_bs4_result)
        bs4_thread.start()
        ScraperThread(self.entry_url.get(), self.webdriver_manager, self.on_selenium_result)

    def open_url(self):
        """
        Opens the web page in the url entry field
        """
        if is_valid_url(self.url_var.get()):
            open_page(self.url_var.get())

    def on_img_url_selected(self, event):
        selected_idx = self.cbox_img.current()
        self.replace_img_state.set(True)
        if selected_idx < len(self.img_urls):
            self.mod.thumbnail = self.img_urls[selected_idx]
            name = trim_url(self.mod.thumbnail)
            download_dir = os.path.join(PATH_CACHE, "thumbnails")
            self.set_image(os.path.join(download_dir, name))
    
    def on_img_replace_changed(self):
        should_replace = self.replace_img_state.get()
        if should_replace:
            self.on_img_url_selected(None)
        else:
            self.find_image()

    def on_desc_changed(self, *args, **kwargs)->None:
        """
        Called when mod description is changed
        """
        if args and isinstance(args[0], tk.Event):
            if get_text(self.desc_text) != self.desc_var.get().rstrip('\n'): # Check if text has changed
                self.desc_var.set(get_text(self.desc_text))
        else:
            if self.desc_text is not None:
                pos = self.desc_text.index(tk.INSERT)
                self.desc_text.delete("1.0", "end")
                self.desc_text.insert("1.0", self.desc_var.get().rstrip('\n'))
                self.desc_text.mark_set(tk.INSERT, pos)
                self.desc_text.see(tk.INSERT)
                
        setattr(self.mod, 'description', self.desc_var.get())

    def on_name_changed(self)->None:
        """
        Called when mod name, character, slot fields are changed
        """
        self.display_var.set(
            format_display_name(
                self.char_var.get(),
                self.slot_var.get(),
                self.mod_name_var.get(),
                self.category_var.get()
            )
        )
        self.folder_var.set(
            format_folder_name(
                remove_spacing(self.char_var.get()),
                remove_spacing(self.slot_var.get()),
                remove_spacing(self.mod_name_var.get()),
                remove_spacing(self.category_var.get()))
        )

    def set_img_cbox(self, values=[], selected_option=""):
        self.cbox_img.config(values=values)
        self.cbox_img.set(selected_option)

    def on_scanned(self, mods:list[Mod])->None:
        """
        callback function when the specific mod directory has been scanned
        """
        if len(mods) <= 0:
            return

        self.mod = mods[0]
        self.org_mod = copy.copy(self.mod)
        self.set_values(self.mod)
        self.open(self.root)
        set_text(self.desc_text, self.mod.description)
        includes = self.mod.includes
        self.update_includes(includes)
        self.find_image()

    def update_preview(self):
        """
        Auto-fills empty fields
        """

        self.config.load()
        self.close_on_apply.set(self.config.settings.close_on_apply)

        if self.mod is None:
            ModLoader(
                [self.dir_var.get()],
                self.on_scanned
            )

        set_text(self.label_output, "Changed working directory")

    def change_working_directory(self):
        working_dir = open_file_dialog(self.config.settings.default_directory)
        if not working_dir:
            return

        self.dir_var.set(working_dir)
        self.update_preview()

    def on_update_directory(self, event):
        if self.dir_var.get() and os.path.exists(self.dir_var.get()):
            self.update_preview()

    def apply_changes(self):
        """
        Applies changes to info.toml
        A new file will be generated if it does not exist
        """
        def copy_img(src_file:str, dst_dir):
            """
            Copies image to the new directory and renames to preview.webp
            """
            if is_valid_file(src_file):
                dst_file = os.path.join(dst_dir, "preview.webp")
                if copy_file(src_file, dst_file):
                    set_text(self.entry_img_dir, dst_file)
                
        self.mod.includes = self.get_includes()
        data = self.mod.to_dict()
        dump_toml(
            self.mod.path,
            data
        )

        if self.mod.path:
            copy_img(self.mod.thumbnail, self.mod.path)
            old_dir = self.mod.path
            new_dir = os.path.join(get_parent_dir(self.mod.path), self.mod.folder_name) 
            result, msg = rename_folder(old_dir, new_dir)
            if result:
                self.mod.path = new_dir
                self.find_image()
                self.callback(old_dir, new_dir)

                messagebox.showinfo("Info", msg)
                if self.config.settings.close_on_apply:
                    self.on_close()
            else:
                messagebox.showwarning("Error", msg)
        else:
            set_text(self.label_output, "Working directory is empty!")

    def update_image(self):
        """
        Open file selection dialog for new thumbnail image
        """
        image_file_types = ""
        for extension in IMAGE_TYPES:
            image_file_types += f"*{extension};"
        image_path =  filedialog.askopenfilename(filetypes=[("Image files", image_file_types)])
        if not image_path or not os.path.exists(image_path):
            return
        self.set_image(image_path)

    def on_update_image(self, event)->None:
        """
        Called when image directory is changed
        """
        image_dir = self.entry_img_dir.get()
        if self.mod.thumbnail == image_dir:
            return

        self.mod.thumbnail = image_dir

        if image_dir and os.path.exists(image_dir):
            for extension in IMAGE_TYPES:
                if image_dir.endswith(extension):
                    self.set_image(image_dir)
                    break

    def set_image(self, directory):
        if not directory or not os.path.exists(directory):
            return
        
        self.entry_img_dir.delete(0, tk.END)
        self.entry_img_dir.insert(tk.END, directory)
        self.mod.thumbnail = directory
        ImageHandler(directory, self.label_img.winfo_width(), self.label_img.winfo_height(), self.on_img_resized)

    def find_image(self):
        img_list = get_direct_child_by_extension(self.mod.path, ".webp")
        
        if len(img_list) > 0:
            img_path = os.path.join(self.mod.path, img_list[0])
            self.set_image(img_path)
            self.replace_img_state.set(False)
            return
        
        other_types = [type for type in IMAGE_TYPES if type != ".webp"]
        for img_type in other_types:
            img_list = get_direct_child_by_extension(self.mod.path, img_type)
            if len(img_list) > 0:
                img_path = os.path.join(self.mod.path, img_list[0])
                self.set_image(img_path)
                self.replace_img_state.set(False)
                return
        
        self.entry_img_dir.delete(0, tk.END)
        self.label_img.config(image=None)
        self.label_img.image = None

    def update_includes(self, includes:list):
        self.treeview.clear()
        for element in ELEMENTS + self.config.settings.additional_elements:
            self.treeview.add_item([element], element in includes)

    def get_includes(self):
        outputs = []
        for item in self.treeview.get_checked_items():
            text = self.treeview.get_row_text(item)
            if text not in outputs:
                outputs.append(text)
        return outputs

    def on_window_resize(self, event):
        self.set_image(self.entry_img_dir.get())

    def on_change_close_on_apply(self):
        self.config.set_close_on_apply(self.close_on_apply.get())

    def open_config(self):
        """
        Opens config popup
        """
        self.config.open_config(self.new_window) 

    def open_comparison(self):
        """
        Opens before/after comparison popup
        """
        self.comparison.open(self.new_window, src=self.org_mod, dst=self.mod)

    def open(self, root):
        if self.new_window is not None:
            self.new_window.destroy()

        self.new_window = tk.Toplevel(root)
        self.new_window.title("Edit")
        self.new_window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.is_running = True
        self.show(self.new_window)

    def show(self, root):
        """
        Shows editor window and binds widget commands
        """
        self.new_window = root
        for i in range(3):
            self.new_window.columnconfigure(i, weight=1)
            self.new_window.columnconfigure(i, minsize=200)

        self.new_window.rowconfigure(12, weight=1)
        self.new_window.minsize(640, 340)
        self.new_window.geometry("920x560")
        self.new_window.configure(padx=10, pady=10)

        dir_label = tk.Label(self.new_window, text="Directory")
        dir_label.grid(row=0, column=0, sticky=tk.W, pady = (0, PAD_V))

        self.btn_config = tk.Button(self.new_window, image=self.icon_config, width=15,height=15,relief=tk.FLAT ,cursor='hand2',command=self.open_config )
        self.btn_config.grid(row=0, column=2, sticky=tk.E, pady = (0, PAD_V))

        self.frame_work_dir = tk.Frame(self.new_window)
        self.frame_work_dir.grid(row=1, column=0, rowspan=2, columnspan=3, sticky=tk.EW, pady = (0, PAD_V))

        self.btn_change_work_dir = tk.Button(self.frame_work_dir, image=self.icon_browse, relief=tk.FLAT, cursor='hand2', command=self.change_working_directory)
        self.btn_change_work_dir.pack(side="left", padx = (0, PAD_H))

        self.entry_work_dir = tk.Entry(self.frame_work_dir, width=10, textvariable=self.dir_var)
        self.entry_work_dir.pack(fill=tk.X, expand=True)
        self.entry_work_dir.bind("<Return>", self.on_update_directory)

        # URL entry field
        url_label = tk.Label(self.new_window, text="Url")
        url_label.grid(row=3, column=0, sticky=tk.W)
        self.url_frame = tk.Frame(self.new_window)
        self.url_frame.grid(row=4, column=0, columnspan=3, sticky=tk.EW, pady = (0, PAD_V))
        self.entry_url = tk.Entry(self.url_frame, width=10, textvariable=self.url_var)
        self.entry_url.pack(side='left', fill=tk.X, expand=True)

        self.btn_fetch_data = tk.Button(self.url_frame, text="Get", cursor='hand2', command=self.get_data_from_url, anchor='n')
        self.btn_fetch_data.pack(side=tk.LEFT, padx=(PAD_H, PAD_H))
        self.btn_open_web = tk.Button(self.url_frame, text="Open", cursor='hand2', command=self.open_url, anchor='n')
        self.btn_open_web.pack(side=tk.LEFT)

        # Mod name entry field
        mod_name_label = tk.Label(self.new_window, text="Mod Title")
        mod_name_label.grid(row=5, column=0, sticky=tk.W)
        self.entry_mod_name = tk.Entry(self.new_window, width=10, textvariable=self.mod_name_var)
        self.entry_mod_name.grid(row=6, column=0, sticky=tk.EW, padx = (0, PAD_H), pady = (0, PAD_V))

        # Authors entry field
        author_label = tk.Label(self.new_window, text="Authors")
        author_label.grid(row=7, column=0, sticky=tk.W)
        self.entry_authors = tk.Entry(self.new_window, width=10, textvariable=self.authors_var)
        self.entry_authors.grid(row=8, column=0, sticky=tk.EW, padx = (0, PAD_H), pady = (0, PAD_V))
        
        self.frame = tk.Frame(self.new_window)
        self.frame.grid(row=9, column=0, rowspan=2, sticky=tk.EW, padx = (0, PAD_H), pady = (0, PAD_V))
        self.frame.columnconfigure(1, weight=1)

        # Version entry field
        version_label = tk.Label(self.frame, text="Version")
        version_label.grid(row=0, column=0, sticky=tk.W)
        self.entry_ver = tk.Entry(self.frame, width=10, textvariable=self.version_var)
        self.entry_ver .grid(row=1, column=0, sticky=tk.W, padx=(0,PAD_H))
        
        # Category combobox
        category_label = tk.Label(self.frame, text="Category")
        category_label.grid(row=0, column=1, sticky=tk.W)
        self.combobox_cat = ttk.Combobox(self.frame, values=CATEGORIES, width=10, textvariable=self.category_var)
        self.combobox_cat.grid(row=1, column=1, sticky=tk.EW)

        # Image label
        self.label_img_dir = tk.Label(self.new_window, text="Image", anchor='w')
        self.label_img_dir.grid(row=11, column=0, sticky=tk.W, padx = (0, PAD_H))
        self.frame_img = tk.Frame(self.new_window, width=10)
        self.frame_img.grid(row=12, column=0, sticky=tk.NSEW, padx = (0, PAD_H), pady = (0, PAD_V))
        self.frame_img_dir = tk.Frame(self.frame_img, width = 10)
        self.frame_img_dir.pack(side=tk.TOP, fill=tk.X, expand=False, pady = (0, PAD_V))
        self.btn_select_img = tk.Button(self.frame_img_dir, image=self.icon_browse, relief=tk.FLAT, cursor='hand2', command=self.update_image, anchor='n')
        self.btn_select_img.pack(side=tk.LEFT, padx = (0, PAD_H))
        self.entry_img_dir = tk.Entry(self.frame_img_dir, width=10)
        self.entry_img_dir.pack(fill=tk.X, expand=True)
        self.entry_img_dir.bind("<KeyRelease>", self.on_update_image)
        fr_img_download = tk.Frame(self.frame_img)
        fr_img_download.pack(side=tk.BOTTOM, anchor=tk.NW, fill='x')
        self.replace_img_state = tk.IntVar()  # Use IntVar for 1 (checked) or 0 (unchecked)
        self.ckbox_replace_img = tk.Checkbutton(fr_img_download, text="replace with", relief=tk.FLAT, cursor="hand2", command=self.on_img_replace_changed, state="disabled", variable=self.replace_img_state)
        self.ckbox_replace_img.pack(side=tk.LEFT, anchor=tk.NW, padx = (0, PAD_H))
        self.cbox_img = ttk.Combobox(fr_img_download, width=10, state="disabled")
        self.cbox_img.pack(side=tk.LEFT, anchor=tk.NW, expand=True, fill='x')
        self.cbox_img.bind("<<ComboboxSelected>>", self.on_img_url_selected)
        self.label_img = tk.Label(self.frame_img, justify='center', anchor='center', bg='black')
        self.label_img.pack(fill=tk.BOTH, expand=True)

        self.label_char_names = tk.Label(self.new_window, text="Characters")
        self.label_char_names.grid(row=5, column=1, sticky=tk.W)
        
        self.entry_char_names = tk.Entry(self.new_window, width=10, textvariable=self.char_var)
        self.entry_char_names.grid(row=6, column=1, sticky=tk.EW, padx = (0, PAD_H), pady = (0, PAD_V))

        slots_label = tk.Label(self.new_window, text="Slots")
        slots_label.grid(row=7, column=1, sticky=tk.W)
        self.entry_slots = tk.Entry(self.new_window, width=10, textvariable=self.slot_var)
        self.entry_slots.grid(row=8, column=1, sticky=tk.EW, padx = (0, PAD_H), pady = (0, PAD_V))

        wifi_safe_label = tk.Label(self.new_window, text="Wifi-Safe")
        wifi_safe_label.grid(row=9, column=1, sticky=tk.W)
        self.cbox_wifi_safe = ttk.Combobox(self.new_window, width=10, values=WIFI_TYPES, textvariable=self.wifi_var)
        self.cbox_wifi_safe.grid(row=10, column=1, sticky=tk.EW, padx = (0, PAD_H), pady = (0, PAD_V))
        self.cbox_wifi_safe.set("Uncertain")

        includes_label = tk.Label(self.new_window, text="Includes")
        includes_label.grid(row=11, column=1, sticky=tk.W)

        self.treeview = Treeview(self.new_window, False)
        self.treeview.construct(["Elements"])
        self.treeview.widget.grid(row=12, column=1, sticky=tk.NSEW, padx = (0, PAD_H), pady = (0, PAD_V))

        # Folder name entry field
        folder_name_label = tk.Label(self.new_window, text="Folder Name")
        folder_name_label .grid(row=5, column=2, sticky=tk.W)
        self.entry_folder_name = tk.Entry(self.new_window, textvariable=self.folder_var)
        self.entry_folder_name.grid(row=6, column=2, sticky=tk.EW, pady = (0, PAD_V))

        # Display name entry field
        display_name_label = tk.Label(self.new_window, text="Display Name")
        display_name_label.grid(row=7, column=2, sticky=tk.W)
        self.entry_display_name = tk.Entry(self.new_window, width=10, textvariable=self.display_var)
        self.entry_display_name.grid(row=8, column=2, sticky=tk.EW, pady = (0, PAD_V))

        # Description text field
        desc_label = tk.Label(self.new_window, text="Description")
        desc_label.grid(row=11, column=2, sticky=tk.W)
        self.desc_text = tk.Text(self.new_window, height=10, width=10, wrap="word")
        self.desc_text.grid(row=12, column=2, sticky=tk.NSEW, pady = (0, PAD_V))
        self.desc_text.bind("<KeyRelease>", self.on_desc_changed)

        self.frame_btn = tk.Frame(self.new_window)
        self.frame_btn.grid(row=13, column=0, columnspan=3, sticky=tk.NSEW)

        self.btn_apply = tk.Button(self.frame_btn, text="Apply", command=self.apply_changes)
        self.btn_apply.pack(side=tk.RIGHT, fill="y")

        self.btn_compare = tk.Button(self.frame_btn, text="Compare", command=self.open_comparison)
        self.btn_compare.pack(side=tk.RIGHT, fill="y", padx=(0, PAD_H))

        self.close_on_apply = tk.IntVar()
        self.ckbtn_close = tk.Checkbutton(self.frame_btn, text="Close window when applied", variable=self.close_on_apply, command=self.on_change_close_on_apply, cursor='hand2')
        self.ckbtn_close.pack(side=tk.RIGHT)

        self.label_output = tk.Label(self.frame_btn)
        self.label_output.pack(side=tk.LEFT)

        self.new_window.bind("<Configure>", self.on_window_resize)
