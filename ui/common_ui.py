import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from utils.files import is_valid_dir

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
    
def get_is_digit(text:str, num_digits:int=3):
    if (str.isdigit(text) and len(text) <= num_digits) or text == "":
        return True
    else:
        return False
    
def validate_slot(P):
    return get_is_digit(P)

def validate_page(P):
    return get_is_digit(P, 4)