from PyQt6.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem, QToolButton, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, QRect

class CheckBoxTree(QTreeWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setColumnCount(1)
        self.setHeaderLabels(["Elements ▲"])
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.toggle_btn = QToolButton(self.header())  # parent = header
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.toggled.connect(self.toggle_all_items)
        self.toggle_btn.setGeometry(200,10,5,5)

        self.header().setSectionResizeMode(0, self.header().ResizeMode.ResizeToContents)
        self.header().setStretchLastSection(True)
        self.header().setSectionsClickable(False)
        
        self.header().sectionResized.connect(self.update_button_geometry)
        self.update_button_geometry()  # initial geometry

        self.header().setSectionResizeMode(0, self.header().ResizeMode.Fixed)
        self.header().resizeSection(0, 200)  # example width
    
    def update_button_geometry(self):
        rect: QRect = self.header().sectionViewportPosition(0), 0, self.header().sectionSize(0), self.header().height()
        self.toggle_btn.setGeometry(*rect)

    def toggle_all_items(self, expand: bool):
        """Expand or collapse all top-level items."""
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            item.setHidden(not expand)

        # Update button symbol
        self.headerItem().setText(0, "Elements ▲" if expand else "Elements ▼")
        if expand:
            self.adjust_tree_height()
        else:
            self.setFixedHeight(20)

    def add_item(self, value:str):
        item = QTreeWidgetItem([value])
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(0, Qt.CheckState.Unchecked)
        self.addTopLevelItem(item)

    def adjust_tree_height(self):
        total_height = self.header().height()  # include header
        for i in range(self.topLevelItemCount()):
            total_height += self.sizeHintForRow(i)
        self.setFixedHeight(total_height)