import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import tomli_w as tomli
import os
from common import is_valid_dir

def set_text(widget, text:str)->None:
    if isinstance(widget, tk.Entry):
        widget.delete(0, tk.END)
        widget.insert(0, text)
    elif isinstance(widget, tk.Label):
        widget.config(text=text)
    elif isinstance(widget, tk.Text):
        widget.delete(1.0, tk.END)
        widget.insert(tk.END, text)

def clear_text(widget)->None:
    if isinstance(widget, tk.Entry):
        widget.delete(0, tk.END)
    elif isinstance(widget, tk.Label):
        widget.config(text="")
    elif isinstance(widget, tk.Text):
        widget.delete(1.0, tk.END)
        
def get_text(widget, remove_spacing:bool = False)->str:
    output = ""

    if isinstance(widget, tk.Entry):
        output = widget.get()
    elif isinstance(widget, tk.Label):
        output = widget.cget("text")
    elif isinstance(widget, tk.Text):
        output = widget.get("1.0", tk.END)
    elif isinstance(widget, ttk.Combobox):
        output = widget.get()
    
    if remove_spacing:
        output = output.replace(" ", "")

    return output

def set_enabled(widget, is_enabled:bool=True):
    if is_enabled:
        widget.config(state="normal")
    else:
        widget.config(state="disabled")

class TomlParams:
    def __init__(self, display_name:str = "", authors:str = "", description:str = "", version:str = "", category:str = "", 
                 url:str = "", mod_name:str = "", wifi_safe:str = "Unknown") -> None:
        self.display_name = display_name
        self.authors = authors 
        self.description = description 
        self.version = version
        self.category = category
        self.url = url
        self.mod_name = mod_name
        self.wifi_safe = wifi_safe

    def __init__(self, display_name:tk.Entry, authors:tk.Entry, description:tk.Text, version:tk.Entry, category:ttk.Combobox, 
                 url:tk.Entry, mod_name:tk.Entry, wifi_safe:ttk.Combobox) -> None:
        self.display_name = get_text(display_name)
        self.authors = get_text(authors) 
        self.description = get_text(description) 
        self.version = get_text(version)
        self.category = get_text(category)
        self.url = get_text(url)
        self.mod_name = get_text(mod_name)
        self.wifi_safe = get_text(wifi_safe)

# Create and write to the info.toml file
def dump_toml(path, params:TomlParams):
    output_path = os.path.join(path, "info.toml")
    with open(output_path, "wb") as toml_file:
        tomli.dump({
            "display_name": params.display_name, 
            "authors": params.authors,
            "description": params.description,
            "version": params.version,
            "category": params.category,
            "url": params.url,
            "mod_name": params.mod_name,
            "wifi_safe":params.wifi_safe
        }, toml_file)

def open_file_dialog(default_dir:str=""):
    if is_valid_dir(default_dir):
        return filedialog.askdirectory(initialdir=default_dir)
    else:
        return filedialog.askdirectory()