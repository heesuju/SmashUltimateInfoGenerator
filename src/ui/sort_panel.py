from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QComboBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap
from src.ui.components.side_panel import SidePanel
from src.ui.components.toggle_button import ToggleButton
from src.constants.styles import MAIN_BUTTON
from src.models.settings import SortRule
from src.managers.data_manager import ButtonIcons

FONT = "Arial"
FONT_SIZE = 10
BODY_FONT_SIZE = 8


class SortPanel(SidePanel):
    def __init__(self, config_manager):
        super().__init__("Sort")
        self.config_manager = config_manager
        
        # Sorting label
        sorting_label = QLabel("Sorting")
        sorting_label.setFont(QFont(FONT, FONT_SIZE))
        self.body.addWidget(sorting_label)
        
        # Sorting options for comboboxes
        sort_options = ["None", "Category", "Characters", "Mod Name", "Authors", "Slots"]
        
        # Sort by row 1
        sort_row_1 = QHBoxLayout()
        sort_label_1 = QLabel("Sort by:")
        sort_label_1.setFont(QFont(FONT, BODY_FONT_SIZE))
        sort_label_1.setFixedWidth(60)
        sort_row_1.addWidget(sort_label_1)
        self.sort_combo_1 = QComboBox()
        self.sort_combo_1.addItems(sort_options)
        self.sort_combo_1.currentIndexChanged.connect(self.validate_sort_selections)
        sort_row_1.addWidget(self.sort_combo_1)
        self.sort_toggle_1 = ToggleButton(
            ButtonIcons.SORT_ASC.value, ButtonIcons.SORT_DESC.value,
            lambda: None, lambda: None, 24, initial_state=True
        )
        sort_row_1.addWidget(self.sort_toggle_1)
        self.body.addLayout(sort_row_1)
        
        # Sort by row 2
        sort_row_2 = QHBoxLayout()
        sort_label_2 = QLabel("Then by:")
        sort_label_2.setFont(QFont(FONT, BODY_FONT_SIZE))
        sort_label_2.setFixedWidth(60)
        sort_row_2.addWidget(sort_label_2)
        self.sort_combo_2 = QComboBox()
        self.sort_combo_2.addItems(sort_options)
        self.sort_combo_2.currentIndexChanged.connect(self.validate_sort_selections)
        sort_row_2.addWidget(self.sort_combo_2)
        self.sort_toggle_2 = ToggleButton(
            ButtonIcons.SORT_ASC.value, ButtonIcons.SORT_DESC.value,
            lambda: None, lambda: None, 24, initial_state=True
        )
        sort_row_2.addWidget(self.sort_toggle_2)
        self.body.addLayout(sort_row_2)
        
        # Sort by row 3
        sort_row_3 = QHBoxLayout()
        sort_label_3 = QLabel("Then by:")
        sort_label_3.setFont(QFont(FONT, BODY_FONT_SIZE))
        sort_label_3.setFixedWidth(60)
        sort_row_3.addWidget(sort_label_3)
        self.sort_combo_3 = QComboBox()
        self.sort_combo_3.addItems(sort_options)
        self.sort_combo_3.currentIndexChanged.connect(self.validate_sort_selections)
        sort_row_3.addWidget(self.sort_combo_3)
        self.sort_toggle_3 = ToggleButton(
            ButtonIcons.SORT_ASC.value, ButtonIcons.SORT_DESC.value,
            lambda: None, lambda: None, 24, initial_state=True
        )
        sort_row_3.addWidget(self.sort_toggle_3)
        self.body.addLayout(sort_row_3)
        
        # Sort by row 4
        sort_row_4 = QHBoxLayout()
        sort_label_4 = QLabel("Then by:")
        sort_label_4.setFont(QFont(FONT, BODY_FONT_SIZE))
        sort_label_4.setFixedWidth(60)
        sort_row_4.addWidget(sort_label_4)
        self.sort_combo_4 = QComboBox()
        self.sort_combo_4.addItems(sort_options)
        self.sort_combo_4.currentIndexChanged.connect(self.validate_sort_selections)
        sort_row_4.addWidget(self.sort_combo_4)
        self.sort_toggle_4 = ToggleButton(
            ButtonIcons.SORT_ASC.value, ButtonIcons.SORT_DESC.value,
            lambda: None, lambda: None, 24, initial_state=True
        )
        sort_row_4.addWidget(self.sort_toggle_4)
        self.body.addLayout(sort_row_4)
        
        self.body.addStretch(1)

        clear_button = QPushButton("Reset")
        clear_button.clicked.connect(self.reset)
        apply_button = QPushButton("Apply")
        apply_button.setStyleSheet(MAIN_BUTTON)
        apply_button.clicked.connect(self.apply)
        self.footer.addWidget(clear_button)
        self.footer.addWidget(apply_button)
        
        # Load saved sort rules from config
        self.load_sort_rules()
    

    
    def validate_sort_selections(self):
        """Validate that no two dropdowns have the same non-None selection"""
        combos = [self.sort_combo_1, self.sort_combo_2, self.sort_combo_3, self.sort_combo_4]
        selected_values = []
        
        for combo in combos:
            value = combo.currentText()
            if value != "None" and value in selected_values:
                # Duplicate found - reset this combo to None
                combo.blockSignals(True)
                combo.setCurrentText("None")
                combo.blockSignals(False)
                return
            if value != "None":
                selected_values.append(value)
    
    def reset(self):
        """Reset sort combos to saved settings from config"""
        self.load_sort_rules()
    
    def apply(self):
        """Save sort rules to config and trigger filter update"""
        # Build sort rules from dropdowns
        sort_rules = []
        combos = [(self.sort_combo_1, self.sort_toggle_1), 
                  (self.sort_combo_2, self.sort_toggle_2),
                  (self.sort_combo_3, self.sort_toggle_3),
                  (self.sort_combo_4, self.sort_toggle_4)]
        
        for priority, (combo, toggle) in enumerate(combos, start=1):
            sort_name = combo.currentText()
            if sort_name != "None":
                is_asc = toggle.toggle_state  # True = ASC, False = DESC
                sort_rules.append(SortRule(name=sort_name, priority=priority, asc=is_asc))
        
        # Save to config
        self.config_manager.config.sort_rules = sort_rules
        self.config_manager.save()
        
        # Trigger sort change callback if set
        if hasattr(self, 'on_sort_change_callback') and self.on_sort_change_callback:
            self.on_sort_change_callback(sort_rules)
    
    def load_sort_rules(self):
        """Load saved sort rules from config and set combobox values"""
        sort_rules = self.config_manager.config.sort_rules
        combos = [(self.sort_combo_1, self.sort_toggle_1),
                  (self.sort_combo_2, self.sort_toggle_2),
                  (self.sort_combo_3, self.sort_toggle_3),
                  (self.sort_combo_4, self.sort_toggle_4)]
        
        # Reset all combos first
        for combo, toggle in combos:
            combo.blockSignals(True)
            combo.setCurrentText("None")
            toggle.set_state(True)  # True = ASC
            combo.blockSignals(False)
        
        # Apply saved rules
        for rule in sorted(sort_rules, key=lambda r: r.priority):
            if 1 <= rule.priority <= 4:
                combo, toggle = combos[rule.priority - 1]
                combo.blockSignals(True)
                combo.setCurrentText(rule.name)
                toggle.set_state(rule.asc)  # True = ASC, False = DESC
                combo.blockSignals(False)
    
    
    def set_sort_change_callback(self, callback):
        """Set callback to be called when sort rules change"""
        self.on_sort_change_callback = callback
    
    def get_sort_rules(self):
        """Get current sort rules from config"""
        return self.config_manager.config.sort_rules
