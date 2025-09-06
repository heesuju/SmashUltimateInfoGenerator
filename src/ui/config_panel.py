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
from functools import partial
from PyQt6.QtGui import QPixmap, QColor, QPalette, QIcon, QFont
from PyQt6.QtCore import Qt, QSize, QPoint, QPointF
from src.ui.components.layout import HBox, VBox
from src.ui.components.checkbox_group import CheckboxGroup
from src.constants.styles import MAIN_BUTTON
from src.constants.ui import ButtonIcons
from src.constant import Theme
from src.managers.config_manager import ConfigManager
from src.ui.components.side_panel import SidePanel
from src.ui.components.input_button_widget import InputButtonWidget, InputButton
from src.ui.common import choose_folder
from src.utils.common import is_valid_dir

class Config(SidePanel):
    def __init__(self, config_manager:ConfigManager):
        super().__init__("Config")
        self.config_manager = config_manager
        
        self.root_dir = InputButtonWidget("Enter mod directory", InputButton(text="Browse", img=ButtonIcons.BROWSE, callback=self.choose_root_dir))
        self.body.addWidget(self.root_dir)

        self.cache_dir = InputButtonWidget("Enter cache directory", InputButton(text="Browse", img=ButtonIcons.BROWSE, callback=self.choose_cache_dir))
        self.body.addWidget(self.cache_dir)

        self.theme_drop = QComboBox()
        self.theme_drop.addItems(Theme.list())
        self.theme_drop.setEditable(False)  # ComboBox itself is not editable
        self.theme_drop.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # Prevent adding new items
        self.body.addWidget(self.theme_drop)

        restore_btn = QPushButton("Restore")
        restore_btn.clicked.connect(self.init)
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet(MAIN_BUTTON)
        save_btn.clicked.connect(self.save)

        self.footer.addWidget(restore_btn)
        self.footer.addWidget(save_btn)
        
        self.body.addStretch(1)
        self.init()
    
    def init(self):
        """
        Initialize all values to their default state.
        """
        theme = str(self.config_manager.config.theme)
        self.root_dir.set_text(self.config_manager.config.root_dir)
        self.cache_dir.set_text(self.config_manager.config.cache_dir)
        self.theme_drop.setCurrentText(theme)
        self.check_validity()

    def save(self):
        if self.check_validity():
            self.config_manager.config.theme = Theme(self.theme_drop.currentText())
            self.config_manager.config.root_dir = self.root_dir.get_text()
            self.config_manager.config.cache_dir = self.cache_dir.get_text()
            self.config_manager.save()
        else:
            pass

    def choose_root_dir(self):
        root_dir = choose_folder(self, self.config_manager.config.root_dir)
        if root_dir:
            self.root_dir.set_text(root_dir)
        
    def choose_cache_dir(self):
        cache_dir = choose_folder(self, self.config_manager.config.cache_dir)
        if cache_dir:
            self.cache_dir.set_text(cache_dir)

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
        
        return is_valid