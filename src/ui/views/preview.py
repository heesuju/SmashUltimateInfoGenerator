"""
preview.py: A panel that can be toggled from the main menu to show a preview of the mod
"""

import os
from tkinter import ttk
import tkinter as tk
from src.constants.ui_params import PAD_H, PAD_V
from src.ui.base import set_text, set_enabled, clear_text, get_icon
from src.utils.file import get_base_name, is_valid_dir, is_valid_file, get_parent_dir
from src.utils.image_handler import ImageHandler
from src.constants.colors import DEFAULT, WHITE
from src.core.hide_folder import hide_folder, is_hidden
from src.models.mod import Mod

IMG_SIZE_X = 334
IMG_SIZE_Y = 190

class Preview:
    """
    UI class for previewing mod information
    """
    def __init__(
            self,
            root:tk.Frame,
            edit_callback:callable=None,
            open_callback:callable=None,
            toggle_callback:callable=None,
            hide_callback:callable=None
        ) -> None:

        self.root = root
        self.edit_callback = edit_callback
        self.open_callback = open_callback
        self.toggle_callback = toggle_callback
        self.hide_callback = hide_callback
        self.is_shown = False
        self.is_desc_shown = True
        self.is_incl_shown = False
        self.mod = None
        self.icon_on = get_icon("on")
        self.icon_off = get_icon("off")
        self.icon_edit = get_icon("edit")
        self.icon_open = get_icon("open")
        self.icon_visible = get_icon("visible")
        self.icon_invisible = get_icon("invisible")
        self.icon_hide = get_icon("open")
        self.show()

    def show(self):
        self.top_frame = tk.Frame(self.root)
        self.top_frame.grid(row=0, padx=PAD_H, pady=(PAD_V/2, 0), sticky=tk.NSEW)

        separator = ttk.Separator(self.root, orient='vertical')
        separator.grid(row=0, column=4, rowspan=5, sticky=tk.NS)

        self.label_title = tk.Label(self.top_frame, width=10, justify="left", anchor='w')
        self.label_title.pack(side=tk.LEFT, fill=tk.X, expand=True)

        separator = ttk.Separator(self.top_frame, orient='vertical')
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=PAD_H)

        self.btn_toggle = tk.Button(self.top_frame, image=self.icon_off, text="Disabled ", cursor='hand2', compound="right", relief=tk.FLAT, borderwidth=0, command=self.toggle_callback, width=84, anchor='e', font=("None", 10, "bold"))
        self.btn_toggle.pack(side=tk.RIGHT, fill=tk.X)

        self.label_img = tk.Label(self.root, bg="black", width=IMG_SIZE_X, height=IMG_SIZE_Y)
        self.label_img.grid(row=1, padx=PAD_H, pady=(PAD_V, 0), sticky=tk.NSEW)

        info_frame = tk.Frame(self.root)
        info_frame.grid(row=2, padx=PAD_H, pady=(0, PAD_V), sticky=tk.NSEW)

        self.label_version = tk.Label(info_frame, anchor="w", justify="left")
        self.label_version.pack(side=tk.LEFT)

        self.label_author = tk.Label(info_frame, anchor="e", justify="right", width=1)
        self.label_author.pack(side=tk.RIGHT, fill="x", expand=True)

        self.frame_details = tk.Frame(self.root, borderwidth=1, relief='ridge')
        self.frame_details.grid(row=3, padx=PAD_H, pady=(0, PAD_V), sticky=tk.NSEW)
        self.frame_details.rowconfigure(index=2, weight=1)
        self.frame_details.columnconfigure(index=0, weight=1, uniform="equal")
        self.frame_details.columnconfigure(index=2, weight=1, uniform="equal")
        self.btn_desc = tk.Button(self.frame_details, text="Description", relief=tk.FLAT, background=DEFAULT, font=("Helvetica", 10, "bold"), command=self.on_show_desc, cursor="hand2")
        self.btn_desc.grid(row=0, column=0, sticky=tk.EW)
        separator = ttk.Separator(self.frame_details, orient='vertical')
        separator.grid(row=0, column=1, sticky=tk.NS)
        
        self.btn_incl = tk.Button(self.frame_details, text="Includes", relief=tk.FLAT, background="#dcdcdc", foreground="snow4", command=self.on_show_incl, cursor="hand2")
        self.btn_incl.grid(row=0, column=2, sticky=tk.EW)
        self.desc_separator = ttk.Separator(self.frame_details, orient='horizontal')
        self.desc_separator.grid(row=1, column=0, sticky=tk.EW)
        self.desc_separator.grid_forget()
        self.incl_separator = ttk.Separator(self.frame_details, orient='horizontal')
        self.incl_separator.grid(row=1, column=2, sticky=tk.EW)

        self.label_desc = tk.Text(self.frame_details, height=1, width=10, state="disabled", wrap="word")
        self.label_desc.grid(row=2, column=0, columnspan=3, sticky=tk.NSEW, padx=PAD_H, pady=PAD_V)

        frame_actions = tk.Frame(self.root)
        frame_actions.grid(row=4, padx=PAD_H, pady=(0, PAD_V), sticky=tk.EW)
        frame_actions.columnconfigure(index=0, weight=1, uniform="equal")
        frame_actions.columnconfigure(index=2, weight=1, uniform="equal")
        frame_actions.columnconfigure(index=4, weight=1, uniform="equal")

        frame_actions.rowconfigure(index=0, weight=1)

        
        self.btn_edit = tk.Button(frame_actions, image=self.icon_edit, text=" Edit", cursor='hand2', relief=tk.FLAT, compound="left", command=self.edit_callback, width=10)
        self.btn_edit.grid(row=0, column=0, sticky=tk.EW, padx=(0, PAD_H/2))

        separator = ttk.Separator(frame_actions, orient='vertical')
        separator.grid(row=0, column=1, padx=PAD_H/2, sticky=tk.NS)

        self.btn_open = tk.Button(frame_actions, image=self.icon_open, text=" Open", cursor='hand2', relief=tk.FLAT, compound="left", command=self.open_callback, width=10)
        self.btn_open.grid(row=0, column=2, sticky=tk.EW, padx=PAD_H/2)

        separator = ttk.Separator(frame_actions, orient='vertical')
        separator.grid(row=0, column=3, padx=PAD_H/2, sticky=tk.NS)
        
        self.btn_hide = tk.Button(frame_actions, image=self.icon_invisible, text=" Hide", cursor='hand2', relief=tk.FLAT, compound="left", command=self.on_hide_folder, width=10)
        self.btn_hide.grid(row=0, column=4, sticky=tk.EW, padx=PAD_H/2)

    def update(self, is_enabled:bool, mod:Mod):
        self.mod = mod
        path = self.mod.path
        self.set_toggle_label(is_enabled)

        title = ""

        if mod is not None: 
            self.label_version.config(text=mod.version, width=5)
            self.label_author.config(text=mod.authors, width=1)
            title = mod.display_name
        else: 
            clear_text(self.label_version)
            clear_text(self.label_author)

        if not title:
            title = get_base_name(path)

        set_text(self.label_title, title)
        self.set_description()

        img_preview = os.path.join(path, "preview.webp")

        if os.path.exists(img_preview):
            self.set_image(img_preview)
        else:
            self.label_img.image = ""
            self.label_version.config(text="")
            self.label_author.config(text="")

        is_hidden_item = is_hidden(get_base_name(path))
        if is_hidden_item:
            self.btn_hide.config(text=" Show", image=self.icon_visible)
        else:
            self.btn_hide.config(text=" Hide", image=self.icon_invisible)
        set_enabled(self.btn_edit)
        set_enabled(self.btn_open)
        set_enabled(self.btn_toggle)
        set_enabled(self.btn_hide)

    def on_img_resized(self, image):
        self.label_img.config(image=image, width=IMG_SIZE_X, height=IMG_SIZE_Y)
        self.label_img.image = image  # Keep a reference to prevent garbage collection

    def clear(self):
        self.mod = None
        set_enabled(self.label_desc)
        clear_text(self.label_desc)
        set_enabled(self.label_desc, False)
        self.label_img.image = ""
        clear_text(self.label_version)
        clear_text(self.label_author)
        clear_text(self.label_title)
        self.set_toggle_label(False)
        set_enabled(self.btn_edit, False)
        set_enabled(self.btn_open, False)
        set_enabled(self.btn_toggle, False)
        set_enabled(self.btn_hide, False)

    def on_hide_folder(self):
        path = self.mod.path
        if path:
            hide_folder(path)
            if self.hide_callback:
                self.hide_callback()

    def set_toggle_label(self, is_enabled:bool):
        if is_enabled:
            self.btn_toggle.config(image=self.icon_on, 
                                   text="Enabled ", 
                                   foreground="#3FB54D",
                                   activeforeground="#3FB54D",
                                   disabledforeground="#F5C0C0")
        else:
            self.btn_toggle.config(image=self.icon_off, 
                                   text="Disabled ", 
                                   foreground="#FF6363",
                                   activeforeground="#FF6363",
                                    disabledforeground="#F5C0C0")

    def set_image(self, directory):
        root_dir = get_parent_dir(directory)
        if is_valid_dir(root_dir) and is_valid_file(directory):
            ImageHandler(directory, width=IMG_SIZE_X, height=IMG_SIZE_Y, on_finish=self.on_img_resized)

    def toggle(self):
        """
        Toggles on/off preview panel
        """
        if self.is_shown:
            self.root.pack_forget()
        else:
            self.root.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)
            
        self.is_shown = False if self.is_shown else True

    def format_includes(self, includes:list):
        if includes is None:
            return ""
        return "\n".join([f"⁃ {i}" for i in includes])
    
    def clean_description(self, description:str):
        cleaned_text = description.strip('\n')
        return cleaned_text

    def on_show_desc(self):
        """
        Toggles on description
        """
        self.btn_desc.config(background=DEFAULT, font=("Helvetica", 10, "bold"), foreground="black")
        self.btn_incl.config(background="#dcdcdc", font=("Helvetica", 10), foreground="snow4")
        self.desc_separator.grid_forget()
        self.incl_separator.grid(row=1, column=2, sticky=tk.EW)
        self.is_desc_shown = True
        self.is_incl_shown = False
        self.set_description()

    def on_show_incl(self):
        """
        Toggles on included elements
        """
        self.btn_desc.config(background="#dcdcdc", font=("Helvetica", 10), foreground="snow4")
        self.btn_incl.config(background=DEFAULT, font=("Helvetica", 10, "bold"), foreground="black")
        self.desc_separator.grid(row=1, column=0, sticky=tk.EW)
        self.incl_separator.grid_forget()
        self.is_desc_shown = False
        self.is_incl_shown = True
        self.set_description()

    def set_description(self):
        """
        Handles description label
        """
        description = ""
        includes = []

        if self.mod is not None:
            description = self.mod.description
            includes = self.mod.includes

        if not description:
            description = "Description is empty\nClick 'Edit' to add one."

        set_enabled(self.label_desc)

        if self.is_desc_shown:
            set_text(self.label_desc, self.clean_description(description))
        else:
            set_text(self.label_desc, self.format_includes(includes))

        set_enabled(self.label_desc, False)
