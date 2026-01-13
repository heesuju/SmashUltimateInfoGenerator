from pydantic import BaseModel
import os
from typing import List
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QWidget, QSizePolicy, QLabel, QFrame, QPushButton, QComboBox, QHBoxLayout
)
from PyQt6.QtGui import (
    QPixmap, QIcon, QFont
)
from src.core.formatting import format_slots
from src.ui.components.layout import VBox
from src.ui.grid_list import GridList
from src.ui.tree_list import TreeList
from src.models.mod import Mod, ModItem
from src.ui.components.toggle_button import ToggleButton
from src.ui.components.paging import Paging
from src.ui.search_bar import SearchBar
from src.ui.components.filter_chips import FilterChips
from src.managers.mod_manager import ModManager

from src.constants.enums import Fighter, ListLayout
from src.managers.data_manager import ButtonIcons, DataManager
from src.managers.filter_manager import FilterManager, FilterParameters
from src.managers.config_manager import ConfigManager
from src.constants.ui_params import SPACING, GRID_PAGE_SIZE, LIST_PAGE_SIZE

class ModList(QWidget):
    def __init__(self, mod_manager:ModManager, filter_manager:FilterManager, config_manager:ConfigManager):
        super().__init__()
        self.mod_manager = mod_manager
        
        self.mod_manager.set_callback(self.on_filter_changed)
        
        self.filter_manager = filter_manager
        self.filter_manager.add_callback(self.on_filter_changed)
        self.config_manager = config_manager

        self.mode = ListLayout.LIST
        
        layout = VBox()
        self.setLayout(layout)
        
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Performance optimization: Cache icon existence and group data
        self._icon_cache = {}  # Cache for icon file existence
        self._group_cache = {}  # Cache for group character data
        self._initialize_caches()
        
        # Cache for filtered results to avoid re-filtering on page changes
        self.cached_filtered_mods = []
        
        self.frame = QFrame()
        self.frame.setObjectName("modListFrame")
        self.frame.setFrameShape(QFrame.Shape.Box)
        self.frame.setAutoFillBackground(True)
        self.frame.setStyleSheet("""QFrame#modListFrame {
                                 border-radius: 0px;
                                 }""")
        self.frame_layout = VBox(margin=0, spacing=0)
        
        self.frame.setLayout(self.frame_layout)
        layout.addWidget(self.frame)
        
        # init mod list
        self.grid_list = GridList(self.mod_manager)
        self.tree_list = TreeList(self.mod_manager)

        self.search = SearchBar(self.mod_manager, self.filter_manager)
        self.frame_layout.addWidget(self.search)
        
        # Filter chips widget
        self.filter_chips = FilterChips(self.filter_manager)
        self.frame_layout.addWidget(self.filter_chips)

        # init child layouts
        header_layout = QHBoxLayout(spacing=10)
        
        self.frame_layout.addLayout(header_layout)

        self.body_layout = VBox()
        self.frame_layout.addLayout(self.body_layout)

        footer_layout = QHBoxLayout(spacing=10)
        self.frame_layout.addLayout(footer_layout)

        layout_toggle = ToggleButton(
            ButtonIcons.LIST.value, ButtonIcons.GRID.value, self.on_list_selected, self.on_grid_selected)
        header_layout.addWidget(layout_toggle)
        
        # Add header checkbox for select all
        from PyQt6.QtWidgets import QCheckBox, QLabel
        select_all_container = QHBoxLayout(spacing=4)
        self.header_checkbox = QCheckBox()
        self.header_checkbox.setFixedSize(20, 20)
        self.header_checkbox.setTristate(True)  # Allow partial state for visual feedback
        self.header_checkbox.stateChanged.connect(self.on_header_checkbox_changed)
        select_all_label = QLabel("Select All")
        select_all_container.addWidget(self.header_checkbox)
        select_all_container.addWidget(select_all_label)
        header_layout.addLayout(select_all_container)
        
        header_layout.addStretch(1)

        select_button = QPushButton("Deselect All")
        select_button.clicked.connect(self.on_deselect_all)
        header_layout.addWidget(select_button)
        
        add_button = QPushButton("+ Add New")
        header_layout.addWidget(add_button)

        action_dropdown = QComboBox()
        action_dropdown.addItems(["Batch Actions", "Enable", "Disable", "Generate Info.toml", "Remove"])
        header_layout.addWidget(action_dropdown)
        
        self.body_layout.addWidget(self.tree_list)
        
        self.paging = Paging(callback=self.on_page_changed)
        footer_layout.addWidget(self.paging)
        self.paging.page_size = LIST_PAGE_SIZE

        # Start scanning if valid root mod directory exists
        if self.config_manager.config.root_dir:
            self.scan()
    
    def _initialize_caches(self):
        """Initialize caches for icon existence and group data to improve performance"""
        # Pre-cache which character icons exist
        from src.constants.enums import Fighter
        for fighter in Fighter:
            icon_path = DataManager.get_character_icon(str(fighter.value))
            self._icon_cache[str(fighter.value)] = os.path.exists(icon_path)
        
        # Pre-cache group character data
        character_data = DataManager.get_character_data()
        groups = set()
        for char in character_data:
            group = char.get("Group")
            if group:
                groups.add(group)
        
        for group in groups:
            self._group_cache[group] = DataManager.get_group_characters(group)
            # Also cache whether the group icon exists
            icon_path = DataManager.get_character_icon(group)
            self._icon_cache[group] = os.path.exists(icon_path)

    def on_grid_selected(self):
        self.mode = ListLayout.GRID
        self.tree_list.setParent(None)
        self.body_layout.addWidget(self.grid_list)
        self.paging.cur_page = 1
        self.paging.page_size = GRID_PAGE_SIZE
        self.paging.update(len(self.cached_filtered_mods))
        self.update_view()
        
    def on_list_selected(self):
        self.mode = ListLayout.LIST
        self.grid_list.setParent(None)
        self.body_layout.addWidget(self.tree_list)
        self.paging.cur_page = 1
        self.paging.page_size = LIST_PAGE_SIZE
        self.paging.update(len(self.cached_filtered_mods))
        self.update_view()
    
    def on_page_changed(self, page:int, size:int):
        self.update_view()

    def on_filter_changed(self):
        self.refresh_filtered_data()

    def refresh_filtered_data(self):
        """Re-runs filtering/sorting and updates the cache. Called when filters/data change."""
        mods = self.mod_manager.get_mods()
        if self.filter_manager:
            mods = self.filter_manager.apply_filters(mods)
        self.cached_filtered_mods = mods
        
        # Reset to page 1 for new results
        self.paging.cur_page = 1
        self.paging.update(len(self.cached_filtered_mods))
        
        self.update_view()

    def update_view(self):
        """Updates the UI from the cached filtered data. Called on page/layout change."""
        # Clear immediately to show responsive feedback
        self.clear()
        
        # Defer the rendering to allow UI to remain responsive
        def process_render():
            total_items = len(self.cached_filtered_mods)
            self.populate(self.cached_filtered_mods)
            
            # Update count label in filter chips
            current_page = self.paging.cur_page
            page_size = self.paging.page_size
            current_items = min(page_size, total_items - (current_page - 1) * page_size)
            self.filter_chips.update_count(current_items, total_items)
        
        QTimer.singleShot(0, process_render)

    def set_data(self):
        """Legacy method - redirects to refresh_filtered_data"""
        self.refresh_filtered_data()

    def clear(self):
        self._populate_active = False
        self._populate_index = None
        self._populate_mods = None
        self.tree_list.clear()
        self.grid_list.clear()

    def populate(self, mods:List[Mod]):
        self.clear()
        current_page = self.paging.cur_page
        page_size = self.paging.page_size
        paged_mods = mods[(current_page - 1) * page_size : current_page * page_size]

        self._populate_index = 0
        self._populate_mods = paged_mods
        self._populate_active = True

        def process(mod:Mod)->ModItem:
            keys = mod.get_grouped_character_keys()
            
            # Check if group icons exist, if not ungroup them (using cache)
            final_keys = []
            for key in keys:
                # Use cached icon existence check
                icon_exists = self._icon_cache.get(key, False)
                if icon_exists:
                    # Icon exists, use the key as-is
                    final_keys.append(key)
                else:
                    # Icon doesn't exist, check if it's a group and ungroup it (using cache)
                    group_chars = self._group_cache.get(key, [])
                    if group_chars:
                        # This is a group without an icon, add all individual characters
                        final_keys.extend(group_chars)
                    else:
                        # Not a group, keep the key anyway (fallback)
                        final_keys.append(key)
            
            character_icons = DataManager.get_character_icons([character for character in final_keys])

            return ModItem(
                id=str(mod.hash),
                name=mod.mod_name,
                thumbnail=mod.thumbnail,
                category=str(mod.category),
                authors=mod.authors,
                slots=format_slots(mod.get_character_slots(), self.config_manager.config.name_rules.cap_slots_display),
                version=mod.version,
                enabled=False,
                selected=self.mod_manager.is_selected(str(mod.hash)),
                character_icons=character_icons
            )


        def add_next():
            if not self._populate_active or self._populate_index is None or self._populate_mods is None:
                return  # Stop if cancelled or cleared
            
            # Batch process multiple items per tick for better performance
            batch_size = 5
            end_index = min(self._populate_index + batch_size, len(self._populate_mods))
            
            for i in range(self._populate_index, end_index):
                mod = self._populate_mods[i]
                if self.mode == ListLayout.LIST:
                    self.tree_list.add_item(process(mod))
                elif self.mode == ListLayout.GRID:
                    self.grid_list.add_item(process(mod))
            
            self._populate_index = end_index
            
            if self._populate_index < len(self._populate_mods):
                QTimer.singleShot(0, add_next)
            else:
                self._populate_mods = None
                self._populate_index = None
                # Update header checkbox once after all items are loaded
                self.update_header_checkbox_state()

        add_next()

    def scan(self):
        self.mod_manager.scan_all()

    def on_scanned(self):
        self.refresh_filtered_data()
    
    def on_progress(self, mod:Mod):
        pass
        #     self.tree_list.add_item(mod)
        # elif self.mode == ModListMode.GRID:
        #     self.grid_list.add_item(mod)

    def on_mod_saved(self, mod_id:str):
        self.refresh_filtered_data()
    
    def on_header_checkbox_changed(self, state):
        """Handle header checkbox state change - delegates to current view"""
        from PyQt6.QtCore import Qt
        
        # If user clicks while in partial state, toggle to checked
        if state == Qt.CheckState.PartiallyChecked.value:
            # Block signals to prevent recursion
            self.header_checkbox.blockSignals(True)
            self.header_checkbox.setCheckState(Qt.CheckState.Checked)
            self.header_checkbox.blockSignals(False)
            state = Qt.CheckState.Checked.value
        
        if self.mode == ListLayout.LIST:
            # TreeList handles selection directly now
            self.tree_list.on_header_checkbox_changed(state)
        elif self.mode == ListLayout.GRID:
            # GridList will handle selection via its items
            self.grid_list.on_header_checkbox_changed(state)
    
    def on_deselect_all(self):
        """Deselect all mods"""
        self.mod_manager.clear_selection()
        # Update all checkboxes/visuals
        if self.mode == ListLayout.LIST:
            # Update row checkboxes
            for item_id, checkbox in self.tree_list.item_checkboxes.items():
                checkbox.blockSignals(True)
                checkbox.setChecked(False)
                checkbox.blockSignals(False)
            # Update header checkbox via ModList
            self.update_header_checkbox_state()
        elif self.mode == ListLayout.GRID:
            # Update visual state of all grid items
            for item_id, widget in self.grid_list.item_widgets.items():
                widget.mod.selected = False
                widget.update_selection_style()
            # Update header checkbox via ModList
            self.update_header_checkbox_state()
    
    def update_header_checkbox_state(self):
        """Update the shared header checkbox based on current view"""
        from PyQt6.QtCore import Qt
        
        if self.mode == ListLayout.LIST:
            # Calculate state from TreeList current page items
            if not self.tree_list.current_page_item_ids:
                self.header_checkbox.blockSignals(True)
                self.header_checkbox.setCheckState(Qt.CheckState.Unchecked)
                self.header_checkbox.blockSignals(False)
                return
            
            selected_count = sum(1 for item_id in self.tree_list.current_page_item_ids 
                               if self.mod_manager.is_selected(item_id))
            total_count = len(self.tree_list.current_page_item_ids)
            
            self.header_checkbox.blockSignals(True)
            if selected_count == 0:
                self.header_checkbox.setCheckState(Qt.CheckState.Unchecked)
            elif selected_count == total_count:
                self.header_checkbox.setCheckState(Qt.CheckState.Checked)
            else:
                self.header_checkbox.setCheckState(Qt.CheckState.PartiallyChecked)
            self.header_checkbox.blockSignals(False)
            
        elif self.mode == ListLayout.GRID:
            # Calculate state from GridList
            from PyQt6.QtCore import Qt
            if not self.grid_list.current_page_item_ids:
                self.header_checkbox.blockSignals(True)
                self.header_checkbox.setCheckState(Qt.CheckState.Unchecked)
                self.header_checkbox.blockSignals(False)
                return
            
            selected_count = sum(1 for item_id in self.grid_list.current_page_item_ids 
                               if self.mod_manager.is_selected(item_id))
            total_count = len(self.grid_list.current_page_item_ids)
            
            self.header_checkbox.blockSignals(True)
            if selected_count == 0:
                self.header_checkbox.setCheckState(Qt.CheckState.Unchecked)
            elif selected_count == total_count:
                self.header_checkbox.setCheckState(Qt.CheckState.Checked)
            else:
                self.header_checkbox.setCheckState(Qt.CheckState.PartiallyChecked)
            self.header_checkbox.blockSignals(False)