from typing import Callable
from PyQt6.QtWidgets import (
    QFrame, QPushButton, QHBoxLayout
)
from PyQt6.QtGui import (
    QPixmap, QIcon
)
from PyQt6.QtCore import QSize

from src.ui.components.layout import HBox
from src.constants.styles import BORDERLESS_BUTTON

class ToggleButton(QPushButton):
    def __init__(self, a:str, b:str, callback_a:Callable=None, callback_b:Callable=None, size:int=0):
        super().__init__()
        self.a=a
        self.b=b
        self.callback_a = callback_a
        self.callback_b = callback_b
        self.toggle_state = False
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
            icon = QIcon(QPixmap(self.a))
            self.setIcon(icon)
        else:
            icon = QIcon(QPixmap(self.b))
            self.setIcon(icon)