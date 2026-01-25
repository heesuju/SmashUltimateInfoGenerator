import re
from PyQt6.QtWidgets import ( 
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QLineEdit, QTextEdit, QSizePolicy, QMessageBox, QComboBox, QFileDialog
)
from PyQt6 import QtCore
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt, QSize, pyqtSignal
import shutil
import requests
import tempfile
import os
from src.ui.components.layout import HBox, VBox
from src.ui.components.side_panel import SidePanel
from src.constants.enums import Category, Element, Fighter, Wifi
from src.ui.components.input_button_widget import InputButtonWidget, InputButton
from src.ui.components.multi_combobox import CheckableComboBox
from src.ui.components.single_combobox import SingleComboBox
from src.ui.components.thumbnail_label import ThumbnailLabel, ImageCache
from src.managers.mod_manager import ModManager
from src.managers.cache_manager import CacheManager
from src.managers.data_manager import DataManager
from src.managers.data_manager import ButtonIcons
from src.ui.components.validators import limit_version
from src.core.formatting import (
    format_folder_name, format_display_name, format_character_names_for_display, format_character_names_for_folder, format_slots,
    format_stage_names_for_display, format_stage_names_for_folder, format_stage_slots, format_stage_slots_for_folder
)
from src.core.gamebanana import Gamebanana
from src.utils.web import open_page
from src.core.data import generate_toml
from src.core.scanner import scan_mod
from src.ui.components.assignment_list import AssignmentListWidget
from src.models.mod import Character
from src.constants.enums import Fighter, Category, Wifi, Element
from src.utils.file import get_parent_dir

FONT = "Arial"
FONT_SIZE = 10
BODY_FONT_SIZE = 8



