from PyQt6.QtWidgets import QComboBox
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QMouseEvent


class SingleComboBox(QComboBox):
    """
    Custom QComboBox that:
    - Allows clicking anywhere on the widget to open the dropdown
    - Supports displaying custom text not in the items list
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.lineEdit().setReadOnly(True)
        
        # Make the line edit clickable to open dropdown
        self.lineEdit().installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """Intercept mouse clicks on the line edit to show the dropdown"""
        if obj == self.lineEdit() and event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                self.showPopup()
                return True
        return super().eventFilter(obj, event)
    
    def wheelEvent(self, event):
        """Ignore wheel events to prevent accidental selection changes"""
        event.ignore()
    
    def showPopup(self):
        """Override to sort items alphabetically before showing the popup"""
        # Sort items alphabetically, but preserve the first item if it's a placeholder
        if self.count() > 1:
            first_item = self.itemText(0)
            preserve_first = first_item.startswith("All ")  # Check if it's a placeholder like "All Series"
            
            # Collect all items
            items = [self.itemText(i) for i in range(self.count())]
            
            # Sort items (skip first if it's a placeholder)
            if preserve_first:
                sorted_items = [items[0]] + sorted(items[1:], key=str.lower)
            else:
                sorted_items = sorted(items, key=str.lower)
            
            # Clear and re-add in sorted order
            current_text = self.currentText()
            self.blockSignals(True)
            self.clear()
            self.addItems(sorted_items)
            self.setCurrentText(current_text)
            self.blockSignals(False)
        
        super().showPopup()
