from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QLineEdit, QSizePolicy
)
from PyQt6.QtGui import QPixmap, QIntValidator, QFont, QCursor, QIcon
from PyQt6.QtCore import Qt
from src.constants.ui_params import SPACING
from assets import ICON_PATH
from src.utils.common import clamp
import math
import os
from PyQt6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QWidget,
    QFrame
)
from PyQt6.QtGui import QPixmap, QColor, QPalette, QIcon
from PyQt6.QtCore import Qt, QSize, QPoint, QPointF

class Paging(QWidget):
    def __init__(self, parent=None, callback=None):
        super().__init__(parent)
        self.cur_page = 1
        self.total_pages = 1
        self.page_size = 30
        self.callback = callback
        self.init_ui()

    def init_ui(self):
        # Layouts
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left controls
        left_widget = QFrame()
        left_widget.setStyleSheet("""QFrame {
            border-radius: 0px;
        }""")
        left_layout = QHBoxLayout(left_widget)
        left_layout.setContentsMargins(10,10,10,10)

        label_page = QLabel("Page:")
        self.entry_page = QLineEdit()
        self.entry_page.setFixedWidth(40)
        self.entry_page.setValidator(QIntValidator(1, 9999, self))
        self.entry_page.returnPressed.connect(self.on_page_submitted)

        icon_left = QPixmap(os.path.join(ICON_PATH, 'left.png'))
        self.btn_left = QPushButton()
        self.btn_left.setIcon(QIcon(icon_left))
        self.btn_left.setFlat(True)
        self.btn_left.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_left.clicked.connect(self.prev_page)

        left_layout.addWidget(label_page)
        left_layout.addSpacing(SPACING)
        left_layout.addWidget(self.entry_page)
        left_layout.addStretch(1)
        left_layout.addWidget(self.btn_left)

        # Center paging buttons
        self.frame_paging = QWidget()
        
        self.paging_layout = QHBoxLayout(self.frame_paging)
        self.paging_layout.setContentsMargins(0,0,0,0)
        self.paging_layout.setSpacing(2)

        # Right controls
        right_widget = QFrame()
        right_widget.setStyleSheet("""QFrame {
            border-radius: 0px;
        }""")
        right_layout = QHBoxLayout(right_widget)
        right_layout.setContentsMargins(10,10,10,10)

        icon_right = QPixmap(os.path.join(ICON_PATH, 'right.png'))
        self.btn_right = QPushButton()
        self.btn_right.setIcon(QIcon(icon_right))
        self.btn_right.setFlat(True)
        self.btn_right.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_right.clicked.connect(self.next_page)

        self.entry_size = QLineEdit()
        self.entry_size.setFixedWidth(40)
        self.entry_size.setValidator(QIntValidator(1, 100, self))
        self.entry_size.returnPressed.connect(self.on_size_submitted)

        label_size = QLabel("Size:")

        right_layout.addWidget(self.btn_right)
        right_layout.addStretch(1)
        right_layout.addSpacing(SPACING)
        right_layout.addWidget(label_size)
        
        right_layout.addWidget(self.entry_size)

        # Add to main layout
        main_layout.addWidget(left_widget, stretch=1)
        main_layout.addWidget(self.frame_paging, stretch=1)
        main_layout.addWidget(right_widget, stretch=1)

        effect = QGraphicsDropShadowEffect(
        offset=QPointF(0, 3), blurRadius=20, color=QColor("#111")
        )
        self.setGraphicsEffect(effect)

    def clear(self):
        self.entry_size.setText("")
        self.entry_page.setText("")
        for i in reversed(range(self.paging_layout.count())):
            widget = self.paging_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def show_paging(self):
        # Clear previous buttons
        for i in reversed(range(self.paging_layout.count())):
            widget = self.paging_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        if self.total_pages <= 0:
            return

        prev = 0
        for n in get_pages(self.cur_page, self.total_pages):
            if prev and prev+1 != n:
                label = QLabel("...")
                self.paging_layout.addWidget(label)

            btn = QPushButton(str(n))
            btn.setFlat(True)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(lambda checked, number=n: self.change_page(number))
            if self.cur_page == n:
                btn.setFont(QFont("", weight=QFont.Weight.Bold))
                btn.setStyleSheet("color: #6563FF;")
            self.paging_layout.addWidget(btn)
            prev = n

    def change_page(self, number):
        self.cur_page = number
        self.show_paging()
        self.entry_page.setText(str(self.cur_page))
        if self.callback:
            self.callback(self.cur_page, self.page_size)

    def next_page(self):
        self.cur_page = clamp(self.cur_page+1, 1, self.total_pages)
        self.change_page(self.cur_page)

    def prev_page(self):
        self.cur_page = clamp(self.cur_page-1, 1, self.total_pages)
        self.change_page(self.cur_page)

    def update(self, num:int):
        self.total_pages = math.ceil(num/self.page_size)
        self.show_paging()
        start, end = self.get_range(num)
        self.entry_page.setText(str(self.cur_page))
        self.entry_size.setText(str(self.page_size))
        return start, end

    def get_range(self, num:int):
        start = (self.cur_page-1) * self.page_size
        end = clamp(self.cur_page * self.page_size, start, num)
        return start, end

    def on_page_submitted(self):
        new_page = self.entry_page.text()
        if new_page:
            page_num = int(new_page)
            self.cur_page = clamp(page_num, 1, self.total_pages)
            self.change_page(self.cur_page)

    def on_size_submitted(self):
        page_size = self.entry_size.text()
        if page_size:
            num = int(page_size)
            self.page_size = clamp(num, 1, 100)
            self.entry_size.setText(str(self.page_size))
            self.change_page(1)


def get_pages(current_page=1, total_pages=1, max_size=5):
    out_arr = []
    half = math.floor(max_size/2)
    min_page = clamp(current_page-half, 1, total_pages)
    max_page = clamp(current_page+half, 1, total_pages)

    if current_page-half < 1:
        max_page -= (current_page-half - 1)
    elif current_page+half > total_pages:
        min_page -= (current_page+half - total_pages)

    if total_pages < max_size:
        min_page = 1
        max_page = total_pages

    for n in range(min_page, max_page+1):
        out_arr.append(n)

    if 1 not in out_arr:
        out_arr.append(1)
    if total_pages not in out_arr:
        out_arr.append(total_pages)

    out_arr.sort()
    return out_arr
