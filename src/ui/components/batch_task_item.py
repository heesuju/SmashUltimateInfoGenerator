from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, 
    QGridLayout, QFrame, QLineEdit, QToolTip, QFileDialog, QTextEdit, QComboBox
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QFont, QMovie, QCursor
from src.models.mod import Mod
from src.managers.batch_manager import BatchTaskStatus, BatchTask
from src.managers.data_manager import DataManager
from src.constants.enums import Category, Element, Wifi
from src.ui.components.multi_combobox import CheckableComboBox
from src.ui.components.single_combobox import SingleComboBox
from src.ui.components.thumbnail_label import ThumbnailLabel
from src.ui.components.validators import limit_version
from src.core.formatting import format_slots, format_display_name, format_folder_name, format_character_names_for_display, format_character_names_for_folder, clean_version
import os


# Table cell styles
TABLE_HEADER_STYLE = """
    QLabel {
        background-color: rgba(128, 128, 128, 0.15);
        border: 1px solid rgba(128, 128, 128, 0.3);
        padding: 6px 8px;
        font-weight: bold;
        border-radius: 0;
    }
"""

TABLE_CELL_STYLE = """
    QLabel {
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-top: none;
        padding: 4px 8px;
        background-color: transparent;
        border-radius: 0;
    }
"""

TABLE_INPUT_STYLE = """
    QLineEdit {
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-top: none;
        padding: 4px 8px;
        background-color: transparent;
        border-radius: 0;
    }
    QLineEdit:focus {
        border: 1px solid #2196F3;
        background-color: rgba(33, 150, 243, 0.05);
    }
"""

TABLE_CELL_MUTED_STYLE = """
    QLabel {
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-top: none;
        padding: 4px 8px;
        background-color: transparent;
        color: #888;
        border-radius: 0;
    }
"""

COMBO_CHANGED_STYLE = """
    QComboBox {
        border: 1px solid #2196F3;
        padding: 3px 8px 4px 8px;
        background-color: rgba(33, 150, 243, 0.05);
        border-radius: 0;
    }
    QComboBox QAbstractItemView {
        background-color: #2b2b2b;
        border: 1px solid #555;
    }
"""

TABLE_CHANGED_STYLE = """
    border: 1px solid #2196F3;
    padding: 3px 8px 4px 8px;
    background-color: rgba(33, 150, 243, 0.05);
    border-radius: 0;
"""

TABLE_DEFAULT_STYLE = "border: 1px solid rgba(128, 128, 128, 0.2); border-top: none; padding: 4px 8px; background-color: transparent; border-radius: 0;"

