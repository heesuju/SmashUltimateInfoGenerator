from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt, QSize

class ThumbnailLabel(QLabel):
    def __init__(self, width=320, height=200, parent=None):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self.setStyleSheet("background-color: black;")  # fallback black
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def set_thumbnail(self, path:str):
        if not path:
            return 
        
        size = self.size()  # QSize(320,200)

        # Make black background
        canvas = QPixmap(size)
        canvas.fill(QColor("black"))

        if path:
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                # Scale image keeping aspect ratio
                scaled = pixmap.scaled(
                    size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )

                # Center image onto black canvas
                painter = QPainter(canvas)
                x = (size.width() - scaled.width()) // 2
                y = (size.height() - scaled.height()) // 2
                painter.drawPixmap(x, y, scaled)
                painter.end()

        self.setPixmap(canvas)