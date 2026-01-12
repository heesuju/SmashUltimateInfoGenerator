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
from src.ui.components.zero_padded_spinbox import ZeroPaddedSpinBox
from src.ui.components.single_combobox import SingleComboBox
from src.ui.components.collapsible_section import CollapsibleSection

WIDTH = 300
FONT = "Arial"
FONT_SIZE = 10

BODY_FONT_SIZE = 8


class FilterPanel(SidePanel):
    def __init__(self, filter_manager:FilterManager, config_manager):
        super().__init__("Filter")
        self.filter_manager = filter_manager
        self.config_manager = config_manager
        
        
        # Filters label
        filters_label = QLabel("Filters")
        filters_label.setFont(QFont(FONT, FONT_SIZE))
        self.body.addWidget(filters_label)
        
        self.author = QLineEdit()
        self.author.setPlaceholderText("Author Name")
        self.body.addWidget(self.author)

        self.category = CheckableComboBox(Category.list(), [True] * (len(Category.list()) + 1), True, "All Categories")
        self.body.addWidget(self.category)

        char_layout = QHBoxLayout()
        
        self.series = SingleComboBox()
        self.series.addItem("All Series")
        self.series.addItems(Series.list())
        char_layout.addWidget(self.series)

        characters = DataManager.get_character_names()
        defaults = ([True] * (len(characters) + 1))
        self.character = CheckableComboBox(characters, defaults, True, "All Characters")
        char_layout.addWidget(self.character)
        
        self.body.addLayout(char_layout)
        
        # Connect event handlers for series-character synchronization
        self.series.currentIndexChanged.connect(self.on_series_changed)
        self.character.model().dataChanged.connect(self.on_character_changed)

        self.elements = CheckableComboBox(Element.list(), ([True] * (len(Element.list()) + 1)), True, "All Elements")
        self.body.addWidget(self.elements)
        
        # Slot filter controls in horizontal layout
        slots_layout = QHBoxLayout()
        self.slot_mode = SingleComboBox()
        self.slot_mode.addItems(["Range", "Single"])
        self.slot_mode.setCurrentIndex(0)  # Default to "Range"
        self.slot_mode.currentIndexChanged.connect(self.on_slot_mode_changed)
        slots_layout.addWidget(self.slot_mode)
        
        self.min_value = ZeroPaddedSpinBox()
        self.min_value.setRange(0, 255)
        self.min_value.setPrefix("C")
        slots_layout.addWidget(self.min_value)
        
        # Range separator
        self.range_separator = QLabel("~")
        self.range_separator.setFont(QFont(FONT, FONT_SIZE))
        self.range_separator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.range_separator.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        slots_layout.addWidget(self.range_separator)
        
        self.max_value = ZeroPaddedSpinBox()
        self.max_value.setRange(0, 255)
        self.max_value.setPrefix("C")
        self.max_value.setValue(255) 
        slots_layout.addWidget(self.max_value)
        
        self.body.addLayout(slots_layout)
        
        self.wifi = CheckableComboBox(Wifi.list(), ([True] * (len(Wifi.list()) + 1)), True, "All Wifi States")
        self.body.addWidget(self.wifi)

        self.info = CheckableComboBox(InfoToml.list(), ([True] * (len(InfoToml.list()) + 1)), True, "All Info States")  
        self.body.addWidget(self.info)
        
        self.enabled = CheckableComboBox(EnabledState.list(), ([True] * (len(EnabledState.list()) + 1)), True, "All Enabled States")  
        self.body.addWidget(self.enabled)
        
        # Include Hidden checkbox
        self.include_hidden = QCheckBox("Include Hidden")
        self.body.addWidget(self.include_hidden)

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
        self.slot_mode.setCurrentIndex(0)  # Reset to "Range"
        self.min_value.setValue(0)
        self.max_value.setValue(255)
        

        for checkbox in [self.wifi, self.info, self.enabled]:
            checkbox.reset()
        
        self.include_hidden.setChecked(False)
        
        # Reset filter manager parameters
        self.filter_manager.reset()
        self.filter_manager.on_change()
    
    def on_slot_mode_changed(self, index:int):
        """When slot mode is changed, update the spinbox states and labels"""
        if index == 0:  # "Range" mode
            self.range_separator.setVisible(True)
            self.max_value.setVisible(True)
        else:  # "Single" mode
            self.range_separator.setVisible(False)
            self.max_value.setVisible(False)
    
    def on_series_changed(self, index:int):
        """When series is changed, update character selection to match the series"""
        # Block character model signals to prevent triggering on_character_changed
        self.character.model().blockSignals(True)
        
        if index == 0:  # "All Series" selected
            # Select all characters
            for i in range(self.character.get_item_count()):
                item = self.character.model().invisibleRootItem().child(i)
                item.setCheckState(Qt.CheckState.Checked)
        else:
            # Get series name and find matching characters
            series_name = self.series.currentText()
            
            # Ignore if it's "Custom" text (not an actual series)
            if series_name == "Custom":
                self.character.model().blockSignals(False)
                return
            
            series_characters = DataManager.get_characters_by_series(series_name)
            
            # Update character checkboxes
            for i in range(self.character.get_item_count()):
                item = self.character.model().invisibleRootItem().child(i)
                char_name = item.text()
                
                # Skip "Select All" item (first item)
                if i == 0 and char_name == "Select All":
                    item.setCheckState(Qt.CheckState.Unchecked)
                    continue
                
                # Check if character belongs to selected series
                if char_name in series_characters:
                    item.setCheckState(Qt.CheckState.Checked)
                else:
                    item.setCheckState(Qt.CheckState.Unchecked)
        
        # Unblock signals and update display
        self.character.model().blockSignals(False)
        self.character.update_display()
    
    def on_character_changed(self):
        """When character selection changes manually, set series text to 'Custom'"""
        # Only change if a specific series is currently selected (index > 0)
        self.series.blockSignals(True)
            
        if len(self.character.get_checked()) == self.character.get_item_count():
            self.series.setCurrentIndex(0)
        else:
            self.series.setCurrentText("Custom")
        self.series.blockSignals(False)
    
    def apply(self):
        # Get all checked characters and convert to Fighter enums
        checked_chars = self.character.get_checked()
        # Filter out "Select All" if present
        checked_chars = [c for c in checked_chars if c != "Select All"]
        self.filter_manager.params.character = [DataManager.get_character_by_custom(c) for c in checked_chars]
        
        # Set author filter
        self.filter_manager.params.authors = self.author.text()
        
        # Get all checked categories
        checked_categories = self.category.get_checked()
        checked_categories = [c for c in checked_categories if c != "Select All"]
        self.filter_manager.params.category = [Category(c) for c in checked_categories]
        
        # Get all checked elements
        checked_elements = self.elements.get_checked()
        checked_elements = [e for e in checked_elements if e != "Select All"]
        self.filter_manager.params.elements = [Element(e) for e in checked_elements]
        
        # Set slot range
        # In single mode, both min and max should be the same value
        if self.slot_mode.currentIndex() == 1:  # Single mode
            self.filter_manager.params.slot_min = self.min_value.value()
            self.filter_manager.params.slot_max = self.min_value.value()
        else:  # Range mode
            self.filter_manager.params.slot_min = self.min_value.value()
            self.filter_manager.params.slot_max = self.max_value.value()
        
        # Get all checked wifi states
        checked_wifi = self.wifi.get_checked()
        checked_wifi = [w for w in checked_wifi if w != "Select All"]
        self.filter_manager.params.wifi = [Wifi(w) for w in checked_wifi]
        
        # Get all checked info states
        checked_info = self.info.get_checked()
        checked_info = [i for i in checked_info if i != "Select All"]
        self.filter_manager.params.info = [InfoToml(i) for i in checked_info]
        
        # Get all checked enabled states
        checked_enabled = self.enabled.get_checked()
        checked_enabled = [e for e in checked_enabled if e != "Select All"]
        self.filter_manager.params.enabled = [EnabledState(e) for e in checked_enabled]
        
        # Set include_hidden flag
        self.filter_manager.params.include_hidden = self.include_hidden.isChecked()
        
        # Trigger filter update
        self.filter_manager.on_change()
    
    def focus_filter(self, filter_type: str):
        """Focus on a specific filter input based on filter type"""
        if filter_type == "authors":
            self.author.setFocus()
            self.author.selectAll()
        elif filter_type == "category":
            self.category.setFocus()
            self.category.showPopup()
        elif filter_type == "character":
            self.character.setFocus()
            self.character.showPopup()
        elif filter_type == "elements":
            self.elements.setFocus()
            self.elements.showPopup()
        elif filter_type == "slots":
            self.min_value.setFocus()
            self.min_value.selectAll()
        elif filter_type == "wifi":
            self.wifi.setFocus()
            self.wifi.showPopup()
        elif filter_type == "info":
            self.info.setFocus()
            self.info.showPopup()
        elif filter_type == "enabled":
            self.enabled.setFocus()
            self.enabled.showPopup()
        elif filter_type == "include_hidden":
            self.include_hidden.setFocus()
    
    def reset_filter(self, filter_type: str):
        """Reset a specific filter UI component to its default state"""
        if filter_type == "authors":
            self.author.clear()
        elif filter_type == "category":
            self.category.reset()
        elif filter_type == "character":
            self.character.reset()
            self.series.setCurrentIndex(0)  # Also reset series
        elif filter_type == "elements":
            self.elements.reset()
        elif filter_type == "slots":
            self.min_value.setValue(0)
            self.max_value.setValue(255)
            self.slot_mode.setCurrentIndex(0)  # Reset to Range mode
            self.on_slot_mode_changed(0)  # Update visibility
        elif filter_type == "wifi":
            self.wifi.reset()
        elif filter_type == "info":
            self.info.reset()
        elif filter_type == "enabled":
            self.enabled.reset()
        elif filter_type == "include_hidden":
            self.include_hidden.setChecked(False)
    

