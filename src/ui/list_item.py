from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QSizePolicy, QListWidget, QListWidgetItem, QFrame
)
from PyQt6.QtGui import QPixmap, QColor, QPalette, QIcon
from PyQt6.QtCore import Qt, QSize, QPoint, QPointF
from src.utils.image_utils import create_image_overlay, add_text_to_image
from PyQt6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QWidget,
)
from src.ui.components.image_overlay import ImageOverlayWidget
from src.ui.components.layout import HBox, VBox
from overlay_test import Overlay

ICON_ELLIPSIS = "assets/icons/ui/ellipsis.png"
ICON_FAVORITE = "assets/icons/menu/favorite.png"
ICON_HIDE = "assets/icons/menu/visible.png"
ICON_OFF = "assets/icons/cartridge_off"
ICON_ON = "assets/icons/cartridge_off"

class GridListItem(QListWidgetItem):
    def __init__(self, image_path:str, name:str, author:str, characters:list[str], height:int=80):
        super().__init__()

        self.widget = GridListItemWidget(image_path, name, author, characters, height)
        self.setSizeHint(QSize(350, 110))
        # self.setData(Qt.ItemDataRole.UserRole, characters)

class GridListItemWidget(QWidget):
    def __init__(self, image_path:str, name:str, author:str, characters:list[str], height:int=80):
        super().__init__()
        self.image_path = image_path
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.frame = QFrame()
        self.frame.setFrameShape(QFrame.Shape.NoFrame)
        self.frame.setAutoFillBackground(True)
        frame_layout = HBox(margin=4, spacing=4)
        self.frame.setLayout(frame_layout)

        
        palette = self.frame.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))  # White background
        self.frame.setPalette(palette)
        
        overlay = Overlay("assets/img/preview.webp", self)

        frame_layout.addWidget(overlay)
        
        info_layout = QVBoxLayout()

        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        action_layout = HBox()
        # action_layout.addStretch(1)
        action_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        frame_layout.addLayout(info_layout)
        frame_layout.addStretch(1)
        frame_layout.addLayout(right_layout)
        right_layout.addLayout(action_layout)
        frame_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        info_layout.addStretch(1)
        line_text = QLabel(name)
        
        line_text.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Align text to the left

        author_text = QLabel(author)
        
        author_text.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Align text to the left

        info_layout.addWidget(line_text)
        info_layout.addWidget(author_text)
        slot_text = QLabel("C01-04")
        slot_text.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Align text to the left
        info_layout.addWidget(slot_text)

        info_layout.setContentsMargins(0,0,0,0)
        info_layout.setSpacing(0)
        
        

        icon_layout = QHBoxLayout()
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        icon_layout.setContentsMargins(0,0,0,0)
        icon_layout.setSpacing(4)
        info_layout.addLayout(icon_layout)
        
        info_layout.addStretch(1)
        
        for char_img in characters:
            img_label = QLabel()
            char_icon = QPixmap(char_img).scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            img_label.setPixmap(char_icon)
            icon_layout.addWidget(img_label)

        fav_button = QPushButton()
        fav_button.setIcon(QIcon(QPixmap(ICON_FAVORITE)))
        fav_button.setFlat(True)
        fav_button.setObjectName("obj1")
        fav_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        fav_button.setFixedSize(QSize(24, 24))
        action_layout.addWidget(fav_button)
        
        hide_button = QPushButton()
        hide_button.setIcon(QIcon(QPixmap(ICON_HIDE)))
        hide_button.setFlat(True)
        hide_button.setObjectName("obj2")
        hide_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        hide_button.setFixedSize(QSize(24, 24))
        action_layout.addWidget(hide_button)

        menu_button = QPushButton()
        menu_button.setIcon(QIcon(QPixmap(ICON_ELLIPSIS)))
        menu_button.setFlat(True)
        menu_button.setObjectName("obj")
        menu_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        menu_button.setFixedSize(QSize(24, 24))
        action_layout.addWidget(menu_button)

        
        
        right_layout.addStretch(1)

        version_text = QLabel("1.0.0")
        version_text.setAlignment(Qt.AlignmentFlag.AlignRight)  # Align text to the left
        right_layout.addWidget(version_text)

        

        # line_push_button.clicked.connect(self.clicked)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setOffset(2, 2)
        shadow.setColor(QColor(0, 0, 0, 160))  # Semi-transparent black

        # Apply shadow effect to the widget
        self.frame.setGraphicsEffect(shadow)
        layout.addWidget(self.frame)
        
        # self.setSizeHint(QSize(340, height))
        # self.widget.setLayout(item_layout)
        # self.setData(Qt.ItemDataRole.UserRole, characters)

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