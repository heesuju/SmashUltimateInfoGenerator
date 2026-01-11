from PyQt6.QtWidgets import (
    QListView, QSizePolicy, QListWidget, QScrollBar
)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QWheelEvent
from PyQt6.QtCore import Qt, QRect, QSize
from PyQt6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QWidget,
)
from PyQt6.QtCore import Qt, QSize, QPoint, QPointF
from PyQt6.QtGui import QPixmap, QColor, QPalette
from src.ui.grid_item import GridListItem
from PyQt6.QtWidgets import QListWidget, QListView, QStyledItemDelegate, QStyleOptionViewItem, QGraphicsDropShadowEffect, QSizePolicy, QStyle
from src.models.mod import Mod, ModItem
from src.managers.data_manager import ButtonIcons, DataManager
from src.managers.mod_manager import ModManager

class GridList(QListWidget):
    def __init__(self, mod_manager:ModManager):
        super().__init__()
        self.mod_manager =mod_manager
        self.setStyleSheet("QListWidget"
                                  "{"
                                  "border : none;"
                                  "background: transparent;  /* optional if you want no background as well */"
                                  "}"
                                  
                                  )
        
        # Overlay Scrollbar Implementation
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.overlay_scrollbar = QScrollBar(Qt.Orientation.Vertical, self)
        
        # Stylesheet for overlay - make it sit on top transparently
        self.overlay_scrollbar.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 10px;
                margin: 0px; 
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.2);
                min-height: 20px;
                border-radius: 10px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.3);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        # Syncing logic
        self.verticalScrollBar().rangeChanged.connect(self.update_scrollbar_range)
        self.verticalScrollBar().valueChanged.connect(self.overlay_scrollbar.setValue)
        self.overlay_scrollbar.valueChanged.connect(self.verticalScrollBar().setValue)
        
        # Ensure scrollbar is raised
        self.overlay_scrollbar.raise_()

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

    def update_scrollbar_range(self, min_val, max_val):
        self.overlay_scrollbar.setRange(min_val, max_val)
        self.overlay_scrollbar.setPageStep(self.verticalScrollBar().pageStep())
        if max_val <= min_val:
            self.overlay_scrollbar.hide()
        else:
            self.overlay_scrollbar.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        sb_width = 10
        # Position at the right edge, overlaying content
        self.overlay_scrollbar.setGeometry(
            self.width() - sb_width, 
            0, 
            sb_width, 
            self.height()
        )
        self.overlay_scrollbar.raise_()

    def wheelEvent(self, event: QWheelEvent):
        # Forward wheel events to the hidden scrollbar functionality
        super().wheelEvent(event)

    def add_item(self, mod:ModItem):
        item = GridListItem(self,mod)

    def on_item_clicked(self, item):
        print(f"Item clicked: {item.mod.name}")
        self.mod_manager.set_selection(item.mod.id)

    def clear_items(self):
        """
        Removes all items from the grid widget.
        """
        self.clear()