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
from src.constants.categories import CATEGORIES
from src.constants.styles import MAIN_BUTTON

WIDTH = 300
FONT = "Arial"
FONT_SIZE = 10

BODY_FONT_SIZE = 8

class Config(QWidget):
    def __init__(self):
        super().__init__()
        layout = VBox()
        self.setLayout(layout)
        self.setFixedWidth(340)
        # self.setAutoFillBackground(True)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        
        self.frame = QFrame()
        self.frame.setFrameShape(QFrame.Shape.Box)
        self.frame.setAutoFillBackground(True)
        self.frame.setStyleSheet("""QFrame {
                                 border-radius: 0px;
                                 }""")
        frame_layout = VBox(margin=10, spacing=10)
        self.frame.setLayout(frame_layout)

        details_label = QLabel("Config")
        title_font = QFont(FONT, FONT_SIZE)  # Set the font and font size
        title_font.setBold(True)
        details_label.setFont(title_font)
        frame_layout.addWidget(details_label)

        self.directory = QLineEdit()
        self.directory.setPlaceholderText("Enter the mod directory(e.g. sd:/ultimate/mods)")
        frame_layout.addWidget(self.directory)

        self.theme = QComboBox()
        self.theme.addItems(["dark", "light"])
        self.theme.setEditable(False)  # ComboBox itself is not editable
        self.theme.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # Prevent adding new items
        frame_layout.addWidget(self.theme)

        frame_layout.addStretch(1)

        button_layout = QHBoxLayout()
        restore_button = QPushButton("Restore")
        restore_button.clicked.connect(self.reset)
        save_button = QPushButton("Save")
        save_button.setStyleSheet(MAIN_BUTTON)
        button_layout.addWidget(restore_button)
        button_layout.addWidget(save_button)
        frame_layout.addLayout(button_layout)

        # Set the background color using QPalette
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor('red'))
        self.setPalette(palette)

        layout.addWidget(self.frame)
    
    def reset(self):
        """
        Resets all filter fields to their default state.
        """
        pass