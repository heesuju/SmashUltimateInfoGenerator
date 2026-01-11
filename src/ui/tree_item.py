from PyQt6.QtWidgets import QLabel
from functools import partial
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QTreeWidgetItem, QCheckBox
)
from src.managers.data_manager import ButtonIcons, DataManager
from src.models.mod import Mod, ModItem

class TreeItem(QTreeWidgetItem):
    def __init__(self, parent, mod:ModItem, on_clicked:callable, on_enabled:callable):
        self.mod = mod
        self.on_clicked = on_clicked
        self.on_enabled = on_enabled
        self.animations = []
        super().__init__(["", "", "", "", "", "", ""])

        parent.addTopLevelItem(self)

        check_widget = QCheckBox()
        check_widget.setChecked(False)
        check_widget.stateChanged.connect(lambda state: self.on_enabled(self.mod) if self.on_enabled else None)
        name_widget = QLabel(self.mod.name)
        category_widget = QLabel(self.mod.category)
        authors_widget = QLabel(self.mod.authors)
        slot_widget = QLabel(self.mod.slots)

        icons_widget = QWidget()
        from PyQt6.QtWidgets import QHBoxLayout
        icons_layout = QHBoxLayout(icons_widget)
        icons_layout.setContentsMargins(0, 0, 0, 0)
        icons_layout.setSpacing(2)
        
        # Show maximum 3 icons
        max_icons = 3
        total_icons = len(self.mod.character_icons)
        
        for i, path in enumerate(self.mod.character_icons[:max_icons]):
            icon_label = QLabel()
            icon_label.setPixmap(QPixmap(path).scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            icons_layout.addWidget(icon_label)
        
        # Add "+N" label if there are more icons
        if total_icons > max_icons:
            remaining = total_icons - max_icons
            plus_label = QLabel(f"+{remaining}")
            plus_label.setStyleSheet("color: #888; font-size: 11px; padding-left: 4px;")
            icons_layout.addWidget(plus_label)

        icons_layout.addStretch()
        
        # # Add button widget to the last column
        btn = QPushButton()
        btn.setIcon(QIcon(QPixmap(ButtonIcons.ENABLE.value)))
        btn.setStyleSheet(("""QPushButton {
            border-radius: 0px;
            border: none;
        }"""))
        btn.setFixedHeight(32)
        btn.clicked.connect(partial(self.on_item_toggled, self.mod.name, btn))
            
            
        parent.setItemWidget(self, 0, check_widget)     # Column 0: Checkbox
        parent.setItemWidget(self, 1, category_widget)  # Column 1: Category
        parent.setItemWidget(self, 2, name_widget)      # Column 2: Mod Name
        parent.setItemWidget(self, 3, authors_widget)   # Column 3: Authors
        parent.setItemWidget(self, 4, slot_widget)      # Column 4: Slot
        parent.setItemWidget(self, 5, icons_widget)     # Column 5: Characters
        parent.setItemWidget(self, 6, btn)              # Column 6: Enabled
        self.widgets = [check_widget, category_widget, name_widget, authors_widget, slot_widget, icons_widget, btn]

    def on_item_toggled(self):
        pass