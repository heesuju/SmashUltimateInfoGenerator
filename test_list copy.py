import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout
)
import qdarktheme
from src.ui.list_item import GridListItem
from src.ui.grid_list import GridList
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
        layout = HBox(self)
        self.setLayout(layout)

        vlayout = VBox(self)
        self.search = SearchWidget()
        self.menu = MenuWidget()
        self.menu.setContentsMargins(0,0,0,0)
        self.search.setContentsMargins(0,0,0,0)
        self.setContentsMargins(0,0,0,0)
        
        vlayout.addWidget(self.search)
        layout.addLayout(vlayout)
        layout.addWidget(self.menu)
        
        
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = MultiSelectList()
    
    window.show()
    sys.exit(app.exec())