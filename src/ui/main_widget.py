from PyQt6.QtWidgets import QWidget
from src.ui.mod_list_widget import ModListWidget

from src.ui.filter import Filter
from src.ui.preview import Preview
from src.ui.edit import Edit
from src.ui.config import Config


from src.ui.components.navigation import Navigation
from src.ui.components.layout import HBox, VBox
from src.core.data import load_config
from src.core.mod_loader import ModLoader
from src.models.mod import Mod
from src.ui.schema import NavigationMenu
from src.constants.icons import MenuIcons

class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmashGen")
        self.setGeometry(100, 100, 1200, 600)
        
        layout = HBox()
        vlayout = VBox()
        hlayout = HBox()

        self.list_widget = ModListWidget()

        self.filter = Filter()
        self.preview = Preview()
        self.edit = Edit()
        
        self.config = Config()

        self.filter.hide()
        self.preview.hide()
        self.edit.hide()
        self.config.hide()

        
        self.menu = Navigation(
            [
                [
                    NavigationMenu(MenuIcons.FILTER.value, self.filter),
                    NavigationMenu(MenuIcons.PREVIEW.value, self.preview),
                    NavigationMenu(MenuIcons.EDIT.value, self.edit),
                ],
                [
                    NavigationMenu(MenuIcons.CONFIG.value, self.config)
                ]
            ]
        )
        # Add some items
        
        
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
        self.progress_cnt = 0
        config_data = load_config()
        if config_data is not None and config_data.default_directory:
            # set_text(self.entry_dir, config_data.default_directory)
            self.loader_thread = ModLoader(config_data.default_directory)
            mods = self.loader_thread.run()
            # self.loader_thread.finished.connect(self.on_scanned)
            # self.loader_thread.progress.connect(self.on_progress_update)
            # self.loader_thread.start()
            self.on_scanned(mods)
    
    def on_scanned(self, mods:list[Mod]):
        self.list_widget.set_data(mods)