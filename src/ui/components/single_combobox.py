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
