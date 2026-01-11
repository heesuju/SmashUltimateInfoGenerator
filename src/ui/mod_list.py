from pydantic import BaseModel
import os
from typing import List
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QWidget, QSizePolicy, QLabel, QFrame, QPushButton, QComboBox
)
from PyQt6.QtGui import (
    QPixmap, QIcon, QFont
)
from src.core.formatting import format_slots
from src.ui.components.layout import HBox, VBox
from src.ui.grid_list import GridList
from src.ui.tree_list import TreeList
from src.models.mod import Mod, ModItem
from src.ui.components.toggle_button import ToggleButton
from src.ui.components.paging import Paging
from src.ui.search_bar import SearchBar
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

        # Start scanning if valid root mod directory exists
        if self.config_manager.config.root_dir:
            self.scan()

    def on_grid_selected(self):
        self.mode = ListLayout.GRID
        self.tree_list.setParent(None)
        self.body_layout.addWidget(self.grid_list)
        self.paging.cur_page = 1
        self.paging.page_size = GRID_PAGE_SIZE
        self.paging.update(len(self.mod_manager.get_mods()))
        self.set_data()
        
    def on_list_selected(self):
        self.mode = ListLayout.LIST
        self.grid_list.setParent(None)
        self.body_layout.addWidget(self.tree_list)
        self.paging.cur_page = 1
        self.paging.page_size = LIST_PAGE_SIZE
        self.set_data()
    
    def on_page_changed(self, page:int, size:int):
        self.set_data()

    def on_filter_changed(self):
        self.paging.cur_page = 1
        self.set_data()

    def set_data(self):
        mods = self.mod_manager.get_mods()
        if self.filter_manager:
            mods = self.filter_manager.apply_filters(mods)
        self.paging.update(len(mods))
        self.populate(mods)

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
            character_icons = DataManager.get_character_icons([character for character in keys])

            return ModItem(
                id=str(mod.hash),
                name=mod.mod_name,
                thumbnail=mod.thumbnail,
                category=str(mod.category),
                authors=mod.authors,
                slots=format_slots(mod.get_character_slots(), self.config_manager.config.name_rules.cap_slots),
                version=mod.version,
                enabled=False,
                selected=False,
                character_icons=character_icons
            )

        def add_next():
            if not self._populate_active or self._populate_index is None or self._populate_mods is None:
                return  # Stop if cancelled or cleared
            if self._populate_index < len(self._populate_mods):
                mod = self._populate_mods[self._populate_index]
                if self.mode == ListLayout.LIST:
                    self.tree_list.add_item(process(mod))
                elif self.mode == ListLayout.GRID:
                    self.grid_list.add_item(process(mod))
                self._populate_index += 1
                QTimer.singleShot(0, add_next)
            else:
                self._populate_mods = None
                self._populate_index = None

        add_next()

    def scan(self):
        self.mod_manager.scan_all()

    def on_scanned(self):
        self.set_data()
    
    def on_progress(self, mod:Mod):
        pass
        # if self.mode == ModListMode.LIST:
        #     self.tree_list.add_item(mod)
        # elif self.mode == ModListMode.GRID:
        #     self.grid_list.add_item(mod)