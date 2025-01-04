"""
main.py: Entrypoint for the application

Usage:
    To run the application, execute this module directly:
        python main.py
"""

from tkinterdnd2 import TkinterDnD
from src.ui.views.menu import Menu
from src.ui.views.editor import Editor
from src.core.data import get_start_w_editor
from src.core.web.webdriver_manager import WebDriverManager
from src.constants.ui_params import (
    WIN_SIZE_X_DEFAULT,
    WIN_SIZE_Y_DEFAULT,
    WIN_SIZE_X_MIN,
    WIN_SIZE_Y_MIN,
    TITLE
)

def main()->None:
    """
    Main entry point for the application.

    This function is responsible for initializing the application
    and invoking the necessary components to execute the desired functionality.

    Returns:
        None
    """

    root = TkinterDnD.Tk()
    root.minsize(WIN_SIZE_X_MIN, WIN_SIZE_Y_MIN)
    root.geometry(f"{WIN_SIZE_X_DEFAULT}x{WIN_SIZE_Y_DEFAULT}")
    root.title(TITLE)

    webdriver_manager = WebDriverManager()

    if get_start_w_editor():
        Editor(root, webdriver_manager)
    else:
        Menu(root, webdriver_manager)

    root.mainloop()

if __name__ == "__main__":
    main()
