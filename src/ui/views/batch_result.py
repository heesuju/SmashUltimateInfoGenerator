import os
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import tkinter as tk
from src.constants.ui_params import PAD_H, PAD_V
from assets import ICON_PATH
from src.core.data import load_config, generate_batch, get_characters
from src.constants.categories import CATEGORIES
from src.constants.defs import IMAGE_TYPES, WIFI_TYPES
from src.constants.elements import ELEMENTS
from src.utils.image_handler import ImageHandler
from src.core.filter import sort_by_columns
from src.core.formatting import (
    format_character_names,
    format_slots
)
from src.models.mod import Mod
from src.ui.components.popup import Popup
from src.ui.base import (
    RowCount, 
    add_entry,
    add_text,
    set_text,
    add_treeview,
    update_treeview, 
    get_treeview_checked,
    set_image
)
from src.ui.components.checkbox_treeview import Treeview

IMG_SIZE_X = 300
IMG_SIZE_Y = 160

COLUMNS = [
    "Category",
    "Character",
    "Slot",
    "Mod Name",
    "Author",
    "Version",
    "URL",
    "Folder Name",
    "Display Name",
    "Wifi-Safe",
    "Thumbnail",
    "Elements"
]

class BatchResult(Popup):
    def __init__(self, root=None, mods:list[Mod] = []):
        super().__init__(root, "Batch Generation", 800, 800, True)
        sort_priority = load_config().sort_priority
        if sort_priority is not None:
            self.mods = sort_by_columns(mods, sort_priority)
        else:
            self.mods = mods
        self.total_count = tk.IntVar()
        self.selected_count = tk.IntVar()
        self.treeview = None
        self.description = None
        self.category_var:tk.StringVar = tk.StringVar()
        self.mod_name_var:tk.StringVar = tk.StringVar()
        self.authors_var:tk.StringVar = tk.StringVar()
        self.version_var:tk.StringVar = tk.StringVar()
        self.url_var:tk.StringVar = tk.StringVar()
        self.folder_var:tk.StringVar = tk.StringVar()
        self.display_var:tk.StringVar = tk.StringVar()
        self.wifi_var:tk.StringVar = tk.StringVar()
        self.desc_var:tk.StringVar = tk.StringVar()
        self.image_dir_var:tk.StringVar = tk.StringVar()
        self.desc_var.trace_add("write", lambda *args: set_text(self.description, self.desc_var.get()))

        self.show(self.root)

    def set_values(self, mod:Mod):
        """
        Sets mod values
        """
        self.url_var.set(mod.url)
        self.mod_name_var.set(mod.mod_name)
        self.authors_var.set(mod.authors)
        self.version_var.set(mod.version)
        keys, names, groups, series, slots = mod.get_character_data()
        self.folder_var.set(mod.folder_name)
        self.display_var.set(mod.display_name)
        self.category_var.set(mod.category)
        self.wifi_var.set(mod.wifi_safe)
        self.desc_var.set(mod.description)
        self.image_dir_var.set(mod.thumbnail)

    def show(self, root):
        super().show(root)
        self.count_frame = tk.Frame(self.new_window)
        self.count_frame.pack(side=tk.TOP, fill=tk.X)

        self.label_total = tk.Label(self.count_frame, text="0", anchor=tk.W, textvariable=self.total_count)
        self.label_total.pack(side=tk.RIGHT)
        
        self.selected_label = tk.Label(self.count_frame, text="Total:", anchor=tk.W)
        self.selected_label.pack(side=tk.RIGHT)

        self.frame = tk.Frame(self.new_window)
        self.frame.pack(fill="both", expand=True)

        self.treeview = Treeview(self.frame, True)
        self.treeview.construct(COLUMNS)
        self.treeview.widget.pack(side=tk.LEFT, fill="both", expand=True)
        self.treeview.widget.bind('<<TreeviewSelect>>', self.on_item_selected)
