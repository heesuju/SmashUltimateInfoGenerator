from typing import List, Optional, Callable
from PyQt6.QtWidgets import QWidget

class NavigationMenu():
    def __init__(self, icon:str, widget:QWidget, callback:Optional[Callable] = None):
        self.icon = icon
        self.widget = widget
        self.callback = callback
        