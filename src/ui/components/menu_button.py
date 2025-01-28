from typing import Union
from PyQt6.QtWidgets import QPushButton, QSizePolicy
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QSize

ICON_SIZE = 32

class MenuButton(QPushButton):
    def __init__(self, icon:Union[str, QIcon, QPixmap], width:int, height:int, parent=None):
        icon_ref = None
        if isinstance(icon, str):
            pixmap = QPixmap(icon)
            icon_ref = QIcon(pixmap)
        elif isinstance(icon, QPixmap):
            icon_ref = QIcon(icon)
        elif isinstance(icon, QIcon):
            icon_ref = icon
        
        super().__init__(parent)
        self.setIcon(icon_ref)

        self.setFixedSize(width, height)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setIconSize(QSize(32, 32))
        self.setFlat(True)
        # setStyleSheet("""
        #     QPushButton {
        #         border: none;
        #         background-color: white;
        #         border-radius: 0px;
        #     }
        #     QPushButton:hover {
        #         background-color: lightgray;
        #     }
        #     QPushButton:pressed {
        #         background-color: gray;
        #     }
        # """)