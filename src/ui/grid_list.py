from PyQt6.QtWidgets import (
    QListView, QSizePolicy, QListWidget
)
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
from src.models.mod import Mod
from src.managers.data_manager import ButtonIcons, DataManager

class GridList(QListWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QListWidget"
                                  "{"
                                  "border : none;"
                                  "background: transparent;  /* optional if you want no background as well */"
                                  "}"
                                  
                                  )

        # effect = QGraphicsDropShadowEffect(
        # offset=QPointF(3, 3), blurRadius=25, color=QColor("#111")
        # )
        # self.setGraphicsEffect(effect)
        
        self.icon_size = 20  # Size of each icon
        self.setIconSize(QSize(72, 72)) 
        self.setResizeMode(QListView.ResizeMode.Adjust)
        self.setGridSize(QSize(350, 110))
        self.setSpacing(0)
        self.setFlow(QListView.Flow.LeftToRight)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setWrapping(True)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)  # Allows multiple selection
        # self.setSelectionMode(QListWidget.SelectionMode.MultiSelection)  # Allows multiple selection        
        # self.setAutoFillBackground(True)
        self.itemClicked.connect(self.on_item_clicked)

    def add_item(self, mod:Mod):
        item = GridListItem(
            mod.thumbnail, 
            mod.mod_name, 
            mod.authors, 
            DataManager.get_character_icons([character for character in mod.get_grouped_character_keys()]))
        self.addItem(item)
        self.setItemWidget(item, item.widget)

    def on_item_clicked(self, item):
        print(f"Item clicked: {item}")

    def clear_items(self):
        """
        Removes all items from the grid widget.
        """
        self.clear()