import re
from PyQt6.QtWidgets import ( 
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QLineEdit, QTextEdit
)
from PyQt6 import QtCore
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt, QSize
from src.ui.components.layout import HBox, VBox
from src.constants.styles import MAIN_BUTTON
from src.ui.components.side_panel import SidePanel
from src.constants.enums import Category, Element, Fighter, Wifi
from src.ui.components.input_button_widget import InputButtonWidget, InputButton
from src.ui.components.multi_combobox import CheckableComboBox
from src.ui.components.single_combobox import SingleComboBox
from src.managers.mod_manager import ModManager
from src.ui.components.validators import limit_version

FONT = "Arial"
FONT_SIZE = 10
BODY_FONT_SIZE = 8


class EditPanel(SidePanel):
    def __init__(self, mod_manager: ModManager):
        super().__init__("Edit")
        self.mod_manager = mod_manager

        # GameBanana URL section
        self.url = InputButtonWidget(
            "GameBanana URL", 
            [
                InputButton(text="Open", callback=None),
                InputButton(text="Get", callback=None, highlight=True)
            ]
        )
        self.body.addWidget(self.url)
        
        # Thumbnail preview
        thumbnail = QLabel()
        preview_dir = "assets/img/preview.webp"
        preview_img = QPixmap(preview_dir).scaled(314, 314, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        thumbnail.setPixmap(preview_img)
        self.body.addWidget(thumbnail)
        
        # Mod Name
        self._add_label("Mod Name")
        self.mod_name = QLineEdit()
        self.mod_name.setPlaceholderText("Enter mod name")
        self.body.addWidget(self.mod_name)

        # Character
        self._add_label("Character")
        self.character = CheckableComboBox(Fighter.list(), [False] * (len(Fighter.list()) + 1), False, "Select Characters")
        self.body.addWidget(self.character)

        # Slots
        self._add_label("Slots")
        self.slots = CheckableComboBox([f"C{i:02d}" for i in range(256)], [False] * 257, False, "Select Slots")
        self.body.addWidget(self.slots)

        # Category
        self._add_label("Category")
        self.category = SingleComboBox()
        self.category.addItems(Category.list())
        self.body.addWidget(self.category)

        # Authors
        self._add_label("Authors")
        self.author = QLineEdit()
        self.author.setPlaceholderText("Enter author name(s)")
        self.body.addWidget(self.author)

        # Version
        self._add_label("Version")
        self.version = QLineEdit()
        self.version.setPlaceholderText("1.0.0")
        self.version.textChanged.connect(lambda text: limit_version(self.version))
        self.body.addWidget(self.version)
        
        # Description
        self._add_label("Description")
        self.description = QTextEdit()
        self.description.setPlaceholderText("Enter description")
        self.description.setMinimumHeight(80)
        self.description.setMaximumHeight(120)
        self.body.addWidget(self.description)

        # Elements
        self._add_label("Elements")
        self.elements = CheckableComboBox(Element.list(), [False] * (len(Element.list()) + 1), False, "Select Elements")
        self.body.addWidget(self.elements)

        # Wifi Safe
        self._add_label("Wifi Safe")
        self.wifi = SingleComboBox()
        self.wifi.addItems(Wifi.list())
        self.body.addWidget(self.wifi)

        # Display Name
        self._add_label("Display Name")
        self.display = QLineEdit()
        self.display.setPlaceholderText("Auto-generated display name")
        self.body.addWidget(self.display)

        # Folder Name
        self._add_label("Folder Name")
        self.folder = QLineEdit()
        self.folder.setPlaceholderText("Auto-generated folder name")
        self.body.addWidget(self.folder)
        
        self.body.addStretch()

        # Footer buttons
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.reset)
        apply_button = QPushButton("Apply")
        apply_button.setStyleSheet(MAIN_BUTTON)
        self.footer.addWidget(clear_button)
        self.footer.addWidget(apply_button)
    
    def _add_label(self, text: str):
        """Helper to add a consistent label above input fields"""
        label = QLabel(text)
        label_font = QFont(FONT, BODY_FONT_SIZE)
        label_font.setBold(True)
        label.setFont(label_font)
        self.body.addWidget(label)
    
    def reset(self):
        """Clear all fields to their default state"""
        self.url.clear()
        self.mod_name.clear()
        self.character.reset()
        self.slots.reset()
        self.category.setCurrentIndex(0)
        self.author.clear()
        self.version.clear()
        self.description.clear()
        self.elements.reset()
        self.wifi.setCurrentIndex(0)
        self.display.clear()
        self.folder.clear()