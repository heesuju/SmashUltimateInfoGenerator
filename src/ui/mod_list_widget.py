import os
from PyQt6.QtWidgets import (
    QWidget, QSizePolicy, QLabel, QFrame, QPushButton, QComboBox
)
from PyQt6.QtGui import (
    QPixmap, QIcon, QFont
)

from src.ui.components.layout import HBox, VBox
from src.ui.grid_list import GridList
from src.ui.treelist import TreeList
from src.constants.font import *
from src.models.mod import Mod

WIDTH = 300
LIST_ICON = "assets/icons/menu/list.png"
GRID_ICON = "assets/icons/menu/grid.png"
ICON_PATH = "assets/icons"

class ModListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
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
        self.frame_layout = VBox(margin=10)
        self.frame.setLayout(self.frame_layout)
        layout.addWidget(self.frame)
        
        # init mod list
        self.grid_list = GridList()
        self.tree_list = TreeList()

        # init child layouts
        header_layout = HBox(spacing=10)
        self.frame_layout.addLayout(header_layout)

        self.body_layout = VBox(margin=(0, 10))
        self.frame_layout.addLayout(self.body_layout)

        footer_layout = HBox(spacing=10)
        self.frame_layout.addLayout(footer_layout)

        # populate layout
        mod_name_label = QLabel("Mods (30)")
        title_font = QFont(TITLE_FONT, TITLE_FONT_SIZE)  # Set the font and font size
        title_font.setBold(True)
        mod_name_label.setFont(title_font)
        header_layout.addWidget(mod_name_label)
        
        header_layout.addStretch(1)

        select_button = QPushButton("Deselect All")
        header_layout.addWidget(select_button)
        
        action_dropdown = QComboBox()
        action_dropdown.addItems(["Batch Actions", "Enable", "Disable", "Get URL", "Generate Info.toml", "Remove"])
        header_layout.addWidget(action_dropdown)

        list_icon = QIcon(QPixmap(LIST_ICON))
        grid_icon = QIcon(QPixmap(GRID_ICON))

        list_btn = QPushButton()
        list_btn.setIcon(list_icon)
        list_btn.clicked.connect(self.on_list_selected)
        header_layout.addWidget(list_btn)

        grid_btn = QPushButton()
        grid_btn.setIcon(grid_icon)
        grid_btn.clicked.connect(self.on_grid_selected)
        header_layout.addWidget(grid_btn)        

        self.body_layout.addWidget(self.tree_list)

        count_label = QLabel("")
        title_font = QFont(BODY_FONT, BODY_FONT_SIZE)  # Set the font and font size
        count_label.setFont(title_font)
        footer_layout.addWidget(count_label)

        footer_layout.addStretch(1)

        add_button = QPushButton("+ Add New")
        footer_layout.addWidget(add_button)

        save_button = QPushButton("Save (3 Enabled)")
        footer_layout.addWidget(save_button)

    def on_grid_selected(self, event):
        self.tree_list.setParent(None)
        self.body_layout.addWidget(self.grid_list)
        
    def on_list_selected(self, event):
        self.grid_list.setParent(None)
        self.body_layout.addWidget(self.tree_list)
        
    def set_data(self, mods:list[Mod]):
        for mod in mods:
            char_keys = [character.key for character in mod.characters]
            if "elight" in char_keys and "eflame" in char_keys:
                char_keys.remove("elight")
                char_keys.remove("eflame")
                char_keys.append("aegis")
            keys = [os.path.join(ICON_PATH, "characters", character + ".png") for character in char_keys]
            self.tree_list.add_item(mod.thumbnail, keys, mod.mod_name, mod.authors)
            self.grid_list.add_item(mod.thumbnail, keys, mod.mod_name, mod.authors)