THUMBNAIL_SIZE = 60


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text with ellipsis if too long"""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def truncate_to_lines(text: str, max_lines: int = 3) -> str:
    """Truncate text to max number of lines, adding ellipsis if truncated"""
    if not text:
        return ""
    lines = text.split('\n')
    if len(lines) <= max_lines:
        return text
    return '\n'.join(lines[:max_lines]) + "..."


class NonScrollableComboBox(QComboBox):
    def wheelEvent(self, e):
        e.ignore()


class BatchTaskItem(QWidget):
    """Widget representing a single batch task with all info.toml fields"""
    
    remove_requested = pyqtSignal(str)  # Emits mod hash
    
    def __init__(self, task: BatchTask):
        super().__init__()
        self.task = task
        self.mod = task.mod
        self.input_fields = {}  # Store references to input widgets
        self.task = task
        self.mod = task.mod
        self.input_fields = {}  # Store references to input widgets
        self.pending_thumbnail_path = None  # For new thumbnail selection
        
        # Cache original parsed values for comparison
        self.orig_char_names = []
        if self.task.original_characters:
            for c in self.task.original_characters:
                fighter_key = c.get("fighter")
                name = DataManager.get_character_data(fighter_key, "Custom") if fighter_key else fighter_key
                if name:
                    self.orig_char_names.append(name)
        self.orig_char_names.sort()

        self.orig_slots_set = set()
        if self.task.original_characters:
            for c in self.task.original_characters:
                slots = c.get("slots", [])
                self.orig_slots_set.update(slots)
        
        self.orig_elements_set = set(self.task.original_elements or [])
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 10)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)
        
        # Header row: Mod name, status, remove button
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(128, 128, 128, 0.1);
                border: 1px solid rgba(128, 128, 128, 0.3);
            }
        """)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 8, 10, 8)
        
        # Mod name - prioritize display_name from TOML if available
        display_name = self.mod.display_name if self.mod.contains_info and self.mod.display_name else self.mod.mod_name
        name_label = QLabel(display_name)
        name_label.setStyleSheet("border: none; background: transparent;")
        name_font = QFont("Arial", 11)
        name_font.setBold(True)
        name_label.setFont(name_font)
        header_layout.addWidget(name_label, 1)
        
        # Status indicator (hover to show message)
        self.status_label = QLabel()
        self.status_label.setStyleSheet("border: none; background: transparent;")
        status_font = QFont("Arial", 9)
        status_font.setBold(True)
        self.status_label.setFont(status_font)
        self.update_status_display()
        header_layout.addWidget(self.status_label)
        
        # Remove button
        remove_btn = QPushButton("✕")
        remove_btn.setFixedSize(24, 24)
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #999;
                font-size: 16px;
                font-weight: bold;
                padding: 0px;
                margin: 0px;
            }
            QPushButton:hover {
                color: #f44336;
                background-color: rgba(244, 67, 54, 0.1);
                border-radius: 12px;
            }
        """)
        remove_btn.clicked.connect(lambda: self.remove_requested.emit(str(self.mod.hash)))
        header_layout.addWidget(remove_btn)
        
        main_layout.addWidget(header_widget)
        
        # Create table with Original (read-only) and New (editable) columns
        table_widget = QWidget()
        table_layout = QGridLayout(table_widget)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)
        
        # Fonts
        header_font = QFont("Arial", 9)
        header_font.setBold(True)
        data_font = QFont("Arial", 9)
        
        # Table Headers
        field_header = QLabel("Field")
        field_header.setFont(header_font)
        field_header.setStyleSheet(TABLE_HEADER_STYLE)
        field_header.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        table_layout.addWidget(field_header, 0, 0)
        
        original_header = QLabel("Original (info.toml)")
        original_header.setFont(header_font)
        original_header.setStyleSheet(TABLE_HEADER_STYLE)
        original_header.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        table_layout.addWidget(original_header, 0, 1)
        
        new_header = QLabel("New (editable)")
        new_header.setFont(header_font)
        new_header.setStyleSheet(TABLE_HEADER_STYLE.replace("rgba(128, 128, 128, 0.15)", "rgba(33, 150, 243, 0.15)"))
        new_header.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        table_layout.addWidget(new_header, 0, 2)
        
        # Set column stretches
        table_layout.setColumnStretch(0, 1)  # Field names  
        table_layout.setColumnStretch(1, 2)  # Original values
        table_layout.setColumnStretch(2, 2)  # New values (editable)
        
        row = 1
        
        # --- Thumbnail Row ---
        row = self._add_thumbnail_row(table_layout, data_font, row)
        
        # --- Text Field Rows ---
        row = self._add_text_row(table_layout, data_font, row, "Mod Name", 
                                 task.original_mod_name, self.mod.mod_name, "mod_name")
        row = self._add_text_row(table_layout, data_font, row, "Authors", 
                                 task.original_authors, self.mod.authors, "authors")
        initial_version = self.mod.version
        if initial_version:
            initial_version = clean_version(limit_version(initial_version))
        row = self._add_text_row(table_layout, data_font, row, "Version", 
                                 task.original_version, initial_version, "version")
        row = self._add_text_row(table_layout, data_font, row, "URL", 
                                 task.original_url, self.mod.url, "url")
        
        # Description (multi-line, up to 3 lines)
        row = self._add_description_row(table_layout, data_font, row)
        
        # Display Name and Folder Name
        row = self._add_text_row(table_layout, data_font, row, "Display Name", 
                                 task.original_display_name, self.mod.display_name, "display_name")
        row = self._add_text_row(table_layout, data_font, row, "Folder Name", 
                                 task.original_folder_name, self.mod.folder_name, "folder_name")
        
        # --- Category (Single Combobox) ---
        row = self._add_category_row(table_layout, data_font, row)
        
        # --- Wifi Safe (Single Combobox) ---
        row = self._add_wifi_row(table_layout, data_font, row)
        
        # --- Characters (Multi Combobox) ---
        row = self._add_characters_row(table_layout, data_font, row)
        
        # --- Slots (Multi Combobox) ---
        row = self._add_slots_row(table_layout, data_font, row)
        
        # --- Elements (Multi Combobox) ---
        row = self._add_elements_row(table_layout, data_font, row)
        
        main_layout.addWidget(table_widget)
        
        # Schedule thumbnail loading after UI is shown to prevent freezing
        QTimer.singleShot(0, self._load_thumbnails)
    
    def _add_thumbnail_row(self, table_layout: QGridLayout, data_font: QFont, row: int) -> int:
        """Add thumbnail row with original (read-only) and new (clickable) thumbnails"""
        # Field label
        label = QLabel("Thumbnail")
        label.setFont(data_font)
        label.setStyleSheet(TABLE_CELL_STYLE)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        table_layout.addWidget(label, row, 0)
        
        # Original thumbnail (read-only)
        orig_container = QWidget()
        orig_container.setStyleSheet("border: 1px solid rgba(128, 128, 128, 0.2); border-top: none;")
        orig_layout = QHBoxLayout(orig_container)
        orig_layout.setContentsMargins(4, 4, 4, 4)
        
        if self.task.original_thumbnail:
            orig_thumb = ThumbnailLabel()
            orig_thumb.setFixedSize(THUMBNAIL_SIZE, THUMBNAIL_SIZE)
            # orig_thumb.set_thumbnail(self.task.original_thumbnail) # Loading deferred
            self.orig_thumbnail = orig_thumb # Store reference
            orig_layout.addWidget(orig_thumb)
        else:
            self.orig_thumbnail = None
            orig_label = QLabel("—")
            orig_label.setStyleSheet("color: #888; border: none;")
            orig_layout.addWidget(orig_label)
        orig_layout.addStretch()
        table_layout.addWidget(orig_container, row, 1)
        
        # New thumbnail (clickable)
        new_container = QWidget()
        new_container.setStyleSheet("border: 1px solid rgba(128, 128, 128, 0.2); border-top: none;")
        new_layout = QVBoxLayout(new_container)
        new_layout.setContentsMargins(4, 4, 4, 4)
        
        # Top row: Combobox + Browse
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        
        self.thumb_combo = NonScrollableComboBox()
        self.thumb_combo.addItems(["Current"])
        self.thumb_combo.setCurrentIndex(0)
        self.thumb_combo.currentIndexChanged.connect(self._on_thumbnail_source_changed)
        controls_layout.addWidget(self.thumb_combo, 1)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.setFixedHeight(24)
        browse_btn.clicked.connect(self._on_browse_thumbnail)
        browse_btn.setStyleSheet("border: 1px solid rgba(128, 128, 128, 0.3);")
        controls_layout.addWidget(browse_btn)
        
        new_layout.addLayout(controls_layout)
        
        # Bottom row: Thumbnail Preview
        self.new_thumbnail = ThumbnailLabel()
        self.new_thumbnail.setFixedSize(THUMBNAIL_SIZE * 2, THUMBNAIL_SIZE * 2) # Larger preview?
        self.new_thumbnail.setFixedSize(THUMBNAIL_SIZE * 2, int(THUMBNAIL_SIZE * 1.5))
        self.new_thumbnail.setScaledContents(False) # ThumbnailLabel handles scaling
        
        # Center the thumbnail
        thumb_wrapper = QHBoxLayout()
        thumb_wrapper.addStretch()
        thumb_wrapper.addWidget(self.new_thumbnail)
        thumb_wrapper.addStretch()
        new_layout.addLayout(thumb_wrapper)

        table_layout.addWidget(new_container, row, 2)
        
        return row + 1
    
    def _add_text_row(self, table_layout: QGridLayout, data_font: QFont, row: int,
                      label_text: str, orig_value: str, new_value: str, attr_name: str,
                      orig_tooltip: str = None) -> int:
        """Add a text field row with original (read-only) and new (editable)"""
        # Field label
        label = QLabel(label_text)
        label.setFont(data_font)
        label.setStyleSheet(TABLE_CELL_STYLE)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        table_layout.addWidget(label, row, 0)
        
        # Original value (read-only)
        orig_label = QLabel(orig_value if orig_value else "—")
        orig_label.setFont(data_font)
        orig_label.setStyleSheet(TABLE_CELL_STYLE if orig_value else TABLE_CELL_MUTED_STYLE)
        orig_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        if orig_tooltip:
            orig_label.setToolTip(orig_tooltip)
        table_layout.addWidget(orig_label, row, 1)
        
        # New value (editable)
        input_field = QLineEdit(new_value if new_value else "")
        input_field.setFont(data_font)
        input_field.setStyleSheet(TABLE_INPUT_STYLE)
        input_field.setPlaceholderText(f"Enter {label_text.lower()}...")
        input_field.textChanged.connect(lambda text, attr=attr_name: self._on_field_changed(attr, text))
        self.input_fields[attr_name] = input_field
        table_layout.addWidget(input_field, row, 2)
        
        return row + 1
    
    def _add_description_row(self, table_layout: QGridLayout, data_font: QFont, row: int) -> int:
        """Add description row with multi-line support (up to 3 lines)"""
        LINE_HEIGHT = 18  # Approximate height per line
        MAX_LINES = 3
        MAX_HEIGHT = LINE_HEIGHT * MAX_LINES + 10  # Add padding
        
        # Field label
        label = QLabel("Description")
        label.setFont(data_font)
        label.setStyleSheet(TABLE_CELL_STYLE)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        table_layout.addWidget(label, row, 0)
        
        # Original value (read-only, truncated to 3 lines with tooltip)
        orig_desc = self.task.original_description
        truncated_desc = truncate_to_lines(orig_desc, MAX_LINES) if orig_desc else "—"
        
        orig_label = QLabel(truncated_desc)
        orig_label.setFont(data_font)
        orig_label.setStyleSheet(TABLE_CELL_STYLE if orig_desc else TABLE_CELL_MUTED_STYLE)
        orig_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        orig_label.setWordWrap(True)
        orig_label.setMaximumHeight(MAX_HEIGHT)
        if orig_desc and orig_desc != truncated_desc:
            orig_label.setToolTip(orig_desc)  # Full text on hover
        table_layout.addWidget(orig_label, row, 1)
        
        # New value (editable QTextEdit, limited to 3 lines height)
        desc_edit = QTextEdit()
        desc_edit.setFont(data_font)
        desc_edit.setPlainText(self.mod.description or "")
        desc_edit.setPlaceholderText("Enter description...")
        desc_edit.setMaximumHeight(MAX_HEIGHT)
        desc_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid rgba(128, 128, 128, 0.2);
                border-top: none;
                padding: 4px 8px;
                background-color: transparent;
                border-radius: 0;
            }
            QTextEdit:focus {
                border: 1px solid #2196F3;
                background-color: rgba(33, 150, 243, 0.05);
            }
        """)
        desc_edit.textChanged.connect(lambda: self._on_field_changed("description", desc_edit.toPlainText()))
        self.input_fields["description"] = desc_edit
        table_layout.addWidget(desc_edit, row, 2)
        
        return row + 1
    
    def _add_category_row(self, table_layout: QGridLayout, data_font: QFont, row: int) -> int:
        """Add category row with single-select combobox"""
        # Field label
        label = QLabel("Category")
        label.setFont(data_font)
        label.setStyleSheet(TABLE_CELL_STYLE)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        table_layout.addWidget(label, row, 0)
        
        # Original value (read-only)
        orig_label = QLabel(self.task.original_category if self.task.original_category else "—")
        orig_label.setFont(data_font)
        orig_label.setStyleSheet(TABLE_CELL_STYLE if self.task.original_category else TABLE_CELL_MUTED_STYLE)
        orig_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        table_layout.addWidget(orig_label, row, 1)
        
        # New value (combobox)
        combo = SingleComboBox()
        combo.addItems(Category.list())
        # Set current value
        current_cat = self.mod.category.value if self.mod.category else ""
        if current_cat in Category.list():
            combo.setCurrentIndex(Category.list().index(current_cat))
        combo.currentTextChanged.connect(lambda text: self._on_field_changed("category", text))
        combo.currentIndexChanged.connect(self._update_generated_names)
        combo.setStyleSheet("border: 1px solid rgba(128, 128, 128, 0.2); border-top: none;")
        self.input_fields["category"] = combo
        table_layout.addWidget(combo, row, 2)
        
        return row + 1
    
    def _add_wifi_row(self, table_layout: QGridLayout, data_font: QFont, row: int) -> int:
        """Add wifi safe row with single-select combobox"""
        # Field label
        label = QLabel("Wifi Safe")
        label.setFont(data_font)
        label.setStyleSheet(TABLE_CELL_STYLE)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        table_layout.addWidget(label, row, 0)
        
        # Original value (read-only)
        orig_label = QLabel(self.task.original_wifi_safe if self.task.original_wifi_safe else "—")
        orig_label.setFont(data_font)
        orig_label.setStyleSheet(TABLE_CELL_STYLE if self.task.original_wifi_safe else TABLE_CELL_MUTED_STYLE)
        orig_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        table_layout.addWidget(orig_label, row, 1)
        
        # New value (combobox)
        combo = SingleComboBox()
        combo.addItems(Wifi.list())
        # Set current value
        current_wifi = self.mod.wifi_safe.value if self.mod.wifi_safe else ""
        if current_wifi in Wifi.list():
            combo.setCurrentIndex(Wifi.list().index(current_wifi))
        combo.currentTextChanged.connect(lambda text: self._on_field_changed("wifi_safe", text))
        combo.setStyleSheet("border: 1px solid rgba(128, 128, 128, 0.2); border-top: none;")
        self.input_fields["wifi_safe"] = combo
        table_layout.addWidget(combo, row, 2)
        
        return row + 1
    
    def _add_characters_row(self, table_layout: QGridLayout, data_font: QFont, row: int) -> int:
        """Add characters row with multi-select combobox"""
        # Field label
        label = QLabel("Characters")
        label.setFont(data_font)
        label.setStyleSheet(TABLE_CELL_STYLE)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        table_layout.addWidget(label, row, 0)
        
        # Original value (read-only, formatted list)
        orig_chars = []
        if self.task.original_characters:
            for c in self.task.original_characters:
                fighter_key = c.get("fighter")
                name = DataManager.get_character_data(fighter_key, "Custom") if fighter_key else fighter_key
                if name:
                    orig_chars.append(name)
        orig_text = ", ".join(orig_chars) if orig_chars else "—"
        orig_label = QLabel(truncate_text(orig_text, 40))
        orig_label.setFont(data_font)
        orig_label.setStyleSheet(TABLE_CELL_STYLE if orig_chars else TABLE_CELL_MUTED_STYLE)
        orig_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        orig_label.setToolTip(orig_text)
        table_layout.addWidget(orig_label, row, 1)
        
        # New value (multi-select combobox)
        all_characters = DataManager.get_character_names()
        # Determine which are already checked
        current_chars = []
        for c in self.mod.characters:
            name = DataManager.get_character_data(c.fighter, "Custom")
            if name:
                current_chars.append(name)
        
        combo = CheckableComboBox(all_characters, [], False, "Select Characters")
        
        # Manually set check states by matching item text (after sort has happened)
        for i in range(combo.model().rowCount()):
            item = combo.model().item(i)
            if item and item.text() in current_chars:
                item.setCheckState(Qt.CheckState.Checked)
        combo.update_display()
        
        combo.model().dataChanged.connect(self._update_generated_names)
        combo.model().dataChanged.connect(lambda: self._check_field_changed("characters"))
        combo.setStyleSheet("border: 1px solid rgba(128, 128, 128, 0.2); border-top: none;")
        self.input_fields["characters"] = combo
        table_layout.addWidget(combo, row, 2)
        
        return row + 1
    
    def _add_slots_row(self, table_layout: QGridLayout, data_font: QFont, row: int) -> int:
        """Add slots row with multi-select combobox"""
        # Field label
        label = QLabel("Slots")
        label.setFont(data_font)
        label.setStyleSheet(TABLE_CELL_STYLE)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        table_layout.addWidget(label, row, 0)
        
        # Original value (read-only, formatted)
        orig_slots = set()
        if self.task.original_characters:
            for c in self.task.original_characters:
                slots = c.get("slots", [])
                orig_slots.update(slots)
        orig_text = format_slots(sorted(orig_slots)) if orig_slots else "—"
        orig_label = QLabel(orig_text)
        orig_label.setFont(data_font)
        orig_label.setStyleSheet(TABLE_CELL_STYLE if orig_slots else TABLE_CELL_MUTED_STYLE)
        orig_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        table_layout.addWidget(orig_label, row, 1)
        
        # New value (multi-select combobox)
        def slot_formatter(items):
            if not items:
                return ""
            slots_int = []
            for item in items:
                try:
                    if item.startswith("C"):
                        slots_int.append(int(item[1:]))
                except:
                    pass
            return format_slots(sorted(slots_int))
        
        # Get current slots from mod
        current_slots = set()
        for c in self.mod.characters:
            current_slots.update(c.slots)
            
        # Optimize: Only show slots 0-31 + any existing slots used by this mod
        display_slots = set(range(32))
        display_slots.update(current_slots)
        slot_options = [f"C{i:02d}" for i in sorted(display_slots)]
        
        # Don't pass defaults - items get sorted which breaks index-based defaults
        combo = CheckableComboBox(slot_options, [], False, "Select Slots", formatter=slot_formatter)
        
        # Manually set check states by matching slot number (after sort)
        for i in range(combo.model().rowCount()):
            item = combo.model().item(i)
            if item:
                try:
                    slot_num = int(item.text()[1:])  # Remove 'C' prefix
                    if slot_num in current_slots:
                        item.setCheckState(Qt.CheckState.Checked)
                except:
                    pass
        combo.update_display()
        
        combo.model().dataChanged.connect(self._update_generated_names)
        combo.model().dataChanged.connect(lambda: self._check_field_changed("slots"))
        combo.setStyleSheet("border: 1px solid rgba(128, 128, 128, 0.2); border-top: none;")
        self.input_fields["slots"] = combo
        table_layout.addWidget(combo, row, 2)
        
        return row + 1
    
    def _add_elements_row(self, table_layout: QGridLayout, data_font: QFont, row: int) -> int:
        """Add elements row with multi-select combobox"""
        # Field label
        label = QLabel("Elements")
        label.setFont(data_font)
        label.setStyleSheet(TABLE_CELL_STYLE)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        table_layout.addWidget(label, row, 0)
        
        # Original value (read-only, formatted list)
        orig_elements = self.task.original_elements or []
        orig_text = ", ".join(orig_elements) if orig_elements else "—"
        orig_label = QLabel(truncate_text(orig_text, 40))
        orig_label.setFont(data_font)
        orig_label.setStyleSheet(TABLE_CELL_STYLE if orig_elements else TABLE_CELL_MUTED_STYLE)
        orig_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        orig_label.setToolTip(orig_text)
        table_layout.addWidget(orig_label, row, 1)
        
        # New value (multi-select combobox)
        all_elements = Element.list()
        current_elements = [el.value for el in self.mod.includes] if self.mod.includes else []
        
        # Don't pass defaults - items get sorted which breaks index-based defaults
        combo = CheckableComboBox(all_elements, [], False, "Select Elements")
        
        # Manually set check states by matching element text (after sort)
        for i in range(combo.model().rowCount()):
            item = combo.model().item(i)
            if item and item.text() in current_elements:
                item.setCheckState(Qt.CheckState.Checked)
        combo.update_display()
        
        combo.model().dataChanged.connect(lambda: self._check_field_changed("elements"))
        combo.setStyleSheet("border: 1px solid rgba(128, 128, 128, 0.2); border-top: none;")
        self.input_fields["elements"] = combo
        table_layout.addWidget(combo, row, 2)
        
        return row + 1
    
    def _on_field_changed(self, attr_name: str, value: str):
        """Handle field value change - update the mod object"""
        if attr_name == "mod_name":
            self.mod.mod_name = value
            self._update_generated_names()  # Trigger regeneration
        elif attr_name == "authors":
            self.mod.authors = value
        elif attr_name == "version":
            # First limit input characters, then format to 0.0.0
            limited = limit_version(value)
            formatted = clean_version(limited) if limited else ""
            if formatted != value and "version" in self.input_fields:
                self.input_fields["version"].blockSignals(True)
                self.input_fields["version"].setText(formatted)
                self.input_fields["version"].blockSignals(False)
            self.mod.version = formatted
        elif attr_name == "url":
            self.mod.url = value
        elif attr_name == "description":
            self.mod.description = value
        elif attr_name == "display_name":
            self.mod.display_name = value
        elif attr_name == "folder_name":
            self.mod.folder_name = value
        elif attr_name == "category":
            try:
                self.mod.category = Category(value)
            except:
                pass
        elif attr_name == "wifi_safe":
            try:
                self.mod.wifi_safe = Wifi(value)
            except:
                pass
    
    def _update_generated_names(self, *args):
        """Auto-regenerate folder_name and display_name from current field values"""
        if "mod_name" in self.input_fields:
            mod_name = self.input_fields["mod_name"].text()
        else:
            mod_name = self.mod.mod_name
        if not mod_name:
            return
        
        # Get selected characters
        checked_chars = self.get_selected_characters()
        characters_str_display = format_character_names_for_display(checked_chars)
        characters_str_folder = format_character_names_for_folder(checked_chars)
        
        # Get selected slots  
        checked_slots = self.get_selected_slots()
        slots_str = format_slots(sorted(checked_slots)) if checked_slots else ""
        
        # Get category
        category_str = ""
        if "category" in self.input_fields:
            category_str = self.input_fields["category"].currentText()
        
        # Generate new names
        folder_name = format_folder_name(characters_str_folder, slots_str, mod_name, category_str)
        display_name = format_display_name(characters_str_display, slots_str, mod_name, category_str)
        
        # Update the input fields (block signals to avoid infinite loop)
        if "folder_name" in self.input_fields:
            self.input_fields["folder_name"].blockSignals(True)
            self.input_fields["folder_name"].setText(folder_name)
            self.input_fields["folder_name"].blockSignals(False)
            self.mod.folder_name = folder_name
        
        if "display_name" in self.input_fields:
            self.input_fields["display_name"].blockSignals(True)
            self.input_fields["display_name"].setText(display_name)
            self.input_fields["display_name"].blockSignals(False)
            self.mod.display_name = display_name
    
    def _on_browse_thumbnail(self):
        """Open file dialog to select new thumbnail"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Preview Image", "", 
            "Images (*.png *.jpg *.jpeg *.webp)"
        )
        if file_path:
            self.pending_thumbnail_path = file_path
            
            # Update combobox
            # Check if "Custom" already exists
            found = False
            for i in range(self.thumb_combo.count()):
                if self.thumb_combo.itemText(i) == "Custom":
                    # Update data
                    self.thumb_combo.setItemData(i, file_path)
                    self.thumb_combo.setCurrentIndex(i)
                    found = True
                    break
            
            if not found:
                self.thumb_combo.addItem("Custom", file_path)
                self.thumb_combo.setCurrentIndex(self.thumb_combo.count() - 1)
            
            self.new_thumbnail.set_thumbnail(file_path)

    def _on_thumbnail_source_changed(self, index):
        """Handle thumbnail source selection change"""
        data = self.thumb_combo.itemData(index)
        if data:
            # It's a path or URL
            self.pending_thumbnail_path = str(data) # Store URL/Path as pending
            self.new_thumbnail.set_thumbnail(str(data))
        else:
            # It's likely "Current" (index 0 usually), using self.mod.thumbnail
            # Or if data is None
            if index == 0:
                self.pending_thumbnail_path = None # Reset pending, will use mod.thumbnail
                self.new_thumbnail.set_thumbnail(self.mod.thumbnail)
        self._check_field_changed("thumbnail")

    def get_pending_thumbnail(self) -> str:
        """Get the pending thumbnail path if user selected a new one"""
        return self.pending_thumbnail_path

    def update_new_data(self, mod_name: str = None, authors: str = None, 
                        version: str = None, url: str = None, description: str = None,
                        preview_links: list = None, wifi_safe: bool = None,
                        category: str = None, is_moveset: bool = None, is_final_smash: bool = None):
        """Update the editable fields with new data (e.g., after fetching)"""
        if mod_name is not None and "mod_name" in self.input_fields:
            self.input_fields["mod_name"].setText(mod_name)
        if authors is not None and "authors" in self.input_fields:
            self.input_fields["authors"].setText(authors)
        if version is not None and "version" in self.input_fields:
            formatted_version = clean_version(limit_version(version))
            self.input_fields["version"].setText(formatted_version)
        if url is not None and "url" in self.input_fields:
            self.input_fields["url"].setText(url)
        if description is not None and "description" in self.input_fields:
            self.input_fields["description"].setText(description)
            
        if wifi_safe is not None and "wifi_safe" in self.input_fields:
            # wifi_safe is boolean coming from fetch logic
            val = Wifi.SAFE.value if wifi_safe else Wifi.UNCERTAIN.value
            combo = self.input_fields["wifi_safe"]
            idx = combo.findText(val)
            if idx >= 0:
                combo.setCurrentIndex(idx)
                
        if category is not None and "category" in self.input_fields:
            combo = self.input_fields["category"]
            idx = combo.findText(category)
            if idx >= 0:
                combo.setCurrentIndex(idx)
                
        if (is_moveset or is_final_smash) and "elements" in self.input_fields:
            combo = self.input_fields["elements"]
            model = combo.model()
            changed = False
            for i in range(model.rowCount()):
                item = model.item(i)
                if not item: continue
                text = item.text()
                
                if is_moveset and text == Element.MOVESET.value:
                    if item.checkState() != Qt.CheckState.Checked:
                        item.setCheckState(Qt.CheckState.Checked)
                        changed = True
                elif is_final_smash and text == Element.FINAL_SMASH.value:
                    if item.checkState() != Qt.CheckState.Checked:
                        item.setCheckState(Qt.CheckState.Checked)
                        changed = True
            
            if changed:
                combo.update_display()
            
        if preview_links:
            # Add fetched previews to combobox
            # Keep "Current" and "Custom" if selected?
            # Or just append?
            
            # Avoid duplicates if update is called multiple times
            existing_urls = set()
            for i in range(self.thumb_combo.count()):
                data = self.thumb_combo.itemData(i)
                if data:
                    existing_urls.add(str(data))
            
            added_count = 0
            for i, link in enumerate(preview_links):
                if link not in existing_urls:
                    self.thumb_combo.addItem(f"Fetched {i+1}", link)
                    added_count += 1
            
            if added_count > 0 and self.thumb_combo.currentIndex() == 0:
                has_original = False
                if self.task.original_thumbnail and os.path.exists(self.task.original_thumbnail):
                    has_original = True
                
                if not has_original:
                    idx = self.thumb_combo.findText("Fetched 1")
                    if idx >= 0:
                        self.thumb_combo.setCurrentIndex(idx)

    def _set_changed_style(self, widget, changed: bool):
        """Apply changed style to widget if value differs from original"""
        if not widget: return
        style = TABLE_CHANGED_STYLE if changed else TABLE_DEFAULT_STYLE
        
        if isinstance(widget, (QLineEdit, QTextEdit)):
            if changed:
                widget.setStyleSheet(f"{type(widget).__name__} {{ {style} }}")
            else:
                # Restore original input style
                if isinstance(widget, QLineEdit):
                    widget.setStyleSheet(TABLE_INPUT_STYLE)
                else: 
                    # Restore TextEdit style
                    widget.setStyleSheet("""
                        QTextEdit {
                            border: 1px solid rgba(128, 128, 128, 0.2);
                            border-top: none;
                            padding: 4px 8px;
                            background-color: transparent;
                            border-radius: 0;
                        }
                        QTextEdit:focus {
                            border: 1px solid #2196F3;
                            background-color: rgba(33, 150, 243, 0.05);
                        }
                    """)
        elif isinstance(widget, (QComboBox, SingleComboBox, CheckableComboBox)):
            if changed:
                widget.setStyleSheet(COMBO_CHANGED_STYLE)
            else:
                widget.setStyleSheet(TABLE_DEFAULT_STYLE)
        else:
            # Other widgets
            widget.setStyleSheet(style)

    def _check_field_changed(self, field_name: str):
        """Check if field value differs from original and update style"""
        widget = self.input_fields.get(field_name)
        if not widget and field_name != "thumbnail": return
        
        changed = False
        
        if field_name == "mod_name":
            changed = widget.text() != (self.task.original_mod_name or "")
        elif field_name == "authors":
            changed = widget.text() != (self.task.original_authors or "")
        elif field_name == "version":
            # Compare cleaned versions?
            orig = clean_version(limit_version(self.task.original_version) if self.task.original_version else "")
            new_val = clean_version(limit_version(widget.text()))
            changed = orig != new_val
        elif field_name == "url":
            changed = widget.text() != (self.task.original_url or "")
        elif field_name == "description":
            changed = widget.toPlainText() != (self.task.original_description or "")
        elif field_name == "display_name":
            changed = widget.text() != (self.task.original_display_name or "")
        elif field_name == "folder_name":
            changed = widget.text() != (self.task.original_folder_name or "")
        elif field_name == "category":
            changed = widget.currentText() != (self.task.original_category or "")
        elif field_name == "wifi_safe":
            changed = widget.currentText() != (self.task.original_wifi_safe or "")
        elif field_name == "characters":
            # Compare arrays of names
            new_chars = self.get_selected_characters()
            new_chars.sort()
            changed = new_chars != self.orig_char_names
        elif field_name == "slots":
            # Compare sets of ints
            new_slots = set(self.get_selected_slots())
            changed = new_slots != self.orig_slots_set
        elif field_name == "elements":
            # Compare sets of strings
            new_elements = set(widget.get_checked())
            if "Select All" in new_elements: 
                new_elements.remove("Select All")
            changed = new_elements != self.orig_elements_set
        elif field_name == "thumbnail":
            # If pending path is set, it's changed. 
            # Unless pending path is same as original? unlikely if user browsed.
            # If mod.thumbnail is different from original?
            # self.task.original_thumbnail might be None.
            changed = self.pending_thumbnail_path is not None
            # Update thumbnail container style? 
            # The thumbnail widget is inside a container.
            # But we don't have ref to container easily. 
            # We can set style on thumb_combo?
            self._set_changed_style(self.thumb_combo, changed)
            return

        self._set_changed_style(widget, changed)

    def _on_field_changed(self, field_name: str, value=None):
        """Handle field updates"""
        self._check_field_changed(field_name)
        
        # Auto-update logic
        if field_name in ["mod_name", "characters", "slots", "category"]:
            self._update_generated_names()
            
        # Update model for simple fields
        if field_name == "mod_name":
             self.mod.mod_name = value
        elif field_name == "display_name":
             self.mod.display_name = value # Should we specific block signals?
             # But here we are IN the handler.
             pass

    def get_selected_characters(self) -> list:
        """Get list of selected character names"""
        if "characters" in self.input_fields:
            chars = self.input_fields["characters"].get_checked()
            return [c for c in chars if c != "Select All"]
        return []
    
    def get_selected_slots(self) -> list:
        """Get list of selected slot numbers"""
        if "slots" in self.input_fields:
            slots_text = self.input_fields["slots"].get_checked()
            slots = []
            for text in slots_text:
                if text != "Select All" and text.startswith("C"):
                    try:
                        slots.append(int(text[1:]))
                    except:
                        pass
            return slots
        return []
    
    def get_selected_elements(self) -> list:
        """Get list of selected element names"""
        if "elements" in self.input_fields:
            elements = self.input_fields["elements"].get_checked()
            return [e for e in elements if e != "Select All"]
        return []
    
    def update_status_display(self):
        """Update the status label based on current task status"""
        if self.task.status == BatchTaskStatus.PENDING:
            self.status_label.setText("⏳ Pending")
            self.status_label.setStyleSheet("border: none; background: transparent; color: #888;")
            self.status_label.setToolTip("Waiting to be processed")
        elif self.task.status == BatchTaskStatus.PROCESSING:
            self.status_label.setText("⚙️ Processing")
            self.status_label.setStyleSheet("border: none; background: transparent; color: #2196F3;")
            self.status_label.setToolTip(self.task.progress_message or "Processing...")
        elif self.task.status == BatchTaskStatus.COMPLETE:
            self.status_label.setText("✓ Complete")
            self.status_label.setStyleSheet("border: none; background: transparent; color: #4CAF50;")
            self.status_label.setToolTip("Fetch completed successfully")
        elif self.task.status == BatchTaskStatus.ERROR:
            self.status_label.setText("✗ Error")
            self.status_label.setStyleSheet("border: none; background: transparent; color: #f44336;")
            self.status_label.setToolTip(self.task.error_message or "An error occurred")
    
    def update_status(self, status: BatchTaskStatus, progress_message: str = "", error_message: str = ""):
        """Update the task status and display"""
        self.task.status = status
        self.task.progress_message = progress_message
        self.task.error_message = error_message
        
        self.update_status_display()
    
    def _load_thumbnails(self):
        """Load thumbnails asynchronously to avoid UI blocking during creation"""
        if hasattr(self, 'orig_thumbnail') and self.orig_thumbnail:
            self.orig_thumbnail.set_thumbnail(self.task.original_thumbnail)
        
        if hasattr(self, 'new_thumbnail') and self.new_thumbnail:
            # Use pending path if user selected one, otherwise current mod thumbnail
            path = self.pending_thumbnail_path if self.pending_thumbnail_path else self.mod.thumbnail
            self.new_thumbnail.set_thumbnail(path)
