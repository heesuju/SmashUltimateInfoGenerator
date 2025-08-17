from typing import List
from functools import partial
from PyQt6.QtWidgets import (
    QWidget, QSizePolicy, QFrame
)
from PyQt6.QtGui import QColor, QPalette
from src.ui.components.layout import HBox, VBox
from src.ui.components.menu_button import MenuButton
from src.constants.icons import MenuIcons
from src.ui.schema import NavigationMenu

WIDTH = 60

class Navigation(QWidget):
    def __init__(self, menus:List[List[NavigationMenu]]):
        super().__init__()
        self.selected_menu = MenuIcons.NONE
        layout = VBox()
        self.menus:List[NavigationMenu] = []
        self.setLayout(layout)
        self.setFixedWidth(WIDTH)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        self.frame = QFrame()
        self.frame.setFrameShape(QFrame.Shape.NoFrame)
        self.frame.setAutoFillBackground(True)
        frame_layout = VBox()
        self.frame.setLayout(frame_layout)
        layout.addWidget(self.frame)
        palette = self.frame.palette()
        palette.setColor(QPalette.ColorRole.Highlight, QColor(100, 255, 255))  # White background
        self.frame.setPalette(palette)

        for n, group in enumerate(menus):
            for menu in group:
                button = MenuButton(MenuIcons(menu.icon).value, WIDTH, WIDTH, self)
                button.clicked.connect(partial(self.on_clicked, MenuIcons(menu.icon)))
                frame_layout.addWidget(button)
                self.menus.append(menu)

            if n < len(menus) - 1:
                frame_layout.addStretch(1)

        self.frame.setStyleSheet("""QFrame {
                                 background-color: rgba(100, 255, 200, 200);
                                 border-radius: 0px;
                                 }""")
        
    def on_clicked(self, menu:MenuIcons):
        if self.selected_menu != menu:
            self.selected_menu = menu
        else:
            self.selected_menu = MenuIcons.NONE

        for item in self.menus:
            if item.icon == self.selected_menu.value:
                item.widget.show()
                if item.callback is not None:
                    item.callback()
            else:
                item.widget.hide()
