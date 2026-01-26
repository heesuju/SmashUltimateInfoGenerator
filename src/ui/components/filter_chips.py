from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QScrollArea, QPushButton, QLabel, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from src.managers.filter_manager import FilterManager
from src.managers.data_manager import DataManager
from src.constants.enums import Category, Element, Wifi, InfoToml, EnabledState


class FilterChip(QWidget):
    """A single filter chip with a label and close button"""
    clicked = pyqtSignal(str)  # Emits filter type when clicked
    closed = pyqtSignal(str)   # Emits filter type when closed
    
    def __init__(self, label: str, filter_type: str):
        super().__init__()
        self.filter_type = filter_type
        
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)
        self.setLayout(layout)
        
        # Chip label
        self.label = QLabel(label)
        self.label.setFont(QFont("Arial", 9))
        layout.addWidget(self.label)
        
        # Close button
        close_btn = QPushButton("×")
        close_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        close_btn.setFixedSize(16, 16)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(lambda: self.closed.emit(self.filter_type))
        layout.addWidget(close_btn)
        
        # Styling
        self.setStyleSheet("""
            FilterChip {
                background-color: #3a3a3a;
                border: 1px solid #555;
                border-radius: 12px;
            }
            FilterChip:hover {
                background-color: #4a4a4a;
                border-color: #777;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                color: #aaa;
                padding: 0px;
            }
            QPushButton:hover {
                color: #fff;
                background-color: #555;
                border-radius: 8px;
            }
        """)
        
        # Make the whole chip clickable
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def mousePressEvent(self, event):
        """Handle clicks on the chip to focus the filter"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.filter_type)
        super().mousePressEvent(event)


class FilterChips(QWidget):
    """Horizontal scrolling widget displaying active filter chips"""
    chip_clicked = pyqtSignal(str)  # Emits filter type when a chip is clicked
    chip_reset = pyqtSignal(str)    # Emits filter type when a chip is closed to reset UI
    
    def __init__(self, filter_manager: FilterManager):
        super().__init__()
        self.filter_manager = filter_manager
        self.filter_manager.add_callback(self.update_chips)
        
        self.setFixedHeight(40)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Main horizontal layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)
        self.setLayout(main_layout)
        
        # Scroll area for chips
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setFixedHeight(40)
        main_layout.addWidget(self.scroll_area, 1)  # Stretch factor 1
        
        # Count label (aligned to the right)
        self.count_label = QLabel("")
        self.count_label.setFont(QFont("Arial", 9))
        self.count_label.setStyleSheet("color: #aaa; padding: 0px 5px;")
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.count_label.setFixedHeight(40)
        main_layout.addWidget(self.count_label)
        
        # Container widget for chips
        self.chips_container = QWidget()
        self.chips_layout = QHBoxLayout()
        self.chips_layout.setContentsMargins(5, 5, 5, 5)
        self.chips_layout.setSpacing(8)
        self.chips_layout.addStretch(1)
        self.chips_container.setLayout(self.chips_layout)
        self.scroll_area.setWidget(self.chips_container)
        
        # Scroll area initially hidden (no chips)
        self.scroll_area.setVisible(False)
        
    def update_chips(self):
        """Update chips based on current filter state"""
        # Clear existing chips
        while self.chips_layout.count() > 1:  # Keep the stretch
            item = self.chips_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Get filter parameters
        params = self.filter_manager.params
        chip_count = 0
        
        # Authors filter
        if params.authors:
            chip = FilterChip(f'Author: "{params.authors}"', "authors")
            chip.clicked.connect(self.chip_clicked.emit)
            chip.closed.connect(self.on_chip_closed)
            self.chips_layout.insertWidget(chip_count, chip)
            chip_count += 1
        
        # Category filter
        if params.category and len(params.category) < len(Category.list()):
            chip = FilterChip(f"Categories ({len(params.category)})", "category")
            chip.clicked.connect(self.chip_clicked.emit)
            chip.closed.connect(self.on_chip_closed)
            self.chips_layout.insertWidget(chip_count, chip)
            chip_count += 1
        
        # Character filter
        total_characters = len(DataManager.get_character_names())
        if params.character and len(params.character) < total_characters:
            chip = FilterChip(f"Characters ({len(params.character)})", "character")
            chip.clicked.connect(self.chip_clicked.emit)
            chip.closed.connect(self.on_chip_closed)
            self.chips_layout.insertWidget(chip_count, chip)
            chip_count += 1
        
        # Stage filter
        total_stages = len(DataManager.get_stage_names())
        if params.stages and len(params.stages) < total_stages:
            chip = FilterChip(f"Stages ({len(params.stages)})", "stages")
            chip.clicked.connect(self.chip_clicked.emit)
            chip.closed.connect(self.on_chip_closed)
            self.chips_layout.insertWidget(chip_count, chip)
            chip_count += 1

        # Elements filter
        if params.elements and len(params.elements) < len(Element.list()):
            chip = FilterChip(f"Elements ({len(params.elements)})", "elements")
            chip.clicked.connect(self.chip_clicked.emit)
            chip.closed.connect(self.on_chip_closed)
            self.chips_layout.insertWidget(chip_count, chip)
            chip_count += 1
        
        # Slot filter (only show if not the full range 0-255)
        if params.slot_min != 0 or params.slot_max != 255:
            if params.slot_min == params.slot_max:
                label = f"Slot C{params.slot_min:02d}"
            else:
                label = f"Slots C{params.slot_min:02d}-C{params.slot_max:02d}"
            chip = FilterChip(label, "slots")
            chip.clicked.connect(self.chip_clicked.emit)
            chip.closed.connect(self.on_chip_closed)
            self.chips_layout.insertWidget(chip_count, chip)
            chip_count += 1
        
        # WiFi filter
        if params.wifi and len(params.wifi) < len(Wifi.list()):
            chip = FilterChip(f"WiFi ({len(params.wifi)})", "wifi")
            chip.clicked.connect(self.chip_clicked.emit)
            chip.closed.connect(self.on_chip_closed)
            self.chips_layout.insertWidget(chip_count, chip)
            chip_count += 1
        
        # Info.toml filter
        if params.info and len(params.info) < len(InfoToml.list()):
            chip = FilterChip(f"Info ({len(params.info)})", "info")
            chip.clicked.connect(self.chip_clicked.emit)
            chip.closed.connect(self.on_chip_closed)
            self.chips_layout.insertWidget(chip_count, chip)
            chip_count += 1
        
        # Enabled state filter
        if params.enabled and len(params.enabled) < len(EnabledState.list()):
            chip = FilterChip(f"Enabled ({len(params.enabled)})", "enabled")
            chip.clicked.connect(self.chip_clicked.emit)
            chip.closed.connect(self.on_chip_closed)
            self.chips_layout.insertWidget(chip_count, chip)
            chip_count += 1
        
        # Include hidden filter
        if params.include_hidden:
            chip = FilterChip("Include Hidden", "include_hidden")
            chip.clicked.connect(self.chip_clicked.emit)
            chip.closed.connect(self.on_chip_closed)
            self.chips_layout.insertWidget(chip_count, chip)
            chip_count += 1
        
        # Favorites only filter
        if params.favorites_only:
            chip = FilterChip("Favorites Only", "favorites_only")
            chip.clicked.connect(self.chip_clicked.emit)
            chip.closed.connect(self.on_chip_closed)
            self.chips_layout.insertWidget(chip_count, chip)
            chip_count += 1
        
        self.scroll_area.setVisible(chip_count > 0)
    
    def on_chip_closed(self, filter_type: str):
        """Reset the specific filter when its chip is closed"""
        # Emit signal to reset UI component in filter panel
        self.chip_reset.emit(filter_type)
        
        params = self.filter_manager.params
        
        if filter_type == "authors":
            params.authors = ""
        elif filter_type == "category":
            params.category = []
        elif filter_type == "character":
            params.character = []
        elif filter_type == "stages":
            params.stages = []
        elif filter_type == "elements":
            params.elements = []
        elif filter_type == "slots":
            params.slot_min = 0
            params.slot_max = 255
        elif filter_type == "wifi":
            params.wifi = []
        elif filter_type == "info":
            params.info = []
        elif filter_type == "enabled":
            params.enabled = []
        elif filter_type == "include_hidden":
            params.include_hidden = False
        elif filter_type == "favorites_only":
            params.favorites_only = False
        
        # Trigger filter update
        self.filter_manager.on_change()
    
    def update_count(self, current_items: int, total_items: int):
        """Update the count label showing current items out of total"""
        if total_items == 0:
            self.count_label.setText("")
        else:
            self.count_label.setText(f"Showing {current_items} items of {total_items}")
