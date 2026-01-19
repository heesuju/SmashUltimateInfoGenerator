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
    QTextEdit,
    QMessageBox,
    QApplication
)
import os
import sys
from functools import partial
from PyQt6.QtGui import QPixmap, QColor, QPalette, QIcon, QFont
from PyQt6.QtCore import Qt, QSize, QPoint, QPointF
from src.ui.components.layout import HBox, VBox
from src.ui.components.checkbox_group import CheckboxGroup
from src.managers.data_manager import ButtonIcons
from src.constants.enums import Theme
from src.managers.config_manager import ConfigManager
from src.ui.components.side_panel import SidePanel
from src.ui.components.input_button_widget import InputButtonWidget, InputButton
from src.ui.components.format_editor import FormatEditor
from src.ui.common import choose_folder
from src.utils.common import is_valid_dir

class Config(SidePanel):
    def __init__(self, config_manager:ConfigManager):
        super().__init__("Config")
        self.config_manager = config_manager
        
        self.root_dir = InputButtonWidget("Enter mod directory", InputButton(img=ButtonIcons.BROWSE, callback=self.choose_root_dir))
        self.body.addWidget(self.root_dir)

        self.cache_dir = InputButtonWidget("Enter cache directory", InputButton(img=ButtonIcons.BROWSE, callback=self.choose_cache_dir))
        self.body.addWidget(self.cache_dir)

        self.export_dir = InputButtonWidget("Enter export directory", InputButton(img=ButtonIcons.BROWSE, callback=self.choose_export_dir))
        self.body.addWidget(self.export_dir)

        self.theme_drop = QComboBox()
        self.theme_drop.addItems(Theme.list())
        self.theme_drop.setEditable(False)  # ComboBox itself is not editable
        self.theme_drop.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # Prevent adding new items
        self.body.addWidget(self.theme_drop)

        # Name Format Settings
        format_group = QGroupBox("Name Format Settings")
        format_layout = QVBoxLayout()
        
        # Folder Name Format
        folder_format_label = QLabel("Folder Name Format:")
        folder_format_label.setStyleSheet("font-weight: bold; margin-top: 4px;")
        format_layout.addWidget(folder_format_label)
        
        self.folder_name_format = FormatEditor(
            placeholder_text="{category}_{characters}[{slots}]_{mod}",
            sample_data={
                "category": "Fighter",
                "characters": "Sonic",
                "slots": "C01-03",
                "mod": "Shadow"
            }
        )
        format_layout.addWidget(self.folder_name_format)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("color: gray; margin: 8px 0px;")
        format_layout.addWidget(separator)
        
        # Display Name Format
        display_format_label = QLabel("Display Name Format:")
        display_format_label.setStyleSheet("font-weight: bold; margin-top: 4px;")
        format_layout.addWidget(display_format_label)
        
        self.display_name_format = FormatEditor(
            placeholder_text="{characters} {slots} {mod}",
            sample_data={
                "category": "Fighter",
                "characters": "Sonic",
                "slots": "C01-03",
                "mod": "Shadow"
            }
        )
        format_layout.addWidget(self.display_name_format)
        
        format_group.setLayout(format_layout)
        self.body.addWidget(format_group)

        # Cache management section
        cache_group = QGroupBox("Cache Management")
        cache_layout = QVBoxLayout()
        
        cache_info = QLabel("Clear scan cache to force rescan of all mods on next load.")
        cache_info.setWordWrap(True)
        cache_layout.addWidget(cache_info)
        
        clear_cache_btn = QPushButton("Clear Scan Cache")
        clear_cache_btn.clicked.connect(self.clear_scan_cache)
        cache_layout.addWidget(clear_cache_btn)
        
        cache_group.setLayout(cache_layout)
        self.body.addWidget(cache_group)

        self.add_footer_button("Restore", self.init, icon=ButtonIcons.RESTORE.value)
        self.add_footer_button("Save", self.save, primary=True, icon=ButtonIcons.SAVE.value)
        
        self.body.addStretch(1)
        self.init()
    
    def init(self):
        """
        Initialize all values to their default state.
        """
        theme = str(self.config_manager.config.theme)
        self.root_dir.set_text(self.config_manager.config.root_dir)
        self.cache_dir.set_text(self.config_manager.config.cache_dir)
        self.export_dir.set_text(self.config_manager.config.export_dir)
        self.theme_drop.setCurrentText(theme)
        self.folder_name_format.set_text(self.config_manager.config.name_rules.folder_name_format)
        self.folder_name_format.set_cap_slots(self.config_manager.config.name_rules.cap_slots_folder)
        self.display_name_format.set_text(self.config_manager.config.name_rules.display_name_format)
        self.display_name_format.set_cap_slots(self.config_manager.config.name_rules.cap_slots_display)
        self.check_validity()

    def save(self):
        if self.check_validity():
            current_theme = str(self.config_manager.config.theme)
            new_theme = self.theme_drop.currentText()
            
            self.config_manager.config.theme = Theme(new_theme)
            self.config_manager.config.root_dir = self.root_dir.get_text()
            self.config_manager.config.cache_dir = self.cache_dir.get_text()
            self.config_manager.config.export_dir = self.export_dir.get_text()
            self.config_manager.config.name_rules.folder_name_format = self.folder_name_format.get_text()
            self.config_manager.config.name_rules.cap_slots_folder = self.folder_name_format.get_cap_slots()
            self.config_manager.config.name_rules.display_name_format = self.display_name_format.get_text()
            self.config_manager.config.name_rules.cap_slots_display = self.display_name_format.get_cap_slots()
            self.config_manager.save()
            
            if current_theme != new_theme:
                reply = QMessageBox.question(
                    self, 
                    "Restart Required", 
                    "Theme change requires a restart to take full effect.\nRestart now?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.restart_program()
        else:
            pass

    def restart_program(self):
        """Restarts the current program."""
        QApplication.quit()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def choose_root_dir(self):
        root_dir = choose_folder(self, self.config_manager.config.root_dir)
        if root_dir:
            self.root_dir.set_text(root_dir)
        
    def choose_cache_dir(self):
        cache_dir = choose_folder(self, self.config_manager.config.cache_dir)
        if cache_dir:
            self.cache_dir.set_text(cache_dir)
            
    def choose_export_dir(self):
        export_dir = choose_folder(self, self.config_manager.config.export_dir)
        if export_dir:
            self.export_dir.set_text(export_dir)
    
    def clear_scan_cache(self):
        """Clear the mod scan cache"""
        from src.managers.cache_manager import CacheManager
        cache_manager = CacheManager()
        cache_manager.clear_all()

    def check_validity(self)->bool:
        is_valid = True
        root_dir = self.root_dir.get_text()
        cache_dir = self.cache_dir.get_text()

        if not root_dir or not is_valid_dir(root_dir):
            self.root_dir.set_border_color("red")
            is_valid = False
        else:
            self.root_dir.set_border_color("")
        
        if not cache_dir or not is_valid_dir(cache_dir):
            self.cache_dir.set_border_color("red")
            is_valid = False
        else:
            self.cache_dir.set_border_color("")
        
        # Export directory is optional, but if provided must be valid
        export_dir = self.export_dir.get_text()
        if export_dir and not is_valid_dir(export_dir):
            self.export_dir.set_border_color("red")
            is_valid = False
        else:
            self.export_dir.set_border_color("")
        
        return is_valid