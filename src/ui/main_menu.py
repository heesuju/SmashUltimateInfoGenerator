from PyQt6.QtWidgets import QWidget

from src.ui.mod_list import ModList
from src.ui.filter_panel import FilterPanel
from src.ui.preview_panel import PreviewPanel
from src.ui.edit_panel import EditPanel
from src.ui.config_panel import Config
from src.ui.components.navigation import Navigation, NavigationMenu
from src.ui.components.layout import HBox, VBox
from src.models.mod import Mod
from src.managers.data_manager import NavigationMenuIcon
from src.managers.config_manager import ConfigManager
from src.managers.mod_manager import ModManager
from src.managers.filter_manager import FilterManager

class MainMenu(QWidget):
    def __init__(self, config_manager:ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self.mod_manager = ModManager(config_manager)
        self.filter_manager = FilterManager()
        self.setWindowTitle("SmashGen")
        self.setGeometry(100, 100, 1400, 800)
        
        layout = HBox()
        vlayout = VBox()
        hlayout = HBox()

        self.list_widget = ModList(self.mod_manager, self.filter_manager, self.config_manager)
        self.filter = FilterPanel(self.filter_manager)
        self.preview = PreviewPanel(self.mod_manager)
        self.edit = EditPanel(self.mod_manager, config_manager)
        self.config = Config(config_manager)
        
        # Connect preview edit button to edit panel
        self.preview.edit_requested.connect(self.on_edit_requested)
        
        # Connect edit panel cancel to close edit
        self.edit.close_requested.connect(self.on_edit_close)

        self.filter.hide()
        self.preview.hide()
        self.edit.hide()
        self.config.hide()

        self.menu = Navigation(
            [
                [
                    NavigationMenu(NavigationMenuIcon.FILTER.value, self.filter),
                    NavigationMenu(NavigationMenuIcon.PREVIEW.value, self.preview),
                    NavigationMenu(NavigationMenuIcon.EDIT.value, self.edit),
                ],
                [
                    NavigationMenu(NavigationMenuIcon.CONFIG.value, self.config)
                ]
            ]
        )
        
        # Hide edit button by default (will be shown when edit is clicked)
        edit_button = self.menu.buttons.get(NavigationMenuIcon.EDIT.value)
        if edit_button:
            edit_button.hide()        
        
        hlayout.addWidget(self.list_widget)
        
        hlayout.addWidget(self.filter)
        hlayout.addWidget(self.preview)
        hlayout.addWidget(self.edit)
        hlayout.addWidget(self.config)
        
        vlayout.addLayout(hlayout)
        
        # Connect filter chips to filter panel
        self.list_widget.filter_chips.chip_clicked.connect(self.on_filter_chip_clicked)
        self.list_widget.filter_chips.chip_reset.connect(self.filter.reset_filter)
        
        layout.addLayout(vlayout)
        layout.addWidget(self.menu)
        self.setLayout(layout)
    
    def on_filter_chip_clicked(self, filter_type: str):
        """Handle filter chip clicks by showing filter panel and focusing the input"""
        # Show the filter panel if it's hidden
        if self.filter.isHidden():
            self.menu.show_panel(self.filter)
        
        # Focus on the specific filter input
        self.filter.focus_filter(filter_type)
    
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
     