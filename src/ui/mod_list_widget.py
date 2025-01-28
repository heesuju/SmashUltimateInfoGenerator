from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QSizePolicy, QLabel, QFrame, QPushButton, QComboBox
)
from PyQt6.QtGui import QPixmap, QColor, QPalette, QIcon, QFont
from PyQt6.QtCore import Qt, QSize, QPoint, QPointF
from src.ui.components.layout import HBox, VBox, set_margin
from src.ui.grid_list import GridList

WIDTH = 300
FONT = "Arial"
FONT_SIZE = 10

BODY_FONT_SIZE = 8

class ModListWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = VBox()
        self.setLayout(layout)
        # self.setAutoFillBackground(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self.frame = QFrame()
        self.frame.setObjectName("modListFrame")
        self.frame.setFrameShape(QFrame.Shape.Box)
        self.frame.setAutoFillBackground(True)
        self.frame.setStyleSheet("""QFrame#modListFrame {
                                 border-radius: 0px;
                                 }""")
        frame_layout = VBox()
        set_margin(frame_layout, 10)
        self.frame.setLayout(frame_layout)

        action_layout = HBox()
        action_layout.setSpacing(10)
        mod_name_label = QLabel("Mods (30)")
        title_font = QFont(FONT, FONT_SIZE)  # Set the font and font size
        title_font.setBold(True)
        mod_name_label.setFont(title_font)
        action_layout.addWidget(mod_name_label)
        action_layout.addStretch(1)

        select_button = QPushButton("Deselect All")
        action_layout.addWidget(select_button)
        
        

        action_dropdown = QComboBox()
        action_dropdown.addItems(["Batch Actions (3 Selected)", "Enable", "Disable", "Get URL", "Generate Info.toml", "Remove"])
        action_layout.addWidget(action_dropdown)


        frame_layout.addLayout(action_layout)

        self.list_widget = GridList()
        items = [
            ("assets/img/preview.webp", ["assets/icons/characters/sonic.png", "assets/icons/characters/simon.png", "assets/icons/characters/jack.png"], "Blade of Evil's Bane", "Shun_One", "C01"),
            ("assets/img/preview.webp", ["assets/icons/characters/aegis.png", "assets/icons/characters/element.png", "assets/icons/characters/jack.png"],"Master Shield", "DarkHero", "C02"),
            ("assets/img/preview.webp", ["assets/icons/characters/wolf.png", "assets/icons/characters/simon.png", "assets/icons/characters/jack.png"],"Phantom Armor", "GhostKnight", "C03"),
            ("assets/img/preview.webp", ["assets/icons/characters/sonic.png", "assets/icons/characters/simon.png", "assets/icons/characters/jack.png"], "Blade of Evil's Bane", "Shun_One", "C01"),
            ("assets/img/preview.webp", ["assets/icons/characters/sonic.png", "assets/icons/characters/simon.png", "assets/icons/characters/jack.png"], "Blade of Evil's Bane", "Shun_One", "C01"),
            ("assets/img/preview.webp", ["assets/icons/characters/sonic.png", "assets/icons/characters/simon.png", "assets/icons/characters/jack.png"], "Blade of Evil's Bane", "Shun_One", "C01"),
            ("assets/img/preview.webp", ["assets/icons/characters/sonic.png", "assets/icons/characters/simon.png", "assets/icons/characters/jack.png"], "Blade of Evssssssssssssssssil's Bane", "Shun_One", "C01"),
            ("assets/img/preview.webp", ["assets/icons/characters/sonic.png", "assets/icons/characters/simon.png", "assets/icons/characters/jack.png"], "Blade of Evil's Bane", "Shun_One", "C01"),
            ("assets/img/preview.webp", ["assets/icons/characters/sonic.png", "assets/icons/characters/simon.png", "assets/icons/characters/jack.png"], "Blade of Evil's Bane", "Shun_One", "C01"),
            ("assets/img/preview.webp", ["assets/icons/characters/sonic.png", "assets/icons/characters/simon.png", "assets/icons/characters/jack.png"], "Blade of Evil's Bane", "Shun_One", "C01"),
        ]

        for icon_path, character_icons, name, author, slot in items:
            self.list_widget.add_item(icon_path, character_icons, name, author)

        # Set the background color using QPalette
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor('red'))
        self.setPalette(palette)
        frame_layout.addWidget(self.list_widget)


        footer_layout = HBox()
        footer_layout.setSpacing(10)

        count_label = QLabel("")
        title_font = QFont(FONT, 10)  # Set the font and font size
        
        count_label.setFont(title_font)
        footer_layout.addWidget(count_label)

        footer_layout.addStretch(1)


        restore_btn = QPushButton("Restore")
        footer_layout.addWidget(restore_btn)

        disable_btn = QPushButton("Disable All")
        footer_layout.addWidget(disable_btn)

        add_button = QPushButton("+ Add New")
        footer_layout.addWidget(add_button)

        save_button = QPushButton("Save (3 Enabled)")
        footer_layout.addWidget(save_button)
        
        frame_layout.addLayout(footer_layout)

        layout.addWidget(self.frame)

        