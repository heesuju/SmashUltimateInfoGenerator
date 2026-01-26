from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem, 
    QPushButton, QHeaderView, QLineEdit, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer, QEvent
from PyQt6.QtGui import QFont, QIcon, QPixmap, QAction
from src.managers.data_manager import ButtonIcons
from src.managers.workspace_manager import WorkspaceManager

FONT = "Arial"
BODY_FONT_SIZE = 8

class WorkspaceList(QWidget):
    def __init__(self, workspace_manager: WorkspaceManager):
        super().__init__()
        self.workspace_manager = workspace_manager
        self.editing_item = None
        self.editor = None
        self._is_committing = False
        
        self.init_ui()
        self.workspace_manager.workspace_changed.connect(self.refresh)
        self.refresh()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Tree
        self.tree = QTreeWidget()
        self.tree.setColumnCount(1)
        self.tree.setHeaderLabels(["Workspace Name"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid rgba(255, 255, 255, 0.1);
                background: rgba(0, 0, 0, 0.2);
                border-radius: 5px;
                outline: 0;
            }
            QTreeWidget::item {
                padding: 4px;
                border: none;
            }
            QTreeWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.08);
            }
            QTreeWidget::item:selected {
                background-color: rgba(100, 150, 255, 0.2);
            }
            QHeaderView::section {
                background-color: rgba(0, 0, 0, 0.3);
                color: white;
                padding: 4px;
                border: none;
                border-right: 1px solid rgba(255, 255, 255, 0.1);
                border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            }
        """)
        self.tree.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.tree)
        
        # Add Button (Overlay on Header)
        self.add_btn = QPushButton("+", self.tree.header())
        self.add_btn.setFixedSize(16, 16)
        self.add_btn.setToolTip("Add Workspace")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 3px;
                color: white;
                font-weight: bold;
                padding-bottom: 2px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        self.add_btn.clicked.connect(self.on_add_clicked)
        
        # Install event filter to position button
        self.tree.header().installEventFilter(self)
        self.tree.installEventFilter(self)
        
        # Disable scrollbars for auto-height
        self.tree.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    
    def eventFilter(self, source, event):
        if source == self.tree.header() or source == self.tree:
            if event.type() == QEvent.Type.Resize or event.type() == QEvent.Type.Move:
                self.update_add_btn_position()
                self.adjust_height()
        return super().eventFilter(source, event)
        
    def showEvent(self, event):
        super().showEvent(event)
        self.update_add_btn_position()
        self.adjust_height()
        
    def adjust_height(self):
        """Adjust tree height to fit content"""
        # Calculate height based on rows
        row_height = 28 # Approximation of item height + padding
        header_height = self.tree.header().height()
        count = self.tree.topLevelItemCount()
        
        total_height = header_height + (count * row_height) + 4 # Extra padding
        if self.editor: 
            # If editor is open, it's an item, so it's included in count? 
            # Yes, we add item first.
            pass
            
        self.tree.setFixedHeight(total_height)
        self.setFixedHeight(total_height)
        
    def update_add_btn_position(self):
        header = self.tree.header()
        # Position on the right of the single column
        idx = 0
        w = header.sectionSize(idx)
        h = header.height()
        
        # Align right with some padding
        btn_w, btn_h = 16, 16
        padding_right = 8
        pos_x = w - btn_w - padding_right
        pos_y = (h - btn_h) // 2
        
        self.add_btn.setGeometry(pos_x, pos_y, btn_w, btn_h)

    def refresh(self):
        """Reload workspaces from manager"""
        # Reset editing state if we refresh (e.g. forced via switch)
        self.editing_item = None
        self.editor = None
        
        self.tree.blockSignals(True)
        self.tree.clear()
        
        current_ws = self.workspace_manager.current_workspace_name
        
        for name in self.workspace_manager.workspace_map.keys():
            self.add_tree_item(name, is_default=(name == "Default"))
            
        # Select current
        items = self.tree.findItems(current_ws, Qt.MatchFlag.MatchExactly, 0)
        if items:
            items[0].setSelected(True)
            
        self.tree.blockSignals(False)
        self.adjust_height()

    def add_tree_item(self, name: str, is_default: bool):
        item = QTreeWidgetItem(self.tree)
        item.setText(0, name) 
        item.setData(0, Qt.ItemDataRole.UserRole, is_default)
        
        # Container Widget
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 0, 4, 0) # Match padding
        layout.setSpacing(0)
        
        # Label (Name)
        label = QLabel(name)
        label.setStyleSheet("background: transparent; color: white;")
        layout.addWidget(label)
        
        def select_item(event):
            self.tree.setCurrentItem(item)

        container.mousePressEvent = select_item
        label.mousePressEvent = select_item
        
        layout.addStretch()
        
        # Remove Button
        if not is_default:
            remove_btn = QPushButton(text="-")
            remove_btn.setFixedSize(16, 16)
            remove_btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    background: transparent;
                    border-radius: 3px;
                    color: #ff5555;
                    font-weight: bold;
                    padding-bottom: 2px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 100, 100, 0.3);
                }
            """)
            remove_btn.clicked.connect(lambda: self.remove_workspace(name))
            layout.addWidget(remove_btn)
            
        self.tree.setItemWidget(item, 0, container)

    def on_add_clicked(self):
        """Create a temporary item for editing"""
        if self.editing_item:
            return 
            
        item = QTreeWidgetItem(self.tree)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        self.tree.scrollToItem(item)
        
        # Create input editor
        self.editor = QLineEdit()
        self.editor.setPlaceholderText("Name...")
        self.editor.setStyleSheet("background: #2b2b2b; color: white; border: 1px solid #555;")
        self.editor.returnPressed.connect(self.commit_add)
        self.editor.editingFinished.connect(self.cancel_add_on_blur)
        
        self.tree.setItemWidget(item, 0, self.editor)
        self.editor.setFocus()
        self.editing_item = item
        self.adjust_height()

    def clean_editor(self):
        if self.editing_item:
            pass

    def cancel_add_on_blur(self):
        if self.editor and not self.editor.hasFocus():
            QTimer.singleShot(0, self.commit_add)

    def cancel_add(self):
        if self.editing_item:
            self.tree.blockSignals(True)
            root = self.tree.invisibleRootItem()
            if root.indexOfChild(self.editing_item) != -1:
                root.removeChild(self.editing_item)
            self.editing_item = None
            self.editor = None
            self.tree.blockSignals(False)
            self.adjust_height()

    def commit_add(self):
        if self._is_committing or not self.editor: 
            return
            
        name = self.editor.text().strip()
        if not name:
            self.cancel_add()
            return

        self._is_committing = True
        
        try:
            self.editor.returnPressed.disconnect(self.commit_add)
            self.editor.editingFinished.disconnect(self.cancel_add_on_blur)
        except: pass

        success = self.workspace_manager.add_workspace(name)
        if success:
            self.editing_item = None
            self.editor = None
            self.refresh()
            self._is_committing = False
        else:
            QMessageBox.warning(self, "Error", f"Workspace '{name}' already exists.")
            self.editor.returnPressed.connect(self.commit_add)
            self.editor.editingFinished.connect(self.cancel_add_on_blur)
            self.editor.selectAll()
            self.editor.setFocus()
            self._is_committing = False

    def on_selection_changed(self):
        if self.editing_item:
            return
            
        selected = self.tree.selectedItems()
        if not selected:
            return
            
        item = selected[0]
        if item == self.editing_item:
            return
            
        name = item.text(0)
        # Avoid switching if empty (placeholder) or same
        if not name: 
            return
            
        if name != self.workspace_manager.current_workspace_name:
            self.workspace_manager.switch_workspace(name)

    def remove_workspace(self, name: str):
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            f"Delete workspace '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.workspace_manager.remove_workspace(name)
            self.refresh()
