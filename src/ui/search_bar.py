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
from src.ui.components.input_button_widget import InputButtonWidget, InputButton

from src.managers.data_manager import ButtonIcons
from src.managers.mod_manager import ModManager
from src.managers.filter_manager import FilterManager, FilterParameters

ICON_ELLIPSIS = "assets/img/search.png"

class SearchBar(QWidget):
    def __init__(self, mod_manager:ModManager, filter_manager:FilterManager):
        super().__init__()
        self.mod_manager = mod_manager
        self.filter_manager = filter_manager
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

        self.search_bar = InputButtonWidget(
            "Search mod name...", [
                InputButton(text="",img=ButtonIcons.REFRESH, callback=self.on_refresh_clicked), 
                InputButton(text="",img=ButtonIcons.CLEAR, callback=self.on_clear_clicked), 
                InputButton(text="",img=ButtonIcons.SEARCH, callback=self.on_search_clicked)
            ],
            self.on_search_clicked
        )
        
        frame_layout.addWidget(self.search_bar)        
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

    def on_search_clicked(self):
        text = self.search_bar.get_text()
        self.filter_manager.params.mod_name = text
        self.filter_manager.on_change()

    def on_clear_clicked(self):
        self.search_bar.set_text("")
        self.filter_manager.params.mod_name = ""
        self.filter_manager.on_change()

    def on_refresh_clicked(self):
        self.search_bar.set_text("")
        self.filter_manager.params.mod_name = ""
        self.mod_manager.scan_all()