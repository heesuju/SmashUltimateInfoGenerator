from typing import List
from PyQt6.QtWidgets import QApplication, QComboBox, QStyledItemDelegate
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt

class ComboBox(QComboBox):
    def __init__(self, default:str="", items:List=[]):
        super().__init__()
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        self.setMinimumWidth(100)  # compact width
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)  # user cannot type
        self.lineEdit().installEventFilter(self)  # intercept clicks

        if default:
            self.default=default

        if len(items) > 0:
            self.add_items(items)

        self.reset()
    
    def reset(self):
        self.setCurrentIndex(-1)
        self.setCurrentText(f"--Select {self.default}--")

    def add_items(self, items:List):
        for item in items:
            self.addItem(str(item))

    def eventFilter(self, obj, event):
        # Intercept clicks on the line edit
        if obj == self.lineEdit() and event.type() == event.Type.MouseButtonPress:
            self.showPopup()  # open dropdown instead of focusing text
            return True  # stop further handling
        return super().eventFilter(obj, event)
    
    def wheelEvent(self, event):
        event.ignore()  # disable scroll changing value