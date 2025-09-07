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
    QSpinBox
)
from PyQt6.QtGui import QPixmap, QColor, QPalette, QIcon, QFont
from PyQt6.QtCore import Qt, QSize, QPoint, QPointF
from src.ui.components.layout import HBox, VBox
from src.ui.components.checkbox_group import CheckboxGroup
from src.constants.enums import Category, Element
from src.constants.styles import MAIN_BUTTON
from src.managers.filter_manager import FilterManager, FilterParameters
from src.managers.data_manager import DataManager
from src.constants.enums import *
from src.ui.components.side_panel import SidePanel

WIDTH = 300
FONT = "Arial"
FONT_SIZE = 10

BODY_FONT_SIZE = 8

class FilterPanel(SidePanel):
    def __init__(self, filter_manager:FilterManager):
        super().__init__("Filter")
        self.filter_manager = filter_manager
        
        self.author = QLineEdit()
        self.author.setPlaceholderText("Author Name")
        self.body.addWidget(self.author)

        self.category = QComboBox()
        self.category.addItem("All Categories")
        self.category.addItems(Category.list())
        self.category.setEditable(True)  # ComboBox itself is not editable
        self.category.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # Prevent adding new items
        self.body.addWidget(self.category)

        self.series = QComboBox()
        self.series.addItem("All Series")
        self.series.addItems(Series.list())
        self.series.setEditable(True)  # ComboBox itself is not editable
        self.series.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # Prevent adding new items
        self.body.addWidget(self.series)

        self.character = QComboBox()
        self.character.addItem("All Characters")
        self.character.addItems(DataManager.get_character_names())
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

        self.wifi = CheckboxGroup("Wifi-safe", Wifi.list(), [True, True, True])  
        self.body.addWidget(self.wifi)

        self.info = CheckboxGroup("Info.toml", InfoToml.list(), [True, True])  
        self.body.addWidget(self.info)
        
        self.visibility = CheckboxGroup("Visibility", Visibility.list(), [True, False])  
        self.body.addWidget(self.visibility)

        self.enabled = CheckboxGroup("State", EnabledState.list(), [True, True])  
        self.body.addWidget(self.enabled)

        self.body.addStretch(1)

        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.reset)
        apply_button = QPushButton("Apply")
        apply_button.setStyleSheet(MAIN_BUTTON)
        apply_button.clicked.connect(self.apply)
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
    
    def apply(self):
        self.filter_manager.params.character = [DataManager.get_character_by_custom(self.character.currentText())] if self.character.currentText() and self.character.currentIndex() != 0 else []
        self.filter_manager.params.authors = self.author.text()
        self.filter_manager.params.category = [Category(self.category.currentText())] if self.category.currentText() and self.category.currentIndex() != 0 else []
        self.filter_manager.params.series = [Series(self.series.currentText())] if self.series.currentIndex() != 0 else []
        self.filter_manager.params.elements = [Element(self.elements.currentText())] if self.elements.currentIndex() != 0 else []
        self.filter_manager.params.slot_min=self.min_value.value()
        self.filter_manager.params.slot_max=self.max_value.value()
        self.filter_manager.on_change()
