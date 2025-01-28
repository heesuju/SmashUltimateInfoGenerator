from typing import Union
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QStackedLayout, QWidget
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class ImageOverlayWidget(QWidget):
    def __init__(self, image:Union[QPixmap, list[QPixmap]], text:str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        text_label = QLabel(text, self)
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 0);")

        

        if isinstance(image, list):
            for img in image:
                image_label = QLabel(self)
                image_label.setPixmap(img)
                image_label.move(0, 0)
                layout.addWidget(image_label)    
                
        else:
            image_label = QLabel(self)
            image_label.setPixmap(image)
            image_label.move(0, 0)
            layout.addWidget(image_label)
            

        layout.addWidget(text_label)
        text_label.move(0, 0)

        self.setLayout(layout)