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

        self.frame = QFrame()
        self.frame.setFrameShape(QFrame.Shape.NoFrame)
        self.frame.setAutoFillBackground(True)
        frame_layout = VBox()
        self.frame.setLayout(frame_layout)
        layout.addWidget(self.frame)
        palette = self.frame.palette()
        palette.setColor(QPalette.ColorRole.Highlight, QColor(100, 255, 255))  # White background
        self.frame.setPalette(palette)

        preview_button = MenuButton("assets/icons/menu/details.png", WIDTH, WIDTH, self)
        frame_layout.addWidget(preview_button)

        workspace_button = MenuButton("assets/icons/menu/workspace.png", WIDTH, WIDTH, self)
        frame_layout.addWidget(workspace_button)

        
        frame_layout.addStretch(1)

        config_button = MenuButton("assets/icons/menu/config.png", WIDTH, WIDTH, self)
        frame_layout.addWidget(config_button)


        self.frame.setStyleSheet("""QFrame {
                                 background-color: rgba(100, 255, 200, 200);
                                 border-radius: 0px;
                                 }""")


