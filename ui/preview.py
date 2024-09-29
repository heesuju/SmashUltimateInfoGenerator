from tkinter import ttk
from PIL import ImageTk
import tkinter as tk
from defs import PAD_H, PAD_V
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
        self.open()

    def open(self):
        self.label_img = tk.Label(self.root, bg="black")
        self.label_img.grid(row=0, padx=PAD_H, pady=(PAD_V, 0), sticky=tk.NSEW)

        info_frame = tk.Frame(self.root)
        info_frame.grid(row=1, padx=PAD_H, pady=(0, PAD_V), sticky=tk.NSEW)

        self.label_version = tk.Label(info_frame, anchor="w", justify="left")
        self.label_version.pack(side=tk.LEFT)

        self.label_author = tk.Label(info_frame, anchor="e", justify="right", width=1)
        self.label_author.pack(side=tk.RIGHT, fill="x", expand=True)

        label_d = tk.Label(self.root, text="Description", anchor="w", justify="left")
        label_d.grid(row=2, padx=PAD_H, sticky=tk.W)

        self.label_desc = tk.Text(self.root, height=1, width=10, state="disabled")
        self.label_desc.grid(row=3, padx=PAD_H, pady=(0, PAD_V), sticky=tk.NSEW)

        frame_actions = tk.Frame(self.root)
        frame_actions.grid(row=4, padx=PAD_H, pady=(0, PAD_V), sticky=tk.EW)
        frame_actions.columnconfigure(index=0, weight=1, uniform="equal")
        frame_actions.columnconfigure(index=1, weight=1, uniform="equal")
        frame_actions.columnconfigure(index=2, weight=1, uniform="equal")
        frame_actions.rowconfigure(index=0, weight=1)

        self.btn_edit = tk.Button(frame_actions, text="Edit", cursor='hand2', command=self.edit_callback)
        self.btn_edit.grid(row=0, column=0, sticky=tk.EW, padx=(0, PAD_H/2))
        
        self.btn_open = tk.Button(frame_actions, text="Open", cursor='hand2', command=self.open_callback)
        self.btn_open.grid(row=0, column=1, sticky=tk.EW, padx=PAD_H/2)

        self.btn_toggle = tk.Button(frame_actions, text="Enable", cursor='hand2', width=2, command=self.toggle_callback)
        self.btn_toggle.grid(row=0, column=2, sticky=tk.EW, padx=(PAD_H/2, 0))

    def update(self, is_enabled:bool, loader:Loader, path:str):
        self.btn_toggle.config(text="Disable" if is_enabled else "Enable")
        set_enabled(self.label_desc, True)
        self.label_desc.delete(1.0, tk.END)
        
        if loader is not None: 
            set_text(self.label_desc, loader.description)
            self.label_version.config(text=loader.version, width=5)
            self.label_author.config(text=loader.authors, width=1)
        else: 
            set_text(self.label_desc, "No info.toml found")

        set_enabled(self.label_desc, False)
        img_preview = os.path.join(path, "preview.webp")
        if os.path.exists(img_preview):
            resize_thread = ImageResize(img_preview, self.label_img.winfo_width(), self.label_img.winfo_height(), self.on_img_resized)
            resize_thread.start()
        else:
            self.label_img.image = ""
            self.label_version.config(text="")
            self.label_author.config(text="")

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

    def set_toggle_label(self, is_enabled:bool):
        if is_enabled:
            self.btn_toggle.config(text="Disable")
        else:
            self.btn_toggle.config(text="Enable")