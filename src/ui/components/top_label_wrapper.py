from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QTextEdit, QComboBox, QVBoxLayout
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from src.constants.colors import ROYAL_BLUE

class TopLabelWrapper(QWidget):
    def __init__(self, widget, label_text,
                 height=44,
                 font_size=9,
                 label_color=ROYAL_BLUE):
        super().__init__()

        self.input_widget = widget
        self.input_widget.setParent(self)
        self.input_widget.setMinimumHeight(height)

        # Create label stuck at top
        self.label = QLabel(label_text, self)
        self.label.setFont(QFont("Arial", font_size))
        self.label.setStyleSheet(f"color: {label_color}; font-size: {font_size}pt;")
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.label.raise_()

        # Add padding so input text doesn't overlap label
        if isinstance(widget, QLineEdit):
            self.input_widget.setStyleSheet(
                f"QLineEdit {{ padding-top: {font_size + 6}px; padding-left: 8px; }}"
            )
        elif isinstance(widget, QComboBox):
            self.input_widget.setStyleSheet(
                f"QComboBox {{ padding-top: {font_size + 6}px; padding-left: 8px; }}"
            )
        elif isinstance(widget, QTextEdit):
            self.input_widget.setStyleSheet(
                f"QTextEdit {{ padding-top: {font_size + 6}px; padding-left: 8px; }}"
            )

        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.input_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Position label inside input box at top
        self.label.setGeometry(8, 2, self.input_widget.width() - 16, font_size + 4)