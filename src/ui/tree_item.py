from PyQt6.QtWidgets import (
    QListView, QSizePolicy, QListWidget
)
from functools import partial
from PyQt6.QtGui import QIcon, QPixmap, QPainter
from PyQt6.QtCore import Qt, QRect, QSize
from PyQt6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QWidget,
)
from PyQt6.QtCore import Qt, QSize, QPoint, QPointF
from PyQt6.QtGui import QPixmap, QColor, QPalette
from src.ui.grid_item import GridListItem
from PyQt6.QtWidgets import QListWidget, QListView, QStyledItemDelegate, QStyleOptionViewItem, QGraphicsDropShadowEffect, QSizePolicy, QStyle
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget,
    QTreeWidgetItem, QCheckBox, QHeaderView
)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPainterPath, QImage, QBrush, QPen, QColor
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QRect, QSize
from src.ui.components.layout import HBox, VBox
from src.constants.ui import ButtonIcons
from src.models.mod import Mod
    
class TreeItem(QTreeWidgetItem):
    def __init__(self, mod:Mod):
        self.mod = mod
        super().__init__([self.mod.name, self.mod.category, self.mod.author, "C01-02", "", "", ""])
        # Add Checkbox
        self.setFlags(self.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        self.setCheckState(0, Qt.CheckState.Unchecked)  # Unchecked by default
        # Add Multiple Icons to 4th Column
        icons = [QIcon(QPixmap(path)) for path in character_icons]
        self.setData(4, Qt.ItemDataRole.UserRole, icons)
        # item.setData(0, Qt.ItemDataRole.UserRole, icons)

        self.tree_widget.addTopLevelItem(item)
        # # Add button widget to the last column
        btn = QPushButton()
        btn.setIcon(QIcon(QPixmap(ButtonIcons.ENABLED.value)))
        btn.setStyleSheet(("""QPushButton {
            border-radius: 0px;
            border: none;
        }"""))
        btn.setFixedHeight(20)  # keep it small to fit row
        btn.clicked.connect(partial(self.on_item_toggled, name, btn))
            
        self.tree_widget.setItemWidget(item, 5, btn)  # <-- column index 5 (last column)

    def on_item_toggled(self, name, btn):
        print(f"Button clicked for {name}")
        btn.setIcon(QIcon(QPixmap(ButtonIcons.DISABLED.value)))

    def on_item_clicked(self, item, column):
        print(f"Item clicked: {item.text(0)} in column {column}")