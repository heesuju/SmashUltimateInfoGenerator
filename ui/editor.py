import shutil, os, sys
import common, defs
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from cache import remove_cache
from utils import open_web, format_version
from utils.generator import Generator
from utils.loader import Loader
from utils.static_scraper import Extractor
from utils.dynamic_scraper import Selenium
from utils.downloader import Downloader
from utils.image_resize import ImageResize
from .comparison import Comparison
from .config import Config
from . import PATH_ICON
from .common_ui import get_text, set_text, set_enabled, open_file_dialog, dump_toml, TomlParams

class Editor:
    def __init__(self, callback=None) -> None:
        self.new_window = None
        self.generator = Generator()
        self.config = Config()
        self.loader = Loader()
        self.comparison = Comparison()
        self.img_urls = []
        self.img_descriptions = []
        self.callback = callback

    def on_img_resized(self, image):
        self.label_img.config(image=image, width=10, height=10)
        self.label_img.image = image  # Keep a reference to prevent garbage collection

    def download_img(self):
        download_data = []
        download_dir = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "cache/thumbnails")
        os.makedirs(download_dir, exist_ok=True)
        remove_cache()

        for img_url in self.img_urls:
            file_name = common.trim_url(img_url)
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
            self.generator.mod_title_web = mod_title
            set_text(self.entry_mod_name, common.trim_mod_name(self.generator.mod_title_web, self.generator.ignore_names))
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
        set_text(self.entry_ver, format_version(version))
        self.cbox_wifi_safe.set(wifi_safe)

        if len(self.img_urls) > 0:
            self.label_output.config(text="Downloading thumbnails...")
            self.download_img()
            if self.replace_img_state.get():
                self.generator.img_url = self.img_urls[0]
                download_dir = os.path.join(common.get_project_dir(), "cache/thumbnails")
                self.set_image(os.path.join(download_dir, common.trim_url(self.img_urls[0])))
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
        if not self.entry_url.get() or not common.is_valid_url(self.entry_url.get()):
            return
        
        self.btn_fetch_data.config(state="disabled")
        set_text(self.label_output, "Fetching elements...")
        set_enabled(self.ckbox_replace_img, False)
        self.generator.url = self.entry_url.get()
        self.cbox_img.config(state="disabled")
        self.replace_img_state.set(False)
        bs4_thread = Extractor(self.entry_url.get(), self.on_bs4_result)
        selenium_thread = Selenium(self.entry_url.get(), self.on_selenium_result)
        
        bs4_thread.start()
        selenium_thread.start()

    def on_url_changed(self, event):
        self.generator.url = get_text(self.entry_url)

    def open_url(self):
        if common.is_valid_url(self.entry_url.get()):
            open_web(self.entry_url.get())

    def on_combobox_select(self, event):
        set_text(self.entry_folder_name, self.combobox_cat.get() + "_" + self.entry_char_names.get().replace(" ", "") + "[" + self.entry_slots.get().replace(" ", "")  + "]_" + self.entry_mod_name.get().replace(" ", "") ) 
    
    def on_img_url_selected(self, event):
        selected_idx = self.cbox_img.current()
        self.replace_img_state.set(True)
        if selected_idx < len(self.img_urls):
            self.generator.img_url = self.img_urls[selected_idx]
            name = common.trim_url(self.generator.img_url)
            download_dir = os.path.join(common.get_project_dir(), "cache/thumbnails")
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
        self.entry_display_name.delete(0, tk.END)
        display_name = self.config.display_name_format
        display_name = display_name.replace("{characters}", character_names)
        display_name = display_name.replace("{slots}", slots)
        display_name = display_name.replace("{mod}", mod_name)
        display_name = display_name.replace("{category}", category)
        self.entry_display_name.insert(0, display_name) 

    def set_folder_name(self, character_names, slots, mod_name, category):
        self.entry_folder_name.delete(0, tk.END)
        folder_name = self.config.folder_name_format
        folder_name = folder_name.replace("{characters}", character_names)
        folder_name = folder_name.replace("{slots}", slots)
        folder_name = folder_name.replace("{mod}", mod_name)
        folder_name = folder_name.replace("{category}", category)
        self.entry_folder_name.insert(0, folder_name)

    def toggle_checkbox(self, index):
        self.checkbox_states[index] = not self.checkbox_states[index]
        self.update_listbox()

    def update_listbox(self):
        self.listbox.delete(0, tk.END)

        # Add items with checkboxes
        for i, item in enumerate(defs.ELEMENTS + self.config.additional_elements):
            if i >= len(self.checkbox_states):
                self.checkbox_states.append(False)
            checkbox = "[O]" if self.checkbox_states[i] else "[X]"
            self.listbox.insert(tk.END, f"{checkbox} {item}")

        self.set_description()
 
    def set_img_cbox(self, values=[], selected_option=""):
        self.cbox_img.config(values=values)
        self.cbox_img.set(selected_option)

    def update_preview(self):
        self.entry_url.delete(0, tk.END)
        self.config.load()
        #self.config.set_default_dir(os.path.dirname(self.entry_work_dir.get()))

        dict_info = self.generator.preview_info_toml(
            get_text(self.entry_work_dir), 
            "", 
            get_text(self.entry_ver), 
            ""
        )

        set_text(self.label_output, "Changed working directory")
        self.update_description()
        self.combobox_cat.set(dict_info["category"])

        names = common.group_char_name(self.generator.char_names, self.generator.group_names)           
        set_text(self.entry_char_names, names)

        self.entry_slots.delete(0, tk.END)
        
        slots_cleaned = ""
        if self.generator.slots:
            slots_cleaned = common.slots_to_string(dict_info["slots"])
            self.entry_slots.insert(0, slots_cleaned)    

        mod_name = ""
        if not self.entry_url.get():
            dir_name = common.get_dir_name(self.generator.working_dir)
            title = common.get_mod_title(dir_name, self.generator.char_names, self.config.folder_name_format)
            capitalized = common.add_spaces_to_camel_case(title)
            mod_name = capitalized
            self.generator.mod_name = mod_name

            if self.loader.load_toml(self.entry_work_dir.get()):
                set_text(self.entry_authors, self.loader.authors)
                set_text(self.entry_ver, self.loader.version)
                set_text(self.entry_url, self.loader.url)
                self.combobox_cat.set(self.loader.category)
                self.cbox_wifi_safe.set(self.loader.wifi_safe)
        else:
            mod_name = self.generator.mod_title_web
        
        set_text(self.entry_mod_name, mod_name)
        self.set_display_name(names, slots_cleaned, mod_name, dict_info["category"])
        self.set_folder_name(names.replace(" ", "") , slots_cleaned.replace(" ", ""), mod_name.replace(" ", ""), dict_info["category"])
        self.generator.url = self.entry_url.get()

        self.find_image()

    def change_working_directory(self):
        working_dir = open_file_dialog(self.config.default_dir)
        if not working_dir:
            return
        
        set_text(self.entry_work_dir, working_dir)
        self.update_preview()

    def on_update_directory(self,event):
        work_dir = get_text(self.entry_work_dir)
        if work_dir and os.path.exists(work_dir):
            self.update_preview()

    def apply_changes(self):
        dump_toml(
            self.generator.working_dir,
            TomlParams(self.entry_display_name, self.entry_authors, self.txt_desc, self.entry_ver, 
                       self.combobox_cat, self.entry_url, self.entry_mod_name, self.cbox_wifi_safe,
                       self.generator.slots)
        )
        
        old_directory = self.generator.working_dir
        
        self.move_file()
        new_directory = self.rename_directory()
        set_text(self.label_output, "Applied changes")
        self.callback(old_directory, new_directory)

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
        image_extensions = [".png", ".jpg", ".jpeg", ".gif", ".webp"]
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
        resize_thread = ImageResize(directory, self.label_img.winfo_width(), self.label_img.winfo_height(), self.on_img_resized)
        resize_thread.start()
        
    def move_file(self):
        source_file = get_text(self.entry_img_dir) 
        dst_dir = get_text(self.entry_work_dir)
        
        if not source_file or not os.path.exists(source_file):
            print("image dir is empty or invalid")
            return
        
        new_path = os.path.join(dst_dir, defs.IMAGE_NAME)
        set_text(self.entry_img_dir, new_path)
        
        if os.path.exists(new_path):
            if os.path.samefile(source_file, new_path):
                print("paths are same")
                return
            
        shutil.copy(source_file, new_path)

    def find_image(self):
        for type in defs.IMAGE_TYPES:
            img_list = common.get_direct_child_by_extension(self.generator.working_dir, type)
            if len(img_list) > 0:
                self.set_image(self.generator.working_dir +  "/" + img_list[0])
                self.replace_img_state.set(False)
                return

        self.entry_img_dir.delete(0, tk.END)
        self.label_img.config(image=None)
        self.label_img.image = None

    def rename_directory(self):
        if not self.generator.working_dir or not self.entry_folder_name.get():
            return ""
        
        # Define the old folder name and the new folder name
        old_directory_path = self.generator.working_dir
        dir_name = common.get_dir_name(old_directory_path)
        new_directory_path = old_directory_path[0:-len(dir_name)]
        new_directory_path += self.entry_folder_name.get()
        # Check if the old directory exists
        if common.is_valid_dir(old_directory_path):
            try:
                # Rename the directory
                os.rename(old_directory_path, new_directory_path)
                set_text(self.entry_work_dir, new_directory_path)
                self.generator.working_dir = new_directory_path
                self.find_image()
            except OSError as e:
                print(f"Error renaming directory: {e}")
        else:
            print(f"The directory '{old_directory_path}' does not exist.")
        
        return new_directory_path

    def set_description(self):
        description = "Includes:\n"
        self.txt_desc.delete(1.0, tk.END)
        combined_list = defs.ELEMENTS + self.config.additional_elements
        for n in range(len(self.checkbox_states)):
            if n >= len(combined_list):
                self.checkbox_states[n] = False
            elif self.checkbox_states[n]:
                description += "- " + combined_list[n] + "\n"

        if True in self.checkbox_states:
            self.txt_desc.insert(tk.END, description)

    def update_description(self):
        self.listbox.selection_clear(0, tk.END)
        self.checkbox_states[0] = self.generator.is_skin
        self.checkbox_states[1] = self.generator.is_motion
        self.checkbox_states[2] = self.generator.is_effect
        self.checkbox_states[3] = self.generator.is_single_effect
        self.checkbox_states[4] = self.generator.is_voice
        self.checkbox_states[5] = self.generator.is_sfx
        self.checkbox_states[6] = self.generator.is_narrator_voice
        self.checkbox_states[7] = self.generator.is_victory_theme
        self.checkbox_states[8] = self.generator.is_victory_animation
        self.checkbox_states[9] = self.generator.is_custom_name
        self.checkbox_states[10] = self.generator.is_single_name
        self.checkbox_states[11] = self.generator.is_ui
        self.checkbox_states[12] = self.generator.is_kirby
        self.checkbox_states[13] = self.generator.is_stage

        self.update_listbox()

    def on_window_resize(self, event):
        self.set_image(self.entry_img_dir.get())

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
        self.show(self.new_window, working_dir)

    def show(self, root, working_dir = ""):
        self.new_window = root
        for i in range(3):
            self.new_window.columnconfigure(i, weight=1)
            self.new_window.columnconfigure(i, minsize=200)

        self.new_window.rowconfigure(12, weight=1)
        self.new_window.minsize(640, 340)
        self.new_window.geometry("920x540")
        self.new_window.configure(padx=10, pady=10) 

        self.icon_browse = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'browse.png'))
        self.icon_config = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'config.png'))
        self.icon_download = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'download.png'))

        # column 0
        self.label_work_dir = tk.Label(self.new_window, text="Directory")
        self.label_work_dir.grid(row=0, column=0, sticky=tk.W, pady = (0, defs.PAD_V))

        self.btn_config = tk.Button(self.new_window, image=self.icon_config, width=15,height=15,relief=tk.FLAT ,cursor='hand2',command=self.open_config )
        self.btn_config.grid(row=0, column=2, sticky=tk.E, pady = (0, defs.PAD_V))

        self.frame_work_dir = tk.Frame(self.new_window)
        self.frame_work_dir.grid(row=1, column=0, rowspan=2, columnspan=3, sticky=tk.EW, pady = (0, defs.PAD_V))

        self.btn_change_work_dir = tk.Button(self.frame_work_dir, image=self.icon_browse, relief=tk.FLAT, cursor='hand2', command=self.change_working_directory)
        self.btn_change_work_dir.pack(side="left", padx = (0, defs.PAD_H))

        self.entry_work_dir = tk.Entry(self.frame_work_dir, width=10)
        self.entry_work_dir.pack(fill=tk.X, expand=True)
        self.entry_work_dir.bind("<KeyRelease>", self.on_update_directory)

        self.label_url = tk.Label(self.new_window, text="Url")
        self.label_url.grid(row=3, column=0, sticky=tk.W)

        self.url_frame = tk.Frame(self.new_window)
        self.url_frame.grid(row=4, column=0, columnspan=3, sticky=tk.EW, pady = (0, defs.PAD_V))
        
        self.entry_url = tk.Entry(self.url_frame, width=10)
        self.entry_url.pack(side='left', fill=tk.X, expand=True)
        self.entry_url.bind("<KeyRelease>", self.on_url_changed)

        self.btn_fetch_data = tk.Button(self.url_frame, text="Get", cursor='hand2', command=self.get_data_from_url, anchor='n')
        self.btn_fetch_data.pack(side=tk.LEFT, padx=(defs.PAD_H, defs.PAD_H))

        self.btn_open_web = tk.Button(self.url_frame, text="Open", cursor='hand2', command=self.open_url, anchor='n')
        self.btn_open_web.pack(side=tk.LEFT)

        self.label_mod_name = tk.Label(self.new_window, text="Mod Title")
        self.label_mod_name.grid(row=5, column=0, sticky=tk.W)

        self.entry_mod_name = tk.Entry(self.new_window, width=10)
        self.entry_mod_name.grid(row=6, column=0, sticky=tk.EW, padx = (0, defs.PAD_H), pady = (0, defs.PAD_V))
        self.entry_mod_name.bind("<KeyRelease>", self.on_entry_change)


        self.label_authors = tk.Label(self.new_window, text="Authors")
        self.label_authors.grid(row=7, column=0, sticky=tk.W)

        self.entry_authors = tk.Entry(self.new_window, width=10)
        self.entry_authors.grid(row=8, column=0, sticky=tk.EW, padx = (0, defs.PAD_H), pady = (0, defs.PAD_V))

        self.frame = tk.Frame(self.new_window)
        self.frame.grid(row=9, column=0, rowspan=2, sticky=tk.EW, padx = (0, defs.PAD_H), pady = (0, defs.PAD_V))
        self.frame.columnconfigure(1, weight=1)

        self.label_ver = tk.Label(self.frame, text="Version")
        self.label_ver.grid(row=0, column=0, sticky=tk.W)

        self.entry_ver = tk.Entry(self.frame, width=10)
        self.entry_ver .grid(row=1, column=0, sticky=tk.W, padx=(0,defs.PAD_H))
        self.entry_ver.insert(0, "1.0.0")

        self.label_cat = tk.Label(self.frame, text="Category")
        self.label_cat.grid(row=0, column=1, sticky=tk.W)

        self.combobox_cat = ttk.Combobox(self.frame, values=defs.CATEGORIES, width=10)
        self.combobox_cat.grid(row=1, column=1, sticky=tk.EW)
        self.combobox_cat.bind("<<ComboboxSelected>>", self.on_combobox_select)
        self.combobox_cat.set(defs.CATEGORIES[-1])

        self.label_img_dir = tk.Label(self.new_window, text="Image", anchor='w')
        self.label_img_dir.grid(row=11, column=0, sticky=tk.W, padx = (0, defs.PAD_H))

        self.frame_img = tk.Frame(self.new_window, width=10)
        self.frame_img.grid(row=12, column=0, sticky=tk.NSEW, padx = (0, defs.PAD_H), pady = (0, defs.PAD_V))

        self.frame_img_dir = tk.Frame(self.frame_img, width = 10)
        self.frame_img_dir.pack(side=tk.TOP, fill=tk.X, expand=False, pady = (0, defs.PAD_V))

        self.btn_select_img = tk.Button(self.frame_img_dir, image=self.icon_browse, relief=tk.FLAT, cursor='hand2', command=self.update_image, anchor='n')
        self.btn_select_img.pack(side=tk.LEFT, padx = (0, defs.PAD_H))

        self.entry_img_dir = tk.Entry(self.frame_img_dir, width=10)
        self.entry_img_dir.pack(fill=tk.X, expand=True)
        self.entry_img_dir.bind("<KeyRelease>", self.on_update_image)

        fr_img_download = tk.Frame(self.frame_img)
        fr_img_download.pack(side=tk.BOTTOM, anchor=tk.NW, fill='x')

        self.replace_img_state = tk.IntVar()  # Use IntVar for 1 (checked) or 0 (unchecked)
        self.ckbox_replace_img = tk.Checkbutton(fr_img_download, text="replace with", relief=tk.FLAT, cursor="hand2", command=self.on_img_replace_changed, state="disabled", variable=self.replace_img_state)
        self.ckbox_replace_img.pack(side=tk.LEFT, anchor=tk.NW, padx = (0, defs.PAD_H))

        self.cbox_img = ttk.Combobox(fr_img_download, width=10, state="disabled")
        self.cbox_img.pack(side=tk.LEFT, anchor=tk.NW, expand=True, fill='x')
        self.cbox_img.bind("<<ComboboxSelected>>", self.on_img_url_selected)

        self.label_img = tk.Label(self.frame_img, justify='center', anchor='center', bg='black')
        self.label_img.pack(fill=tk.BOTH, expand=True)

        # column 1
        self.label_char_names = tk.Label(self.new_window, text="Characters")
        self.label_char_names.grid(row=5, column=1, sticky=tk.W)

        self.entry_char_names = tk.Entry(self.new_window, width=10)
        self.entry_char_names.grid(row=6, column=1, sticky=tk.EW, padx = (0, defs.PAD_H), pady = (0, defs.PAD_V))
        self.entry_char_names.bind("<KeyRelease>", self.on_entry_change)

        self.label_slots = tk.Label(self.new_window, text="Slots")
        self.label_slots.grid(row=7, column=1, sticky=tk.W)

        self.entry_slots = tk.Entry(self.new_window, width=10)
        self.entry_slots.grid(row=8, column=1, sticky=tk.EW, padx = (0, defs.PAD_H), pady = (0, defs.PAD_V))
        self.entry_slots.bind("<KeyRelease>", self.on_entry_change)

        self.l_wifi_safe = tk.Label(self.new_window, text="Wifi-Safe")
        self.l_wifi_safe.grid(row=9, column=1, sticky=tk.W)
    
        self.cbox_wifi_safe = ttk.Combobox(self.new_window, width=10, values=["Uncertain", "Safe", "Not Safe"])
        self.cbox_wifi_safe.grid(row=10, column=1, sticky=tk.EW, padx = (0, defs.PAD_H), pady = (0, defs.PAD_V))
        self.cbox_wifi_safe.set("Uncertain")
        # self.cbox_wifi_safe.bind("<<ComboboxSelected>>", self.on_img_url_selected)

        self.label_list = tk.Label(self.new_window, text="Includes")
        self.label_list.grid(row=11, column=1, sticky=tk.W)

        self.listbox = tk.Listbox(self.new_window, selectmode=tk.SINGLE, width=10)
        self.listbox.grid(row=12, column=1, sticky=tk.NSEW, padx = (0, defs.PAD_H), pady = (0, defs.PAD_V))

        # column 2
        self.label_folder_name = tk.Label(self.new_window, text="Folder Name")
        self.label_folder_name .grid(row=5, column=2, sticky=tk.W)

        self.entry_folder_name = tk.Entry(self.new_window)
        self.entry_folder_name.grid(row=6, column=2, sticky=tk.EW, pady = (0, defs.PAD_V))

        self.label_display_name = tk.Label(self.new_window, text="Display Name")
        self.label_display_name.grid(row=7, column=2, sticky=tk.W)

        self.entry_display_name = tk.Entry(self.new_window, width=10)
        self.entry_display_name.grid(row=8, column=2, sticky=tk.EW, pady = (0, defs.PAD_V))

        self.label_desc = tk.Label(self.new_window, text="Description")
        self.label_desc.grid(row=11, column=2, sticky=tk.W)

        self.txt_desc = tk.Text(self.new_window, height=10, width=10)
        self.txt_desc.grid(row=12, column=2, sticky=tk.NSEW, pady = (0, defs.PAD_V))

        self.frame_btn = tk.Frame(self.new_window)
        self.frame_btn.grid(row=13, column=2, sticky=tk.E, pady = (0, defs.PAD_V))

        self.btn_compare = tk.Button(self.frame_btn, text="Compare", command=self.open_comparison)
        self.btn_compare.pack(side='left', fill="y", padx=(0, defs.PAD_H))

        self.btn_apply = tk.Button(self.frame_btn, text="Apply", command=self.apply_changes)
        self.btn_apply.pack(fill="y")

        self.label_output = tk.Label(self.new_window)
        self.label_output .grid(row=13, column=0, sticky=tk.W, columnspan=2)

        self.checkbox_states = [False] * len(defs.ELEMENTS + self.config.additional_elements)
        self.update_listbox()
        self.listbox.bind("<Button-1>", lambda event: self.toggle_checkbox(self.listbox.nearest(event.y)))

        self.new_window.bind("<Configure>", self.on_window_resize)

        self.entry_work_dir.delete(0, tk.END)
        if working_dir:
            self.entry_work_dir.insert(tk.END, working_dir)
            self.update_preview()
