"""
comparison.py: View for comparing changes to the info.toml file
"""
from PIL import Image, ImageTk

import tkinter as tk
from tkinter import ttk
from src.constants.ui_params import PAD_H, PAD_V
from src.constants.categories import CATEGORIES
from src.constants.colors import LIGHT_GREEN, WHITE
from src.models.mod import Mod
from src.utils.file import get_base_name
from src.ui.base import set_text
from src.utils.image_handler import ImageHandler

IMG_SIZE_X = 300
IMG_SIZE_Y = 160

class Comparison:
    def __init__(self):
        self.new_window = None
        self.src = None
        self.dst = None
        self.reset()

    def reset(self):
        """
        Resets differences
        """
        self.folder_name_changed = False
        self.mod_name_changed = False
        self.display_name_changed = False
        self.slot_changed = False
        self.category_changed = False
        self.version_changed = False
        self.description_changed = False
        self.author_changed = False
        self.url_changed = False
        self.wifi_safe_changed = False
        self.character_changed = False
        self.includes_changed = False
        self.thumbnail_changed = False

    def init_column(self, frame, mod:Mod, is_current:bool=False):
        """
        Initializes column (previous/new)
        """
        row = 0
        folder_name = tk.Label(frame, text="Folder Name")
        folder_name.grid(row=row, column=0, sticky=tk.W)
        
        row +=1
        folder_name_entry = tk.Entry(frame, width=10)
        folder_name_entry.grid(row=row, column=0, sticky=tk.EW, pady = (0, PAD_V))
        set_text(folder_name_entry, get_base_name(mod.folder_name))
        
        row +=1
        display_name = tk.Label(frame, text="Display Name")
        display_name.grid(row=row, column=0, sticky=tk.W)
        
        row +=1
        display_name_entry = tk.Entry(frame, width=10)
        display_name_entry.grid(row=row, column=0, sticky=tk.EW, pady = (0, PAD_V))
        set_text(display_name_entry, mod.display_name)

        row +=1
        mod_name = tk.Label(frame, text="Mod Name")
        mod_name.grid(row=row, column=0, sticky=tk.W)
        row +=1
        mod_name_entry = tk.Entry(frame, width=10)
        mod_name_entry.grid(row=row, column=0, sticky=tk.EW, pady = (0, PAD_V))
        set_text(mod_name_entry, mod.mod_name)

        row +=1
        character = tk.Label(frame, text="Character(s)")
        character.grid(row=row, column=0, sticky=tk.W)
        row +=1
        character_entry = tk.Entry(frame, width=10)
        character_entry.grid(row=row, column=0, sticky=tk.EW, pady = (0, PAD_V))
        set_text(character_entry, mod.character)

        row +=1
        authors = tk.Label(frame, text="Authors")
        authors.grid(row=row, column=0, sticky=tk.W)
        row +=1
        authors_entry = tk.Entry(frame, width=10)
        authors_entry.grid(row=row, column=0, sticky=tk.EW, pady = (0, PAD_V))
        set_text(authors_entry, mod.authors)

        group = tk.Frame(frame)
        row +=1
        group.grid(row=row, column=0, sticky=tk.NSEW)
        group.columnconfigure(0, weight=3)
        group.columnconfigure(1, weight=7)
        group.rowconfigure(3, weight=1)

        version = tk.Label(group, text="Version")
        version.grid(row=0, column=0, sticky=tk.W)

        version_entry = tk.Entry(group, width=10)
        version_entry.grid(row=1, column=0, sticky=tk.EW, pady = (0, PAD_V))
        set_text(version_entry, mod.version)

        category = tk.Label(group, text="Category")
        category.grid(row=0, column=1, sticky=tk.W)

        category_entry = tk.Entry(group, width=10)
        category_entry.grid(row=1, column=1, sticky=tk.EW, pady = (0, PAD_V))
        set_text(category_entry, mod.category)

        description = tk.Label(group, text="Description")
        description.grid(row=2, column=0, columnspan=2, sticky=tk.W)

        description_text = tk.Text(group, height=10, width=10)
        description_text.grid(row=3, column=0, columnspan=2, sticky=tk.NSEW)
        set_text(description_text, mod.description)
        
        frame.rowconfigure(row, weight=1)

        if is_current:
            folder_name_entry.config(bg=LIGHT_GREEN if self.folder_name_changed else WHITE)
            mod_name_entry.config(bg=LIGHT_GREEN if self.mod_name_changed else WHITE)
            display_name_entry.config(bg=LIGHT_GREEN if self.display_name_changed else WHITE)
            character_entry.config(bg=LIGHT_GREEN if self.character_changed else WHITE)
            authors_entry.config(bg=LIGHT_GREEN if self.author_changed else WHITE)
            version_entry.config(bg=LIGHT_GREEN if self.version_changed else WHITE)
            category_entry.config(bg=LIGHT_GREEN if self.category_changed else WHITE)
            description_text.config(bg=LIGHT_GREEN if self.description_changed else WHITE)

    def find_differences(self):
        """
        Finds differences to highlight
        """
        self.reset()
        self.folder_name_changed = self.src.folder_name != self.dst.folder_name
        self.mod_name_changed = self.src.mod_name != self.dst.mod_name
        self.display_name_changed = self.src.display_name != self.dst.display_name
        self.slot_changed = self.src.character_slots != self.dst.character_slots
        self.category_changed = self.src.category != self.dst.category
        self.version_changed = self.src.version != self.dst.version
        self.description_changed = self.src.description != self.dst.description
        self.author_changed = self.src.authors != self.dst.authors
        self.url_changed = self.src.url != self.dst.url
        self.wifi_safe_changed = self.src.wifi_safe != self.dst.wifi_safe
        self.character_changed = self.src.character != self.dst.character
        self.includes_changed = self.src.includes != self.dst.includes
        self.thumbnail_changed = self.src.thumbnail != self.dst.thumbnail

    def open(self, root, src:Mod, dst:Mod):
        """
        Shows comparison view
        """
        blank_image = Image.new('RGB', (IMG_SIZE_X, IMG_SIZE_Y), color='black')
        blank_image_tk = ImageTk.PhotoImage(blank_image)

        self.src = src
        self.dst = dst
        if self.new_window is not None:
            self.new_window.destroy()

        self.new_window = tk.Toplevel(root)
        self.new_window.title("Comparison")

        self.new_window.columnconfigure(0, weight=1)
        self.new_window.columnconfigure(0, minsize=200)
        self.new_window.columnconfigure(2, weight=1)
        self.new_window.columnconfigure(2, minsize=200)

        self.new_window.rowconfigure(2, weight=1)
        self.new_window.minsize(640, 500)

        # Set the size of the window
        self.new_window.geometry("640x600")
        self.new_window.configure(padx=10, pady=10)

        self.find_differences()

        prev_title = tk.Label(self.new_window, text="Previous", font='Helvetica 10 bold')
        prev_title.grid(row=0, column=0, sticky=tk.W)
        self.prev_img_label = tk.Label(self.new_window, bg="black", width=IMG_SIZE_X, height=IMG_SIZE_Y)
        self.prev_img_label.grid(row=1, column=0, sticky=tk.NSEW)
        prev_frame = tk.Frame(self.new_window)
        prev_frame.grid(row=2, column=0, sticky=tk.NSEW)
        prev_frame.columnconfigure(0, weight=1)

        spacing = tk.Label(self.new_window, width=1, height=10)
        spacing.grid(row=0, rowspan=3, column=1, sticky=tk.EW)

        current_title = tk.Label(self.new_window, text="Current", font='Helvetica 10 bold')
        current_title.grid(row=0, column=2, sticky=tk.W)
        self.current_img_label = tk.Label(self.new_window, bg="black", width=IMG_SIZE_X, height=IMG_SIZE_Y)
        self.current_img_label.grid(row=1, column=2, sticky=tk.NSEW)
        current_frame = tk.Frame(self.new_window)
        current_frame.grid(row=2, column=2, sticky=tk.NSEW)
        current_frame.columnconfigure(0, weight=1)
        self.init_column(prev_frame, self.src)
        self.init_column(current_frame, self.dst, True)


        self.prev_img_label.config(image=blank_image_tk, width=IMG_SIZE_X, height=IMG_SIZE_Y)
        self.prev_img_label.image = blank_image_tk
        self.current_img_label.config(image=blank_image_tk, width=IMG_SIZE_X, height=IMG_SIZE_Y)
        self.current_img_label.image = blank_image_tk
        directories = [self.src.thumbnail, self.dst.thumbnail] if self.thumbnail_changed else [self.src.thumbnail]
        
        if True in [True for d in directories if d]:
            ImageHandler(
                directories,
                IMG_SIZE_X,
                IMG_SIZE_Y,
                self.on_img_load,
                True
            )

    def on_img_load(self, thumbnails):
        self.prev_img_label.config(image=thumbnails[0], width=IMG_SIZE_X, height=IMG_SIZE_Y)
        self.prev_img_label.image = thumbnails[0]
        if len(thumbnails) > 1:
            self.current_img_label.config(image=thumbnails[1], width=IMG_SIZE_X, height=IMG_SIZE_Y)
            self.current_img_label.image = thumbnails[1]
        else:
            self.current_img_label.config(image=thumbnails[0], width=IMG_SIZE_X, height=IMG_SIZE_Y)
            self.current_img_label.image = thumbnails[0]
