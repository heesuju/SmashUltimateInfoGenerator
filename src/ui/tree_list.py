from functools import partial
from PyQt6.QtCore import Qt, QRect, QSize
from PyQt6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QWidget,
)
from PyQt6.QtCore import Qt, QSize, QPoint, QPointF
from PyQt6.QtGui import QPixmap, QColor, QPalette
from PyQt6.QtWidgets import QListWidget, QListView, QStyledItemDelegate, QStyleOptionViewItem, QGraphicsDropShadowEffect, QSizePolicy, QStyle
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget,
    QTreeWidgetItem, QCheckBox, QHeaderView
)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPainterPath, QImage, QBrush, QPen, QColor
from PyQt6.QtWidgets import QGraphicsOpacityEffect
from PyQt6.QtCore import QPropertyAnimation

from src.ui.components.layout import HBox, VBox
from src.managers.data_manager import ButtonIcons

from src.ui.tree_item import TreeItem
from src.models.mod import Mod, ModItem
from src.managers.mod_manager import ModManager

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
        size.setHeight(32)
        return size
    
class TreeList(QWidget):
    def __init__(self, mod_manager:ModManager):
        super().__init__()
        self.mod_manager=mod_manager
        self.animations = []
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
                background: transparent;
                outline: 0;
            }
            QTreeWidget::item {
                padding: 4px;
                border: none;
            }
            QTreeWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.12);
            }
            QTreeWidget::item:selected {
                background-color: rgba(100, 150, 255, 0.2);
                color: white;
            }
            QTreeWidget::item:selected:hover {
                background-color: rgba(100, 150, 255, 0.3);
            }
            QHeaderView::section {
                background-color: rgba(0, 0, 0, 0.3);
                color: white;
                padding: 6px;
                border: none;
                border-right: 1px solid rgba(255, 255, 255, 0.1);
                border-bottom: 1px solid rgba(255, 255, 255, 0.2);
                font-weight: bold;
            }
        """)
        self.tree_widget.setAlternatingRowColors(True)
        self.tree_widget.setColumnCount(7)
        self.tree_widget.setHeaderLabels(["", "Category", "Mod Name", "Authors", "Slot", "Characters", "Enabled"])
        
        # Prevent the last column from auto-stretching
        self.tree_widget.header().setStretchLastSection(False)
        
        # Column 0: Checkbox - Fixed width
        self.tree_widget.setColumnWidth(0, 50)
        self.tree_widget.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        
        # Column 1: Category - Fixed width
        self.tree_widget.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.tree_widget.setColumnWidth(1, 80)
        
        # Column 2: Mod Name - Stretch
        self.tree_widget.header().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tree_widget.setColumnWidth(2, 300)  # Initial/minimum width
        
        # Column 3: Authors - Stretch
        self.tree_widget.header().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.tree_widget.setColumnWidth(3, 150)  # Initial/minimum width
        
        # Column 4: Slot - Fixed width
        self.tree_widget.header().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.tree_widget.setColumnWidth(4, 120)
        
        # Column 5: Characters - Fixed width
        self.tree_widget.header().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.tree_widget.setColumnWidth(5, 120)
        
        # Column 6: Enabled - Fixed width
        self.tree_widget.header().setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self.tree_widget.setColumnWidth(6, 50)
        
        # Set minimum section sizes for stretch columns to prevent over-squashing
        self.tree_widget.header().setMinimumSectionSize(50)
        
        # Add checkbox to header
        header = self.tree_widget.header()
        self.header_checkbox = QCheckBox()
        self.header_checkbox.setText("")
        self.header_checkbox.setFixedSize(20, 20)
        # Position the checkbox over the first column header
        header_pos = header.sectionPosition(0)
        self.header_checkbox.move(header_pos + 20, 2)
        self.header_checkbox.setParent(header)
        self.header_checkbox.show()

        layout.addWidget(self.tree_widget)
        self.setLayout(layout)
        self.tree_widget.itemClicked.connect(self.on_item_clicked)

    def add_item(self, mod:ModItem):
        item = TreeItem(self.tree_widget, mod, None, None)

    def on_item_toggled(self, name, btn):
        print(f"Button clicked for {name}")
        btn.setIcon(QIcon(QPixmap(ButtonIcons.DISABLE.value)))

    def on_item_clicked(self, item, column):
        print(f"Item clicked: {item.mod.name} in column {column}")
        self.mod_manager.set_selection(item.mod.id)

    def clear(self):
        """
        Removes all items from the tree widget.
        """
        self.tree_widget.clear()
