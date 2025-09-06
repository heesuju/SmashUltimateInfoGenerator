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
from src.constant import Category, Element
from src.constants.styles import MAIN_BUTTON

WIDTH = 300
FONT = "Arial"
FONT_SIZE = 10

BODY_FONT_SIZE = 8

class Filter(QWidget):
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
                                 border: none;
                                 }""")
        frame_layout = VBox(margin=10, spacing=10)
        self.frame.setLayout(frame_layout)

        details_label = QLabel("Filter")
        title_font = QFont(FONT, FONT_SIZE)  # Set the font and font size
        title_font.setBold(True)
        details_label.setFont(title_font)
        frame_layout.addWidget(details_label)

        self.author = QLineEdit()
        self.author.setPlaceholderText("Author Name")
        frame_layout.addWidget(self.author)

        self.category = QComboBox()
        self.category.addItem("All Categories")
        self.category.addItems(Category.list())
        self.category.setEditable(True)  # ComboBox itself is not editable
        self.category.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # Prevent adding new items
        frame_layout.addWidget(self.category)

        self.series = QComboBox()
        self.series.addItem("All Series")
        self.series.addItems(Category.list())
        self.series.setEditable(True)  # ComboBox itself is not editable
        self.series.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # Prevent adding new items
        frame_layout.addWidget(self.series)

        self.character = QComboBox()
        self.character.addItem("All Characters")
        self.character.addItems(Category.list())
        self.character.setEditable(True)  # ComboBox itself is not editable
        self.character.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # Prevent adding new items
        frame_layout.addWidget(self.character)

        self.elements = QComboBox()
        self.elements.addItem("All Elements")
        self.elements.addItems(Element.list())
        self.elements.setEditable(True)  # ComboBox itself is not editable
        self.elements.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # Prevent adding new items
        frame_layout.addWidget(self.elements)
        
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
        frame_layout.addWidget(slots)

        self.wifi = CheckboxGroup("Wifi-safe", ["Safe", "Unknown", "Unsafe"], [True, True, True])  
        frame_layout.addWidget(self.wifi)

        self.info = CheckboxGroup("Info.toml", ["Included", "Not Included"], [True, True])  
        frame_layout.addWidget(self.info)
        
        self.visibility = CheckboxGroup("Visibility", ["Visible", "Hidden"], [True, False])  
        frame_layout.addWidget(self.visibility)

        self.enabled = CheckboxGroup("State", ["Enabled", "Disabled"], [True, True])  
        frame_layout.addWidget(self.enabled)

        frame_layout.addStretch(1)

        button_layout = QHBoxLayout()
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.reset)
        apply_button = QPushButton("Apply")
        apply_button.setStyleSheet(MAIN_BUTTON)
        button_layout.addWidget(clear_button)
        button_layout.addWidget(apply_button)
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
        self.author.clear()
        self.category.setCurrentIndex(0)
        self.series.setCurrentIndex(0)
        self.character.setCurrentIndex(0)
        self.elements.setCurrentIndex(0)
        self.min_value.setValue(0)
        self.max_value.setValue(255)
        
        for checkbox in [self.wifi, self.info, self.visibility, self.enabled]:
            checkbox.reset()