from tkinterdnd2 import TkinterDnD
from src.ui.views.menu import Menu
from src.ui.views.editor import Editor 
from src.core.data import get_start_w_editor
from src.core.web.webdriver_manager import WebDriverManager
from src.constants.ui_params import *

root = TkinterDnD.Tk()
root.minsize(WIN_SIZE_X_MIN, WIN_SIZE_Y_MIN)
root.geometry(f"{WIN_SIZE_X_DEFAULT}x{WIN_SIZE_Y_DEFAULT}")
root.title(TITLE)

menu = None
webdriver_manager = WebDriverManager()

if get_start_w_editor():
    menu = Editor(root, webdriver_manager)
else: 
    menu = Menu(root, webdriver_manager)

root.mainloop()