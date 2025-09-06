from PyQt6.QtWidgets import (
    QWidget, 
    QHBoxLayout, 
    QLabel, 
    QSizePolicy, 
    QFrame,
    QScrollArea
)
from PyQt6.QtCore import Qt, QSize, QPoint, QPointF
from PyQt6.QtGui import QFont
from src.ui.components.layout import VBox

FONT = "Arial"
FONT_SIZE = 10
BODY_FONT_SIZE = 8

class SidePanel(QWidget):
    def __init__(self, title:str):
        super().__init__()
        self.width = 340
        layout = VBox()
        self.setLayout(layout)
        self.setFixedWidth(self.width)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        
        self.frame = QFrame()
        self.frame.setFrameShape(QFrame.Shape.Box)
        self.frame.setAutoFillBackground(True)
        self.frame.setStyleSheet("""QFrame {
                                 border-radius: 0px;
                                 }""")
        self.root = VBox(margin=10, spacing=10)
        self.frame.setLayout(self.root)

        title_label = QLabel(title)
        title_font = QFont(FONT, FONT_SIZE)  # Set the font and font size
        title_font.setBold(True)
        title_label.setFont(title_font)
        self.root.addWidget(title_label)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)   # horizontal line
        line.setFrameShadow(QFrame.Shadow.Sunken)  # optional, makes it look recessed
        self.root.addWidget(line)
        
        scroll = QScrollArea()
        scroll.setStyleSheet("QScrollArea { border-radius: 0px; border: none; }")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # Disable horizontal scroll
        self.root.addWidget(scroll, stretch=1)

        self.body_frame = QFrame()
        self.body_frame.setStyleSheet("QFrame { border-radius: 0px; border: 0px; }")
        self.body = VBox(margin=0, spacing=10)
        self.body_frame.setLayout(self.body)
        scroll.setWidget(self.body_frame)

        self.footer = QHBoxLayout()
        self.root.addLayout(self.footer)

        # Set the background color using QPalette
        # palette = self.palette()
        # palette.setColor(QPalette.ColorRole.Window, QColor('red'))
        # self.setPalette(palette)

        layout.addWidget(self.frame)