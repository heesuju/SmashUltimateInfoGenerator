from PyQt6.QtWidgets import (
    QWidget, 
    QHBoxLayout, 
    QVBoxLayout, 
    QPushButton, 
    QLabel, 
    QSizePolicy, 
    QListWidget, 
    QListWidgetItem, 
    QFrame, 
    QLineEdit,
    QComboBox,
    QCheckBox,
    QGroupBox,
    QSpinBox,
    QTreeWidget,
    QTreeWidgetItem,
    QScrollArea
)
from PyQt6 import QtGui, QtCore
from PyQt6.QtGui import QPixmap, QColor, QPalette, QIcon, QFont
from PyQt6.QtCore import Qt, QSize, QPoint, QPointF
from src.ui.components.layout import HBox, VBox
from src.ui.components.checkbox_group import CheckboxGroup
from src.constants.styles import MAIN_BUTTON
from src.ui.components.side_panel import SidePanel
from src.ui.components.checkbox_tree import CheckBoxTree
from src.constants.enums import Category, Element, Fighter
from src.ui.components.input_button_widget import InputButtonWidget, InputButton
from src.ui.components.multi_combobox import CheckableComboBox
from src.ui.components.collapsible_text_edit import ShrinkingTextEdit
from src.managers.mod_manager import ModManager

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

        # self.fetch_data = QPushButton("GET")
        # self.fetch_data.setStyleSheet(MAIN_BUTTON)
        # self.url_group.addWidget(self.fetch_data)
        
        self.display = QLineEdit()
        self.display.setPlaceholderText("Display Name")
        self.body.addWidget(self.display)

        self.folder = QLineEdit()
        self.folder.setPlaceholderText("Folder Name")
        self.body.addWidget(self.folder)
        
        self.mod_name = QLineEdit()
        self.mod_name.setPlaceholderText("Mod Name")
        self.body.addWidget(self.mod_name)
        
        self.author = QLineEdit()
        self.author.setPlaceholderText("Author Name")
        self.body.addWidget(self.author)

        self.version = QLineEdit()
        self.version.setPlaceholderText("Version")
        self.body.addWidget(self.version)

        self.category = QComboBox()
        self.category.addItem("Category")
        self.category.addItems(Category.list())
        self.category.setEditable(True)  # ComboBox itself is not editable
        self.category.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # Prevent adding new items
        self.body.addWidget(self.category)
        
        self.slots = CheckableComboBox()
        for c in range(255):
            self.slots.add_item(str(c))
        self.slots.setCurrentText("Slots")
        self.body.addWidget(self.slots)

        self.wifi = CheckboxGroup("Wifi-safe", ["Safe", "Unknown", "Unsafe"], [True, True, True])  
        self.body.addWidget(self.wifi)

        self.combo = CheckableComboBox()
        for c in Fighter.list():
            self.combo.add_item(c)
        self.combo.setCurrentText("Characters")
        self.body.addWidget(self.combo)
        

        self.tree_widget = CheckableComboBox()
        for i in Element.list():
            self.tree_widget.add_item(i)
        self.tree_widget.setCurrentText("Elements")
        self.body.addWidget(self.tree_widget)
        
        self.description = ShrinkingTextEdit("Description")
        self.body.addWidget(self.description, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
        # self.body.addWidget(self.description)
        
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