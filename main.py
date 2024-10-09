import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from ui.menu import Menu
from ui.editor import Editor 
from ui.config import load_config
from web.webdriver_manager import WebDriverManager

root = TkinterDnD.Tk()
root.minsize(640, 340)
root.geometry("920x580")
root.title("Toml Manager")

menu = None
config_data = load_config()
webdriver_manager = WebDriverManager()

if config_data is not None and config_data.get("start_with_editor") == True:
    menu = Editor(root, webdriver_manager)
else: 
    menu = Menu(root, webdriver_manager)

root.mainloop()