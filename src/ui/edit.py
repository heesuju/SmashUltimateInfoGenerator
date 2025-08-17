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
from src.constants.categories import CATEGORIES
from src.constants.styles import MAIN_BUTTON

WIDTH = 300
FONT = "Arial"
FONT_SIZE = 10

BODY_FONT_SIZE = 8

class Edit(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(340)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        main_layout = QVBoxLayout()

        main_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(main_layout)

        # Scrollable area for all content except buttons
        

        
        details_label = QLabel("Edit")
        title_font = QFont(FONT, FONT_SIZE)  # Set the font and font size
        title_font.setBold(True)
        details_label.setFont(title_font)
        main_layout.addWidget(details_label)

        thumbnail = QLabel()
        preview_dir = "assets/img/preview.webp"
        preview_img = QPixmap(preview_dir).scaled(320, WIDTH, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        thumbnail.setPixmap(preview_img)
        main_layout.addWidget(thumbnail)

        scroll = QScrollArea()
        scroll.setStyleSheet("QScrollArea { border-radius: 0px; border: none; }")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # Disable horizontal scroll
        main_layout.addWidget(scroll)

        self.frame = QFrame()
        self.frame.setStyleSheet("QFrame { border-radius: 5px; border: 1px; }")
        frame_layout = VBox(margin=0, spacing=10)
        self.frame.setLayout(frame_layout)
        scroll.setWidget(self.frame)


        self.url_group = HBox()
        frame_layout.addLayout(self.url_group)

        self.url = QLineEdit()
        self.url.setPlaceholderText("Gamebanana URL")
        self.url_group.addWidget(self.url)

        self.open_url = QPushButton("OPEN")
        self.open_url.setStyleSheet("""QPushButton {
        border: 0px;
        border-top-left-radius: 0px;
        border-bottom-left-radius: 0px;
        border-top-right-radius: 0px;
        border-bottom-right-radius: 0px;
    }
                                    """)
        self.url_group.addWidget(self.open_url)

        self.fetch_data = QPushButton("GET")
        self.fetch_data.setStyleSheet(MAIN_BUTTON)
        self.url_group.addWidget(self.fetch_data)
        
        self.mod_name = QLineEdit()
        self.mod_name.setPlaceholderText("Mod Name")
        frame_layout.addWidget(self.mod_name)
        
        self.author = QLineEdit()
        self.author.setPlaceholderText("Author Name")
        frame_layout.addWidget(self.author)

        self.version = QLineEdit()
        self.version.setPlaceholderText("Version")
        frame_layout.addWidget(self.version)

        self.category = QComboBox()
        self.category.addItem("Category")
        self.category.addItems(CATEGORIES)
        self.category.setEditable(True)  # ComboBox itself is not editable
        self.category.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # Prevent adding new items
        frame_layout.addWidget(self.category)

        self.character = QComboBox()
        self.character.addItem("Characters")
        self.character.addItems(CATEGORIES)
        self.character.setEditable(True)  # ComboBox itself is not editable
        self.character.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # Prevent adding new items
        frame_layout.addWidget(self.character)

        self.elements = QComboBox()
        self.elements.addItem("All Elements")
        self.elements.addItems(CATEGORIES)
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

        frame_layout.addStretch(1)

        button_layout = QHBoxLayout()
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.reset)
        apply_button = QPushButton("Apply")
        apply_button.setStyleSheet(MAIN_BUTTON)
        button_layout.addWidget(clear_button)
        button_layout.addWidget(apply_button)

        main_layout.addLayout(button_layout)

        # Set the background color using QPalette
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor('red'))
        self.setPalette(palette)
    
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