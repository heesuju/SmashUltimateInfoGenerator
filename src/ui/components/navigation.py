from typing import List
from functools import partial
from PyQt6.QtWidgets import (
    QWidget, QSizePolicy, QFrame
)
from PyQt6.QtGui import QColor, QPalette
from src.ui.components.layout import HBox, VBox
from src.ui.components.menu_button import MenuButton
from src.managers.data_manager import NavigationMenuIcon

WIDTH = 60
from typing import List, Optional, Callable
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

class NavigationMenu():
    def __init__(self, icon:str, widget:QWidget, callback:Optional[Callable] = None):
        self.icon = icon
        self.widget = widget
        self.callback = callback       

class Navigation(QWidget):
    selection_changed = pyqtSignal()

    def __init__(self, menus:List[List[NavigationMenu]]):
        super().__init__()
        self.selected_menu = NavigationMenuIcon.NONE
        layout = VBox()
        self.menus:List[NavigationMenu] = []
        self.buttons = {}  # Dictionary to track buttons by icon
        self.setLayout(layout)
        self.setFixedWidth(WIDTH)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        self.frame = QFrame()
        self.frame.setFrameShape(QFrame.Shape.NoFrame)
        self.frame.setAutoFillBackground(False)  # Use theme colors
        frame_layout = VBox()
        self.frame.setLayout(frame_layout)
        layout.addWidget(self.frame)

        for n, group in enumerate(menus):
            for menu in group:
                button = MenuButton(NavigationMenuIcon(menu.icon).value, WIDTH, WIDTH, self)
                button.clicked.connect(partial(self.on_clicked, NavigationMenuIcon(menu.icon)))
                frame_layout.addWidget(button)
                self.menus.append(menu)
                self.buttons[menu.icon] = button  # Store button reference

            if n < len(menus) - 1:
                frame_layout.addStretch(1)

        # Navigation frame styling with subtle background
        self.frame.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 0.2);
                border-radius: 0px;
            }
        """)
        
    def on_clicked(self, menu:NavigationMenuIcon):
        if self.selected_menu != menu:
            self.selected_menu = menu
        else:
            self.selected_menu = NavigationMenuIcon.NONE

        # Update button states and panel visibility
        for item in self.menus:
            button = self.buttons.get(item.icon)
            if item.icon == self.selected_menu.value:
                item.widget.show()
                if button:
                    button.setChecked(True)
                if item.callback is not None:
                    item.callback()
            else:
                item.widget.hide()
                if button:
                    button.setChecked(False)
        
        self.selection_changed.emit()
    
    def show_panel(self, panel_widget: QWidget):
        """Programmatically show a specific panel"""
        for item in self.menus:
            button = self.buttons.get(item.icon)
            if item.widget == panel_widget:
                self.selected_menu = NavigationMenuIcon(item.icon)
                item.widget.show()
                if button:
                    button.setChecked(True)
                if item.callback is not None:
                    item.callback()
            else:
                item.widget.hide()
                if button:
                    button.setChecked(False)

        self.selection_changed.emit()
