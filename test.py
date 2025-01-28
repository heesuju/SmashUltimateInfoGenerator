import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QLabel, QSizePolicy, QListWidget, QListWidgetItem,QListView
)
from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtCore import Qt, QSize, QPoint, QPointF
from src.utils.image_utils import create_image_overlay, add_text_to_image
from PyQt6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QWidget,
)
from PyQt6.QtGui import QIcon, QPixmap, QPainter

ICON_OFF = "assets/icons/cartridge_off"
ICON_ON = "assets/icons/cartridge_off"

class StringListWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the layout
        layout = QVBoxLayout()

        # Create a QListWidget
        self.list_widget = QListWidget()
        self.list_widget.setSpacing(100)
        self.list_widget.setResizeMode(QListView.ResizeMode.Adjust)
        self.list_widget.setGridSize(QSize(340, 80))
        self.list_widget.setFlow(QListView.Flow.LeftToRight)
        self.list_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.list_widget.setWrapping(True)
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)  # Allows multiple selection


        # Add some items to the list
        items = [
            "Item 1\ndskljdfls\nkjdsflsdjf",
            "Item 2\ndskljdfls\nkjdsflsdjf",
            "Item 3\ndskljdfls\nkjdsflsdjf",
            "Item 4\ndskljdfls\nkjdsflsdjf",
            "Item 5\ndskljdfls\nkjdsflsdjf"
        ]

        for item in items:
            base_pixmap = QPixmap(ICON_OFF)
            wid = QListWidgetItem(QIcon(base_pixmap), item)
            self.list_widget.addItem(wid)

        # Add the QListWidget to the layout
        layout.addWidget(self.list_widget)

        # Set the layout for the main window
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StringListWidget()
    window.show()
    sys.exit(app.exec())