class ImageDownloadThread(QtCore.QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            response = requests.get(self.url, stream=True)
            if response.status_code == 200:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
                with open(temp_file, 'wb') as f:
                    shutil.copyfileobj(response.raw, f)
                self.finished.emit(temp_file)
            else:
                self.error.emit(f"Status code: {response.status_code}")
        except Exception as e:
            self.error.emit(str(e))

class EditPanel(SidePanel):
    close_requested = pyqtSignal()  # Signal to close edit panel
    gb_data_ready = pyqtSignal(dict) # Signal for thread-safe data update
    save_complete = pyqtSignal(str) # Signal when save is complete (emits mod hash)
    
    def __init__(self, mod_manager: ModManager, config_manager):
        super().__init__("Edit")
        self.mod_manager = mod_manager
        self.config_manager = config_manager
        self.pending_preview_path = None
        self.mod_path = None
        self.mod = None # Current Mod object
        self.preview_map = {} # Maps display text to URL

        # Add Rescan button to header
        self.rescan_button = QPushButton("Rescan")
        self.rescan_button.setFixedWidth(60)
        self.rescan_button.setFixedHeight(26)
        self.rescan_button.clicked.connect(self.on_rescan)
        self.header.addWidget(self.rescan_button)

        # GameBanana URL section
        self.url = InputButtonWidget(
            "GameBanana URL", 
            [
                InputButton(text="Open", callback=self.on_open_url),
                InputButton(text="Get", callback=self.on_get_url, highlight=True)
            ]
        )
        self.body.addWidget(self.url)
        
        # Thumbnail preview (async loading)
        self.thumbnail = ThumbnailLabel()
        self.body.addWidget(self.thumbnail)
        
        # Preview Selector (Files from GB) + Browse Button
        preview_layout = QHBoxLayout()
        self.preview_selector = QComboBox()
        self.preview_selector.setPlaceholderText("Select Preview from GameBanana")
        self.preview_selector.currentIndexChanged.connect(self.on_preview_selected)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.on_browse_image)
        
        preview_layout.addWidget(self.preview_selector)
        preview_layout.addWidget(self.browse_button)
        self.body.addLayout(preview_layout)
        
        # Mod Name
        self._add_label("Mod Name")
        self.mod_name = QLineEdit()
        self.mod_name.setPlaceholderText("Enter mod name")
        self.mod_name.textChanged.connect(self._update_generated_names)
        self.body.addWidget(self.mod_name)

        # Character Inputs
        self._add_label("Character")
        characters = DataManager.get_character_names()
        # Simple Mode Container
        self.char_simple_container = QWidget()
        char_simple_layout = QHBoxLayout(self.char_simple_container)
        char_simple_layout.setContentsMargins(0, 0, 0, 0)
        
        self.character = CheckableComboBox(characters, [False] * (len(characters) + 1), False, "Select Characters")
        self.character.model().dataChanged.connect(self._update_generated_names)
        
        # Slots (Simple Mode)
        def slot_formatter(items):
            if not items: return ""
            # Convert "C00" -> 0
            slots_int = []
            for item in items:
                try:
                    if item.startswith("C"):
                        slots_int.append(int(item[1:]))
                except:
                    pass
            return format_slots(sorted(slots_int))
        self._slot_formatter = slot_formatter # Store for reuse

        self.slots = CheckableComboBox([f"C{i:02d}" for i in range(256)], [False] * 257, False, "Select Slots", formatter=slot_formatter)
        self.slots.model().dataChanged.connect(self._update_generated_names)
        
        char_simple_layout.addWidget(self.character, 1) # Stretch character
        char_simple_layout.addWidget(self.slots)
        
        self.body.addWidget(self.char_simple_container)

        # Advanced Mode Widget
        self.char_assignments = AssignmentListWidget("Character", "Slots")
        self.char_assignments.set_entities(DataManager.get_character_dict()) # {ID: Name}
        self.char_assignments.set_slot_options([f"C{i:02d}" for i in range(256)], formatter=slot_formatter)
        self.char_assignments.assignments_changed.connect(self._update_generated_names)
        self.char_assignments.hide()
        self.body.addWidget(self.char_assignments)


        # Stages
        self._add_label("Stages")
        stage_names = DataManager.get_stage_names()
        
        # Simple Mode Container
        self.stage_simple_container = QWidget()
        stage_simple_layout = QHBoxLayout(self.stage_simple_container)
        stage_simple_layout.setContentsMargins(0, 0, 0, 0)

        self.stages = CheckableComboBox(stage_names, [False] * (len(stage_names) + 1), False, "Select Stages")
        self.stages.model().dataChanged.connect(self._update_generated_names)
        
        # Stage Slots (Simple Mode)
        # StageSlot enum values: "normal", "battle"
        from src.constants.enums import StageSlot
        stage_slots_list = StageSlot.list()
        self.stage_slots = CheckableComboBox(stage_slots_list, [False] * (len(stage_slots_list) + 1), False, "Select Stage Slots", formatter=format_stage_slots)
        self.stage_slots.model().dataChanged.connect(self._update_generated_names)
        
        stage_simple_layout.addWidget(self.stages, 1)
        stage_simple_layout.addWidget(self.stage_slots)
        
        self.body.addWidget(self.stage_simple_container)

        # Advanced Mode Widget
        self.stage_assignments = AssignmentListWidget("Stage", "Slots")
        
        # Create stage dict {Key: Name}
        stage_dict = {}
        for s_key in DataManager.get_stage_keys():
            name = DataManager.get_stage_data(s_key, "Value")
            if name:
                stage_dict[s_key] = name
        
        self.stage_assignments.set_entities(stage_dict)
        self.stage_assignments.set_slot_options(StageSlot.list(), formatter=format_stage_slots)
        self.stage_assignments.assignments_changed.connect(self._update_generated_names)
        self.stage_assignments.hide()
        self.body.addWidget(self.stage_assignments)
        

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
        # Footer buttons
        self.add_footer_button("Cancel", self.on_cancel, icon=ButtonIcons.CLEAR.value)
        self.add_footer_button("Save", self.on_save, primary=True, icon=ButtonIcons.SAVE.value)
        
        # Connect signal
        self.gb_data_ready.connect(self._populate_mod_info)

    def on_get_url(self):
        url = self.url.get_text()
        
        # Auto-Search Mode
        if not url:
            mod_name = self.mod_name.text().strip()
            if not mod_name:
                QMessageBox.warning(self, "Missing Information", "Please enter a Mod Name to search.")
                return
            
            author_name = self.author.text().strip()
            
            # Append Characters to search query to filter results
            selected_chars = self.character.get_checked()
            
            # Limit to 3 characters to prevent query from becoming too long/messy
            if 0 < len(selected_chars) <= 3:
                # Group characters if possible
                search_terms = set()
                mod_name_lower = mod_name.lower()
                
                for char_name in selected_chars:
                    fighter_key = DataManager.get_character_by_custom(char_name)
                    group = DataManager.get_character_groups(fighter_key)
                    
                    term_to_add = None
                    # Use Group if available, else Custom Name
                    if group:
                        term_to_add = group
                    else:
                        term_to_add = char_name
                        
                    # Only add if not already in the mod name (case-insensitive)
                    if term_to_add and term_to_add.lower() not in mod_name_lower:
                        search_terms.add(term_to_add)
                
                # Append unique terms to mod name
                if search_terms:
                    mod_name += " " + " ".join(search_terms)

            # Start thread in search mode
            # Pass mod_name as ID, but set is_search=True
            Gamebanana(mod_name, self.gb_data_ready.emit, is_search=True, author_filter=author_name)
            return
            
        # Direct URL Mode
        match = re.search(r"gamebanana\.com/mods/(\d+)", url)
        if match:
            mod_id = match.group(1)
            Gamebanana(mod_id, self.gb_data_ready.emit)
        else:
            QMessageBox.warning(self, "Invalid URL", "Could not parse Mod ID from the URL.")

    def on_open_url(self):
        url = self.url.get_text()
        if url:
            open_page(url)

    def _populate_mod_info(self, data:dict):
        # Data is dict of {id: info}
        if not data:
            QMessageBox.warning(self, "Mod not found", "Could not find any mod matching the search criteria.")
            return

        # Get first key (ID) and value (Info)
        mod_id = next(iter(data))
        info = data[mod_id]
        
        # Update URL field if empty (Auto-Search case) or different
        current_url = self.url.get_text()
        new_url = f"https://gamebanana.com/mods/{mod_id}"
        if not current_url or current_url != new_url:
             self.url.set_text(new_url)

        # Populate fields
        if info.get("mod_name"):
            self.mod_name.setText(info["mod_name"])
            
        if info.get("authors"):
            self.author.setText(info["authors"])
            
        if info.get("version"):
            self.version.setText(info["version"])

        # Populate Description (Only if empty)
        if info.get("description"):
            current_desc = self.description.toPlainText().strip()
            if not current_desc:
                self.description.setText(info["description"])

        # Populate Preview Selector
        if info.get("preview_files"):
            files = info["preview_files"]
            links = info["preview_links"]
            self.preview_selector.blockSignals(True)
            self.preview_selector.clear()
            self.preview_map = {}
            
            # Combine logic if lengths match (they should from gamebanana.py)
            for i, name in enumerate(files):
                if i < len(links):
                    self.preview_map[name] = links[i]
                    self.preview_selector.addItem(name)
            
            self.preview_selector.blockSignals(False)

            if self.preview_selector.count() > 0:
                self.preview_selector.setPlaceholderText("Select Preview Image")
                
                # Check if current mod has a valid thumbnail
                has_thumbnail = False
                if self.mod and self.mod.thumbnail and os.path.exists(self.mod.thumbnail):
                    has_thumbnail = True
                
                # If no thumbnail exists, auto-select the first one from GB
                if not has_thumbnail:
                    # Manually trigger download if signal assumes change (index might be 0 already if logic differs, but here it is new items)
                    # Actually, if we just added items, index is -1. Setting to 0 should trigger.
                    self.preview_selector.setCurrentIndex(0)
                else:
                    self.preview_selector.setCurrentIndex(-1)

        # Wifi Safe
        if "is_wifi_safe" in info:
            is_safe = info["is_wifi_safe"]
            safe_index = 0 if is_safe else 2 
            
            try:
                if is_safe:
                    target = Wifi.SAFE.value
                else:
                    target = Wifi.UNCERTAIN.value # Default to uncertain
                
                self.wifi.setCurrentText(target)
            except:
                pass

        # Elements (Moveset / Final Smash)
        targets = []
        if info.get("is_moveset"):
            targets.append("Moveset")
        if info.get("is_final_smash"):
            targets.append("Final Smash")
            
        if targets:
            for i in range(self.elements.get_item_count()):
                item = self.elements.model().invisibleRootItem().child(i)
                if item.text() in targets:
                    item.setCheckState(Qt.CheckState.Checked)
            self.elements.update_display()

        # Trigger name generation updates
        self._update_generated_names()

    
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
        mod_name = self.mod_name.text().strip()
        if not mod_name:
            return
        
        category_str = self.category.currentText()
        
        if category_str == Category.STAGE.value:
            # Use Stage Name and Slot fields for generation
            if self.stage_assignments.isVisible():
                # Advanced Mode
                assignments = self.stage_assignments.get_assignments()
                checked_stages = []
                checked_stage_slots = []
                
                for item in assignments:
                    stage_key = item["id"]
                    stage_name = DataManager.get_stage_data(stage_key, "Value")
                    if stage_name:
                        checked_stages.append(stage_name)
                    checked_stage_slots.extend(item["slots"])
                
                # Unique slots
                checked_stage_slots = sorted(list(set(checked_stage_slots)))
            
            else:
                # Simple Mode
                checked_stages = []
                for i in range(self.stages.get_item_count()):
                    item = self.stages.model().invisibleRootItem().child(i)
                    if item.checkState() == Qt.CheckState.Checked:
                        stage_text = item.text()
                        checked_stages.append(stage_text)
                
                # Stage Slots
                checked_stage_slots = []
                for i in range(self.stage_slots.get_item_count()):
                    item = self.stage_slots.model().invisibleRootItem().child(i)
                    if item.checkState() == Qt.CheckState.Checked:
                        slot_text = item.text()
                        checked_stage_slots.append(slot_text)
            
            characters_str_display = format_stage_names_for_display(checked_stages)
            characters_str_folder = format_stage_names_for_folder(checked_stages)
            
            slots_str_display = format_stage_slots(checked_stage_slots)
            slots_str_folder = format_stage_slots_for_folder(checked_stage_slots)

        else:
            # Characters
            if self.char_assignments.isVisible():
                # Advanced Mode
                assignments = self.char_assignments.get_assignments()
                checked_chars = []
                checked_slots = []
                
                for item in assignments:
                    char_key = item["id"]
                    char_name = DataManager.get_character_Name(char_key) # Helper needed or direct dict access
                    char_data = DataManager.get_character_by_key().get(char_key)
                    if char_data:
                        name = char_data[1] if char_data[1] else char_data[0]
                        checked_chars.append(name)
                    
                    # Parse slots C00 -> 0
                    for s_text in item["slots"]:
                        try:
                            if s_text.startswith("C"):
                                checked_slots.append(int(s_text[1:]))
                        except:
                            pass
                
                checked_slots = sorted(list(set(checked_slots)))
                
            else:
                # Simple Mode
                checked_chars = self.character.get_checked()
                checked_chars = [c for c in checked_chars]
                
                checked_slots = []
                for i in range(self.slots.get_item_count()):
                    item = self.slots.model().invisibleRootItem().child(i)
                    if item.checkState() == Qt.CheckState.Checked:
                        slot_text = item.text()
                        try:
                            slot_num = int(slot_text[1:])  # Remove 'C' prefix
                            checked_slots.append(slot_num)
                        except (ValueError, IndexError):
                            pass
            
            characters_str_display = format_character_names_for_display(checked_chars)
            characters_str_folder = format_character_names_for_folder(checked_chars)
            
            slots_str_folder = ""
            slots_str_display = ""
            if checked_slots:
                sorted_slots = sorted(checked_slots)
                # Get cap_slots settings from config
                cap_slots_folder = self.config_manager.config.name_rules.cap_slots_folder
                cap_slots_display = self.config_manager.config.name_rules.cap_slots_display
                slots_str_folder = format_slots(sorted_slots, cap_slots_folder)
                slots_str_display = format_slots(sorted_slots, cap_slots_display)
        
        folder_name = format_folder_name(characters_str_folder, slots_str_folder, mod_name, category_str)
        
        display_name = format_display_name(characters_str_display, slots_str_display, mod_name, category_str)
        
        self.folder.setText(folder_name)
        self.display.setText(display_name)
    
    def load_mod(self, mod_id: str):
        """Load mod data into edit panel"""
        # Reset panel first to clear any previous state
        self.reset()
        
        mod = self.mod_manager.get_mod(mod_id)
        self.mod = mod # Store ref
        self.mod_path = mod.path # Store path for saving
        self.pending_preview_path = None # Reset pending changes
        
        # Set URL if available
        if mod.url:
            self.url.set_text(mod.url)
        else:
            self.url.set_text("")
        
        # Set mod name
        self.mod_name.setText(mod.mod_name)
        
        # Set characters
        # Check if we need advanced mode (mixed slots)
        mixed_slots = False
        first_slots = None
        if len(mod.characters) > 0:
            first_slots = set(mod.characters[0].slots)
            for char in mod.characters[1:]:
                if set(char.slots) != first_slots:
                    mixed_slots = True
                    break
        
        if mixed_slots:
            # Switch to Advanced Mode
            self.char_simple_container.setVisible(False)
            self.char_assignments.setVisible(True)
            
            # Populate Assignment List
            data = []
            if mod.characters:
                for char in mod.characters:
                     slots_text = [f"C{s:02d}" for s in char.slots]
                     data.append({"id": char.fighter, "slots": slots_text})
            self.char_assignments.set_assignments(data)
            
            # Clear simple view to avoid confusion? Or just leave it.
            self.character.reset()
            self.slots.reset()
            
        else:
            # Simple Mode
            self.char_simple_container.setVisible(True)
            self.char_assignments.setVisible(False)

            # Standard loading logic (check all matching fighters)
            for i in range(self.character.get_item_count()):
                item = self.character.model().invisibleRootItem().child(i)
                char_text = item.text()
                
                # Convert custom name back to Fighter key for comparison
                fighter_key = DataManager.get_character_by_custom(char_text)
                
                # Match character from mod's character list
                is_checked = any(char.fighter == fighter_key for char in mod.characters)
                item.setCheckState(Qt.CheckState.Checked if is_checked else Qt.CheckState.Unchecked)
            
            self.character.update_display()
            
            # Set slots (common slots)
            common_slots = first_slots if first_slots else set()
            self.slots.model().blockSignals(True)
            try:
                for i in range(self.slots.get_item_count()):
                    item = self.slots.model().invisibleRootItem().child(i)
                    slot_text = item.text()

                    try:
                        slot_num = int(slot_text[1:])
                        is_checked = slot_num in common_slots
                        item.setCheckState(Qt.CheckState.Checked if is_checked else Qt.CheckState.Unchecked)
                    except: pass
            finally:
                self.slots.model().blockSignals(False)
            self.slots.update_display()

        
        # Set category
        try:
            self.category.setCurrentText(mod.category.value)
        except AttributeError:
            self.category.setCurrentText(Category.MISC.value)
        
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
            
            # Match element from mod's includes list
            is_checked = any(el.value == element_text for el in mod.includes)
            item.setCheckState(Qt.CheckState.Checked if is_checked else Qt.CheckState.Unchecked)
        
        self.elements.update_display()

        # Set Stages
        # Check for mixed stage slots
        mixed_stage_slots = False
        first_stage_slots = None
        if len(mod.stages) > 0:
            first_stage_slots = set([s.value for s in mod.stages[0].slots])
            for stage in mod.stages[1:]:
                current_slots = set([s.value for s in stage.slots])
                if current_slots != first_stage_slots:
                    mixed_stage_slots = True
                    break
        
        if mixed_stage_slots:
             # Advanced Stage Mode
            self.stage_simple_container.setVisible(False)
            self.stage_assignments.setVisible(True)
            
            data = []
            if mod.stages:
                for stage in mod.stages:
                    slots_text = [s.value for s in stage.slots]
                    val = stage.stage.value if hasattr(stage.stage, 'value') else str(stage.stage)
                    data.append({"id": val, "slots": slots_text})
            self.stage_assignments.set_assignments(data)
            
            self.stages.reset()
            self.stage_slots.reset()
        else:
            # Simple Stage Mode
            self.stage_simple_container.setVisible(True)
            self.stage_assignments.setVisible(False)

            for i in range(self.stages.get_item_count()):
                item = self.stages.model().invisibleRootItem().child(i)
                stage_text = item.text()
                stage_key = DataManager.get_stage_by_name(stage_text)
                is_checked = any(s.stage == stage_key for s in mod.stages)
                item.setCheckState(Qt.CheckState.Checked if is_checked else Qt.CheckState.Unchecked)
            self.stages.update_display()
            
            common_s_slots = first_stage_slots if first_stage_slots else set()
            for i in range(self.stage_slots.get_item_count()):
                item = self.stage_slots.model().invisibleRootItem().child(i)
                slot_text = item.text()
                is_checked = slot_text in common_s_slots
                item.setCheckState(Qt.CheckState.Checked if is_checked else Qt.CheckState.Unchecked)
            self.stage_slots.update_display()
        
        # Set wifi safe
        try:
            self.wifi.setCurrentText(mod.wifi_safe.value)
        except AttributeError:
            self.wifi.setCurrentText(Wifi.UNCERTAIN.value)
        
        # Set display name
        self.display.setText(mod.display_name)
        
        # Set folder name
        self.folder.setText(mod.folder_name)
        
        # Set thumbnail from mod's preview.webp
        self.thumbnail.set_thumbnail(mod.thumbnail)
    
    def reset(self):
        """Clear all fields to their default state and remove any temporary preview data."""
        self.url.input_box.clear()
        self.mod_name.clear()
        self.character.reset()
        self.slots.reset()
        self.stages.reset()
        self.stage_slots.reset()
        self.category.setCurrentText(Category.MISC.value)
        self.author.clear()
        self.version.clear()
        self.description.clear()
        self.elements.reset()
        self.wifi.setCurrentText(Wifi.UNCERTAIN.value)
        self.display.clear()
        self.folder.clear()
        # Clear preview selector and map
        self.preview_selector.clear()
        self.preview_map = {}
        # Delete temporary preview file if it exists
        if self.pending_preview_path and os.path.exists(self.pending_preview_path):
            try:
                os.remove(self.pending_preview_path)
            except Exception:
                pass
        self.pending_preview_path = None
        self.mod_path = None
        self.mod = None
        # Reset thumbnail widget to placeholder/empty
        try:
            self.thumbnail.set_thumbnail("")
        except Exception:
            pass
    
    def on_cancel(self):
        """Cancel edit and close panel"""
        self.reset()
        self.close_requested.emit()
    
    def on_save(self):
        """Save changes"""
        # 1. Update Mod Object
        self.mod.mod_name = self.mod_name.text()
        self.mod.url = self.url.get_text()
        self.mod.authors = self.author.text()
        self.mod.version = self.version.text()
        self.mod.display_name = self.display.text()
        self.mod.folder_name = self.folder.text()
        self.mod.description = self.description.toPlainText()
        
        # Enums
        try:
            self.mod.wifi_safe = Wifi(self.wifi.currentText())
        except:
            pass 
             
        try:
            self.mod.category = Category(self.category.currentText())
        except:
            pass
            
        # Elements
        self.mod.includes = []
        checked_elements = self.elements.get_checked()
        for text in checked_elements:
            try:
                self.mod.add_to_included(Element(text))
            except:
                pass

        # Characters
        new_chars = []
        if self.char_assignments.isVisible():
            # Advanced Mode
            assignments = self.char_assignments.get_assignments()
            for item in assignments:
                fighter = item["id"]
                slots = []
                for s_text in item["slots"]:
                    try:
                         if s_text.startswith("C"):
                             slots.append(int(s_text[1:]))
                    except: pass
                slots.sort()
                new_chars.append(Character(fighter=fighter, slots=slots))
        else:
            # Simple Mode
            selected_chars = self.character.get_checked()
            selected_slots_text = self.slots.get_checked()
            slots = []
            for text in selected_slots_text:
                try:
                    slots.append(int(text[1:]))
                except:
                    pass
            
            for char_text in selected_chars:
                try:
                    # Convert display name ("Mario") to Fighter key value ("mario")
                    fighter = DataManager.get_character_by_custom(char_text)
                    if fighter:
                        new_chars.append(Character(fighter=fighter, slots=slots))
                except:
                    pass
        
        self.mod.characters = new_chars

        # Stages
        from src.models.mod import StageModel
        from src.constants.enums import Stage, StageSlot
        
        new_stages = []
        if self.stage_assignments.isVisible():
             # Advanced Mode
             assignments = self.stage_assignments.get_assignments()
             for item in assignments:
                stage_key = item["id"]
                stage_slots = []
                for s_text in item["slots"]:
                    try:
                        stage_slots.append(StageSlot(s_text))
                    except: pass
                new_stages.append(StageModel(stage=Stage(stage_key), slots=stage_slots))
        else:
            # Simple Mode
            selected_stages = self.stages.get_checked()
            selected_stage_slots_text = self.stage_slots.get_checked()
            
            stage_slots = []
            for text in selected_stage_slots_text:
                try:
                    stage_slots.append(StageSlot(text))
                except:
                    pass
                    
            for stage_text in selected_stages:
                try:
                    stage_key = DataManager.get_stage_by_name(stage_text)
                    if stage_key:
                        new_stages.append(StageModel(stage=Stage(stage_key), slots=stage_slots))
                except:
                    pass
        
        self.mod.stages = new_stages

        # 2. Save Preview (Deferred)
        if self.pending_preview_path and self.mod_path:
            try:
                dest = os.path.join(self.mod_path, "preview.webp")
                shutil.copy2(self.pending_preview_path, dest)
                
                # Invalidate cache for this image
                ImageCache().remove(dest)
                
                # Update Mod's thumbnail path immediately
                self.mod.thumbnail = dest
            except Exception as e:
                print(f"Error saving preview: {e}")
                
        # 3. Generate TOML & Rename
        try:
            generate_toml(self.mod)
             
            new_dir = os.path.join(get_parent_dir(self.mod.path), self.mod.folder_name)
            if os.path.exists(new_dir):
                self.mod.path = new_dir
                self.mod_path = new_dir # Update local ref too
                
                if self.mod.thumbnail and not os.path.exists(self.mod.thumbnail):
                    base_name = os.path.basename(self.mod.thumbnail)
                    possible_new = os.path.join(new_dir, base_name)
                    if os.path.exists(possible_new):
                        self.mod.thumbnail = possible_new
                    else:
                        self.mod.thumbnail = os.path.join(new_dir, "preview.webp")
            else:
                pass
                
        except Exception as e:
            print(f"Save error: {e}")
             
        # 4. Update Persistent Cache
        try:
            # ModLoader uses path as key. Path is now self.mod.path (updated above if renamed).
            cache_data = self.mod.model_dump(mode='json', exclude={'is_selected', 'path', 'hash'})
            CacheManager().set_cached_mod(self.mod.path, cache_data)
        except Exception as e:
            print(f"Cache update error: {e}")

        # 5. Emit
        self.save_complete.emit(str(self.mod.hash))
        
        self.reset()
        self.close_requested.emit()

    def on_browse_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Preview Image", "", "Images (*.png *.jpg *.jpeg *.webp)")
        if file_path:
            self.pending_preview_path = file_path
            self.thumbnail.set_thumbnail(file_path)

    def on_preview_selected(self, index):
        name = self.preview_selector.currentText()
        url = self.preview_map.get(name)
        if not url:
            return
            
        # Download in background to avoid freezing UI
        if hasattr(self, 'image_downloader') and self.image_downloader.isRunning():
            self.image_downloader.terminate()
            self.image_downloader.wait()
            
        self.image_downloader = ImageDownloadThread(url)
        self.image_downloader.finished.connect(self._on_download_complete)
        self.image_downloader.error.connect(lambda e: print(f"Download error: {e}"))
        self.image_downloader.start()
        
    def _on_download_complete(self, path):
         self.pending_preview_path = path
         self.thumbnail.set_thumbnail(path)

    def on_rescan(self):
        """Rescan the mod folder to detect elements and update the elements dropdown"""
        if not self.mod or not self.mod.path:
            QMessageBox.warning(self, "No Mod Loaded", "Please load a mod first before rescanning.")
            return
        
        # Create a temporary copy of the mod to scan
        from src.models.mod import Mod
        temp_mod = Mod(path=self.mod.path)
        
        # Run the scanner
        temp_mod = scan_mod(temp_mod)
        
        # Build set of detected element values for quick lookup
        detected_elements = {el.value for el in temp_mod.includes}
        
        # Update elements checkboxes using text-based matching
        for i in range(self.elements.get_item_count()):
            item = self.elements.model().invisibleRootItem().child(i)
            element_text = item.text()
            is_checked = element_text in detected_elements
            item.setCheckState(Qt.CheckState.Checked if is_checked else Qt.CheckState.Unchecked)
        
        self.elements.update_display()
        
        # Also update category if it was detected
        if temp_mod.category:
            try:
                self.category.setCurrentText(temp_mod.category.value)
            except AttributeError:
                pass
        
        # Update characters and slots from scan
        if temp_mod.characters:
            # Build set of detected fighter keys
            detected_fighters = {char.fighter for char in temp_mod.characters}
            
            # Update characters using text-based matching
            for i in range(self.character.get_item_count()):
                item = self.character.model().invisibleRootItem().child(i)
                char_text = item.text()
                fighter_key = DataManager.get_character_by_custom(char_text)
                is_checked = fighter_key in detected_fighters
                item.setCheckState(Qt.CheckState.Checked if is_checked else Qt.CheckState.Unchecked)
            
            self.character.update_display()
            
            # Collect all slots from detected characters
            all_slots = set()
            for char in temp_mod.characters:
                all_slots.update(char.slots)
            
            # Update slots using text-based matching
            self.slots.model().blockSignals(True)
            try:
                for i in range(self.slots.get_item_count()):
                    item = self.slots.model().invisibleRootItem().child(i)
                    slot_text = item.text()
                    try:
                        slot_num = int(slot_text[1:])  # "C00" -> 0
                        is_checked = slot_num in all_slots
                        item.setCheckState(Qt.CheckState.Checked if is_checked else Qt.CheckState.Unchecked)
                    except (ValueError, IndexError):
                        pass
            finally:
                self.slots.model().blockSignals(False)
            
            self.slots.update_display()
        
        # Update stages and stage slots from scan
        if temp_mod.stages:
            # Stages
            detected_stages = {s.stage for s in temp_mod.stages}
            for i in range(self.stages.get_item_count()):
                item = self.stages.model().invisibleRootItem().child(i)
                stage_text = item.text()
                stage_key = DataManager.get_stage_by_name(stage_text)
                is_checked = stage_key in detected_stages
                item.setCheckState(Qt.CheckState.Checked if is_checked else Qt.CheckState.Unchecked)
            self.stages.update_display()
            
            # Stage Slots
            all_stage_slots = set()
            for s in temp_mod.stages:
                for slot in s.slots:
                    all_stage_slots.add(slot.value)
            
            for i in range(self.stage_slots.get_item_count()):
                item = self.stage_slots.model().invisibleRootItem().child(i)
                slot_text = item.text()
                is_checked = slot_text in all_stage_slots
                item.setCheckState(Qt.CheckState.Checked if is_checked else Qt.CheckState.Unchecked)
            self.stage_slots.update_display()
            
        # Update generated names
        self._update_generated_names()
