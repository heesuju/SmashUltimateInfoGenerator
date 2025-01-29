from PyQt6.QtWidgets import QWidget
from src.ui.mod_list_widget import ModListWidget
from src.ui.preview import Preview
from src.ui.search_widget import SearchWidget
from src.ui.menu_widget import MenuWidget
from src.ui.components.layout import HBox, VBox
from src.core.data import load_config
from src.core.mod_loader import ModLoader
from src.models.mod import Mod

class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmashGen")
        self.setGeometry(100, 100, 1200, 600)
        
        layout = HBox()
        vlayout = VBox()
        hlayout = HBox()

        self.list_widget = ModListWidget()
        self.preview = Preview()
        self.search = SearchWidget()
        self.menu = MenuWidget()
        # Add some items
        
        vlayout.addWidget(self.search)
        hlayout.addWidget(self.list_widget)
        hlayout.addWidget(self.preview)
        
        vlayout.addLayout(hlayout)
        
        layout.addWidget(self.menu)
        layout.addLayout(vlayout)
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