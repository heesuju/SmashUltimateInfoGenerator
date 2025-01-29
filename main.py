import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout
)
import qdarktheme
from src.ui.list_item import GridListItem
from src.ui.mod_list_widget import ModListWidget
from src.ui.preview import Preview
from PyQt6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QWidget,
)
from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtCore import Qt, QSize, QPoint, QPointF
from src.ui.search_widget import SearchWidget
from src.ui.menu_widget import MenuWidget
from src.ui.components.layout import HBox, VBox

class MultiSelectList(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Selectable List")
        self.setGeometry(100, 100, 1200, 600)
        
        # self.setStyleSheet("padding: 0px;};")
        layout = HBox()
        vlayout = VBox()
        hlayout = HBox()

        self.list_widget = ModListWidget()
        self.preview = Preview()
        self.search = SearchWidget()
        self.menu = MenuWidget()
        # Add some items
        
        
        
        vlayout.addWidget(self.search)
        hlayout.addWidget(self.list_widget)
        hlayout.addWidget(self.preview)
        
        vlayout.addLayout(hlayout)
        
        layout.addWidget(self.menu)
        layout.addLayout(vlayout)
        self.setLayout(layout)     

if __name__ == "__main__":
    app = QApplication(sys.argv)
    qdarktheme.setup_theme("dark")
    window = MultiSelectList()
    window.show()
    sys.exit(app.exec())