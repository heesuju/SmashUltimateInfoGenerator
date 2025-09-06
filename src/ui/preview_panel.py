from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QSizePolicy, QLabel, QFrame, QHBoxLayout, QPushButton
)
from PyQt6.QtGui import QPixmap, QColor, QPalette, QIcon, QFont
from PyQt6.QtCore import Qt, QSize, QPoint, QPointF
from src.ui.components.layout import HBox, VBox
from src.constants.styles import MAIN_BUTTON

WIDTH = 300
FONT = "Arial"
FONT_SIZE = 10

ICON_ELLIPSIS = "assets/icons/ui/ellipsis.png"
ICON_FAVORITE = "assets/icons/menu/favorite.png"
ICON_HIDE = "assets/icons/menu/visible.png"
ICON_OFF = "assets/icons/cartridge_off"
ICON_ON = "assets/icons/cartridge_off"

BODY_FONT_SIZE = 8

class Preview(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(340)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        
        frame_layout = VBox(margin=10, spacing=10)
        self.setLayout(frame_layout)

        header = HBox()
        frame_layout.addLayout(header)

        mod_name_label = QLabel("Valentine Sisters")
        title_font = QFont(FONT, FONT_SIZE)  # Set the font and font size
        title_font.setBold(True)
        mod_name_label.setFont(title_font)
        header.addWidget(mod_name_label)

        fav_button = QPushButton()
        fav_button.setIcon(QIcon(QPixmap(ICON_FAVORITE)))
        fav_button.setFlat(True)
        fav_button.setObjectName("obj1")
        fav_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        fav_button.setFixedSize(QSize(24, 24))
        header.addWidget(fav_button)
        
        hide_button = QPushButton()
        hide_button.setIcon(QIcon(QPixmap(ICON_HIDE)))
        hide_button.setFlat(True)
        hide_button.setObjectName("obj2")
        hide_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        hide_button.setFixedSize(QSize(24, 24))
        header.addWidget(hide_button)

        menu_button = QPushButton()
        menu_button.setIcon(QIcon(QPixmap(ICON_ELLIPSIS)))
        menu_button.setFlat(True)
        menu_button.setObjectName("obj")
        menu_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        menu_button.setFixedSize(QSize(24, 24))
        header.addWidget(menu_button)
        
        
        
        thumbnail = QLabel()
        preview_dir = "assets/img/preview.webp"
        preview_img = QPixmap(preview_dir).scaled(320, WIDTH, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        thumbnail.setPixmap(preview_img)
        frame_layout.addWidget(thumbnail)

        
        author_layout = QHBoxLayout()
        frame_layout.addLayout(author_layout)

        author_label = QLabel("Author:")
        body_font = QFont(FONT, BODY_FONT_SIZE)  # Set the font and font size
        author_label.setFont(body_font)
        author_layout.addWidget(author_label)
        author = QLabel("Hanxulz")
        body_font = QFont(FONT, BODY_FONT_SIZE)  # Set the font and font size
        author.setFont(body_font)
        author_layout.addWidget(author)
        author_layout.addStretch(1)
        
        version_layout = QHBoxLayout()
        frame_layout.addLayout(version_layout)
        version_label = QLabel("Version:")
        body_font = QFont(FONT, BODY_FONT_SIZE)  # Set the font and font size
        version_label.setFont(body_font)
        version_layout.addWidget(version_label)
        version = QLabel("1.2.4")
        body_font = QFont(FONT, BODY_FONT_SIZE)  # Set the font and font size
        version.setFont(body_font)
        version_layout.addWidget(version)
        version_layout.addStretch(1)

        version_layout = QHBoxLayout()
        frame_layout.addLayout(version_layout)
        version_label = QLabel("Wifi-Safe:")
        body_font = QFont(FONT, BODY_FONT_SIZE)  # Set the font and font size
        version_label.setFont(body_font)
        version_layout.addWidget(version_label)
        version = QLabel("Safe")
        body_font = QFont(FONT, BODY_FONT_SIZE)  # Set the font and font size
        version.setFont(body_font)
        version_layout.addWidget(version)
        version_layout.addStretch(1)

        description_label = QLabel(
            "This is a longer description of the mod.\n"
            "It can span multiple lines and wrap automatically."
        )
        description_label.setWordWrap(True)
        description_label.setFont(QFont(FONT, BODY_FONT_SIZE))
        frame_layout.addWidget(description_label)

        elements = QLabel(
            "* Skin\n* Motion\n* Effect"
        )
        elements.setWordWrap(True)
        elements.setFont(QFont(FONT, BODY_FONT_SIZE))
        frame_layout.addWidget(elements)

        frame_layout.addStretch(1)

        button_layout = QHBoxLayout()
        
        restore_button = QPushButton("Open")
        button_layout.addWidget(restore_button)

        edit = QPushButton("Edit")
        button_layout.addWidget(edit)

        save_button = QPushButton("Enable")
        save_button.setStyleSheet(MAIN_BUTTON)
        button_layout.addWidget(save_button)
        frame_layout.addLayout(button_layout)

        # Set the background color using QPalette
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor('red'))
        self.setPalette(palette)

        