# -------------------------------------------------------------------------------------
        self.info_frame = tk.Frame(self.frame)
        self.info_frame.pack(side=tk.RIGHT, fill=tk.BOTH)
        
        row = RowCount()

        self.label_img = tk.Label(self.info_frame, image=None, bg="black", width=36, height=10)
        blank_image = Image.new('RGB', (IMG_SIZE_X, IMG_SIZE_Y), color='black')
        blank_image_tk = ImageTk.PhotoImage(blank_image)
        self.label_img.config(image=blank_image_tk, width=IMG_SIZE_X, height=IMG_SIZE_Y)
        self.label_img.image = blank_image_tk
        
        self.label_img.grid(row=row.get_row(), column=0, columnspan=2, pady=(PAD_V, 0), sticky=tk.EW)
        self.display_name_entry = add_entry(self.info_frame, "Display Name", self.display_var, row)
        self.folder_name_entry = add_entry(self.info_frame, "Folder Name", self.folder_var, row)        
        self.url_entry = add_entry(self.info_frame, "URL", self.url_var, row)
        self.combobox_cat = add_entry(self.info_frame, "Category", self.category_var, row, CATEGORIES)
        self.mod_name_entry = add_entry(self.info_frame, "Mod Name", self.mod_name_var, row)
        self.author_entry = add_entry(self.info_frame, "Authors", self.authors_var, row)
        self.version_entry = add_entry(self.info_frame, "Version", self.version_var, row)
        self.wifi_combobox = add_entry(self.info_frame, "Wifi-Safe", self.wifi_var, row, WIFI_TYPES)
        self.description = add_text(self.info_frame, "Description", row)
        self.characters = add_treeview(self.info_frame, "Characters", row, get_characters())
        self.slots = add_treeview(self.info_frame, "Slots", row, range(255))
        self.elements = add_treeview(self.info_frame, "Elements", row, ELEMENTS)
        
        self.footer = tk.Frame(self.new_window)
        self.footer.pack(pady=(PAD_V, PAD_V/2), fill="x")

        self.icon_export = ImageTk.PhotoImage(file=os.path.join(ICON_PATH, 'close.png'))
        

        self.find_url_btn = tk.Button(self.footer, image=self.icon_export, relief=tk.FLAT, compound="left", text="Find URL", cursor='hand2', command=self.on_apply)
        self.find_url_btn.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)

        self.generate_btn = tk.Button(self.footer, image=self.icon_export, relief=tk.FLAT, compound="left", text="Generate", cursor='hand2', command=self.on_apply)
        self.generate_btn.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)
        
        self.update()

    def update(self):
        if self.treeview is not None:
            for mod in self.mods:
                self.add_item(mod)  

        self.total_count.set(len(self.mods))

    def update_mod(self):
        idx = self.treeview.get_selected_index()
        if len(self.mods) > idx:
            self.mods[idx].display_name = self.display_var.get()
            self.mods[idx].folder_name = self.folder_var.get()
            self.mods[idx].url = self.url_var.get()
            self.mods[idx].category = self.category_var.get()
            self.mods[idx].mod_name = self.mod_name_var.get()
            self.mods[idx].authors = self.authors_var.get()
            self.mods[idx].version = self.version_var.get()
            self.mods[idx].description = self.desc_var.get()
            self.mods[idx].wifi_safe = self.wifi_var.get()
            set_text(self.description, self.desc_var.get())

    def add_item(self, mod:Mod, checked:bool=True):
        if self.treeview is not None:
            keys, names, groups, series, slots = mod.get_character_data()
            characters = format_character_names(names)
            slots = format_slots(slots)
            self.treeview.add_item([mod.category, characters, slots, mod.mod_name, mod.authors, mod.version, mod.url, mod.folder_name, mod.display_name, mod.wifi_safe, mod.thumbnail, ", ".join(mod.includes)], checked)

    def on_item_selected(self, event:tk.Event = None):
        self.treeview.on_row_select(event)
        idx = self.treeview.get_selected_index()
        if len(self.mods) > idx:
            self.set_values(self.mods[idx])
            if self.mods[idx].thumbnail:
                set_image(self.mods[idx].thumbnail, IMG_SIZE_X, IMG_SIZE_Y, self.on_img_resized)
            else:
                blank_image = Image.new('RGB', (IMG_SIZE_X, IMG_SIZE_Y), color='black')
                blank_image_tk = ImageTk.PhotoImage(blank_image)
                self.label_img.config(image=blank_image_tk, width=IMG_SIZE_X, height=IMG_SIZE_Y)
                self.label_img.image = blank_image_tk

            update_treeview(self.characters, [character.custom for character in self.mods[idx].characters])
            slots = []
            for character in self.mods[idx].characters:
                for slot in character.slots:
                    if slot not in slots:
                        slots.append(slot)
            
            update_treeview(self.slots, slots)
            update_treeview(self.elements, self.mods[idx].includes)

    def on_img_resized(self, image):
        if self.new_window.winfo_exists() == False:
            return
        
        if self.is_running:
            self.label_img.config(image=image, width=IMG_SIZE_X, height=IMG_SIZE_Y)
            self.label_img.image = image

    def on_apply(self):
        pass