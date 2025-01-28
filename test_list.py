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
        layout = HBox()
        vlayout = VBox()

        self.list_widget = GridList()
        self.preview = Preview()
        self.search = SearchWidget()
        self.menu = MenuWidget()
        # Add some items
        items = [
            ("assets/img/preview.webp", ["assets/icons/characters/sonic.png", "assets/icons/characters/simon.png", "assets/icons/characters/jack.png"], "Blade of Evil's Bane", "Shun_One", "C01"),
            ("assets/img/preview.webp", ["assets/icons/characters/aegis.png", "assets/icons/characters/element.png", "assets/icons/characters/jack.png"],"Master Shield", "DarkHero", "C02"),
            ("assets/img/preview.webp", ["assets/icons/characters/wolf.png", "assets/icons/characters/simon.png", "assets/icons/characters/jack.png"],"Phantom Armor", "GhostKnight", "C03"),
            ("assets/img/preview.webp", ["assets/icons/characters/sonic.png", "assets/icons/characters/simon.png", "assets/icons/characters/jack.png"], "Blade of Evil's Bane", "Shun_One", "C01"),
            ("assets/img/preview.webp", ["assets/icons/characters/sonic.png", "assets/icons/characters/simon.png", "assets/icons/characters/jack.png"], "Blade of Evil's Bane", "Shun_One", "C01"),
            ("assets/img/preview.webp", ["assets/icons/characters/sonic.png", "assets/icons/characters/simon.png", "assets/icons/characters/jack.png"], "Blade of Evil's Bane", "Shun_One", "C01"),
            ("assets/img/preview.webp", ["assets/icons/characters/sonic.png", "assets/icons/characters/simon.png", "assets/icons/characters/jack.png"], "Blade of Evssssssssssssssssil's Bane", "Shun_One", "C01"),
            ("assets/img/preview.webp", ["assets/icons/characters/sonic.png", "assets/icons/characters/simon.png", "assets/icons/characters/jack.png"], "Blade of Evil's Bane", "Shun_One", "C01"),
            ("assets/img/preview.webp", ["assets/icons/characters/sonic.png", "assets/icons/characters/simon.png", "assets/icons/characters/jack.png"], "Blade of Evil's Bane", "Shun_One", "C01"),
            ("assets/img/preview.webp", ["assets/icons/characters/sonic.png", "assets/icons/characters/simon.png", "assets/icons/characters/jack.png"], "Blade of Evil's Bane", "Shun_One", "C01"),
        ]

        for icon_path, character_icons, name, author, slot in items:
            self.list_widget.add_item(icon_path, character_icons, name, author)
        
        
        vlayout.addWidget(self.search)
        vlayout.addWidget(self.list_widget)
        
        layout.addWidget(self.menu)
        layout.addLayout(vlayout)
        layout.addWidget(self.preview)
        
        self.setLayout(layout)     

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # qdarktheme.setup_theme("dark")
    window = MultiSelectList()
    window.show()
    sys.exit(app.exec())