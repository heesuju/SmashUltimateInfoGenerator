from typing import Callable, Optional
from PyQt6.QtWidgets import (
    QFrame, QPushButton, QHBoxLayout
)
from PyQt6.QtGui import (
    QPixmap, QIcon, QColor
)
from PyQt6.QtCore import QSize

from src.ui.components.layout import HBox
from src.constants.styles import BORDERLESS_BUTTON
from src.utils.image_utils import tint_pixmap

class ToggleButton(QPushButton):
    def __init__(self, a:str, b:str, callback_a:Callable=None, callback_b:Callable=None, size:int=0, initial_state:bool=True, 
                 color_a:Optional[str]=None, color_b:Optional[str]=None):
        super().__init__()
        self.a=a
        self.b=b
        self.callback_a = callback_a
        self.callback_b = callback_b
        self.color_a = color_a  # Color for state A (on)
        self.color_b = color_b  # Color for state B (off)
        self.toggle_state = initial_state  # Allow customizable initial state
        if size > 0:
            self.setFixedSize(QSize(size, size))
        
        self.setStyleSheet(BORDERLESS_BUTTON)
        self.clicked.connect(self.on_clicked)
        self.set_state(toggled=self.toggle_state)

    def on_clicked(self, event):
        self.toggle_state = not self.toggle_state
        self.set_state(self.toggle_state)
        if self.toggle_state:
            self.callback_a()
        else:
            self.callback_b()

    def set_state(self, toggled:bool):
        self.toggle_state = toggled
        if toggled:
            pixmap = QPixmap(self.a)
            if self.color_a:
                pixmap = tint_pixmap(pixmap, QColor(self.color_a))
            icon = QIcon(pixmap)
            self.setIcon(icon)
        else:
            pixmap = QPixmap(self.b)
            if self.color_b:
                pixmap = tint_pixmap(pixmap, QColor(self.color_b))
            icon = QIcon(pixmap)
            self.setIcon(icon)