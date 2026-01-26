from PyQt6.QtWidgets import QApplication, QTextEdit, QWidget, QVBoxLayout 
from PyQt6.QtCore import QPropertyAnimation
from PyQt6 import QtGui, QtCore
from PyQt6.QtGui import QTextDocument

class ShrinkingTextEdit(QTextEdit):
    def __init__(self, placeholder="", line_height=60, max_height=400):
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
            shortened_text = self.get_first_n_lines()
            if len(self.current_text) > len(shortened_text):
                self.setText(shortened_text + "...")
            else:
                self.setText(shortened_text)

            self.setReadOnly(True)
        else:
            self.adjust_height()
            self.setReadOnly(False)
            self.setText(self.current_text)
            cursor = self.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.setTextCursor(cursor)

    def get_first_n_lines(self, n=2):
        text = self.toPlainText()
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            # Check if adding this word exceeds a line (rough approx)
            if current_line:
                candidate = current_line + " " + word
            else:
                candidate = word

            doc = QTextDocument()
            doc.setPlainText(candidate)
            doc.setTextWidth(self.viewport().width())
            line_count = doc.blockCount()

            if line_count > 1:  # exceeded line width
                lines.append(current_line)
                current_line = word
            else:
                current_line = candidate

            if len(lines) >= n:
                break

        if len(lines) < n and current_line:
            lines.append(current_line)

        return "\n".join(lines[:n])