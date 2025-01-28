from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QSizePolicy, QLabel, QPushButton, QFrame
)
from PyQt6.QtGui import QPixmap, QColor, QPalette, QIcon, QFont
from PyQt6.QtCore import Qt, QSize, QPoint, QPointF
from src.ui.components.layout import HBox, VBox
from src.ui.components.menu_button import MenuButton

WIDTH = 60
FONT = "Arial"
FONT_SIZE = 10

BODY_FONT_SIZE = 8

class MenuWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = VBox()
        self.setLayout(layout)
        self.setFixedWidth(WIDTH)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        
        preview_button = MenuButton("assets/icons/menu/details.png", WIDTH, WIDTH, self)
        layout.addWidget(preview_button)

        workspace_button = MenuButton("assets/icons/menu/workspace.png", WIDTH, WIDTH, self)
        layout.addWidget(workspace_button)

        
        layout.addStretch(1)

        config_button = MenuButton("assets/icons/menu/config.png", WIDTH, WIDTH, self)
        layout.addWidget(config_button)


        save_button = MenuButton("assets/icons/menu/save.png", WIDTH, WIDTH, self)
        layout.addWidget(save_button)

        # Set the background color using QPalette
        
        self.setStyleSheet("""
            QWidget#MenuWidget {
                background-color: red;
            }
        """)
