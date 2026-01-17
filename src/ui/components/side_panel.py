from PyQt6.QtWidgets import (
    QWidget, 
    QHBoxLayout, 
    QLabel, 
    QSizePolicy, 
    QFrame,
    QScrollArea,
    QPushButton
)
from PyQt6.QtCore import Qt, QSize, QPoint, QPointF
from PyQt6.QtGui import QFont, QIcon, QPixmap
from src.ui.components.layout import VBox, HBox
from src.constants.styles import MAIN_BUTTON, DANGER_BUTTON, SECONDARY_BUTTON

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
        self.frame.setFrameShape(QFrame.Shape.NoFrame)
        self.frame.setAutoFillBackground(True)
        self.root = VBox(margin=0, spacing=10)
        self.frame.setLayout(self.root)

        self.header = HBox(margin=0, spacing=2)
        self.root.addLayout(self.header)

        scroll = QScrollArea()
        scroll.setStyleSheet("""
            QScrollArea { 
                border: none; 
            }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.2);
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.3);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # Disable horizontal scroll
        self.root.addWidget(scroll, stretch=1)

        self.body_frame = QFrame()
        self.body_frame.setStyleSheet("QFrame { border: 0px; }")
        self.body_frame.setContentsMargins(0,0,0,0)
        self.body_frame.setFrameShape(QFrame.Shape.NoFrame)
        self.body = VBox(margin=10, spacing=10)
        self.body_frame.setLayout(self.body)
        scroll.setWidget(self.body_frame)

        self.footer = QHBoxLayout()
        self.footer.setContentsMargins(10, 0, 10, 10)
        self.footer.setSpacing(10)
        self.root.addLayout(self.footer)

        layout.addWidget(self.frame)

    def add_footer_button(self, text: str, callback, primary: bool = False, danger: bool = False, icon: str = None) -> QPushButton:
        """Add a consistent button to the footer"""
        btn = QPushButton(text)
        if icon:
            if isinstance(icon, str):
                btn.setIcon(QIcon(QPixmap(icon)))
            else:
                btn.setIcon(icon)
            
        if primary:
            btn.setStyleSheet(MAIN_BUTTON)
        elif danger:
            btn.setStyleSheet(DANGER_BUTTON)
        else:
            btn.setStyleSheet(SECONDARY_BUTTON)
            
        btn.setFixedHeight(26)
        btn.clicked.connect(callback)
        self.footer.addWidget(btn)
        return btn