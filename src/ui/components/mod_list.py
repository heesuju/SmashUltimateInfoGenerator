import os
from typing import List
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QSizePolicy, QLabel, QFrame, QPushButton, QHBoxLayout,
    QMenu, QFileDialog, QMessageBox
)
from PyQt6.QtGui import (
    QPixmap, QIcon, QFont, QDragEnterEvent, QDropEvent, QColor
)

from src.core.formatting import format_slots, format_stage_slots
from src.models.mod import Mod, ModItem
from src.managers.mod_manager import ModManager
from src.managers.data_manager import ButtonIcons, DataManager
from src.managers.filter_manager import FilterManager, FilterParameters
from src.managers.config_manager import ConfigManager

from src.ui.components.layout import VBox, HBox
from src.ui.components.grid_list import GridList
from src.ui.components.tree_list import TreeList
from src.ui.components.toggle_button import ToggleButton
from src.ui.components.paging import Paging
from src.ui.components.search_bar import SearchBar
from src.ui.components.filter_chips import FilterChips

from src.utils.image_utils import tint_pixmap
from src.constants.enums import Fighter, ListLayout
from src.constants.ui_params import SPACING, GRID_PAGE_SIZE, LIST_PAGE_SIZE
from src.constants.colors import AppColors
from src.constants.strings import AppStrings

