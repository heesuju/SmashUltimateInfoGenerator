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
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget,
    QTreeWidgetItem, QCheckBox, QHeaderView
)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPainterPath, QImage, QBrush, QPen, QColor
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QRect, QSize
from src.ui.components.layout import HBox, VBox

class CustomTreeWidget(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.icon_size = 20  # Size of each icon

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.viewport())

        for row in range(self.topLevelItemCount()):
            item = self.topLevelItem(row)
            rect = self.visualItemRect(item)
            
            # Specify the column where you want multiple icons
            icons = item.data(4, Qt.ItemDataRole.UserRole)
            if icons:
                x_offset = self.columnViewportPosition(4) + 5  # Adjust position in column
                y_center = rect.center().y() - self.icon_size // 2
                for icon in icons:
                    icon_rect = QRect(x_offset, y_center, self.icon_size, self.icon_size)
                    icon.paint(painter, icon_rect, Qt.AlignmentFlag.AlignCenter)
                    x_offset += self.icon_size + 5  # Add spacing between icons


class TreeList(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QListWidget"
                                  "{"
                                  "border : none;"
                                  "}"
                                  
                                  )
        layout = VBox()

        # Top Controls
        
        self.tree_widget = CustomTreeWidget()
        self.tree_widget.setIconSize(QSize(72, 72)) 
        self.tree_widget.setColumnCount(2)
        self.tree_widget.setColumnWidth(0, 200)
        
        self.tree_widget.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tree_widget.setHeaderLabels(["Mod Name", "Category", "Authors", "Slot", "Characters"])
        
        layout.addWidget(self.tree_widget)
        self.setLayout(layout)


    def add_item(self, icon_path, character_icons, name, author):
        item = QTreeWidgetItem([name, "FIGHTER", author, "C01-02", ""])

        # Add Checkbox
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(0, Qt.CheckState.Unchecked)  # Unchecked by default
        # Add Multiple Icons to 4th Column
        icons = [QIcon(QPixmap(path)) for path in character_icons]
        item.setData(4, Qt.ItemDataRole.UserRole, icons)
        # item.setData(0, Qt.ItemDataRole.UserRole, icons)

        self.tree_widget.addTopLevelItem(item)