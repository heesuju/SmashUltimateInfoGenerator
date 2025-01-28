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
from src.ui.list_item import GridListItem
from PyQt6.QtWidgets import QListWidget, QListView, QStyledItemDelegate, QStyleOptionViewItem, QGraphicsDropShadowEffect, QSizePolicy, QStyle



class GridList(QListWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QListWidget"
                                  "{"
                                  "border : none;"
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
        self.setSelectionMode(QListWidget.SelectionMode.MultiSelection)  # Allows multiple selection
        
        # self.setAutoFillBackground(True)

    def add_item(self, icon_path, character_icons, name, author):
        item = GridListItem(icon_path, name, author, character_icons)
        self.addItem(item)
        self.setItemWidget(item, item.widget)