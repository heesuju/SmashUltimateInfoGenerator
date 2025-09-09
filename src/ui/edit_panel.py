import re
from PyQt6.QtWidgets import ( QWidget, QHBoxLayout, QVBoxLayout,  QPushButton,  QLabel, QTreeWidgetItem,QScrollArea,
    QSizePolicy, QListWidget, QListWidgetItem, QFrame, QLineEdit,QComboBox,QCheckBox,QGroupBox,QSpinBox,QTreeWidget,
)
from PyQt6 import QtGui, QtCore
from PyQt6.QtGui import QPixmap, QColor, QPalette, QIcon, QFont
from PyQt6.QtCore import Qt, QSize, QPoint, QPointF
from src.ui.components.layout import HBox, VBox
from src.ui.components.checkbox_group import CheckboxGroup
from src.constants.styles import MAIN_BUTTON
from src.ui.components.side_panel import SidePanel
from src.ui.components.checkbox_tree import CheckBoxTree
from src.constants.enums import Category, Element, Fighter, Wifi
from src.ui.components.input_button_widget import InputButtonWidget, InputButton
from src.ui.components.multi_combobox import CheckableComboBox
from src.ui.components.collapsible_text_edit import ShrinkingTextEdit
from src.ui.components.top_label_wrapper import TopLabelWrapper
from src.ui.components.line_edit import LineEdit
from src.ui.components.combo_box import ComboBox
from src.managers.mod_manager import ModManager
from src.constants.strings import (
    PLACEHOLDER_EDIT_DISPLAY_NAME,
    PLACEHOLDER_EDIT_FOLDER_NAME,
    PLACEHOLDER_EDIT_MOD_NAME,
    PLACEHOLDER_EDIT_VERSION,
    PLACEHOLDER_EDIT_AUTHORS
)
from src.ui.components.validators import limit_version

class EditPanel(SidePanel):
    def __init__(self, mod_manager:ModManager):
        super().__init__("Edit")
        self.mod_manager = mod_manager

        self.url = InputButtonWidget(
            "Gamebanana URL", 
            [
                InputButton(text="Open", callback=None),
                InputButton(text="Get", callback=None, highlight=True)
            ]
        )
        self.body.addWidget(self.url)
        
        thumbnail = QLabel()
        preview_dir = "assets/img/preview.webp"
        preview_img = QPixmap(preview_dir).scaled(314, 314, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        thumbnail.setPixmap(preview_img)
        self.body.addWidget(thumbnail)
        
        self.mod_name = LineEdit(PLACEHOLDER_EDIT_MOD_NAME)
        self.body.addWidget(TopLabelWrapper(self.mod_name, "Mod Name"))

        self.character = CheckableComboBox(Fighter.list())
        self.body.addWidget(TopLabelWrapper(self.character, "Character"))

        self.slots = CheckableComboBox(range(255))
        self.body.addWidget(TopLabelWrapper(self.slots, "Slots"))

        self.category = ComboBox("Category", Category.list())
        self.body.addWidget(TopLabelWrapper(self.category, "Category"))

        self.author = LineEdit(PLACEHOLDER_EDIT_AUTHORS)
        self.body.addWidget(TopLabelWrapper(self.author, "Authors"))

        self.version = LineEdit(PLACEHOLDER_EDIT_VERSION, limit_version)
        self.body.addWidget(TopLabelWrapper(self.version, "Version"))
        
        self.description = ShrinkingTextEdit("Enter description")
        self.body.addWidget(TopLabelWrapper(self.description, "Description"), alignment=QtCore.Qt.AlignmentFlag.AlignTop)
        self.description.setFixedHeight(self.description.line_height)

        self.elements = CheckableComboBox(Element.list())
        self.body.addWidget(TopLabelWrapper(self.elements, "Elements"))

        self.wifi = ComboBox("Wifi Safe", Wifi.list())
        self.body.addWidget(TopLabelWrapper(self.wifi, "Wifi Safe"))

        self.display = LineEdit(PLACEHOLDER_EDIT_DISPLAY_NAME)
        self.body.addWidget(TopLabelWrapper(self.display, "Display Name"))

        self.folder = LineEdit(PLACEHOLDER_EDIT_FOLDER_NAME)
        self.body.addWidget(TopLabelWrapper(self.folder, "Folder Name"))        
        
        self.body.addStretch()

        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.reset)
        apply_button = QPushButton("Apply")
        apply_button.setStyleSheet(MAIN_BUTTON)
        self.footer.addWidget(clear_button)
        self.footer.addWidget(apply_button)
    
    def reset(self):
        """
        Resets all filter fields to their default state.
        """
        self.author.clear()
        self.category.setCurrentIndex(0)
        self.series.setCurrentIndex(0)
        self.character.setCurrentIndex(0)
        self.elements.setCurrentIndex(0)
        self.min_value.setValue(0)
        self.max_value.setValue(255)
        
        for checkbox in [self.wifi, self.info, self.visibility, self.enabled]:
            checkbox.reset()