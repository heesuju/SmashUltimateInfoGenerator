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
from src.ui.components.multi_combobox import CheckableComboBox

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

        self.category = CheckableComboBox(Category.list(), [True] * (len(Category.list()) + 1), True, "All Categories")
        self.body.addWidget(self.category)

        self.series = QComboBox()
        self.series.addItem("All Series")
        self.series.addItems(Series.list())
        self.series.setEditable(True)  # ComboBox itself is not editable
        self.series.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # Prevent adding new items
        self.body.addWidget(self.series)

        characters = DataManager.get_character_names()
        defaults = ([True] * (len(characters) + 1))
        self.character = CheckableComboBox(characters, defaults, True, "All Characters")
        self.body.addWidget(self.character)

        self.elements = CheckableComboBox(Element.list(), ([True] * (len(Element.list()) + 1)), True, "All Elements")
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

        self.wifi = CheckableComboBox(Wifi.list(), ([True] * (len(Wifi.list()) + 1)), True, "All Wifi States")
        self.body.addWidget(self.wifi)

        self.info = CheckableComboBox(InfoToml.list(), ([True] * (len(InfoToml.list()) + 1)), True, "All Info States")  
        self.body.addWidget(self.info)
        

        self.visibility = CheckableComboBox(Visibility.list(), ([True] * (len(Visibility.list()) + 1)), True, "All Visibility")  
        self.body.addWidget(self.visibility)

        self.enabled = CheckableComboBox(EnabledState.list(), ([True] * (len(EnabledState.list()) + 1)), True, "All Enabled States")  
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
        self.category.reset()
        self.series.setCurrentIndex(0)
        self.character.reset()
        self.elements.reset()
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
