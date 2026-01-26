from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QLabel,
    QPushButton,
    QFrame,
    QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class PlaceholderChip(QPushButton):
    """Clickable chip that inserts a placeholder"""
    def __init__(self, placeholder:str, label:str):
        super().__init__(label)
        self.placeholder = placeholder
        self.setFixedHeight(28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2d5f8d;
                color: white;
                border: none;
                border-radius: 14px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #3a7ab8;
            }
            QPushButton:pressed {
                background-color: #1e4a6b;
            }
        """)

class FormatEditor(QWidget):
    """Visual format editor with clickable placeholders and live preview"""
    
    formatChanged = pyqtSignal(str)
    capSlotsChanged = pyqtSignal(bool)
    
    def __init__(self, placeholder_text:str = "", sample_data:dict = None):
        super().__init__()
        self.sample_data = sample_data or {
            "category": "Fighter",
            "characters": "Sonic",
            "slots": "C01-03",
            "mod": "Shadow"
        }
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Placeholder chips
        chips_label = QLabel("Insert placeholders:")
        chips_label.setStyleSheet("font-size: 10px; color: gray;")
        layout.addWidget(chips_label)
        
        chips_layout = QHBoxLayout()
        chips_layout.setSpacing(6)
        chips_layout.setContentsMargins(0, 0, 0, 0)
        
        placeholders = [
            ("{category}", "Category"),
            ("{characters}", "Characters"),
            ("{slots}", "Slots"),
            ("{mod}", "Mod Name")
        ]
        
        for placeholder, label in placeholders:
            chip = PlaceholderChip(placeholder, label)
            chip.clicked.connect(lambda checked, p=placeholder: self.insert_placeholder(p))
            chips_layout.addWidget(chip)
        
        chips_layout.addStretch(1)
        layout.addLayout(chips_layout)
        
        # Text input
        input_label = QLabel("Format template:")
        input_label.setStyleSheet("font-size: 10px; color: gray; margin-top: 4px;")
        layout.addWidget(input_label)
        
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText(placeholder_text)
        self.text_input.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.text_input)
        
        # Cap slots checkbox
        self.cap_slots_checkbox = QCheckBox("Capitalize slots (C01 vs c01)")
        self.cap_slots_checkbox.setChecked(True)
        self.cap_slots_checkbox.setStyleSheet("font-size: 10px;")
        self.cap_slots_checkbox.stateChanged.connect(self.on_cap_slots_changed)
        layout.addWidget(self.cap_slots_checkbox)
        
        # Preview section
        preview_container = QFrame()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(0, 8, 0, 0)
        preview_layout.setSpacing(4)
        
        preview_title = QLabel("Preview:")
        preview_title.setStyleSheet("font-size: 10px; color: gray; font-weight: bold;")
        preview_layout.addWidget(preview_title)
        
        self.preview_label = QLabel("")
        self.preview_label.setStyleSheet("font-size: 12px; color: white;")
        self.preview_label.setWordWrap(True)
        preview_layout.addWidget(self.preview_label)
        
        layout.addWidget(preview_container)
        
        # Help text
        help_text = QLabel("💡 Tip: Click chips to insert placeholders, or type manually. Add text between placeholders for separators.")
        help_text.setWordWrap(True)
        help_text.setStyleSheet("font-size: 9px; color: gray; margin-top: 4px;")
        layout.addWidget(help_text)
    
    def insert_placeholder(self, placeholder:str):
        """Insert placeholder at cursor position"""
        cursor_pos = self.text_input.cursorPosition()
        current_text = self.text_input.text()
        new_text = current_text[:cursor_pos] + placeholder + current_text[cursor_pos:]
        self.text_input.setText(new_text)
        self.text_input.setCursorPosition(cursor_pos + len(placeholder))
        self.text_input.setFocus()
    
    def on_text_changed(self, text:str):
        """Update preview when text changes"""
        self.update_preview(text)
        self.formatChanged.emit(text)
    
    def on_cap_slots_changed(self, state:int):
        """Emit signal when cap_slots changes"""
        is_checked = state == Qt.CheckState.Checked.value
        self.update_preview(self.text_input.text())
        self.capSlotsChanged.emit(is_checked)
    
    def update_preview(self, format_text:str):
        """Update preview with formatted sample data"""
        if not format_text:
            self.preview_label.setText("<i>Enter a format to see preview...</i>")
            return
        
        preview = format_text
        sample_data_copy = self.sample_data.copy()
        
        # Apply cap_slots to slots in preview
        if "slots" in sample_data_copy:
            slots_value = sample_data_copy["slots"]
            if self.cap_slots_checkbox.isChecked():
                sample_data_copy["slots"] = slots_value.upper() if slots_value else slots_value
            else:
                sample_data_copy["slots"] = slots_value.lower() if slots_value else slots_value
        
        for placeholder, value in sample_data_copy.items():
            preview = preview.replace(f"{{{placeholder}}}", value)
        
        self.preview_label.setText(f"<b>{preview}</b>")
    
    def get_text(self) -> str:
        """Get current format text"""
        return self.text_input.text()
    
    def set_text(self, text:str):
        """Set format text"""
        self.text_input.setText(text)
    
    def get_cap_slots(self) -> bool:
        """Get cap_slots checkbox state"""
        return self.cap_slots_checkbox.isChecked()
    
    def set_cap_slots(self, value:bool):
        """Set cap_slots checkbox state"""
        self.cap_slots_checkbox.setChecked(value)
    
    def set_sample_data(self, data:dict):
        """Update sample data for preview"""
        self.sample_data = data
        self.update_preview(self.text_input.text())
