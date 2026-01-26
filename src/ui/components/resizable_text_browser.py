from PyQt6.QtWidgets import QTextEdit, QApplication
from PyQt6.QtCore import Qt, QSize, QUrl
from PyQt6.QtGui import QDesktopServices, QCursor, QTextCharFormat, QTextOption

class ResizableTextBrowser(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameShape(QTextEdit.Shape.NoFrame)
        # Mouse tracking needed for changing cursor over links
        self.setMouseTracking(True)
        self.setStyleSheet("background: transparent;")
        self.setWordWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere) 
    
    def fit_content(self):
        """Adjust height to fit content"""
        # Force a layout update to get correct height
        self.document().setTextWidth(self.viewport().width())
        height = self.document().size().height()
        margin = self.contentsMargins().top() + self.contentsMargins().bottom()
        self.setFixedHeight(int(height + margin))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fit_content()

    def _reset_formatting(self):
        self.clear()
        cursor = self.textCursor()
        fmt = QTextCharFormat()
        cursor.setCharFormat(fmt)
        self.setTextCursor(cursor)

    def set_html(self, html: str):
        self._reset_formatting()
        self.setHtml(html)
        self.fit_content()

    def setText(self, text: str):
        self._reset_formatting()
        super().setText(text)
        self.fit_content()
        
    def mouseMoveEvent(self, event):
        # Update cursor if hovering over a link
        anchor = self.anchorAt(event.pos())
        if anchor:
            self.viewport().setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        else:
            self.viewport().setCursor(QCursor(Qt.CursorShape.IBeamCursor))
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        anchor = self.anchorAt(event.pos())
        if anchor:
            QDesktopServices.openUrl(QUrl(anchor))
        else:
            super().mouseReleaseEvent(event)
