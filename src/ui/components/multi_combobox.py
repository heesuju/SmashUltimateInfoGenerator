from typing import List
from PyQt6.QtWidgets import QApplication, QComboBox, QStyledItemDelegate
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt

class CheckableComboBox(QComboBox):
    def __init__(self, items:List[str]=[], include_all:bool=False):
        super().__init__()
        self.include_all = include_all
        self.setModel(QStandardItemModel(self))
        # self.setEditable(False)  # prevent typing
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.view().pressed.connect(self.handle_item_pressed)
        self.setMinimumWidth(100)  # compact width
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)  # user cannot type
        self.lineEdit().installEventFilter(self)  # intercept clicks
        if include_all:
            self.add_item("Select All")
        if len(items) > 0:
            self.add_items(items)
        
    def add_items(self, items:List[str]):
        for item in items:
            self.add_item(item)

    def add_item(self, text):
        item = QStandardItem(text)
        
        item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        item.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
        self.model().appendRow(item)

    def get_all_items(self):
        model = self.model()
        root = model.invisibleRootItem()
        items = []
        for row in range(root.rowCount()):
            item = root.child(row)  # each QStandardItem
            items.append(item)
        return items
    
    def is_item_selected(self, index:int)->bool:
        if index < self.get_item_count():
            item = self.model().invisibleRootItem().child(index)
            return item.checkState == Qt.CheckState.Checked
        return False

    def get_item_count(self)->int:
        model = self.model()
        root = model.invisibleRootItem()
        return root.rowCount()

    def handle_item_pressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == Qt.CheckState.Checked:
            item.setCheckState(Qt.CheckState.Unchecked)
        else:
            item.setCheckState(Qt.CheckState.Checked)
        
        if self.include_all:
            if self.model().indexFromItem(item).row() == 0:
                self.select_all(item.checkState() == Qt.CheckState.Checked)
            else:
                first_item = self.model().invisibleRootItem().child(0)
                first_item.setCheckState(Qt.CheckState.Unchecked)
        self.update_display()

    def select_all(self, is_selected:bool):
        for item in self.get_all_items():
            if is_selected:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)

    def update_display(self):
        checked = [self.model().item(i).text()
                   for i in range(self.model().rowCount())
                   if self.model().item(i).checkState() == Qt.CheckState.Checked]
        text = ", ".join(checked)
        if self.include_all:
            if len(checked) == self.get_item_count():
                self.setCurrentText("All")
                return None
            elif self.is_item_selected(0):
                checked = checked[1:]
            
        self.setCurrentText(", ".join(checked))

    def eventFilter(self, obj, event):
        # Intercept clicks on the line edit
        if obj == self.lineEdit() and event.type() == event.Type.MouseButtonPress:
            self.showPopup()  # open dropdown instead of focusing text
            return True  # stop further handling
        return super().eventFilter(obj, event)
    
    def wheelEvent(self, event):
        event.ignore()  # disable scroll changing value