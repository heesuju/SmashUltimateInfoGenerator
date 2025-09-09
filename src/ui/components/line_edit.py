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
from src.constants.enums import Category, Element, Fighter
from src.ui.components.input_button_widget import InputButtonWidget, InputButton
from src.ui.components.multi_combobox import CheckableComboBox
from src.ui.components.collapsible_text_edit import ShrinkingTextEdit
from src.ui.components.top_label_wrapper import TopLabelWrapper
from src.managers.mod_manager import ModManager
from src.constants.strings import (
    PLACEHOLDER_EDIT_DISPLAY_NAME,
    PLACEHOLDER_EDIT_FOLDER_NAME,
    PLACEHOLDER_EDIT_MOD_NAME,
    PLACEHOLDER_EDIT_VERSION,
    PLACEHOLDER_EDIT_AUTHORS
)

class LineEdit(QLineEdit):
    def __init__(self, placeholder:str="", validator:callable=None, parent=None):
        super().__init__(parent)
        if placeholder:
            self.setPlaceholderText(placeholder)
        self.validator = validator
        self.textChanged.connect(self._validate_input)

    def _validate_input(self, text):
        """Validate text using the provided function"""
        if self.validator is None:
            return  # no validation
        else:
            text = self.validator(text)
            self.setText(text)