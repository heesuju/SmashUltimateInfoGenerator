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
from src.managers.data_manager import ButtonIcons

class CustomTreeWidget(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.icon_size = 20  # Size of each icon
        self.setItemDelegate(CustomDelegate())
        
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

class CustomDelegate(QStyledItemDelegate):
    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(20)  # Set row height
        return size
    
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
        self.tree_widget.setStyleSheet("""
    QTreeWidget {
        border: none;
        background: transparent;  /* optional if you want no background as well */
    }
""")
        self.tree_widget.setColumnCount(2)
        self.tree_widget.setColumnWidth(0, 200)
        
        self.tree_widget.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tree_widget.setHeaderLabels(["Mod Name", "Category", "Authors", "Slot", "Characters", "Enabled", ""])
        
        layout.addWidget(self.tree_widget)
        self.setLayout(layout)

        self.tree_widget.itemClicked.connect(self.on_item_clicked)

    def add_item(self, icon_path, character_icons, name, author):
        item = QTreeWidgetItem([name, "FIGHTER", author, "C01-02", "", "", ""])

        # Add Checkbox
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(0, Qt.CheckState.Unchecked)  # Unchecked by default
        # Add Multiple Icons to 4th Column
        icons = [QIcon(QPixmap(path)) for path in character_icons]
        item.setData(4, Qt.ItemDataRole.UserRole, icons)
        # item.setData(0, Qt.ItemDataRole.UserRole, icons)

        self.tree_widget.addTopLevelItem(item)
        # # Add button widget to the last column
        btn = QPushButton()
        btn.setIcon(QIcon(QPixmap(ButtonIcons.ENABLE.value)))
        btn.setStyleSheet(("""QPushButton {
            border-radius: 0px;
            border: none;
        }"""))
        btn.setFixedHeight(20)  # keep it small to fit row
        btn.clicked.connect(partial(self.on_item_toggled, name, btn))
            
        self.tree_widget.setItemWidget(item, 5, btn)  # <-- column index 5 (last column)

    def on_item_toggled(self, name, btn):
        print(f"Button clicked for {name}")
        btn.setIcon(QIcon(QPixmap(ButtonIcons.DISABLE.value)))

    def on_item_clicked(self, item, column):
        print(f"Item clicked: {item.text(0)} in column {column}")

    def clear_items(self):
        """
        Removes all items from the tree widget.
        """
        self.tree_widget.clear()