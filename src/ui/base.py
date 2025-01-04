import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from src.utils.file import is_valid_dir
from src.utils.string_helper import is_digit
from assets import ICON_PATH
from PIL import ImageTk

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

def open_file_dialog(default_dir:str=""):
    if is_valid_dir(default_dir):
        return filedialog.askdirectory(initialdir=default_dir)
    else:
        return filedialog.askdirectory()
    
def validate_slot(P):
    return is_digit(P)

def validate_page(P):
    return is_digit(P, 4)

def get_icon(name:str, extension:str="png"):
    path = os.path.join(ICON_PATH, f'{name}.{extension}')
    return ImageTk.PhotoImage(file=path)

def style_label_as_entry(label, color):
    label.config(relief=tk.SUNKEN, borderwidth=1)  # Add a border
    label.config(bg=color)  # Set background color to white
    label.config(font=("Helvetica", 9))  # Set font style and size

class WrappingLabel(tk.Label):
    def __init__(self, master=None, **kwargs):
        tk.Label.__init__(self, master, **kwargs)
        self.bind('<Configure>', lambda e: self.config(wraplength=self.winfo_width()))
