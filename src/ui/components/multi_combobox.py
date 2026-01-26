from typing import List
from PyQt6.QtWidgets import QApplication, QComboBox, QStyledItemDelegate
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt

class CheckableComboBox(QComboBox):
    def __init__(self, items:List=[], defaults:List[bool]=[], include_all:bool=False, placeholder_text:str="All", formatter=None, sorter=None):
        super().__init__()
        self.include_all = include_all
        self.defaults = defaults
        self.placeholder_text = placeholder_text
        self.formatter = formatter
        self.sorter = sorter
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
            # self.sort_items()  # Disabled for performance on init

        if len(self.defaults) > 0:
            self.reset()
        
        self.update_display()  # Initialize display with proper text
        
    def reset(self):
        items = self.get_all_items()

        for n in range(self.get_item_count()):
            if len(self.defaults) - 1 >= n:
                if self.defaults[n]:
                    items[n].setCheckState(Qt.CheckState.Checked)
                else:
                    items[n].setCheckState(Qt.CheckState.Unchecked)
            else:
                items[n].setCheckState(Qt.CheckState.Unchecked)

        # self.sort_items()  # Disabled for performance
        self.update_display()

    def add_items(self, items:List):
        for item in items:
            self.add_item(str(item))

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

    def get_checked(self)->List[str]:
        return [self.model().item(i).text()
            for i in range(self.model().rowCount())
            if self.model().item(i).checkState() == Qt.CheckState.Checked]

    def get_item_count(self)->int:
        model = self.model()
        root = model.invisibleRootItem()
        return root.rowCount()
    
    def sort_items(self):
        """Sort items alphabetically, with selected items appearing first.
        'Select All' option always stays at index 0."""
        if self.get_item_count() <= 1:  # Nothing to sort if 0 or 1 items
            return
        
        model = self.model()
        root = model.invisibleRootItem()
        
        # Collect all items except "Select All" (if present)
        items_data = []
        start_index = 1 if self.include_all else 0
        
        for row in range(start_index, root.rowCount()):
            item = root.child(row)
            items_data.append({
                'text': item.text(),
                'checked': item.checkState() == Qt.CheckState.Checked,
                'item': item
            })
        
        # Sort by: 1. checked status (checked first), 2. sorter or alphabetically
        sort_func = self.sorter if self.sorter else lambda x: x.lower()
        items_data.sort(key=lambda x: (not x['checked'], sort_func(x['text'])))
        
        # Remove all items except "Select All"
        for _ in range(len(items_data)):
            root.removeRow(start_index)
        
        # Re-add items in sorted order
        for data in items_data:
            new_item = QStandardItem(data['text'])
            new_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            check_state = Qt.CheckState.Checked if data['checked'] else Qt.CheckState.Unchecked
            new_item.setData(check_state, Qt.ItemDataRole.CheckStateRole)
            root.appendRow(new_item)

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
    
    def showPopup(self):
        """Override to sort items before showing the popup"""
        self.sort_items()  # Sort only when opening the dropdown
        super().showPopup()

    def hidePopup(self):
        """Override to ensure display text is correct after closing"""
        super().hidePopup()
        self.update_display()

    def update_display(self):
        checked = self.get_checked()
        
        # Show placeholder text when all items are selected or none selected
        if self.include_all:
            if len(checked) == self.get_item_count():
                self.setCurrentText(self.placeholder_text)
                return
            elif len(checked) == self.get_item_count() - 1 and "Select All" not in checked:
                self.model().item(0).setCheckState(Qt.CheckState.Checked)
                self.setCurrentText(self.placeholder_text)
                return
            elif self.is_item_selected(0):
                checked = checked[1:]  # Remove "Select All" from display
            
        if self.formatter:
            self.setCurrentText(self.formatter(checked))
        else:
            self.setCurrentText(", ".join(checked))

    def eventFilter(self, obj, event):
        # Intercept clicks on the line edit
        if obj == self.lineEdit() and event.type() == event.Type.MouseButtonPress:
            self.showPopup()  # open dropdown instead of focusing text
            return True  # stop further handling
        return super().eventFilter(obj, event)
    
    def wheelEvent(self, event):
        event.ignore()  # disable scroll changing value