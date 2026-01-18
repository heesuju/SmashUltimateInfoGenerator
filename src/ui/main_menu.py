from PyQt6.QtWidgets import QWidget, QTabWidget, QFrame

from src.ui.mod_list import ModList
from src.ui.filter_panel import FilterPanel
from src.ui.sort_panel import SortPanel
from src.ui.preview_panel import PreviewPanel
from src.ui.edit_panel import EditPanel
from src.ui.batch_panel import BatchPanel
from src.ui.config_panel import Config
from src.ui.workspace_panel import WorkspacePanel
from src.ui.components.navigation import Navigation, NavigationMenu
from src.ui.components.layout import HBox, VBox
from src.models.mod import Mod
from src.managers.data_manager import NavigationMenuIcon
from src.managers.config_manager import ConfigManager
from src.managers.mod_manager import ModManager
from src.managers.filter_manager import FilterManager
from src.managers.batch_manager import BatchManager
from src.managers.online_manager import OnlineManager
from src.managers.download_manager import DownloadManager
from src.ui.online_mod_list import OnlineModList
from src.ui.online_filter_panel import OnlineFilterPanel
from src.ui.download_panel import DownloadPanel

class MainMenu(QWidget):
    def __init__(self, config_manager:ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self.mod_manager = ModManager(config_manager)
        self.filter_manager = FilterManager()
        self.batch_manager = BatchManager()
        self.setWindowTitle("SmashGen")
        self.setGeometry(100, 100, 1400, 800)
        
        layout = HBox()
        vlayout = VBox()
        hlayout = HBox()

        self.list_widget = ModList(self.mod_manager, self.filter_manager, self.config_manager, self.batch_manager)
        self.filter = FilterPanel(self.filter_manager, config_manager)
        self.sort = SortPanel(config_manager)
        
        # Online panels
        self.online_manager = OnlineManager()
        self.online_filter = OnlineFilterPanel(self.online_manager)
        
        # Download Manager
        self.download_manager = DownloadManager(config_manager)
        self.download_panel = DownloadPanel(self.download_manager)
        
        # Auto-open download panel on start
        self.download_manager.download_started.connect(self.on_download_started)
        # Auto-scan on install
        self.download_manager.install_finished.connect(self.on_mod_installed)
        # Refresh mod when thumbnail finishes
        self.download_manager.thumbnail_updated.connect(self.on_mod_installed)
        
        # Connect total progress
        self.download_manager.total_progress_updated.connect(self.update_download_progress)
        
        # Pass both managers to preview panel for dual mode support
        self.preview = PreviewPanel(self.mod_manager, self.online_manager, self.download_manager)
        
        self.edit = EditPanel(self.mod_manager, config_manager)
        self.batch = BatchPanel(self.batch_manager)
        self.config = Config(config_manager)
        self.workspace = WorkspacePanel(config_manager)
        
        # Connect preview edit button to edit panel
        self.preview.edit_requested.connect(self.on_edit_requested)
        
        # Connect edit panel cancel to close edit
        self.edit.close_requested.connect(self.on_edit_close)
        
        # Connect edit panel save to update list
        self.edit.save_complete.connect(self.list_widget.on_mod_saved)
        
        # Connect batch panel apply to refresh list (use lambda since on_mod_saved expects mod_id)
        self.batch.apply_requested.connect(lambda: self.list_widget.on_mod_saved(""))
        
        # Connect list widget batch signal to show batch panel
        self.list_widget.batch_tasks_added.connect(self.on_batch_tasks_added)
        
        # Connect mod selection to show preview panel
        self.mod_manager.add_focus_callback(self.on_mod_selected)
        
        # Connect online mod selection to show preview panel
        self.online_manager.add_focus_callback(self.on_online_mod_selected)
        
        # Connect sort panel to filter manager
        self.sort.set_sort_change_callback(self.on_sort_changed)
        
        # Load and apply saved sort rules from config on startup
        saved_sort_rules = self.sort.get_sort_rules()
        if saved_sort_rules:
            self.filter_manager.set_sort_rules(saved_sort_rules)
            
        # Connect batch manager to update progress on nav button
        self.batch_manager.add_callback(self.update_batch_progress)

        self.filter.hide()
        self.online_filter.hide()
        self.sort.hide()
        self.preview.hide()
        self.edit.hide()
        self.batch.hide()
        self.config.hide()
        self.workspace.hide()
        self.download_panel.hide()

        self.menu = Navigation(
            [
                [
                    NavigationMenu(NavigationMenuIcon.FILTER.value, self.filter),
                    # Online filter uses same icon but different panel
                    # We'll show/hide based on active tab
                    NavigationMenu(NavigationMenuIcon.SORT.value, self.sort),
                    NavigationMenu(NavigationMenuIcon.PREVIEW.value, self.preview),
                    NavigationMenu(NavigationMenuIcon.EDIT.value, self.edit),
                    NavigationMenu(NavigationMenuIcon.BATCH.value, self.batch),
                    NavigationMenu(NavigationMenuIcon.DOWNLOAD.value, self.download_panel),
                ],
                [
                    NavigationMenu(NavigationMenuIcon.WORKSPACE.value, self.workspace),
                    NavigationMenu(NavigationMenuIcon.CONFIG.value, self.config)
                ]
            ]
        )
        
        # Hide edit and batch buttons by default
        edit_button = self.menu.buttons.get(NavigationMenuIcon.EDIT.value)
        if edit_button:
            edit_button.hide()
        
        batch_button = self.menu.buttons.get(NavigationMenuIcon.BATCH.value)
        if batch_button:
            batch_button.hide()        
        
        if batch_button:
            batch_button.hide()        
        
        # Tabs for Installed vs Online
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)  # Remove frame border
        self.tabs.addTab(self.list_widget, "Installed")
        
        # Create dedicated filter manager for online (or reuse the same one)
        self.online_list = OnlineModList(self.online_manager, self.filter_manager, self.download_manager)
        self.tabs.addTab(self.online_list, "Online")
        
        # Connect tab change to show/hide appropriate panels
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        hlayout.addWidget(self.tabs)
        
        # Vertical separator 1 (between list and side panel)
        self.separator1 = self._create_separator()
        hlayout.addWidget(self.separator1)
        
        hlayout.addWidget(self.filter)
        hlayout.addWidget(self.online_filter)
        hlayout.addWidget(self.sort)
        hlayout.addWidget(self.preview)
        hlayout.addWidget(self.edit)
        hlayout.addWidget(self.batch)
        hlayout.addWidget(self.config)
        hlayout.addWidget(self.config)
        hlayout.addWidget(self.workspace)
        hlayout.addWidget(self.download_panel)
        
        
        vlayout.addLayout(hlayout)
        
        # Connect filter chips to filter panel
        self.list_widget.filter_chips.chip_clicked.connect(self.on_filter_chip_clicked)
        self.list_widget.filter_chips.chip_reset.connect(self.filter.reset_filter)
        
        layout.addLayout(vlayout)
        
        # Vertical separator 2 (between side panel and navigation)
        self.separator2 = self._create_separator()
        layout.addWidget(self.separator2)
        
        layout.addWidget(self.menu)
        self.setLayout(layout)
        
        # Connect navigation selection changes
        self.menu.selection_changed.connect(self.update_separators_visibility)
        
        # Initialize visibility
        self.update_separators_visibility()
        
        # Initialize panel visibility for installed tab (index 0)
        self.on_tab_changed(0)

    def _create_separator(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        sep.setStyleSheet("color: rgba(255, 255, 255, 0.1); background-color: rgba(255, 255, 255, 0.1); width: 1px;")
        return sep

    def update_separators_visibility(self):
        """Show separators only if a side panel is visible"""
        any_visible = any(p.isVisible() for p in [
            self.filter, self.online_filter, self.sort, 
            self.preview, self.edit, self.batch, 
            self.config, self.workspace, self.download_panel
        ])
        
        self.separator1.setVisible(any_visible)
    
    def on_tab_changed(self, index):
        """Handle tab changes to show/hide appropriate panels"""
        is_online = (index == 1)
        
        # Get navigation buttons
        filter_btn = self.menu.buttons.get(NavigationMenuIcon.FILTER.value)
        sort_btn = self.menu.buttons.get(NavigationMenuIcon.SORT.value)
        preview_btn = self.menu.buttons.get(NavigationMenuIcon.PREVIEW.value)
        edit_btn = self.menu.buttons.get(NavigationMenuIcon.EDIT.value)
        batch_btn = self.menu.buttons.get(NavigationMenuIcon.BATCH.value)
        
        # Find the filter menu item
        filter_menu = None
        for menu in self.menu.menus:
            if menu.icon == NavigationMenuIcon.FILTER.value:
                filter_menu = menu
                break
        
        if is_online:
            # Online tab - hide installed-only panels, swap filter panel
            if filter_menu:
                # Swap the widget in the menu item
                filter_menu.widget = self.online_filter
            if sort_btn:
                sort_btn.setVisible(False)
            # Preview is now supported in online mode, keep it visible
            if edit_btn:
                edit_btn.setVisible(False)
            if batch_btn:
                batch_btn.setVisible(False)
            
            # Close any open installed panels
            self.filter.hide()
            self.sort.hide()
            self.preview.hide()
            self.edit.hide()
            self.batch.hide()
            
            # Auto-search if empty
            if (not self.online_manager.current_query and 
                not self.online_manager.search_results and 
                not self.online_manager.is_loading and
                not self.online_manager.current_author):
                self.online_manager.search()

        else:
            # Installed tab - restore all panels
            if filter_menu:
                filter_menu.widget = self.filter
            if sort_btn:
                sort_btn.setVisible(True)
            if preview_btn:
                preview_btn.setVisible(True)
            if edit_btn:
                edit_btn.setVisible(True)
            if batch_btn:
                batch_btn.setVisible(True)
            
            # Close any open online panels
            self.online_filter.hide()
            
        self.update_separators_visibility()

    
    def on_filter_chip_clicked(self, filter_type: str):
        """Handle filter chip clicks by showing filter panel and focusing the input"""
        # Show the filter panel if it's hidden
        if self.filter.isHidden():
            self.menu.show_panel(self.filter)
        
        # Focus on the specific filter input
        self.filter.focus_filter(filter_type)
    
    def on_mod_selected(self, mod_id: str):
        """Handle mod selection from list - show preview panel"""
        if self.preview.isHidden():
            self.menu.show_panel(self.preview)
    
    def on_online_mod_selected(self, mod_id: str):
        """Handle online mod selection from list - show preview panel"""
        if self.preview.isHidden():
            self.menu.show_panel(self.preview)
    
    def on_sort_changed(self, sort_rules):
        """Handle sort rules change from sort panel"""
        self.filter_manager.set_sort_rules(sort_rules)
        self.filter_manager.on_change()
    
    def on_edit_requested(self, mod_id: str):
        """Handle edit button click from preview panel"""
        # Show edit button in navigation if hidden
        edit_button = self.menu.buttons.get(NavigationMenuIcon.EDIT.value)
        if edit_button:
            edit_button.show()
        
        # Load mod data into edit panel
        self.edit.load_mod(mod_id)
        
        # Switch to edit panel
        self.menu.show_panel(self.edit)
    
    def on_edit_close(self):
        """Handle edit panel close/cancel"""
        # Hide edit panel
        self.edit.hide()
        
        # Hide edit button from navigation
        edit_button = self.menu.buttons.get(NavigationMenuIcon.EDIT.value)
        if edit_button:
            edit_button.hide()
        
        # Reset navigation state
        self.menu.selected_menu = NavigationMenuIcon.NONE
        
        self.update_separators_visibility()
    
    def on_batch_tasks_added(self):
        """Handle when batch tasks are added from mod_list"""
        # Show batch button in navigation
        batch_button = self.menu.buttons.get(NavigationMenuIcon.BATCH.value)
        if batch_button:
            batch_button.show()
        
        # Switch to batch panel (but don't auto-start processing)
        self.menu.show_panel(self.batch)

    def update_batch_progress(self):
        """Update batch progress indicator on navigation button"""
        batch_button = self.menu.buttons.get(NavigationMenuIcon.BATCH.value)
        if not batch_button:
            return
            
        tasks = self.batch_manager.get_tasks()
        total = len(tasks)
        if total == 0:
            batch_button.set_progress(-1)
            return

        processing = self.batch_manager.get_processing_count()
        pending = self.batch_manager.get_pending_count()
        complete = self.batch_manager.get_complete_count()
        error = self.batch_manager.get_error_count()
        
        # Only show progress if there are processing tasks or we are in the middle of a queue
        if processing == 0 and pending == 0:
            batch_button.set_progress(-1)
            return
            
        # Calculate progress
        done = complete + error
        progress = done / total if total > 0 else 0
        
        if processing > 0 and progress == 0:
            progress = 0.1
            
        batch_button.set_progress(progress)

    def on_download_started(self, id, name):
        """Auto open download panel if not already open"""
        if self.download_panel.isHidden():
            self.menu.show_panel(self.download_panel)
            
    def on_mod_installed(self, path:str):
        """Handle new mod installed -> scan it"""
        self.mod_manager.scan([path])
        
    def on_download_progress(self, start=True):
        """Update download progress on nav button"""
        pass

    def update_download_progress(self, progress: float):
        """Update download progress indicator on navigation button"""
        download_btn = self.menu.buttons.get(NavigationMenuIcon.DOWNLOAD.value)
        if download_btn:
             download_btn.set_progress(progress)