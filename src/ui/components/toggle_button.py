from typing import Callable
from PyQt6.QtWidgets import (
    QFrame, QPushButton, QHBoxLayout
)
from PyQt6.QtGui import (
    QPixmap, QIcon
)

from src.ui.components.layout import HBox
from src.constants.styles import BORDERLESS_BUTTON

class ToggleButton(QFrame):
    def __init__(self, a:str, b:str, callback_a:Callable=None, callback_b:Callable=None):
        super().__init__()
        
        self.setContentsMargins(0,0,0,0)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setAutoFillBackground(True)

        self.setStyleSheet("""QFrame {
            border-radius: 0px;
            border: none;
        }""")
        
        frame_layout = QHBoxLayout()
        self.setLayout(frame_layout)
        frame_layout.setContentsMargins(0,0,0,0)
        frame_layout.setSpacing(0)

        self.callback_a = callback_a
        self.callback_b = callback_b

        self.button_a = QPushButton()
        self.button_b = QPushButton()
        icon_a = QIcon(QPixmap(a))
        icon_b = QIcon(QPixmap(b))
        self.button_a.setIcon(icon_a)
        self.button_b.setIcon(icon_b)
        self.button_a.setStyleSheet(BORDERLESS_BUTTON)
        self.button_b.setStyleSheet(BORDERLESS_BUTTON)
        
        self.button_a.clicked.connect(self.on_a_clicked)
        self.button_b.clicked.connect(self.on_b_clicked)
        self.button_a.hide()
        self.button_b.show()

        frame_layout.addWidget(self.button_a)
        frame_layout.addWidget(self.button_b)        

    def on_a_clicked(self, event):
        self.button_a.hide()
        self.button_b.show()
        self.callback_a()
        
    def on_b_clicked(self, event):
        self.button_a.show()
        self.button_b.hide()
        self.callback_b()
