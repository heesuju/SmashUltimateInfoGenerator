from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, 
    QGridLayout, QLineEdit, QToolTip, QFileDialog, QTextEdit, QComboBox,
    QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QFont, QMovie, QCursor
from src.models.mod import Mod
from src.managers.batch_manager import BatchTaskStatus, BatchTask
from src.managers.data_manager import DataManager
from src.constants.enums import Category, Element, Wifi
from src.ui.components.multi_combobox import CheckableComboBox
from src.ui.components.single_combobox import SingleComboBox
from src.ui.components.validators import limit_version
from src.models.mod import Character, StageModel
from src.constants.enums import Stage, StageSlot
from src.core.formatting import (
    format_slots, format_display_name, format_folder_name, 
    format_character_names_for_display, format_character_names_for_folder, clean_version, 
    format_stage_names_for_display, format_stage_names_for_folder,
    format_stage_slots, format_stage_slots_for_folder
)
import os

# Import styles and rows
from src.ui.components.batch_task_styles import *
from src.ui.components.batch_task_rows import (
    truncate_text, truncate_to_lines, BatchTaskRow, TextRow, DescriptionRow, 
    ComboRow, MultiComboRow, ThumbnailRow, GridCell, AutoResizingTextEdit, AssignmentRow
)


class ClickableHeader(QWidget):
    clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
            event.accept()
        else:
            super().mousePressEvent(event)

