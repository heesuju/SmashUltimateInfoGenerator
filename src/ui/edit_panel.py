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
    QScrollArea
)
from PyQt6.QtGui import QPixmap, QColor, QPalette, QIcon, QFont
from PyQt6.QtCore import Qt, QSize, QPoint, QPointF
from src.ui.components.layout import HBox, VBox
from src.ui.components.checkbox_group import CheckboxGroup
from src.constants.styles import MAIN_BUTTON
from src.ui.components.side_panel import SidePanel
from src.constants.enums import Category, Element
from src.ui.components.input_button_widget import InputButtonWidget, InputButton

class EditPanel(SidePanel):
    def __init__(self):
        super().__init__("Edit")
        
        thumbnail = QLabel()
        preview_dir = "assets/img/preview.webp"
        preview_img = QPixmap(preview_dir).scaled(314, 314, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        thumbnail.setPixmap(preview_img)
        self.body.addWidget(thumbnail)

        self.url = InputButtonWidget(
            "Gamebanana URL", 
            [
                InputButton(text="Open", callback=None),
                InputButton(text="Get", callback=None, highlight=True)
            ]
        )
        self.body.addWidget(self.url)

        # self.fetch_data = QPushButton("GET")
        # self.fetch_data.setStyleSheet(MAIN_BUTTON)
        # self.url_group.addWidget(self.fetch_data)
        
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

        self.character = QComboBox()
        self.character.addItem("Characters")
        self.character.addItems(Category.list())
        self.character.setEditable(True)  # ComboBox itself is not editable
        self.character.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # Prevent adding new items
        self.body.addWidget(self.character)

        self.elements = QComboBox()
        self.elements.addItem("All Elements")
        self.elements.addItems(Element.list())
        self.elements.setEditable(True)  # ComboBox itself is not editable
        self.elements.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # Prevent adding new items
        self.body.addWidget(self.elements)
        
        slots = QGroupBox("Slots")
        range_layout = QHBoxLayout()
        slots.setLayout(range_layout)
        self.min_value = QSpinBox()
        self.min_value.setRange(0, 255)
        self.min_value.setPrefix("Min: ")
        range_layout.addWidget(self.min_value)
        self.max_value = QSpinBox()
        self.max_value.setRange(0, 255)
        self.max_value.setPrefix("Max: ")
        self.max_value.setValue(255) 
        range_layout.addWidget(self.max_value)
        self.body.addWidget(slots)

        self.wifi = CheckboxGroup("Wifi-safe", ["Safe", "Unknown", "Unsafe"], [True, True, True])  
        self.body.addWidget(self.wifi)

        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.reset)
        apply_button = QPushButton("Apply")
        apply_button.setStyleSheet(MAIN_BUTTON)
        self.footer.addWidget(clear_button)
        self.footer.addWidget(apply_button)

        
        self.body.addStretch(1)
    
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