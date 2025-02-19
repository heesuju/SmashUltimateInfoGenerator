"""
base.py: Contains shared methods for UI
"""

import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from src.utils.file import is_valid_dir
from src.utils.string_helper import is_digit
from src.constants.ui_params import PAD_H, PAD_V
from src.ui.components.checkbox_treeview import Treeview
from src.utils.image_handler import ImageHandler
from assets import ICON_PATH
from PIL import ImageTk

class RowCount():
    def __init__(self):
        self.index = 0

    def get_row(self):
        return self.index
    
    def inc_row(self):
        self.index+=1
        return self.index

def set_text(widget, text:str)->None:
    if widget is None:
        return
    
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

def style_label_as_entry(label:tk.Label, color:str):
    label.config(relief=tk.SUNKEN, borderwidth=1)  # Add a border
    label.config(bg=color)  # Set background color to white
    label.config(font=("Helvetica", 9))  # Set font style and size

class WrappingLabel(tk.Label):
    def __init__(self, master=None, **kwargs):
        tk.Label.__init__(self, master, **kwargs)
        self.bind('<Configure>', lambda e: self.config(wraplength=self.winfo_width()))

def add_filter_entry(frame:tk.Frame, row:int, col:int, name:str, string_var:tk.StringVar, on_submit:callable = None, add_padding:bool=True):
    label = ttk.Label(frame, text=name, width=8)
    label.grid(row=row, column=col, sticky=tk.EW, padx=(0,PAD_H))
    entry = tk.Entry(frame, textvariable=string_var, width=16)
    entry.grid(row=row, column=col+1, sticky=tk.EW, padx=(0,PAD_H if add_padding else 0), pady=PAD_V/2)
    entry.bind("<Return>", on_submit)
    return entry
    
def add_filter_dropdown(frame:tk.Frame, row:int, col:int, name:str, data:list[str], string_var:tk.StringVar, on_submit:callable = None, add_padding:bool=True):
    label = ttk.Label(frame, text=name, width=10)
    label.grid(row=row, column=col, sticky=tk.EW, padx=(0,PAD_H))
    combobox = ttk.Combobox(frame, values=data, width=10, textvariable=string_var)
    combobox.grid(row=row, column=col+1, sticky=tk.EW, padx=(0,PAD_H if add_padding else 0), pady=PAD_V/2)
    combobox.bind("<Return>", on_submit)
    combobox.set(data[0])
    return combobox

def add_entry(root:tk.Frame, label:str, text_var:tk.StringVar, row:RowCount, values:list[str]=None):
    label_w = tk.Label(root, justify=tk.LEFT, text=label, width=12)
    label_w.grid(row=row.inc_row(), column=0, sticky=tk.EW)
    
    widget = None
    if values is not None:
        widget = ttk.Combobox(root, width=20, textvariable=text_var, values=values)
    else:
        widget = tk.Entry(root, width=20, textvariable=text_var)
    if widget is not None:
        widget.grid(row=row.get_row(), column=1, sticky=tk.EW)
    return widget

def add_text(root:tk.Frame, label:str, row:RowCount):
    label_w = tk.Label(root, justify=tk.LEFT, text=label, width=12)
    label_w.grid(row=row.inc_row(), column=0, sticky=tk.EW)
    
    widget = tk.Text(root, height=10, width=10, wrap="word")
    widget.grid(row=row.get_row(), column=1, sticky=tk.EW)
    return widget

def add_treeview(root:tk.Frame, label:str, row:RowCount, values:list[str]=None):
    label_w = tk.Label(root, justify=tk.LEFT, text=label, width=12)
    label_w.grid(row=row.inc_row(), column=0, sticky=tk.EW)
    treeview = Treeview(root, False)
    treeview.construct([label])
    treeview.widget.grid(row=row.get_row(), column=1, sticky=tk.NSEW)
    root.rowconfigure(row.get_row(), weight=1)
    treeview.clear()
    for value in values:
        treeview.add_item([value], False)
    return treeview

def update_treeview(treeview:Treeview, included:list[str], sort:bool = True):
    if sort:
        texts = []
        items = treeview.get_items()
        for item in items:
            texts.append(treeview.get_row_text(item))
        included = sorted(included)
        texts = sorted(texts)
        treeview.clear()
        [treeview.add_item([item], True) for item in included]
        [treeview.add_item([item], False) for item in texts if item not in included]
        treeview.widget.yview_moveto(0)
    else:
        items = treeview.get_items()
        for item in items:
            text = treeview.get_row_text(item)
            treeview.set_row_checked(item, text in included)

def get_treeview_checked(treeview:Treeview)->list[str]:
    outputs = []
    for item in treeview.get_checked_items():
        text = treeview.get_row_text(item)
        if text not in outputs:
            outputs.append(text)
    return outputs

def set_image(directory:str, width:int, height:int, callback:callable):
    if not directory or not os.path.exists(directory):
        return
    
    ImageHandler(directory, width, height, callback)