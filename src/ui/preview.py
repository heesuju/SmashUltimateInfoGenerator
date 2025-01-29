from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QSizePolicy, QLabel, QFrame
)
from PyQt6.QtGui import QPixmap, QColor, QPalette, QIcon, QFont
from PyQt6.QtCore import Qt, QSize, QPoint, QPointF
from src.ui.components.layout import HBox, VBox

WIDTH = 300
FONT = "Arial"
FONT_SIZE = 10

BODY_FONT_SIZE = 8

class Preview(QWidget):
    def __init__(self):
        super().__init__()
        layout = VBox()
        self.setLayout(layout)
        self.setFixedWidth(340)
        # self.setAutoFillBackground(True)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        
        self.frame = QFrame()
        self.frame.setFrameShape(QFrame.Shape.Box)
        self.frame.setAutoFillBackground(True)
        self.frame.setStyleSheet("""QFrame {
                                 border-radius: 0px;
                                 }""")
        frame_layout = VBox(margin=10, spacing=10)
        self.frame.setLayout(frame_layout)

        details_label = QLabel("Details")
        title_font = QFont(FONT, FONT_SIZE)  # Set the font and font size
        title_font.setBold(True)
        details_label.setFont(title_font)
        frame_layout.addWidget(details_label)

        thumbnail = QLabel()
        preview_dir = "assets/img/preview.webp"
        preview_img = QPixmap(preview_dir).scaled(WIDTH, WIDTH, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        thumbnail.setPixmap(preview_img)
        frame_layout.addWidget(thumbnail)

        mod_name_label = QLabel("Valentine Sisters")
        title_font = QFont(FONT, FONT_SIZE)  # Set the font and font size
        title_font.setBold(True)
        mod_name_label.setFont(title_font)
        frame_layout.addWidget(mod_name_label)

        version_label = QLabel("1.2.4")
        body_font = QFont(FONT, BODY_FONT_SIZE)  # Set the font and font size
        version_label.setFont(body_font)
        frame_layout.addWidget(version_label)
        frame_layout.addStretch(1)

        # Set the background color using QPalette
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor('red'))
        self.setPalette(palette)

        layout.addWidget(self.frame)

        