import tkinter as tk
from tkinter import ttk, messagebox
from src.constants.ui_params import (
    PAD_H, 
    PAD_V, 
    WIN_SIZE_X_DEFAULT, 
    WIN_SIZE_Y_DEFAULT
)
from src.constants.strings import (
    ASK_CLOSE_WINDOW_TITLE, 
    ASK_CLOSE_WINDOW_MSG
)

class Popup:
    def __init__(self, root=None, title:str="", width:int=1, height:int=1, confirm_close:bool=True) -> None:
        self.root = root
        self.title = title
        if width <= 1:
            self.width = WIN_SIZE_X_DEFAULT
        else:
            self.width = width

        if height <= 1:
            self.height = WIN_SIZE_Y_DEFAULT
        else:
            self.height = height

        self.confirm_close = confirm_close
        self.new_window = None
        self.is_running = True

    def on_escape(self, event:tk.Event):
        result = False
        
        if self.confirm_close:
            result = messagebox.askokcancel(ASK_CLOSE_WINDOW_TITLE, ASK_CLOSE_WINDOW_MSG)
        
        if result or self.confirm_close == False:
            self.is_running = False
            self.new_window.unbind('<Escape>')
            self.new_window.destroy()
        
    def show(self, root):
        if self.new_window is not None:
            self.new_window.destroy()

        self.is_running = True
        self.new_window = tk.Toplevel(root)
        self.new_window.title(self.title)
        self.new_window.bind('<Escape>', self.on_escape)
        self.new_window.minsize(self.width, self.height)
        self.new_window.geometry(f"{self.width}x{self.height}")
        self.new_window.configure(padx=PAD_H, pady=PAD_V)
        self.new_window.focus_set()