"""
editor.py: The editor view from which info.toml parameters can be modified manually
"""

import shutil, os, sys
from src.constants.elements import ELEMENTS
from src.constants.ui_params import PAD_H, PAD_V
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from src.core.data import remove_cache
from src.utils.web import open_page, is_valid_url
from src.utils.string_helper import clean_mod_name, clean_vesion
from src.core.mod_loader import ModLoader
from src.core.web.static_scraper import Extractor
from src.utils.web import trim_url
from src.utils.downloader import Downloader
from src.utils.image_handler import ImageHandler
from src.utils.file import get_base_name, get_parent_dir, rename_folder
from src.utils.toml import dump_toml
from src.core.formatting import format_folder_name, format_display_name, format_slots, group_char_name, get_mod_name
from src.utils.common import get_project_dir
from .comparison import Comparison
from .config import Config
from assets import ICON_PATH
from src.ui.base import get_text, set_text, clear_text, set_enabled, open_file_dialog
from src.ui.components.checkbox_treeview import Treeview
from src.core.web.scraper_thread import ScraperThread

class Editor:
    def __init__(self, root, webdriver_manager, directory:str="", callback=None) -> None:
        self.root = root
        self.webdriver_manager = webdriver_manager
        self.new_window = None
        self.config = Config()
        self.comparison = Comparison()
        self.img_urls = []
        self.img_descriptions = []
        self.is_running = True
        self.callback = callback
        self.directory = directory
        self.open(self.root, self.directory)
    
    def on_close(self):
        self.is_running = False
        self.new_window.destroy()

    def on_img_resized(self, image):
        if self.is_running:
            self.label_img.config(image=image, width=10, height=10)
            self.label_img.image = image  # Keep a reference to prevent garbage collection

    def download_img(self):
        download_data = []
        download_dir = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "cache/thumbnails")
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
        
    def on_bs4_result(self, mod_title, authors):
        if mod_title:
            self.generator.mod_title_web = clean_mod_name(mod_title)
            set_text(self.entry_mod_name, self.generator.mod_title_web)
        elif self.generator.mod_name:
            set_text(self.entry_mod_name, self.generator.mod_name)
            
        if authors:
            set_text(self.entry_authors, authors)

        self.set_display_name(
            get_text(self.entry_char_names), 
            get_text(self.entry_slots), 
            get_text(self.entry_mod_name), 
            get_text(self.combobox_cat)
        )

        self.set_folder_name(
            get_text(self.entry_char_names, remove_spacing=True), 
            get_text(self.entry_slots, remove_spacing=True), 
            get_text(self.entry_mod_name, remove_spacing=True), 
            get_text(self.combobox_cat)
        )

    def on_selenium_result(self, version, img_urls, img_descriptions, wifi_safe:str):
        self.img_urls = img_urls
        self.img_descriptions = img_descriptions
        set_text(self.label_output, "Fetched elements")
        set_text(self.entry_ver, clean_vesion(version))
        self.cbox_wifi_safe.set(wifi_safe)

        if len(self.img_urls) > 0:
            self.label_output.config(text="Downloading thumbnails...")
            self.download_img()
            if self.replace_img_state.get():
                self.generator.img_url = self.img_urls[0]
                download_dir = os.path.join(get_project_dir(), "cache/thumbnails")
                self.set_image(os.path.join(download_dir, trim_url(self.img_urls[0])))
            else:
                self.set_img_cbox(self.img_descriptions, self.img_descriptions[0])
                set_enabled(self.ckbox_replace_img)
                set_enabled(self.cbox_img)
        else:
            self.generator.img_url = ""
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
        self.generator.url = self.entry_url.get()
        self.cbox_img.config(state="disabled")
        self.replace_img_state.set(False)
        bs4_thread = Extractor(self.entry_url.get(), self.on_bs4_result)
        bs4_thread.start()
        ScraperThread(self.entry_url.get(), self.webdriver_manager, self.on_selenium_result)

    def on_url_changed(self, event):
        self.generator.url = get_text(self.entry_url)

    def open_url(self):
        if is_valid_url(self.entry_url.get()):
            open_page(self.entry_url.get())

    def on_combobox_select(self, event):
        self.set_folder_name(
            self.entry_char_names.get().replace(" ", ""), 
            self.entry_slots.get().replace(" ", ""), 
            self.entry_mod_name.get().replace(" ", ""), 
            self.combobox_cat.get()) 
    
    def on_img_url_selected(self, event):
        selected_idx = self.cbox_img.current()
        self.replace_img_state.set(True)
        if selected_idx < len(self.img_urls):
            self.generator.img_url = self.img_urls[selected_idx]
            name = trim_url(self.generator.img_url)
            download_dir = os.path.join(get_project_dir(), "cache/thumbnails")
            self.set_image(os.path.join(download_dir, name))
    
    def on_img_replace_changed(self):
        should_replace = self.replace_img_state.get()
        if should_replace:
            self.on_img_url_selected(None)
        else:
            self.find_image()
    
    def on_entry_change(self, event):
        self.set_display_name(self.entry_char_names.get(), self.entry_slots.get(), self.entry_mod_name.get(), self.combobox_cat.get())
        self.set_folder_name(self.entry_char_names.get().replace(" ", ""), self.entry_slots.get().replace(" ", ""), self.entry_mod_name.get().replace(" ", ""), self.combobox_cat.get())

    def set_display_name(self, character_names, slots, mod_name, category):
        set_text(self.entry_display_name, format_display_name(character_names, slots, mod_name, category))

    def set_folder_name(self, character_names, slots, mod_name, category):
        set_text(self.entry_folder_name, format_folder_name(character_names, slots, mod_name, category))
 
    def set_img_cbox(self, values=[], selected_option=""):
        self.cbox_img.config(values=values)
        self.cbox_img.set(selected_option)

    def update_preview(self):
        clear_text(self.entry_url)
        self.config.load()

        self.close_on_apply.set(self.config.close_on_apply)

        dict_info = self.generator.preview_info_toml(
            working_dir = get_text(self.entry_work_dir),
            version = get_text(self.entry_ver))

        set_text(self.label_output, "Changed working directory")
        self.combobox_cat.set(dict_info["category"])

        names = group_char_name(self.generator.char_names, self.generator.group_names)           
        set_text(self.entry_char_names, names)

        clear_text(self.entry_slots)
        
        slots_cleaned = ""
        if self.generator.slots:
            slots_cleaned = format_slots(dict_info["slots"])
            set_text(self.entry_slots, slots_cleaned)    

        mod_name = ""
        display_name = ""
        dir_name = get_base_name(self.generator.working_dir)
        includes = []

        if self.loader.load_toml(self.entry_work_dir.get()):
            display_name = self.loader.display_name
            set_text(self.entry_authors, self.loader.authors)
            self.combobox_cat.set(self.loader.category)
            set_text(self.entry_ver, clean_vesion(self.loader.version))
            self.cbox_wifi_safe.set(self.loader.wifi_safe)
            mod_name = self.loader.mod_name
            set_text(self.entry_url, self.loader.url)
            set_text(self.txt_desc, self.loader.description)
            includes = self.loader.includes
        
        if len(includes) <= 0:
            includes = self.generator.includes
        self.update_includes(includes)
        
        if not mod_name:
            mod_name = get_mod_name(
                display_name if display_name else dir_name, 
                self.generator.char_keys,
                self.generator.slots, 
                self.generator.category)
            
        self.generator.mod_name = mod_name
        set_text(self.entry_mod_name, mod_name)
        self.set_display_name(names, slots_cleaned, mod_name, get_text(self.combobox_cat))
        self.set_folder_name(names.replace(" ", "") , slots_cleaned.replace(" ", ""), mod_name.replace(" ", ""), get_text(self.combobox_cat))
        self.generator.url = self.entry_url.get()

        self.find_image()

    def change_working_directory(self):
        working_dir = open_file_dialog(self.config.default_dir)
        if not working_dir:
            return
        
        set_text(self.entry_work_dir, working_dir)
        self.update_preview()

    def on_update_directory(self, event):
        work_dir = get_text(self.entry_work_dir)
        if work_dir and os.path.exists(work_dir):
            self.update_preview()

    def apply_changes(self):
        dump_toml(
            self.generator.working_dir,
            TomlParams(get_text(self.entry_display_name), 
                       get_text(self.entry_authors), 
                       get_text(self.txt_desc), 
                       get_text(self.entry_ver), 
                       get_text(self.combobox_cat), 
                       get_text(self.entry_url), 
                       get_text(self.entry_mod_name), 
                       get_text(self.cbox_wifi_safe),
                       self.get_includes(),
                       self.generator.slots)
        )
        
        if get_text(self.entry_work_dir):
            old_dir = self.generator.working_dir
            self.move_file()
            new_dir = os.path.join(get_parent_dir(old_dir), get_text(self.entry_folder_name)) 
            result, msg = rename_folder(old_dir, new_dir)
            if result:
                set_text(self.entry_work_dir, new_dir)
                self.generator.working_dir = new_dir
                self.find_image()
                self.callback(old_dir, new_dir)

                messagebox.showinfo("Info", msg)
                if self.config.close_on_apply:
                    self.on_close()
            else:
                messagebox.showwarning("Error", msg)
        else:
            set_text(self.label_output, "Working directory is empty!")

    def update_image(self):
        image_path =  filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.webp")])
        if not image_path or not os.path.exists(image_path):
            return
        self.set_image(image_path)

    def on_update_image(self, event):
        image_dir = self.entry_img_dir.get()
        if self.generator.image_dir == image_dir:
            return
        self.generator.image_dir = image_dir
        image_extensions = [".webp", ".png", ".jpg", ".jpeg", ".gif"]
        if image_dir and os.path.exists(image_dir):
            for extension in image_extensions:
                if image_dir.endswith(extension):
                    self.set_image(image_dir)
                    break
        
    def set_image(self, directory):
        if not directory or not os.path.exists(directory):
            return
        
        self.entry_img_dir.delete(0, tk.END)
        self.entry_img_dir.insert(tk.END, directory)
        ImageHandler(directory, self.label_img.winfo_width(), self.label_img.winfo_height(), self.on_img_resized)
        
    def move_file(self):
        source_file = get_text(self.entry_img_dir) 
        dst_dir = get_text(self.entry_work_dir)
        
        if not source_file or not os.path.exists(source_file):
            print("image dir is empty or invalid")
            return
        
        new_path = os.path.join(dst_dir, IMAGE_NAME)
        set_text(self.entry_img_dir, new_path)
        
        if os.path.exists(new_path):
            if os.path.samefile(source_file, new_path):
                print("paths are same")
                return
            
        shutil.copy(source_file, new_path)

    def find_image(self):
        img_list = common.get_direct_child_by_extension(self.generator.working_dir, ".webp")
        if len(img_list) > 0:
            self.set_image(self.generator.working_dir +  "/" + img_list[0])
            self.replace_img_state.set(False)
            return
        
        other_types = [type for type in IMAGE_TYPES if type != ".webp"]
        for type in other_types:
            img_list = common.get_direct_child_by_extension(self.generator.working_dir, type)
            if len(img_list) > 0:
                self.set_image(self.generator.working_dir +  "/" + img_list[0])
                self.replace_img_state.set(False)
                return

        self.entry_img_dir.delete(0, tk.END)
        self.label_img.config(image=None)
        self.label_img.image = None

    def update_includes(self, includes:list):
        self.treeview.clear()
        for element in ELEMENTS + self.config.additional_elements:
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
        self.config.open_config(self.new_window) 

    def open_comparison(self):
        self.comparison.open(self.new_window, loaded_data=self.loader, generated_data={
            'folder_name':self.entry_folder_name.get(), 
            'display_name':self.entry_display_name.get(),
            'authors':self.entry_authors.get(),
            'category':self.combobox_cat.get(),
            'version':self.entry_ver.get(),
            'description':self.txt_desc.get(1.0, tk.END),
            'working_dir':self.generator.working_dir
            })
    
    def open(self, root, working_dir = ""):
        if self.new_window is not None:
            self.new_window.destroy()
        
        self.new_window = tk.Toplevel(root)
        self.new_window.title("Edit")
        self.new_window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.is_running = True
        self.show(self.new_window, working_dir)

    def show(self, root, working_dir = ""):
        self.new_window = root
        for i in range(3):
            self.new_window.columnconfigure(i, weight=1)
            self.new_window.columnconfigure(i, minsize=200)

        self.new_window.rowconfigure(12, weight=1)
        self.new_window.minsize(640, 340)
        self.new_window.geometry("920x560")
        self.new_window.configure(padx=10, pady=10) 

        self.icon_browse = ImageTk.PhotoImage(file=os.path.join(ICON_PATH, 'browse.png'))
        self.icon_config = ImageTk.PhotoImage(file=os.path.join(ICON_PATH, 'config.png'))
        self.icon_download = ImageTk.PhotoImage(file=os.path.join(ICON_PATH, 'download.png'))

        # column 0
        self.label_work_dir = tk.Label(self.new_window, text="Directory")
        self.label_work_dir.grid(row=0, column=0, sticky=tk.W, pady = (0, PAD_V))

        self.btn_config = tk.Button(self.new_window, image=self.icon_config, width=15,height=15,relief=tk.FLAT ,cursor='hand2',command=self.open_config )
        self.btn_config.grid(row=0, column=2, sticky=tk.E, pady = (0, PAD_V))

        self.frame_work_dir = tk.Frame(self.new_window)
        self.frame_work_dir.grid(row=1, column=0, rowspan=2, columnspan=3, sticky=tk.EW, pady = (0, PAD_V))

        self.btn_change_work_dir = tk.Button(self.frame_work_dir, image=self.icon_browse, relief=tk.FLAT, cursor='hand2', command=self.change_working_directory)
        self.btn_change_work_dir.pack(side="left", padx = (0, PAD_H))

        self.entry_work_dir = tk.Entry(self.frame_work_dir, width=10)
        self.entry_work_dir.pack(fill=tk.X, expand=True)
        self.entry_work_dir.bind("<Return>", self.on_update_directory)

        self.label_url = tk.Label(self.new_window, text="Url")
        self.label_url.grid(row=3, column=0, sticky=tk.W)

        self.url_frame = tk.Frame(self.new_window)
        self.url_frame.grid(row=4, column=0, columnspan=3, sticky=tk.EW, pady = (0, PAD_V))
        
        self.entry_url = tk.Entry(self.url_frame, width=10)
        self.entry_url.pack(side='left', fill=tk.X, expand=True)
        self.entry_url.bind("<KeyRelease>", self.on_url_changed)

        self.btn_fetch_data = tk.Button(self.url_frame, text="Get", cursor='hand2', command=self.get_data_from_url, anchor='n')
        self.btn_fetch_data.pack(side=tk.LEFT, padx=(PAD_H, PAD_H))

        self.btn_open_web = tk.Button(self.url_frame, text="Open", cursor='hand2', command=self.open_url, anchor='n')
        self.btn_open_web.pack(side=tk.LEFT)

        self.label_mod_name = tk.Label(self.new_window, text="Mod Title")
        self.label_mod_name.grid(row=5, column=0, sticky=tk.W)

        self.entry_mod_name = tk.Entry(self.new_window, width=10)
        self.entry_mod_name.grid(row=6, column=0, sticky=tk.EW, padx = (0, PAD_H), pady = (0, PAD_V))
        self.entry_mod_name.bind("<KeyRelease>", self.on_entry_change)

        self.label_authors = tk.Label(self.new_window, text="Authors")
        self.label_authors.grid(row=7, column=0, sticky=tk.W)

        self.entry_authors = tk.Entry(self.new_window, width=10)
        self.entry_authors.grid(row=8, column=0, sticky=tk.EW, padx = (0, PAD_H), pady = (0, PAD_V))

        self.frame = tk.Frame(self.new_window)
        self.frame.grid(row=9, column=0, rowspan=2, sticky=tk.EW, padx = (0, PAD_H), pady = (0, PAD_V))
        self.frame.columnconfigure(1, weight=1)

        self.label_ver = tk.Label(self.frame, text="Version")
        self.label_ver.grid(row=0, column=0, sticky=tk.W)

        self.entry_ver = tk.Entry(self.frame, width=10)
        self.entry_ver .grid(row=1, column=0, sticky=tk.W, padx=(0,PAD_H))
        self.entry_ver.insert(0, "1.0.0")

        self.label_cat = tk.Label(self.frame, text="Category")
        self.label_cat.grid(row=0, column=1, sticky=tk.W)

        self.combobox_cat = ttk.Combobox(self.frame, values=CATEGORIES, width=10)
        self.combobox_cat.grid(row=1, column=1, sticky=tk.EW)
        self.combobox_cat.bind("<<ComboboxSelected>>", self.on_combobox_select)
        self.combobox_cat.set(CATEGORIES[-1])

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

        # column 1
        self.label_char_names = tk.Label(self.new_window, text="Characters")
        self.label_char_names.grid(row=5, column=1, sticky=tk.W)

        self.entry_char_names = tk.Entry(self.new_window, width=10)
        self.entry_char_names.grid(row=6, column=1, sticky=tk.EW, padx = (0, PAD_H), pady = (0, PAD_V))
        self.entry_char_names.bind("<KeyRelease>", self.on_entry_change)

        self.label_slots = tk.Label(self.new_window, text="Slots")
        self.label_slots.grid(row=7, column=1, sticky=tk.W)

        self.entry_slots = tk.Entry(self.new_window, width=10)
        self.entry_slots.grid(row=8, column=1, sticky=tk.EW, padx = (0, PAD_H), pady = (0, PAD_V))
        self.entry_slots.bind("<KeyRelease>", self.on_entry_change)

        self.l_wifi_safe = tk.Label(self.new_window, text="Wifi-Safe")
        self.l_wifi_safe.grid(row=9, column=1, sticky=tk.W)
    
        self.cbox_wifi_safe = ttk.Combobox(self.new_window, width=10, values=["Uncertain", "Safe", "Not Safe"])
        self.cbox_wifi_safe.grid(row=10, column=1, sticky=tk.EW, padx = (0, PAD_H), pady = (0, PAD_V))
        self.cbox_wifi_safe.set("Uncertain")
        # self.cbox_wifi_safe.bind("<<ComboboxSelected>>", self.on_img_url_selected)

        self.label_list = tk.Label(self.new_window, text="Includes")
        self.label_list.grid(row=11, column=1, sticky=tk.W)

        self.treeview = Treeview(self.new_window, False)
        self.treeview.construct(["Elements"])
        self.treeview.widget.grid(row=12, column=1, sticky=tk.NSEW, padx = (0, PAD_H), pady = (0, PAD_V))
        
        # column 2
        self.label_folder_name = tk.Label(self.new_window, text="Folder Name")
        self.label_folder_name .grid(row=5, column=2, sticky=tk.W)

        self.entry_folder_name = tk.Entry(self.new_window)
        self.entry_folder_name.grid(row=6, column=2, sticky=tk.EW, pady = (0, PAD_V))

        self.label_display_name = tk.Label(self.new_window, text="Display Name")
        self.label_display_name.grid(row=7, column=2, sticky=tk.W)

        self.entry_display_name = tk.Entry(self.new_window, width=10)
        self.entry_display_name.grid(row=8, column=2, sticky=tk.EW, pady = (0, PAD_V))

        self.label_desc = tk.Label(self.new_window, text="Description")
        self.label_desc.grid(row=11, column=2, sticky=tk.W)

        self.txt_desc = tk.Text(self.new_window, height=10, width=10, wrap="word")
        self.txt_desc.grid(row=12, column=2, sticky=tk.NSEW, pady = (0, PAD_V))

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

        self.entry_work_dir.delete(0, tk.END)
        if working_dir:
            self.entry_work_dir.insert(tk.END, working_dir)
            self.update_preview()