class ModList(QWidget):
    batch_tasks_added = pyqtSignal()  # Signal when tasks are added to batch queue
    data_changed = pyqtSignal() # Signal when data changes (thread-safe update)
    
    def __init__(self, mod_manager:ModManager, filter_manager:FilterManager, config_manager:ConfigManager, batch_manager=None):
        super().__init__()
        self.setAcceptDrops(True)
        self.mod_manager = mod_manager
        self.batch_manager = batch_manager
        
        self.mod_manager.set_callback(self.on_filter_changed)
        self.mod_manager.add_favorite_callback(self.on_favorite_changed)
        self.mod_manager.add_hidden_callback(self.on_hidden_changed)
        self.mod_manager.add_enabled_callback(self.on_enabled_changed)
        self.mod_manager.selection_changed.connect(self.on_selection_changed)
        
        self.filter_manager = filter_manager
        self.filter_manager.add_callback(self.on_filter_changed)
        self.config_manager = config_manager

        self.mode = ListLayout.LIST
        
        layout = VBox()
        self.setLayout(layout)
        
        self.setMinimumWidth(200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Performance optimization: Cache icon existence and group data
        self._icon_cache = {}  # Cache for icon file existence
        self._group_cache = {}  # Cache for group character data
        self._initialize_caches()
        
        # Cache for filtered results to avoid re-filtering on page changes
        self.cached_filtered_mods = []
        
        self.frame = QFrame()
        self.frame.setObjectName("modListFrame")
        self.frame.setFrameShape(QFrame.Shape.NoFrame)
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
        chips_container = HBox(margin=(10, 0))
        chips_container.addWidget(self.filter_chips)
        self.frame_layout.addLayout(chips_container)

        # init child layouts
        header_layout = HBox(spacing=4, margin=(10, 0))
        
        self.frame_layout.addLayout(header_layout)

        self.body_layout = VBox(margin=10)
        self.frame_layout.addLayout(self.body_layout)

        footer_layout = QHBoxLayout(spacing=10)
        self.frame_layout.addLayout(footer_layout)

        layout_toggle = ToggleButton(
            ButtonIcons.LIST.value, ButtonIcons.GRID.value, self.on_list_selected, self.on_grid_selected)
        header_layout.addWidget(layout_toggle)
        
        # Add header checkbox for select all
        from PyQt6.QtWidgets import QCheckBox
        self.header_checkbox = QCheckBox(AppStrings.ACTION_SELECT_ALL)
        self.header_checkbox.setTristate(True)  # Allow partial state for visual feedback
        self.header_checkbox.stateChanged.connect(self.on_header_checkbox_changed)
        header_layout.addWidget(self.header_checkbox)

        # Deselect/Clear Selection Button
        select_button = QPushButton()
        select_button.setIcon(QIcon(ButtonIcons.DESELECT.value))
        select_button.setToolTip(AppStrings.ACTION_DESELECT_ALL)
        select_button.setFixedWidth(24) # Small button
        select_button.setFlat(True) # Make it look like an icon
        select_button.clicked.connect(self.on_deselect_all)
        header_layout.addWidget(select_button)
        
        header_layout.addStretch(1)
        
        add_button = QPushButton(AppStrings.ACTION_ADD)
        tinted_add = tint_pixmap(QPixmap(ButtonIcons.ADD.value), QColor(AppColors.BUTTON_CYAN))
        add_button.setIcon(QIcon(tinted_add))
        add_button.setStyleSheet(f"QPushButton {{ color: {AppColors.BUTTON_CYAN}; }} QPushButton::menu-indicator {{ width: 0px; }}")
        add_button.setFlat(True)
        
        # Create menu for add button
        add_menu = QMenu(self)
        add_folder_action = add_menu.addAction(AppStrings.ADD_FROM_FOLDER)
        add_folder_action.triggered.connect(self.on_add_folder_clicked)
        add_zip_action = add_menu.addAction(AppStrings.ADD_FROM_ZIP)
        add_zip_action.triggered.connect(self.on_add_zip_clicked)
        
        add_button.setMenu(add_menu)
        header_layout.addWidget(add_button)
        
        # Helper to create batch button
        def create_batch_btn(icon_path, text, tooltip, callback, color=None):
            btn = QPushButton(text)
            
            if color:                
                pixmap = QPixmap(icon_path)
                tinted_pixmap = tint_pixmap(pixmap, QColor(color))
                btn.setIcon(QIcon(tinted_pixmap))
                btn.setStyleSheet(f"""
                    QPushButton {{ color: {color}; text-align: left; padding: 4px; }}
                    QPushButton:disabled {{ color: #666666; }}
                """)
            else:
                btn.setIcon(QIcon(icon_path))
                
            btn.setToolTip(tooltip)
            btn.setFlat(True)
            btn.clicked.connect(callback)
            return btn

        btn_generate = create_batch_btn(ButtonIcons.BATCH_GENERATE.value, AppStrings.ACTION_GENERATE, AppStrings.BATCH_GENERATE_TOOLTIP, lambda: self.on_batch_action_btn("Generate Info.toml"), color=AppColors.BUTTON_PURPLE)
        btn_enable = create_batch_btn(ButtonIcons.BATCH_ENABLE.value, AppStrings.ACTION_ENABLE, AppStrings.BATCH_ENABLE_TOOLTIP, lambda: self.on_batch_action_btn("Enable"), color=AppColors.BUTTON_GREEN)
        btn_disable = create_batch_btn(ButtonIcons.BATCH_DISABLE.value, AppStrings.ACTION_DISABLE, AppStrings.BATCH_DISABLE_TOOLTIP, lambda: self.on_batch_action_btn("Disable"), color=AppColors.BUTTON_RED)
        
        # Store buttons to update state
        self.btn_generate = btn_generate
        self.btn_enable = btn_enable
        self.btn_disable = btn_disable
        
        # More actions menu
        btn_more = QPushButton()
        btn_more.setIcon(QIcon(ButtonIcons.MORE.value))
        # More actions menu
        btn_more = QPushButton()
        btn_more.setIcon(QIcon(ButtonIcons.MORE.value))
        btn_more.setToolTip(AppStrings.ACTION_MORE)
        btn_more.setFixedWidth(30)
        btn_more.setFlat(True)
        
        more_menu = QMenu(self)
        self.remove_action = more_menu.addAction(QIcon(ButtonIcons.BATCH_REMOVE.value), AppStrings.BATCH_REMOVE_TOOLTIP)
        self.remove_action.triggered.connect(lambda: self.on_batch_action_btn("Remove"))
        btn_more.setMenu(more_menu)
        btn_more.setStyleSheet("QPushButton::menu-indicator { width: 0px; }")

        header_layout.addWidget(btn_generate)
        header_layout.addWidget(btn_enable)
        header_layout.addWidget(btn_disable)
        header_layout.addWidget(btn_more)
        
        self.body_layout.addWidget(self.tree_list)
        
        self.paging = Paging(callback=self.on_page_changed)
        footer_layout.addWidget(self.paging)
        self.paging.page_size = LIST_PAGE_SIZE

        # Start scanning if valid root mod directory exists
        if self.config_manager.config.root_dir:
            self.scan()
            
        self.data_changed.connect(self.refresh_filtered_data)
        
        # Initialize button states
        self.update_batch_buttons_state()
    
    def on_selection_changed(self, selected_ids: list):
        """Handle selection change signal"""
        self.update_batch_buttons_state()
        
    def update_batch_buttons_state(self):
        """Enable/Disable batch buttons based on selection count"""
        has_selection = len(self.mod_manager.selected_ids) > 0
        
        if hasattr(self, 'btn_generate'):
            self.btn_generate.setEnabled(has_selection)
        if hasattr(self, 'btn_enable'):
            self.btn_enable.setEnabled(has_selection)
        if hasattr(self, 'btn_disable'):
            self.btn_disable.setEnabled(has_selection)
        if hasattr(self, 'remove_action'):
            self.remove_action.setEnabled(has_selection)
    
    def _initialize_caches(self):
        """Initialize caches for icon existence and group data to improve performance"""
        # Pre-cache which character icons exist
        from src.constants.enums import Fighter
        for fighter in Fighter:
            icon_path = DataManager.get_character_icon(str(fighter.value))
            self._icon_cache[str(fighter.value)] = os.path.exists(icon_path)
            
        # Pre-cache stage icons
        self._stage_icon_cache = {}
        stage_keys = DataManager.get_stage_keys()
        for key in stage_keys:
            icon_path = DataManager.get_stage_icon(key)
            self._stage_icon_cache[key] = os.path.exists(icon_path)
        
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
        # Update paging totals in case page size changed
        if self.cached_filtered_mods:
            self.paging.update(len(self.cached_filtered_mods))
        self.update_view()

    def on_filter_changed(self):
        self.data_changed.emit()

    def refresh_filtered_data(self):
        """Re-runs filtering/sorting and updates the cache. Called when filters/data change."""
        mods = self.mod_manager.get_mods()
        if self.filter_manager:
            hidden_ids = self.mod_manager.hidden_ids
            favorite_ids = self.mod_manager.favorite_ids
            enabled_ids = self.mod_manager.enabled_ids
            mods = self.filter_manager.apply_filters(mods, hidden_ids, favorite_ids, enabled_ids)
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
            from src.constants.enums import Category
            
            icon_urls = []
            final_keys = []

            if mod.category == Category.STAGE:
                keys = [str(s.stage) for s in mod.stages]
                for key in keys:
                    if self._stage_icon_cache.get(key, False):
                        final_keys.append(key)
                
                slots_display = format_stage_slots(mod.get_stage_slots())
                
            else:
                slots_display = format_slots(mod.get_character_slots(), self.config_manager.config.name_rules.cap_slots_display)
                keys = mod.get_grouped_character_keys()
                
                for key in keys:
                    icon_exists = self._icon_cache.get(key, False)
                    if icon_exists:
                        final_keys.append(key)
                    else:
                        group_chars = self._group_cache.get(key, [])
                        if group_chars:
                            final_keys.extend(group_chars)
                        else:
                            final_keys.append(key)
                
            final_keys = sorted(final_keys)

            if self.mode == ListLayout.LIST:
                MAX = 4
            else: 
                MAX = 5
            
            original_len = len(final_keys)
            
            all_names = []
            if mod.category == Category.STAGE:
                all_names = [DataManager.get_stage_data(k, "Value") for k in final_keys]
            else:
                all_names = [DataManager.get_character_Name(k) for k in final_keys]

            if original_len > MAX:
                final_keys = final_keys[:MAX]

            if mod.category == Category.STAGE:
                icon_urls = DataManager.get_stage_icons(final_keys)
            else:
                icon_urls = DataManager.get_character_icons(final_keys)

            return ModItem(
                id=str(mod.hash),
                name=mod.mod_name,
                thumbnail=mod.thumbnail,
                category=str(mod.category),
                authors=mod.authors,
                slots=slots_display,
                version=mod.version,
                enabled=str(mod.hash) in self.mod_manager.enabled_ids,
                selected=self.mod_manager.is_selected(str(mod.hash)),
                favorited=str(mod.hash) in self.mod_manager.favorite_ids,
                hidden=str(mod.hash) in self.mod_manager.hidden_ids,
                character_icons=icon_urls,
                character_names=all_names
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

    def on_favorite_changed(self, mod_id:str, is_favorite:bool):
        """Handle favorite change from other components (like PreviewPanel)"""
        # If we are showing favorites only and an item is unfavorited, we must refresh to remove it
        if self.filter_manager.params.favorites_only and not is_favorite:
            self.refresh_filtered_data()
            return
            
        # Pass the update to the active view without reloading
        if self.mode == ListLayout.LIST:
            self.tree_list.update_item_favorite_status(mod_id, is_favorite)
        elif self.mode == ListLayout.GRID:
            self.grid_list.update_item_favorite_status(mod_id, is_favorite)

    def on_hidden_changed(self, mod_id:str, is_hidden:bool):
        """Handle hidden status change from other components"""
        # If we are NOT showing hidden items, we must refresh the list to remove/add the item
        if not self.filter_manager.params.include_hidden:
            self.refresh_filtered_data()
            return

        if self.mode == ListLayout.LIST:
            self.tree_list.update_item_hidden_status(mod_id, is_hidden)
        elif self.mode == ListLayout.GRID:
            self.grid_list.update_item_hidden_status(mod_id, is_hidden)
    
    def on_enabled_changed(self, mod_id:str, is_enabled:bool):
        """Handle enabled status change from other components"""
        from src.constants.enums import EnabledState
        if self.filter_manager.params.enabled and len(self.filter_manager.params.enabled) < len(EnabledState.list()):
            self.refresh_filtered_data()
            return
        
        # Just update the visual state of the item without reloading
        if self.mode == ListLayout.LIST:
            self.tree_list.update_item_enabled_status(mod_id, is_enabled)
        elif self.mode == ListLayout.GRID:
            self.grid_list.update_item_enabled_status(mod_id, is_enabled)
    
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
    
    def on_batch_action_btn(self, action: str):
        """Handle batch action button clicks"""
        if action == "Generate Info.toml":
            # Get selected mods by iterating through all mods and checking is_selected
            selected_mods = []
            for mod in self.mod_manager.get_mods():
                if self.mod_manager.is_selected(str(mod.hash)):
                    selected_mods.append(mod)
            
            if not selected_mods:
                QMessageBox.warning(self, AppStrings.DIALOG_TITLE_NO_SELECTION, AppStrings.DIALOG_MSG_NO_SELECTION)
                return
            
            # Add selected mods to batch queue
            if self.batch_manager:
                self.batch_manager.add_tasks(selected_mods)
                
                # Deselect items after adding to batch queue
                for mod in selected_mods:
                    self.mod_manager.remove_selection(str(mod.hash))
                
                # Update checkboxes visually
                if self.mode == ListLayout.LIST:
                    for item_id, checkbox in self.tree_list.item_checkboxes.items():
                        checkbox.blockSignals(True)
                        checkbox.setChecked(self.mod_manager.is_selected(item_id))
                        checkbox.blockSignals(False)
                elif self.mode == ListLayout.GRID:
                    for item_id, widget in self.grid_list.item_widgets.items():
                        widget.mod.selected = self.mod_manager.is_selected(item_id)
                        widget.update_selection_style()
                
                # Update header checkbox state
                self.update_header_checkbox_state()
                
                # Emit signal to trigger batch panel display
                self.batch_tasks_added.emit()
        
        elif action == "Remove":
            selected_ids = self.mod_manager.get_selected_ids()
            if not selected_ids:
                QMessageBox.warning(self, AppStrings.DIALOG_TITLE_NO_SELECTION, AppStrings.DIALOG_MSG_NO_SELECTION)
                return
            
            
            reply = QMessageBox.question(
                self, 
                AppStrings.DIALOG_TITLE_CONFIRM_DELETE, 
                AppStrings.DIALOG_MSG_CONFIRM_DELETE.format(count=len(selected_ids)),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.mod_manager.delete_mods(selected_ids)
                self.on_deselect_all()

        elif action == "Enable":
            selected_ids = self.mod_manager.get_selected_ids()
            if not selected_ids:
                QMessageBox.warning(self, AppStrings.DIALOG_TITLE_NO_SELECTION, AppStrings.DIALOG_MSG_NO_SELECTION)
                return
                 
            for mod_id in selected_ids:
                self.mod_manager.add_enabled(mod_id)
            
            # Deselect all after action
            self.on_deselect_all()
            # Note: No refresh needed - enabled callback will update items
            
        elif action == "Disable":
            selected_ids = self.mod_manager.get_selected_ids()
            if not selected_ids:
                QMessageBox.warning(self, AppStrings.DIALOG_TITLE_NO_SELECTION, AppStrings.DIALOG_MSG_NO_SELECTION)
                return

            for mod_id in selected_ids:
                self.mod_manager.remove_enabled(mod_id)
            
            # Deselect all after action
            self.on_deselect_all()
            # Note: No refresh needed - enabled callback will update items

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            # Check if at least one URL is a valid directory or zip file
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if os.path.isdir(path) or path.lower().endswith(('.zip', '.7z', '.rar')):
                    event.accept()
                    return
        event.ignore()

    def _check_root_dir(self) -> bool:
        """Check if root directory is set, show warning if not"""
        if not self.config_manager.config.root_dir:
            QMessageBox.warning(self, AppStrings.APP_TITLE, AppStrings.ERR_ROOT_DIR_NOT_SET)
            return False
        return True

    def dropEvent(self, event: QDropEvent):
        if not self._check_root_dir():
            return
            
        paths = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isdir(path) or path.lower().endswith(('.zip', '.7z', '.rar')):
                paths.append(path)
        
        if paths:
            self.mod_manager.add_mod_from_path(paths)
    
    def on_add_folder_clicked(self):
        if not self._check_root_dir():
            return
            
        folder_path = QFileDialog.getExistingDirectory(self, AppStrings.ADD_FROM_FOLDER.replace("...", ""))
        if folder_path:
            self.mod_manager.add_mod_from_path(folder_path)

    def on_add_zip_clicked(self):
        if not self._check_root_dir():
            return
            
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, 
            AppStrings.ADD_FROM_ZIP.replace("...", ""), 
            "", 
            "Archive Files (*.zip *.7z *.rar);;All Files (*)"
        )
        if file_paths:
            self.mod_manager.add_mod_from_path(file_paths)