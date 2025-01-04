import tkinter as tk

def style_label_as_entry(label, color):
    label.config(relief=tk.SUNKEN, borderwidth=1)  # Add a border
    label.config(bg=color)  # Set background color to white
    label.config(font=("Helvetica", 9))  # Set font style and size

class WrappingLabel(tk.Label):
    def __init__(self, master=None, **kwargs):
        tk.Label.__init__(self, master, **kwargs)
        self.bind('<Configure>', lambda e: self.config(wraplength=self.winfo_width()))
