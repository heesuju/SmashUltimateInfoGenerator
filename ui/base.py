import tkinter as tk

def set_text(widget, text:str):
    if isinstance(widget, tk.Entry):
        widget.delete(0, tk.END)
        widget.insert(0, text)
    elif isinstance(widget, tk.Label):
        widget.config(text=text)