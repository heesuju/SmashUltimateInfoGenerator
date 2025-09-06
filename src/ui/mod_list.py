import os
from PyQt6.QtWidgets import (
    QWidget, QSizePolicy, QLabel, QFrame, QPushButton, QComboBox
)
from PyQt6.QtGui import (
    QPixmap, QIcon, QFont
)

from src.ui.components.layout import HBox, VBox
from src.ui.grid_list import GridList
from src.ui.tree_list import TreeList
from src.models.mod import Mod
from src.ui.components.toggle_button import ToggleButton
from src.ui.components.paging import Paging
from src.ui.search_bar import SearchBar
from src.managers.mod_manager import ModManager

from src.constants.enums import Character, ModListMode
from src.managers.data_manager import ButtonIcons, DataManager
from src.constants.ui_params import SPACING, GRID_PAGE_SIZE, LIST_PAGE_SIZE

class ModList(QWidget):
    def __init__(self, parent=None, mod_manager:ModManager=None):
        super().__init__(parent)
        self.mod_manager = mod_manager
        self.mode = ModListMode.LIST
        
        layout = VBox()
        self.setLayout(layout)
        
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
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
        self.grid_list = GridList()
        self.tree_list = TreeList()

        self.search = SearchBar()
        self.frame_layout.addWidget(self.search)

        # init child layouts
        header_layout = HBox(spacing=10)
        
        self.frame_layout.addLayout(header_layout)

        self.body_layout = VBox()
        self.frame_layout.addLayout(self.body_layout)

        footer_layout = HBox(spacing=10)
        self.frame_layout.addLayout(footer_layout)

        layout_toggle = ToggleButton(
            ButtonIcons.LIST.value, ButtonIcons.GRID.value, self.on_list_selected, self.on_grid_selected)
        header_layout.addWidget(layout_toggle)
        
        header_layout.addStretch(1)

        select_button = QPushButton("Deselect All")
        header_layout.addWidget(select_button)
        
        add_button = QPushButton("+ Add New")
        header_layout.addWidget(add_button)

        save_button = QPushButton("Save (3 Enabled)")
        header_layout.addWidget(save_button)

        action_dropdown = QComboBox()
        action_dropdown.addItems(["Batch Actions", "Enable", "Disable", "Get URL", "Generate Info.toml", "Remove"])
        header_layout.addWidget(action_dropdown)
        
        self.body_layout.addWidget(self.tree_list)
        
        self.paging = Paging(callback=self.on_page_changed)
        footer_layout.addWidget(self.paging)
        self.paging.page_size = LIST_PAGE_SIZE

    def on_grid_selected(self):
        self.mode = ModListMode.GRID
        self.tree_list.setParent(None)
        self.body_layout.addWidget(self.grid_list)
        self.paging.cur_page = 1
        self.paging.page_size = GRID_PAGE_SIZE
        self.paging.update(len(self.mod_manager.mods))
        self.populate()
        
    def on_list_selected(self):
        self.mode = ModListMode.LIST
        self.grid_list.setParent(None)
        self.body_layout.addWidget(self.tree_list)
        self.paging.cur_page = 1
        self.paging.page_size = LIST_PAGE_SIZE
        self.paging.update(len(self.mod_manager.mods))
        self.populate()
    
    def on_page_changed(self, page:int, size:int):
        self.populate()

    def set_data(self, mods:list[Mod]):
        self.paging.update(len(self.mod_manager.mods))
        self.populate()

    def populate(self):
        current_page = self.paging.cur_page
        page_size = self.paging.page_size
    
        start = (current_page - 1) * page_size
        end = start + page_size
        mods = self.mod_manager.mods
        paged_mods = mods[start:end]
        self.tree_list.clear_items()
        self.grid_list.clear_items()

        for mod in paged_mods:
            char_keys = [character.key for character in mod.characters]
            if "elight" in char_keys and "eflame" in char_keys:
                char_keys.remove("elight")
                char_keys.remove("eflame")
                char_keys.append("aegis")
            keys = DataManager.get_character_icons([str(character) for character in char_keys])
            if self.mode == ModListMode.LIST:
                self.tree_list.add_item(mod.thumbnail, keys, mod.mod_name, mod.authors)
            elif self.mode == ModListMode.GRID:
                self.grid_list.add_item(mod.thumbnail, keys, mod.mod_name, mod.authors)