from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QSizePolicy, QListWidget, QListWidgetItem, QFrame, QLineEdit
)
from PyQt6.QtGui import QPixmap, QColor, QPalette, QIcon
from PyQt6.QtCore import Qt, QSize, QPoint, QPointF
from src.utils.image_utils import create_image_overlay, add_text_to_image
from PyQt6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QWidget,
)

from src.ui.components.layout import HBox, VBox
from src.managers.asset_manager import ButtonIcons

ICON_ELLIPSIS = "assets/img/search.png"

class SearchBar(QWidget):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        layout = VBox()
        
        self.setLayout(layout)
        # self.setFixedHeight(100)
        self.frame = QFrame()
        
        self.frame.setFrameShape(QFrame.Shape.NoFrame)
        self.frame.setAutoFillBackground(True)
        frame_layout = QHBoxLayout()
        self.frame.setLayout(frame_layout)
        self.frame.setStyleSheet("""QFrame {
        
        border-radius: 5px;
    }""")

        frame_layout.setSpacing(0)
        frame_layout.setContentsMargins(10,10,10,10)
        palette = self.frame.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))  # White background
        self.frame.setPalette(palette)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search mod name...")
        self.search_bar.setStyleSheet("""
    QLineEdit {
        border: 0px;
        border-top-left-radius: 5px;
        border-bottom-left-radius: 5px;
        border-top-right-radius: 0px;
        border-bottom-right-radius: 0px;
    }
""")
        frame_layout.addWidget(self.search_bar)

        clear = QPushButton()
        clear.setIcon(QIcon(QPixmap(ButtonIcons.CLEAR.value)))
        clear.setObjectName("obj1")
        clear.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        frame_layout.addWidget(clear)
        
        # line = QFrame()
        # line.setFrameShape(QFrame.Shape.VLine)
        # line.setFrameShadow(QFrame.Shadow.Raised) # or QFrame.Raised, QFrame.Plain
        # frame_layout.addWidget(line)
        
        refresh = QPushButton()
        refresh.setIcon(QIcon(QPixmap(ButtonIcons.REFRESH.value)))
        refresh.setObjectName("obj2")
        refresh.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        frame_layout.addWidget(refresh)

        search_button = QPushButton()
        search_button.setIcon(QIcon(QPixmap(ButtonIcons.SEARCH.value)))
        # search_button.setStyleSheet(MAIN_BUTTON)
        search_button.setObjectName("obj3")
        search_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        
        clear.setStyleSheet("QPushButton { border: none; border-radius: 0px; }")
        refresh.setStyleSheet("QPushButton { border: none; border-radius: 0px; }")
        search_button.setStyleSheet("QPushButton { border: none; border-radius: 0px; }")

        

        

        frame_layout.addWidget(search_button)

        
        layout.addWidget(self.frame)
        

    def mousePressEvent(self, event):
        # self.frame.setStyleSheet(self.selected_style)

        # base_pixmap = QPixmap(ICON_ON)
        # alpha_pixmap = QPixmap(self.image_path)

        # # Combine images
        # combined_pixmap = create_image_overlay(base_pixmap, alpha_pixmap)
        # self.icon = add_text_to_image(combined_pixmap, "FIGHTER", (0, -64, 0, -64))  # Overlay text "TXT" on image
        # self.icon = self.icon.scaled(70, 70, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        # # self.icon_label.setPixmap(self.icon)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # self.frame.setStyleSheet(self.default_style)
        
        super().mouseReleaseEvent(event)