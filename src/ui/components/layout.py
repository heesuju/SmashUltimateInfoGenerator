from typing import Union
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout
)

class HBox(QHBoxLayout):
    def __init__(self, spacing:int=0, margin:Union[int, tuple[int, int, int, int]]=0, parent=None):
        super().__init__(parent)
        self.setSpacing(spacing)
        if isinstance(margin, int):
            self.setContentsMargins(margin, margin, margin, margin)
        elif isinstance(margin, tuple):
            left, top, right, bottom = margin
            self.setContentsMargins(left, top, right, bottom)

class VBox(QVBoxLayout):
    def __init__(self, spacing:int=0, margin:Union[int, tuple[int, int, int, int]]=0, parent=None):
        super().__init__(parent)
        self.setSpacing(spacing)
        if isinstance(margin, int):
            self.setContentsMargins(margin, margin, margin, margin)
        elif isinstance(margin, tuple):
            left, top, right, bottom = margin
            self.setContentsMargins(left, top, right, bottom)