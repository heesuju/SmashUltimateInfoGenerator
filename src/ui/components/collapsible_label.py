from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class CollapsibleLabel(QWidget):
    def __init__(self, title: str, text: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.is_collapsed = False

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 5, 0)
        self.layout.setSpacing(0)

        # clickable title
        self.header_btn = QPushButton("▲ " + title)
        self.header_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.header_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border: none;
                text-align: left;
                padding: 4px;
                border-top-left-radius: 5px;
                border-bottom-left-radius: 0px;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 0px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)
        self.header_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.header_btn.clicked.connect(self.toggle)
        self.layout.addWidget(self.header_btn)

        # content
        self.content = QLabel(text)
        self.content.setWordWrap(True)
        self.content.setStyleSheet("""
            QLabel {
                background-color: #2c2c2c;
                color: white;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 5px;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 5px;
                padding: 6px;
            }
        """)
        self.layout.addWidget(self.content)

    def toggle(self, event=None):
        self.is_collapsed = not self.is_collapsed
        if self.is_collapsed:
            self.header_btn.setText("▼ " + self.title)
            self.header_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border: none;
                text-align: left;
                padding: 4px;
                
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)
        else:
            self.header_btn.setText("▲ " + self.title)
            
            self.header_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border: none;
                text-align: left;
                padding: 4px;
                border-top-left-radius: 5px;
                border-bottom-left-radius: 0px;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 0px;
                
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)

        self.content.setVisible(not self.is_collapsed)

    def set_value(self, value:str):
        self.content.setText(value)

    def set_title(self, title:str):
        self.title = title
        if self.is_collapsed:
            self.header_btn.setText("▼ " + self.title)
        else:
            self.header_btn.setText("▲ " + self.title)