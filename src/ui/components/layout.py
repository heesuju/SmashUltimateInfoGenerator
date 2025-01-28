from typing import Union
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout
)

def set_margin(layout:Union[QHBoxLayout, QVBoxLayout], margin:int):
    layout.setContentsMargins(margin, margin, margin, margin)

class HBox(QHBoxLayout):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)

class VBox(QVBoxLayout):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)