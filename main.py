import tkinter as tk
from ui.treeview import Menu
from ui.editor import Editor 
from utils import load_config
root = tk.Tk()
root.minsize(640, 340)
root.geometry("920x540")
root.title("Toml Manager")

menu = None
config_data = load_config()

if config_data is not None and config_data.get("start_with_editor") == True:
    menu = Editor()
    menu.show(root)
else: 
    menu = Menu(root)

root.mainloop()