class BatchTaskItem(QWidget):
    """Widget representing a single batch task with all info.toml fields"""
    
    remove_requested = pyqtSignal(str)  # Emits mod hash
    
    def __init__(self, task: BatchTask):
        super().__init__()
        self.task = task
        self.mod = task.mod
        self.input_fields = {}  # Store references to input widgets
        self.rows = {} # Store references to Row objects (for highlighting)
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
        
        self.orig_stages = []
        if self.task.original_stages:
            for s in self.task.original_stages:
                stage_key = s.get("stage")
                if stage_key:
                    name = DataManager.get_stage_data(stage_key, "Value")
                    if name:
                        self.orig_stages.append(name)
        self.orig_stages.sort()

        self.orig_stage_slots_set = set()
        if self.task.original_stages:
            for s in self.task.original_stages:
                slots = s.get("slots", [])
                self.orig_stage_slots_set.update(slots)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 10)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)
        
        # Header row: Mod name, status, remove button
        # ClickableHeader allows collapsing the view
        header_widget = ClickableHeader()
        header_widget.clicked.connect(self.toggle_collapse)
        header_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(128, 128, 128, 0.1);
                border: 1px solid rgba(128, 128, 128, 0.3);
                border-radius: 4px;
            }
            QWidget:hover {
                 background-color: rgba(128, 128, 128, 0.2);
            }
        """)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 8, 10, 8)
        
        # Arrow indicator
        self.arrow_label = QLabel("▼") # Starts expanded, but toggle_collapse will fix it
        self.arrow_label.setStyleSheet("border: none; background: transparent; color: #aaa; font-size: 10px;")
        header_layout.addWidget(self.arrow_label)
        
        # Mod name - prioritize display_name from TOML if available
        display_name = self.mod.display_name if self.mod.contains_info and self.mod.display_name else self.mod.mod_name
        name_label = QLabel(display_name)
        name_label.setStyleSheet("border: none; background: transparent;")
        name_font = QFont("Arial", 11)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setWordWrap(True)
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
                color: #aaa;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #ff6666;
                background-color: rgba(255, 100, 100, 0.15);
                border-radius: 12px;
            }
        """)
        # Stop propagation to prevent collapsing when clicking remove
        # Note: In Qt, buttons usually consume mouse events so this is implicit,
        # but good to be aware.
        remove_btn.clicked.connect(lambda: self.remove_requested.emit(str(self.mod.hash)))
        header_layout.addWidget(remove_btn)

        main_layout.addWidget(header_widget)

        # Create table with QTableWidget
        from PyQt6.QtWidgets import QTableWidget, QHeaderView, QAbstractScrollArea, QAbstractItemView

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Field", "Original (info.toml)", "New (editable)"])

        # Configure Table Structure
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed) # Fit field names
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)          # Stretch original
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)          # Stretch new
        self.table.setColumnWidth(0, 100)

        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setMinimumSectionSize(24)
        self.table.verticalHeader().setDefaultSectionSize(24)
        self.table.setShowGrid(False)  # We handle borders in the cells or style
        self.table.setAlternatingRowColors(False)

        # Sizing and Scrolling policies
        # Ideally, we want the table to be as tall as its content so the parent scrollarea handles scrolling
        self.table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Add basic styling to match previous look
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                border: none;
            }
            QHeaderView::section {
                background-color: rgba(128, 128, 128, 0.2);
                border: 1px solid rgba(128, 128, 128, 0.3);
                padding: 4px;
                font-weight: bold;
            }
        """)

        # Fonts
        data_font = QFont("Arial", 9)

        # Define rows to add
        # We'll collect them first then add
        task_rows = []

        # Field order: mod_name, version, wifi_safe, authors, category, playable_character, slots, elements,
        # description, display_name, folder_name, thumbnail, url

        # --- Mod Name ---
        mod_name_row = TextRow(
            "Mod Name", data_font,
            self.mod.mod_name if self.mod.contains_info else "",
            self.mod.mod_name, "mod_name",
            lambda attr, val: (self._update_generated_names(), self._on_field_changed(attr, val))
        )
        task_rows.append(("mod_name", mod_name_row))

        # --- URL ---
        url_text = self.mod.url if self.mod.url else ""
        url_row = TextRow(
            "URL", data_font,
            url_text, url_text, "url",
            lambda attr, val: self._on_field_changed(attr, val)
        )
        task_rows.append(("url", url_row))

        # --- Version ---
        version_text = self.mod.version if self.mod.version else ""
        version_row = TextRow(
            "Version", data_font,
            version_text, version_text, "version",
            lambda attr, val: self._on_field_changed(attr, val)
        )
        task_rows.append(("version", version_row))

        # --- Wifi Safe (Single Combo) ---
        current_wifi = self.mod.wifi_safe.value if self.mod.wifi_safe else Wifi.SAFE.value
        orig_wifi = self.task.original_wifi_safe if self.task.original_wifi_safe else ""

        wifi_row = ComboRow(
            "Wifi Safe", data_font,
            orig_wifi, current_wifi, Wifi.list(), "wifi_safe",
            lambda attr, val: self._on_field_changed(attr, val)
        )
        task_rows.append(("wifi_safe", wifi_row))

        # --- Authors ---
        authors_text = self.mod.authors if self.mod.authors else ""
        authors_row = TextRow(
            "Authors", data_font,
            authors_text, authors_text, "authors",
            lambda attr, val: self._on_field_changed(attr, val)
        )
        task_rows.append(("authors", authors_row))

        # --- Category (Single Combo) ---
        current_cat = self.mod.category.value if self.mod.category else Category.SKIN.value
        orig_cat = self.task.original_category if self.task.original_category else ""

        category_row = ComboRow(
            "Category", data_font,
            orig_cat, current_cat, Category.list(), "category",
            lambda attr, val: (self._update_generated_names(), self._on_field_changed(attr, val))
        )
        task_rows.append(("category", category_row))

        # --- Display Name (Generated) ---
        display_name_text = self.mod.display_name if self.mod.display_name else ""
        display_name_row = TextRow(
            "Display Name", data_font,
            display_name_text, display_name_text, "display_name",
            lambda attr, val: self._on_field_changed(attr, val)
        )
        task_rows.append(("display_name", display_name_row))

        # --- Folder Name (Export Name) ---
        folder_name_text = self.mod.folder_name if self.mod.folder_name else ""
        folder_name_row = TextRow(
             "Folder Name", data_font,
             folder_name_text, folder_name_text, "folder_name",
             lambda attr, val: self._on_field_changed(attr, val)
        )
        task_rows.append(("folder_name", folder_name_row))

        # --- Description ---
        description_text = self.mod.description if self.mod.description else ""
        description_row = DescriptionRow(
            data_font,
            description_text, description_text,
            lambda attr, val: self._on_field_changed(attr, val)
        )
        task_rows.append(("description", description_row))

        # --- Playable Character (Slots) ---
        # Multi-select combo for characters and slots
        current_fighters = []
        if self.mod.characters:
            for c in self.mod.characters:
                val = c.fighter.value if hasattr(c.fighter, 'value') else str(c.fighter)
                name = DataManager.get_character_data(val, "Custom")
                if name:
                    current_fighters.append(name)
                else:
                    current_fighters.append(val)
        orig_fighters = self.orig_char_names
        orig_fighters_text = ", ".join(orig_fighters) if orig_fighters else "—"

        all_fighters = DataManager.get_character_names()

        def on_character_changed():
            self._update_generated_names()
            self._check_field_changed("playable_character")

        mixed_slots = False
        initial_assignments = []
        if self.mod.characters:
            first_slots = set(self.mod.characters[0].slots)
            for c in self.mod.characters:
                if set(c.slots) != first_slots:
                    mixed_slots = True
                
                # Prepare assignment data
                c_slots = [f"C{s:02d}" for s in c.slots]
                val = c.fighter.value if hasattr(c.fighter, 'value') else str(c.fighter)
                initial_assignments.append({"id": val, "slots": c_slots})
        char_row = MultiComboRow(
            "Fighters", data_font,
            orig_fighters_text, current_fighters, all_fighters, "playable_character",
            on_character_changed
        )
        if mixed_slots:
            slot_options_char = [f"C{i:02d}" for i in range(256)]
            def slot_formatter_adv(items):
                return format_slots(sorted([int(x[1:]) for x in items if x.startswith('C')]))
                
            adv_char_row = AssignmentRow(
                "Fighters", data_font,
                "Different slots per character",
                initial_assignments,
                DataManager.get_character_dict(),
                slot_options_char,
                slot_formatter_adv,
                "playable_character_advanced",
                lambda: (self._update_generated_names(), self._check_field_changed("playable_character_advanced"))
            )
            task_rows.append(("playable_character_advanced", adv_char_row))
        else:
            task_rows.append(("playable_character", char_row))
            
            # --- Slots (Only in simple mode) ---
            current_slots = []
            if self.mod.characters:
                for c in self.mod.characters:
                    current_slots.extend(c.slots)

            slot_options = [f"C{i:02d}" for i in range(256)] # Standard 256 limit
            slot_formatter = lambda items: format_slots(sorted([int(x[1:]) for x in items if x.startswith('C') and x[1:].isdigit()]))

            orig_slots = set()
            if self.task.original_characters:
                for c in self.task.original_characters:
                    slots = c.get("slots", [])
                    orig_slots.update(slots)
            orig_slots_text = format_slots(sorted(orig_slots)) if orig_slots else "—"

            slots_row = MultiComboRow(
                "Slots", data_font,
                orig_slots_text, current_slots, slot_options, "slots",
                lambda: (self._update_generated_names(), self._check_field_changed("slots")),
                formatter=slot_formatter
            )
            task_rows.append(("slots", slots_row))

        # --- Elements ---
        current_elements = [el.value for el in self.mod.includes] if self.mod.includes else []
        orig_elements = self.task.original_elements or []
        orig_elements_text = ", ".join(orig_elements) if orig_elements else "—"

        elements_row = MultiComboRow(
            "Elements", data_font,
            orig_elements_text, current_elements, Element.list(), "elements",
            lambda: self._check_field_changed("elements")
        )
        task_rows.append(("elements", elements_row))

        # --- Stages ---
        current_stages = []
        mixed_stage_slots = False
        initial_stage_assignments = []
        
        if self.mod.stages:
            first_slots = set([s.value for s in self.mod.stages[0].slots])
            for s in self.mod.stages:
                # Check mixed
                current_stage_slots = set([slot.value for slot in s.slots])
                if current_stage_slots != first_slots:
                    mixed_stage_slots = True
                
                # Validation / Name lookup
                val = s.stage.value if hasattr(s.stage, 'value') else str(s.stage)
                name = DataManager.get_stage_data(val, "Value")
                if name:
                    current_stages.append(name)
                
                # assignment data
                s_slots = [slot.value for slot in s.slots]
                initial_stage_assignments.append({"id": val, "slots": s_slots}) # "slots" key needed

        # Create stage dict for AssignmentRow
        stage_dict = {}
        stage_keys = DataManager.get_stage_keys() if hasattr(DataManager, "get_stage_keys") else []
        for key in DataManager.get_stage_keys():
            name = DataManager.get_stage_data(key, "Value")
            if name:
                stage_dict[key] = name
        
        orig_stages_text = ", ".join(self.orig_stages) if self.orig_stages else "—"
        all_stages = DataManager.get_stage_names()

        stages_row = MultiComboRow(
            "Stages", data_font,
            orig_stages_text, current_stages, all_stages, "stages",
            lambda: self._check_field_changed("stages")
        )
        if mixed_stage_slots:
            adv_stage_row = AssignmentRow(
                "Stages", data_font,
                "Different slots per stage",
                initial_stage_assignments,
                stage_dict,
                StageSlot.list(),
                format_stage_slots,
                "stages_advanced",
                lambda: (self._update_generated_names(), self._check_field_changed("stages_advanced"))
            )
            task_rows.append(("stages_advanced", adv_stage_row))
        else:
            task_rows.append(("stages", stages_row))
            
            # --- Stage Slots (Only in simple mode) ---
            current_stage_slots = []
            if self.mod.stages:
                # Flatten slots from all stages
                for s in self.mod.stages:
                    for slot in s.slots:
                        current_stage_slots.append(slot.value)
            
            orig_stage_slots_text = ", ".join(self.task.original_stages_slots) if hasattr(self.task, 'original_stages_slots') and self.task.original_stages_slots else "—"
            # Fallback if original_stages_slots not in task (it should be)
            if not hasattr(self.task, 'original_stages_slots'):
                # Try to reconstruct from orig objects? or just empty
                orig_stage_slots_text = "—"
            
            stage_slots_row = MultiComboRow(
                "Stage Slots", data_font,
                orig_stage_slots_text, current_stage_slots, StageSlot.list(), "stage_slots",
                lambda: (self._update_generated_names(), self._check_field_changed("stage_slots")),
                formatter=format_stage_slots
            )
            task_rows.append(("stage_slots", stage_slots_row))

        # --- Thumbnail ---
        thumb_row = ThumbnailRow(
            data_font, 
            self.task.original_thumbnail,
            None,
            self._on_thumbnail_source_changed
        )
        task_rows.append(("thumbnail", thumb_row))


        # --- Populate Table ---
        self.table.setRowCount(len(task_rows))
        self.row_indices = {} # Map key -> row index

        for i, (key, row_obj) in enumerate(task_rows):
            w1, w2, w3 = row_obj.create_widgets()

            # Helper to resize row allows optional arg for signals that emit nothing
            resize_row = lambda _=None, row_idx=i: self.table.resizeRowToContents(row_idx)

            # Connect input widget changes
            if hasattr(row_obj, 'input_widget') and hasattr(row_obj.input_widget, 'textChanged'):
                # Only resize description row on text change, others are fixed height
                if key == "description":
                    row_obj.input_widget.textChanged.connect(resize_row)

            # Connect sizeChanged signals from ANY widget in the row that supports it
            def connect_recursive(widget):
                if isinstance(widget, AutoResizingTextEdit) or hasattr(widget, 'sizeChanged'):
                    if hasattr(widget, 'sizeChanged'):
                        widget.sizeChanged.connect(resize_row)
                    elif isinstance(widget, AutoResizingTextEdit) and key == "description":
                         # Only connect textChanged/resize for description which is dynamic
                         widget.textChanged.connect(resize_row)

                # Check children
                if isinstance(widget, QWidget):
                    layout = widget.layout()
                    if layout:
                        for j in range(layout.count()):
                            item = layout.itemAt(j)
                            if item and item.widget():
                                connect_recursive(item.widget())

            connect_recursive(w2) # Original
            connect_recursive(w3) # New

            # Store references
            input_w = getattr(row_obj, 'input_widget', None)

            self.input_fields[key] = input_w if input_w else w3
            self.rows[key] = row_obj
            self.row_indices[key] = i

            self.table.setCellWidget(i, 0, w1)
            self.table.setCellWidget(i, 1, w2)
            self.table.setCellWidget(i, 2, w3)

            if key == "description":
                self.table.resizeRowToContents(i)
            else:
                self.table.setRowHeight(i, ROW_CONTENT_HEIGHT)

        main_layout.addWidget(self.table)

        self.is_collapsed = False
        self._update_generated_names()
        self._initial_check_all_fields()
        
        QTimer.singleShot(10, self._enforce_row_heights)
        self.toggle_collapse()

    def _enforce_row_heights(self):
        """Re-apply row heights to ensure single-line rows are compact"""
        for key, row_idx in self.row_indices.items():
            if key == "description":
                self.table.resizeRowToContents(row_idx)
            else:
                self.table.setRowHeight(row_idx, ROW_CONTENT_HEIGHT)

    def toggle_collapse(self):
        """Toggle table visibility, showing only Mod Name and URL when collapsed"""
        self.is_collapsed = not self.is_collapsed

        for key, row_idx in self.row_indices.items():
            if key in ["mod_name", "url"]:
                self.table.setRowHidden(row_idx, False)
            else:
                self.table.setRowHidden(row_idx, self.is_collapsed)

        # Adjust table height policy or just let it resize?
        # QTableWidget AdjustToContents should handle it, but we might need to trigger geometry update
        self.table.updateGeometry()
        self.adjustSize() # Optional: help parent layout adjust
        
        # Update arrow
        self.arrow_label.setText("▶" if self.is_collapsed else "▼")

    def _on_field_changed(self, attr_name: str, value: str):
        """Handle field value change - update the mod object"""
        if attr_name == "version":
            # First limit input characters, then format to 0.0.0
            limited = limit_version(value)
            formatted = clean_version(limited) if limited else ""
            if formatted != value and "version" in self.input_fields:
                self.input_fields["version"].blockSignals(True)
                self.input_fields["version"].setText(formatted)
                self.input_fields["version"].blockSignals(False)
        
        self._check_field_changed(attr_name)

    def _update_generated_names(self, *args):
        """Auto-regenerate folder_name and display_name from current field values"""
        if "mod_name" in self.input_fields:
            if hasattr(self.input_fields["mod_name"], 'text'):
                mod_name = self.input_fields["mod_name"].text()
            else: # Fallback if widget type changed not to have text()
                mod_name = self.mod.mod_name
        else:
            mod_name = self.mod.mod_name
        if not mod_name:
            return
        
        if "category" in self.input_fields:
            category_str = self.input_fields["category"].currentText()
        
        if category_str == Category.STAGE.value:
            # Use Stages and Stage Slots
            is_advanced = False
            if "stages_advanced" in self.rows:
                 is_advanced = True
            
            if is_advanced:
                assignments = self.rows["stages_advanced"].input_widget.get_assignments()
                checked_stages = []
                checked_stage_slots = []
                for item in assignments:
                    stage_key = item["id"]
                    name = DataManager.get_stage_data(stage_key, "Value")
                    if name: checked_stages.append(name)
                    checked_stage_slots.extend(item["slots"])
                checked_stage_slots = sorted(list(set(checked_stage_slots)))
            else:
                checked_stages = self.get_selected_stages()
                checked_stage_slots = self.get_selected_stage_slots()
            
            characters_str_display = format_stage_names_for_display(checked_stages)
            characters_str_folder = format_stage_names_for_folder(checked_stages)
            
            slots_str = format_stage_slots(checked_stage_slots)
            slots_str_folder = format_stage_slots_for_folder(checked_stage_slots)
            
        else:
            is_advanced = False
            if "playable_character_advanced" in self.rows:
                is_advanced = True

            if is_advanced:
                assignments = self.rows["playable_character_advanced"].input_widget.get_assignments()
                checked_chars = []
                checked_slots = []
                for item in assignments:
                    char_key = item["id"]
                    char_data = DataManager.get_character_by_key().get(char_key)
                    if char_data:
                        name = char_data[1] if char_data[1] else char_data[0]
                        checked_chars.append(name)
                    for s in item["slots"]:
                        try: checked_slots.append(int(s[1:]))
                        except: pass
                checked_slots = sorted(list(set(checked_slots)))
            else:
                checked_chars = self.get_selected_characters()
                checked_slots = self.get_selected_slots()

            characters_str_display = format_character_names_for_display(checked_chars)
            characters_str_folder = format_character_names_for_folder(checked_chars)
            
            slots_str = format_slots(sorted(checked_slots)) if checked_slots else ""
            slots_str_folder = slots_str 

        # Generate new names
        folder_name = format_folder_name(characters_str_folder, slots_str_folder, mod_name, category_str)
        display_name = format_display_name(characters_str_display, slots_str, mod_name, category_str)
        
        # Update the input fields (block signals to avoid infinite loop)
        if "folder_name" in self.input_fields:
            self.input_fields["folder_name"].blockSignals(True)
            self.input_fields["folder_name"].setText(folder_name)
            self.input_fields["folder_name"].blockSignals(False)
            self._check_field_changed("folder_name")
        
        if "display_name" in self.input_fields:
            self.input_fields["display_name"].blockSignals(True)
            self.input_fields["display_name"].setText(display_name)
            self.input_fields["display_name"].blockSignals(False)
            self._check_field_changed("display_name")

    def _initial_check_all_fields(self):
        """Check all fields for differences from original values on initialization"""
        fields_to_check = [
            "mod_name", "url", "version", "wifi_safe", "authors", 
            "category", "display_name", "folder_name", "description",
            "playable_character", "slots", "elements", "thumbnail",
            "stages", "stage_slots"
        ]
        
        for field_name in fields_to_check:
            if field_name in self.input_fields:
                self._check_field_changed(field_name)

    def _on_thumbnail_source_changed(self, index):
        """Handle thumbnail source selection change"""
        combo = self.input_fields["thumbnail"]
        text = combo.itemText(index)
        
        if text:
            self.pending_thumbnail_path = text
        else:
            self.pending_thumbnail_path = None
             
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
            current_desc = self.input_fields["description"].toPlainText().strip()
            if not current_desc:
                self.input_fields["description"].setText(description)
            
        if wifi_safe is not None and "wifi_safe" in self.input_fields:
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
            combo = self.input_fields["thumbnail"]
            existing_urls = set()
            for i in range(combo.count()):
                data = combo.itemData(i)
                if data:
                    existing_urls.add(str(data))
            
            added_count = 0
            for i, link in enumerate(preview_links):
                if link not in existing_urls:
                    combo.addItem(link) # Add URL directly as text
                    added_count += 1
            
            if added_count > 0 and combo.currentIndex() == 0:
                has_original = False
                if self.task.original_thumbnail and os.path.exists(self.task.original_thumbnail):
                    has_original = True
                
                if not has_original:
                    first_new_idx = combo.count() - added_count
                    if first_new_idx >= 0:
                        combo.setCurrentIndex(first_new_idx)

    def _check_field_changed(self, field_name: str):
        """Check if field value differs from original and update highlight"""
        widget = self.input_fields.get(field_name)
        row = self.rows.get(field_name)
        if not widget or not row: return
        
        changed = False
        
        if field_name == "mod_name":
            changed = widget.text() != (self.task.original_mod_name or "")
        elif field_name == "authors":
            changed = widget.text() != (self.task.original_authors or "")
        elif field_name == "version":
            orig = clean_version(limit_version(self.task.original_version) if self.task.original_version else "")
            new_val = clean_version(limit_version(widget.text()))
            changed = orig != new_val
        elif field_name == "url":
            changed = widget.text() != (self.task.original_url or "")
        elif field_name == "description":
            # Normalize for comparison: QTextEdit converts non-breaking spaces to regular spaces
            orig = (self.task.original_description or "").strip().replace('\xa0', ' ')
            new = widget.toPlainText().strip().replace('\xa0', ' ')
            changed = orig != new
        elif field_name == "display_name":
            changed = widget.text() != (self.task.original_display_name or "")
        elif field_name == "folder_name":
            changed = widget.text() != (self.task.original_folder_name or "")
        elif field_name == "category":
            changed = widget.currentText() != (self.task.original_category or "")
        elif field_name == "wifi_safe":
            changed = widget.currentText() != (self.task.original_wifi_safe or "")
        elif field_name == "playable_character":
            new_chars = self.get_selected_characters()
            new_chars.sort()
            changed = new_chars != self.orig_char_names
        elif field_name == "slots":
            new_slots = set(self.get_selected_slots())
            changed = new_slots != self.orig_slots_set
        elif field_name == "elements":
            new_elements = set(widget.get_checked())
            if "Select All" in new_elements: 
                new_elements.remove("Select All")
            changed = new_elements != self.orig_elements_set
        elif field_name == "stages":
            new_val = self.get_selected_stages()
            new_val.sort()
            changed = new_val != self.orig_stages
        elif field_name == "stage_slots":
            new_val = set(self.get_selected_stage_slots())
            changed = new_val != self.orig_stage_slots_set
        elif field_name == "thumbnail":
            changed = self.pending_thumbnail_path is not None
        elif field_name == "playable_character_advanced":
            row = self.rows.get(field_name)
            if row and row.input_widget:
                data = row.input_widget.get_assignments()
                changed = len(data) > 0 # Simplification
        elif field_name == "stages_advanced":
            row = self.rows.get(field_name)
            if row and row.input_widget:
                data = row.input_widget.get_assignments()
                changed = len(data) > 0
        
        # Apply highlight to the row/cell
        row.set_highlight(changed)

    def get_selected_characters(self) -> list:
        """Get list of selected character names"""
        if "playable_character" in self.input_fields:
            chars = self.input_fields["playable_character"].get_checked()
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

    def get_selected_stages(self) -> list:
        """Get list of selected stage names"""
        if "stages" in self.input_fields:
            stages = self.input_fields["stages"].get_checked()
            return [s for s in stages if s != "Select All"]
        return []
    
    def get_selected_stage_slots(self) -> list:
        """Get list of selected stage slot names"""
        if "stage_slots" in self.input_fields:
            slots = self.input_fields["stage_slots"].get_checked()
            return [s for s in slots if s != "Select All"]
        return []

    def get_final_characters(self) -> list:
        """Return list of Character objects based on current UI state (Simple or Advanced)"""
        # Advanced Mode
        if "playable_character_advanced" in self.rows:
            row = self.rows["playable_character_advanced"]
            if row.input_widget:
                assignments = row.input_widget.get_assignments() # [{"id": "mario", "slots": ["c00"]}]
                new_chars = []
                for item in assignments:
                    fighter_key = item["id"]
                    slots = []
                    for s_text in item["slots"]:
                        try:
                            if s_text.startswith("C"):
                                slots.append(int(s_text[1:]))
                        except: pass
                    new_chars.append(Character(fighter=fighter_key, slots=sorted(slots)))
                return new_chars
        
        # Simple Mode
        selected_chars = self.get_selected_characters()
        selected_slots = self.get_selected_slots()
        new_chars = []
        for char_name in selected_chars:
            fighter_key = DataManager.get_character_by_custom(char_name)
            if fighter_key:
                new_chars.append(Character(fighter=fighter_key, slots=selected_slots))
        return new_chars

    def get_final_stages(self) -> list:
        """Return list of StageModel objects based on current UI state (Simple or Advanced)"""
        # Advanced Mode
        if "stages_advanced" in self.rows:
            row = self.rows["stages_advanced"]
            if row.input_widget:
                assignments = row.input_widget.get_assignments() # [{"id": "battlefield", "slots": ["normal"]}]
                new_stages = []
                for item in assignments:
                    stage_key = item["id"]
                    stage_slots = []
                    for s_text in item["slots"]:
                        try:
                            stage_slots.append(StageSlot(s_text))
                        except: pass
                    new_stages.append(StageModel(stage=Stage(stage_key), slots=stage_slots))
                return new_stages

        # Simple Mode
        selected_stages = self.get_selected_stages()
        selected_stage_slots = self.get_selected_stage_slots()
        
        if not selected_stages:
            return []
            
        stage_slots_enums = []
        for s_text in selected_stage_slots:
            try:
                stage_slots_enums.append(StageSlot(s_text))
            except: pass
            
        new_stages = []
        for stage_name in selected_stages:
            stage_key = DataManager.get_stage_by_name(stage_name)
            if stage_key:
                new_stages.append(StageModel(stage=Stage(stage_key), slots=stage_slots_enums))
        return new_stages
    
    def update_status_display(self):
        """Update the status label based on current task status"""
        if self.task.status == BatchTaskStatus.PENDING:
            self.status_label.setText("⏳ Pending")
            self.status_label.setStyleSheet("border: none; background: transparent; color: #888;")
        elif self.task.status == BatchTaskStatus.PROCESSING:
            self.status_label.setText("⚙️ Processing")
            self.status_label.setStyleSheet("border: none; background: transparent; color: #2196F3;")
        elif self.task.status == BatchTaskStatus.COMPLETE:
            self.status_label.setText("✓ Complete")
            self.status_label.setStyleSheet("border: none; background: transparent; color: #4CAF50;")
        elif self.task.status == BatchTaskStatus.ERROR:
            self.status_label.setText("✗ Error")
            self.status_label.setStyleSheet("border: none; background: transparent; color: #f44336;")
        
        self.status_label.setToolTip(self.task.progress_message or self.task.error_message or "")
    
    def update_status(self, status: BatchTaskStatus, progress_message: str = "", error_message: str = ""):
        """Update the task status and display"""
        self.task.status = status
        self.task.progress_message = progress_message
        self.task.error_message = error_message
        
        self.update_status_display()