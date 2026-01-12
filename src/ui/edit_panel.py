import re
from PyQt6.QtWidgets import ( 
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QLineEdit, QTextEdit, QSizePolicy
)
from PyQt6 import QtCore
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from src.ui.components.layout import HBox, VBox
from src.constants.styles import MAIN_BUTTON
from src.ui.components.side_panel import SidePanel
from src.constants.enums import Category, Element, Fighter, Wifi
from src.ui.components.input_button_widget import InputButtonWidget, InputButton
from src.ui.components.multi_combobox import CheckableComboBox
from src.ui.components.single_combobox import SingleComboBox
from src.ui.components.thumbnail_label import ThumbnailLabel
from src.managers.mod_manager import ModManager
from src.managers.data_manager import DataManager
from src.ui.components.validators import limit_version
from src.core.formatting import format_folder_name, format_display_name, format_character_names, format_slots

FONT = "Arial"
FONT_SIZE = 10
BODY_FONT_SIZE = 8


class EditPanel(SidePanel):
    close_requested = pyqtSignal()  # Signal to close edit panel
    
    def __init__(self, mod_manager: ModManager, config_manager):
        super().__init__("Edit")
        self.mod_manager = mod_manager
        self.config_manager = config_manager

        # GameBanana URL section
        self.url = InputButtonWidget(
            "GameBanana URL", 
            [
                InputButton(text="Open", callback=None),
                InputButton(text="Get", callback=None, highlight=True)
            ]
        )
        self.body.addWidget(self.url)
        
        # Thumbnail preview (async loading)
        self.thumbnail = ThumbnailLabel()
        self.body.addWidget(self.thumbnail)
        
        # Mod Name
        self._add_label("Mod Name")
        self.mod_name = QLineEdit()
        self.mod_name.setPlaceholderText("Enter mod name")
        self.mod_name.textChanged.connect(self._update_generated_names)
        self.body.addWidget(self.mod_name)

        # Character
        self._add_label("Character")
        characters = DataManager.get_character_names()
        self.character = CheckableComboBox(characters, [False] * (len(characters) + 1), False, "Select Characters")
        self.character.model().dataChanged.connect(self._update_generated_names)
        self.body.addWidget(self.character)

        # Slots
        self._add_label("Slots")
        self.slots = CheckableComboBox([f"C{i:02d}" for i in range(256)], [False] * 257, False, "Select Slots")
        self.slots.model().dataChanged.connect(self._update_generated_names)
        self.body.addWidget(self.slots)

        # Category
        self._add_label("Category")
        self.category = SingleComboBox()
        self.category.addItems(Category.list())
        self.category.currentIndexChanged.connect(self._update_generated_names)
        self.body.addWidget(self.category)

        # Authors
        self._add_label("Authors")
        self.author = QLineEdit()
        self.author.setPlaceholderText("Enter author name(s)")
        self.body.addWidget(self.author)

        # Version
        self._add_label("Version")
        self.version = QLineEdit()
        self.version.setPlaceholderText("1.0.0")
        self.version.textChanged.connect(self._on_version_changed)
        self.body.addWidget(self.version)
        
        # Description
        self._add_label("Description")
        self.description = QTextEdit()
        self.description.setPlaceholderText("Enter description")
        self.description.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.description.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.description.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.description.textChanged.connect(self._adjust_description_height)
        self.body.addWidget(self.description)

        # Elements
        self._add_label("Elements")
        self.elements = CheckableComboBox(Element.list(), [False] * (len(Element.list()) + 1), False, "Select Elements")
        self.body.addWidget(self.elements)

        # Wifi Safe
        self._add_label("Wifi Safe")
        self.wifi = SingleComboBox()
        self.wifi.addItems(Wifi.list())
        self.body.addWidget(self.wifi)

        # Display Name
        self._add_label("Display Name")
        self.display = QLineEdit()
        self.display.setPlaceholderText("Auto-generated display name")
        self.body.addWidget(self.display)

        # Folder Name
        self._add_label("Folder Name")
        self.folder = QLineEdit()
        self.folder.setPlaceholderText("Auto-generated folder name")
        self.body.addWidget(self.folder)
        
        self.body.addStretch()

        # Footer buttons
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.on_cancel)
        save_button = QPushButton("Save")
        save_button.setStyleSheet(MAIN_BUTTON)
        save_button.clicked.connect(self.on_save)
        self.footer.addWidget(cancel_button)
        self.footer.addWidget(save_button)
    
    def _add_label(self, text: str):
        """Helper to add a consistent label above input fields"""
        label = QLabel(text)
        label_font = QFont(FONT, BODY_FONT_SIZE)
        label_font.setBold(True)
        label.setFont(label_font)
        self.body.addWidget(label)
    
    def _on_version_changed(self, text: str):
        """Validate and limit version input"""
        limited = limit_version(text)
        if limited != text:
            self.version.blockSignals(True)
            self.version.setText(limited)
            self.version.blockSignals(False)
    
    def _adjust_description_height(self):
        """Adjust description field height to fit content without scrolling"""
        doc_height = self.description.document().size().height()
        margins = self.description.contentsMargins()
        total_height = int(doc_height + margins.top() + margins.bottom() + 10)
        self.description.setFixedHeight(max(80, total_height))
    
    def _update_generated_names(self):
        """Auto-generate folder_name and display_name when relevant fields change"""
        # Get mod name
        mod_name = self.mod_name.text().strip()
        if not mod_name:
            return
        
        # Get selected characters
        checked_chars = self.character.get_checked()
        checked_chars = [c for c in checked_chars if c != "Select All"]
        
        # Format character names - join with &
        if checked_chars:
            characters_str = " & ".join(checked_chars)
        else:
            characters_str = ""
        
        # Get selected slots
        checked_slots = []
        for i in range(self.slots.get_item_count()):
            item = self.slots.model().invisibleRootItem().child(i)
            if i == 0:  # Skip "Select All"
                continue
            if item.checkState() == Qt.CheckState.Checked:
                slot_text = item.text()
                try:
                    slot_num = int(slot_text[1:])  # Remove 'C' prefix
                    checked_slots.append(slot_num)
                except (ValueError, IndexError):
                    pass
        
        # Format slots using format_slots() - returns "C00-02,05" format (no brackets)
        slots_str_folder = ""
        slots_str_display = ""
        if checked_slots:
            sorted_slots = sorted(checked_slots)
            # Get cap_slots settings from config
            cap_slots_folder = self.config_manager.config.name_rules.cap_slots_folder
            cap_slots_display = self.config_manager.config.name_rules.cap_slots_display
            slots_str_folder = format_slots(sorted_slots, cap_slots_folder)
            slots_str_display = format_slots(sorted_slots, cap_slots_display)
        
        # Get category
        category_str = self.category.currentText()
        
        # Get format templates from config
        folder_format = self.config_manager.config.name_rules.folder_name_format or "{category}_{characters}[{slots}]_{mod}"
        display_format = self.config_manager.config.name_rules.display_name_format or "{characters} {slots} {mod}"
        
        # Generate folder name using.format() (more Pythonic and safer)
        try:
            folder_name = folder_format.format(
                category=category_str,
                characters=characters_str,
                slots=slots_str_folder,
                mod=mod_name
            )
            # Clean the folder name (remove special chars, etc.)
            from src.core.formatting import clean_folder_name
            folder_name = clean_folder_name(folder_name)
        except KeyError:
            # If template has invalid placeholder, fall back to default
            folder_name = f"{category_str}_{characters_str}[{slots_str_folder}]_{mod_name}"
            from src.core.formatting import clean_folder_name
            folder_name = clean_folder_name(folder_name)
        
        # Generate display name using .format()
        try:
            display_name = display_format.format(
                category=category_str,
                characters=characters_str,
                slots=slots_str_display,
                mod=mod_name
            )
            # Clean the display name
            from src.core.formatting import clean_display_name
            display_name = clean_display_name(display_name)
        except KeyError:
            # If template has invalid placeholder, fall back to default
            display_name = f"{characters_str} {slots_str_display} {mod_name}"
            from src.core.formatting import clean_display_name
            display_name = clean_display_name(display_name)
        
        # Update the fields
        self.folder.setText(folder_name)
        self.display.setText(display_name)
    
    def load_mod(self, mod_id: str):
        """Load mod data into edit panel"""
        mod = self.mod_manager.get_mod(mod_id)
        
        # Set URL if available
        if mod.url:
            self.url.set_text(mod.url)
        
        # Set mod name
        self.mod_name.setText(mod.mod_name)
        
        # Set characters - check all matching fighters
        for i in range(self.character.get_item_count()):
            item = self.character.model().invisibleRootItem().child(i)
            char_text = item.text()
            
            # Skip "Select All" item
            if i == 0 and char_text == "Select All":
                continue
            
            # Convert custom name back to Fighter key for comparison
            fighter_key = DataManager.get_character_by_custom(char_text)
            
            # Match character from mod's character list
            is_checked = any(char.fighter == fighter_key for char in mod.characters)
            item.setCheckState(Qt.CheckState.Checked if is_checked else Qt.CheckState.Unchecked)
        
        self.character.update_display()
        
        # Set slots - collect all unique slots from all characters
        all_slots = set()
        for char in mod.characters:
            all_slots.update(char.slots)
        
        for i in range(self.slots.get_item_count()):
            item = self.slots.model().invisibleRootItem().child(i)
            slot_text = item.text()
            
            # Skip "Select All" item
            if i == 0 and slot_text == "Select All":
                continue
            
            # Extract slot number from "C00" format
            try:
                slot_num = int(slot_text[1:])  # Remove 'C' prefix
                is_checked = slot_num in all_slots
                item.setCheckState(Qt.CheckState.Checked if is_checked else Qt.CheckState.Unchecked)
            except (ValueError, IndexError):
                item.setCheckState(Qt.CheckState.Unchecked)
        
        self.slots.update_display()
        
        # Set category
        try:
            category_index = Category.list().index(mod.category.value)
            self.category.setCurrentIndex(category_index)
        except (ValueError, AttributeError):
            self.category.setCurrentIndex(0)
        
        # Set author
        self.author.setText(mod.authors)
        
        # Set version
        self.version.setText(mod.version)
        
        # Set description
        self.description.setText(mod.description)
        
        # Set elements
        for i in range(self.elements.get_item_count()):
            item = self.elements.model().invisibleRootItem().child(i)
            element_text = item.text()
            
            # Skip "Select All" item
            if i == 0 and element_text == "Select All":
                continue
            
            # Match element from mod's includes list
            is_checked = any(el.value == element_text for el in mod.includes)
            item.setCheckState(Qt.CheckState.Checked if is_checked else Qt.CheckState.Unchecked)
        
        self.elements.update_display()
        
        # Set wifi safe
        try:
            wifi_index = Wifi.list().index(mod.wifi_safe.value)
            self.wifi.setCurrentIndex(wifi_index)
        except (ValueError, AttributeError):
            self.wifi.setCurrentIndex(0)
        
        # Set display name
        self.display.setText(mod.display_name)
        
        # Set folder name
        self.folder.setText(mod.folder_name)
        
        # Set thumbnail from mod's preview.webp
        self.thumbnail.set_thumbnail(mod.thumbnail)
    
    def reset(self):
        """Clear all fields to their default state"""
        self.url.clear()
        self.mod_name.clear()
        self.character.reset()
        self.slots.reset()
        self.category.setCurrentIndex(0)
        self.author.clear()
        self.version.clear()
        self.description.clear()
        self.elements.reset()
        self.wifi.setCurrentIndex(0)
        self.display.clear()
        self.folder.clear()
    
    def on_cancel(self):
        """Cancel edit and close panel"""
        self.close_requested.emit()
    
    def on_save(self):
        """Save changes (to be implemented)"""
        # TODO: Implement save functionality
        # This should:
        # 1. Collect all field values
        # 2. Update mod object
        # 3. Generate info.toml
        # 4. Optionally rename folder
        pass