from PyQt6.QtWidgets import QApplication, QTextEdit, QWidget, QVBoxLayout
from PyQt6.QtCore import QPropertyAnimation
from PyQt6 import QtGui, QtCore

class ShrinkingTextEdit(QTextEdit):
    def __init__(self, placeholder="", line_height=30, max_height=400):
        super().__init__()
        self.line_height = line_height
        self.max_height = max_height
        self.current_text = ""
        self.setPlaceholderText(placeholder)

        # ✅ Correct word wrap setting
        self.setWordWrapMode(QtGui.QTextOption.WrapMode.WordWrap)

        # Disable scrollbars
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Start collapsed (one line high)
        self.setFixedHeight(self.line_height)

        # Adjust height while typing
        self.textChanged.connect(self.adjust_height)

        # Keep reference to animation
        self._animation = None

    def focusInEvent(self, event):
        # Expand with content while focused
        self.toggle(False)
        super().focusInEvent(event)
        

    def focusOutEvent(self, event):
        # Force collapse to exactly one line (ignores content height)
        self.toggle(True)
        super().focusOutEvent(event)

    def adjust_height(self):
        if self.hasFocus():     
            doc_height = self.document().size().height()
            margin = self.frameWidth() * 2 + self.document().documentMargin() * 2
            new_height = int(doc_height + margin)
            new_height = max(self.line_height, min(new_height, self.max_height))
            self.setFixedHeight(new_height)

    def toggle(self, shrink:bool):
        if shrink:
            self.current_text = self.toPlainText()
            self.setFixedHeight(self.line_height)
            self.setText(self.current_text.split("\n")[0][:60] + "...")
            self.setReadOnly(True)
        else:
            self.adjust_height()
            self.setReadOnly(False)
            self.setText(self.current_text)
            cursor = self.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.setTextCursor(cursor)