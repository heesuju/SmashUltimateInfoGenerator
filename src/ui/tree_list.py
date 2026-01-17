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
    QTreeWidgetItem, QCheckBox, QHeaderView, QScrollBar
)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPainterPath, QImage, QBrush, QPen, QColor, QWheelEvent
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
                border-radius: 5px;
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
        # Verify overlay updates (usually handled by valueChanged connection)

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
        self.current_page_item_ids = []  # Track IDs of items on current page
        self.item_checkboxes = {}  # Map item ID to checkbox widget
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
            
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.2);
                min-height: 20px;
                border-radius: 4px;
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
        self.tree_widget.setHeaderLabels(["", "Category", "Mod Name", "Authors", "Slot", "Characters", "Actions"])
        
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
        self.tree_widget.setColumnWidth(5, 140)
        
        # Column 6: Actions - Fixed width
        self.tree_widget.header().setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self.tree_widget.setColumnWidth(6, 80)
        
        # Set minimum section sizes for stretch columns to prevent over-squashing
        self.tree_widget.header().setMinimumSectionSize(50)
        
        # Header checkbox removed - using shared checkbox in control bar instead

        layout.addWidget(self.tree_widget)
        self.setLayout(layout)
        self.tree_widget.itemClicked.connect(self.on_item_clicked)

    def add_item(self, mod:ModItem):
        # Track this item as part of current page
        if mod.id not in self.current_page_item_ids:
            self.current_page_item_ids.append(mod.id)
        
        # Update selected state from ModManager
        mod.selected = self.mod_manager.is_selected(mod.id)
        
        item = TreeItem(self.tree_widget, mod, None, None, tree_list=self)

    def on_item_toggled(self, name, btn):
        print(f"Button clicked for {name}")
        btn.setIcon(QIcon(QPixmap(ButtonIcons.DISABLE.value)))

    def on_item_clicked(self, item, column):
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        
        # Check if Ctrl is held down
        modifiers = QApplication.keyboardModifiers()
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            # Ctrl+Click: Toggle checkbox
            if item.mod.id in self.item_checkboxes:
                checkbox = self.item_checkboxes[item.mod.id]
                # Toggle the checkbox
                checkbox.setChecked(not checkbox.isChecked())
            # Don't show preview when Ctrl+clicking
            return
        
        # Normal click: show preview
        print(f"Item clicked: {item.mod.name} in column {column}")
        self.mod_manager.set_selection(item.mod.id)
    
    def on_header_checkbox_changed(self, state):
        """
        Handle header checkbox state change from ModList control bar
        """
        from PyQt6.QtCore import Qt
        
        should_select = (state == Qt.CheckState.Checked.value)
        
        # Update all items on current page
        for item_id in self.current_page_item_ids:
            if should_select:
                self.mod_manager.add_selection(item_id)
            else:
                self.mod_manager.remove_selection(item_id)
            
            # Update the checkbox widget if it exists
            if item_id in self.item_checkboxes:
                checkbox = self.item_checkboxes[item_id]
                checkbox.blockSignals(True)  # Prevent triggering stateChanged
                checkbox.setChecked(should_select)
                checkbox.blockSignals(False)

    def update_item_favorite_status(self, mod_id:str, is_favorite:bool):
        """Update favorite status of a specific item without reloading"""
        # Iterate through visible items
        root = self.tree_widget.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            if isinstance(item, TreeItem) and item.mod.id == mod_id:
                # Update the mod object
                item.mod.favorited = is_favorite
                # Update the button state
                if hasattr(item, 'fav_button'):
                    item.fav_button.set_state(is_favorite)
                break

    def clear(self):
        """
        Removes all items from the tree widget.
        """
        self.tree_widget.clear()
        self.current_page_item_ids = []
        self.item_checkboxes = {}
