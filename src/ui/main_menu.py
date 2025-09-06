from PyQt6.QtWidgets import QWidget
from src.ui.mod_list_widget import ModListWidget
from src.ui.filter_panel import Filter
from src.ui.preview_panel import Preview
from src.ui.edit_panel import EditPanel
from src.ui.config_panel import Config
from src.ui.components.navigation import Navigation, NavigationMenu
from src.ui.components.layout import HBox, VBox
from src.models.mod import Mod
from src.managers.asset_manager import NavigationMenuIcon
from src.managers.config_manager import ConfigManager
from src.managers.mod_manager import ModManager

class MainMenu(QWidget):
    def __init__(self, config_manager:ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self.mod_manager = ModManager(config_manager)
        self.setWindowTitle("SmashGen")
        self.setGeometry(100, 100, 1200, 800)
        
        layout = HBox()
        vlayout = VBox()
        hlayout = HBox()

        self.list_widget = ModListWidget(mod_manager=self.mod_manager)
        self.filter = Filter()
        self.preview = Preview()
        self.edit = EditPanel()
        self.config = Config(config_manager)

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
        
        hlayout.addWidget(self.list_widget)
        
        hlayout.addWidget(self.filter)
        hlayout.addWidget(self.preview)
        hlayout.addWidget(self.edit)
        hlayout.addWidget(self.config)
        
        vlayout.addLayout(hlayout)
        
        
        layout.addLayout(vlayout)
        layout.addWidget(self.menu)
        self.setLayout(layout)     

        self.scan()

    def scan(self):
        self.mod_manager.scan_all(self.on_scanned)
    
    def on_scanned(self, mods:list[Mod]):
        self.list_widget.set_data(mods)