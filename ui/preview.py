from tkinter import ttk
from PIL import ImageTk
import tkinter as tk
from defs import PAD_H, PAD_V
from . import PATH_ICON
from .common_ui import get_text, set_text, set_enabled, clear_text
from utils.image_resize import ImageResize
from utils.loader import Loader
import os

class Preview:
    def __init__(self, root, edit_callback=None, open_callback=None, toggle_callback=None) -> None:
        self.root = root
        self.edit_callback = edit_callback 
        self.open_callback = open_callback
        self.toggle_callback = toggle_callback
        self.show()

    def show(self):
        self.top_frame = tk.Frame(self.root)
        self.top_frame.grid(row=0, padx=PAD_H, pady=(PAD_V/2, 0), sticky=tk.NSEW)
        
        self.label_title = tk.Label(self.top_frame, width=10, justify="left", anchor='w')
        self.label_title.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        separator = ttk.Separator(self.top_frame, orient='vertical')
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=PAD_H)

        self.icon_on = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'on.png'))
        self.icon_off = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'off.png'))
        self.btn_toggle = tk.Button(self.top_frame, image=self.icon_off, text="Disabled ", cursor='hand2', compound="right", relief=tk.FLAT, borderwidth=0, command=self.toggle_callback, width=84, anchor='e', font=("None", 10, "bold"))
        self.btn_toggle.pack(side=tk.RIGHT, fill=tk.X)
    
        self.label_img = tk.Label(self.root, bg="black")
        self.label_img.grid(row=1, padx=PAD_H, pady=(PAD_V, 0), sticky=tk.NSEW)

        info_frame = tk.Frame(self.root)
        info_frame.grid(row=2, padx=PAD_H, pady=(0, PAD_V), sticky=tk.NSEW)

        self.label_version = tk.Label(info_frame, anchor="w", justify="left")
        self.label_version.pack(side=tk.LEFT)

        self.label_author = tk.Label(info_frame, anchor="e", justify="right", width=1)
        self.label_author.pack(side=tk.RIGHT, fill="x", expand=True)

        label_d = tk.Label(self.root, text="Description", anchor="w", justify="left")
        label_d.grid(row=3, padx=PAD_H, sticky=tk.W)

        self.label_desc = tk.Text(self.root, height=1, width=10, state="disabled")
        self.label_desc.grid(row=4, padx=PAD_H, pady=(0, PAD_V), sticky=tk.NSEW)

        frame_actions = tk.Frame(self.root)
        frame_actions.grid(row=5, padx=PAD_H, pady=(0, PAD_V), sticky=tk.EW)
        frame_actions.columnconfigure(index=0, weight=1, uniform="equal")
        frame_actions.columnconfigure(index=2, weight=1, uniform="equal")
        frame_actions.columnconfigure(index=4, weight=1, uniform="equal")

        frame_actions.rowconfigure(index=0, weight=1)

        self.icon_edit = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'edit.png'))
        self.btn_edit = tk.Button(frame_actions, image=self.icon_edit, text=" Edit", cursor='hand2', relief=tk.FLAT, compound="left", command=self.edit_callback)
        self.btn_edit.grid(row=0, column=0, sticky=tk.EW, padx=(0, PAD_H/2))

        separator = ttk.Separator(frame_actions, orient='vertical')
        separator.grid(row=0, column=1, padx=PAD_H/2, sticky=tk.NS)

        self.icon_open = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'open.png'))
        self.btn_open = tk.Button(frame_actions, image=self.icon_open, text=" Open", cursor='hand2', relief=tk.FLAT, compound="left", command=self.open_callback)
        self.btn_open.grid(row=0, column=2, sticky=tk.EW, padx=PAD_H/2)

        separator = ttk.Separator(frame_actions, orient='vertical')
        separator.grid(row=0, column=3, padx=PAD_H/2, sticky=tk.NS)

        self.icon_close = ImageTk.PhotoImage(file=os.path.join(PATH_ICON, 'close.png'))
        self.btn_close = tk.Button(frame_actions, image=self.icon_close, text=" Close", cursor='hand2', relief=tk.FLAT, compound="left", width=2, command=self.close_callback)
        self.btn_close.grid(row=0, column=4, sticky=tk.EW, padx=(PAD_H/2, 0))

    def update(self, is_enabled:bool, loader:Loader, path:str):
        self.set_toggle_label(is_enabled)
        set_enabled(self.label_desc, True)
        self.label_desc.delete(1.0, tk.END)
        
        if loader is not None: 
            set_text(self.label_desc, loader.description)
            self.label_version.config(text=loader.version, width=5)
            self.label_author.config(text=loader.authors, width=1)
            self.label_title.config(text=loader.display_name)
        else: 
            set_text(self.label_desc, "No info.toml found")

        set_enabled(self.label_desc, False)
        img_preview = os.path.join(path, "preview.webp")

        if os.path.exists(img_preview):
            self.set_image(img_preview)
        else:
            self.label_img.image = ""
            self.label_version.config(text="")
            self.label_author.config(text="")
            self.label_title.config(text="")

        set_enabled(self.btn_edit)
        set_enabled(self.btn_open)
        set_enabled(self.btn_toggle)

    def close_callback(self):
        self.root.pack_forget()

    def on_img_resized(self, image):
        self.label_img.config(image=image, width=10, height=10)
        self.label_img.image = image  # Keep a reference to prevent garbage collection

    def clear(self):
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
        # self.close_callback()

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
        if not directory or not os.path.exists(directory):
            return
        
        resize_thread = ImageResize(directory, self.label_img.winfo_width(), self.label_img.winfo_height(), self.on_img_resized)
        resize_thread.start()