from typing import Union
from PyQt6.QtWidgets import QWidget, QPushButton, QSizePolicy
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtCore import QSize, QRect, Qt

ICON_SIZE = 32

class MenuButton(QPushButton):
    def __init__(self, icon:Union[str, QIcon, QPixmap], width:int, height:int, parent=None):
        icon_ref = None
        if isinstance(icon, str):
            pixmap = QPixmap(icon)
            icon_ref = QIcon(pixmap)
        elif isinstance(icon, QPixmap):
            icon_ref = QIcon(icon)
        elif isinstance(icon, QIcon):
            icon_ref = icon
        
        super().__init__(parent)
        self.setIcon(icon_ref)

        self.setFixedSize(width, height)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
        self.setFlat(False)
        self.setCheckable(True)
        self.progress = -1.0
        
        # Theme-aware styling with selected state
        self.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.15);
            }
            QPushButton:checked {
                background-color: rgba(100, 150, 255, 0.3);
                border-left: 3px solid #6496FF;
            }
            QPushButton:checked:hover {
                background-color: rgba(100, 150, 255, 0.4);
            }
        """)

    def set_progress(self, value: float):
        """Set progress value (0.0 to 1.0). -1 to disable."""
        self.progress = value
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        
        if self.progress >= 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Get the current icon pixmap
            icon = self.icon()
            if icon.isNull():
                return
                
            icon_size = ICON_SIZE
            pixmap = icon.pixmap(icon_size, icon_size)
            
            # Create a colored version of the pixmap
            colored = QPixmap(pixmap.size())
            colored.fill(Qt.GlobalColor.transparent)
            
            p = QPainter(colored)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.drawPixmap(0, 0, pixmap)
            p.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
            p.fillRect(colored.rect(), QColor("#4CAF50")) # Green fill
            p.end()
            
            # Calculate centering
            x = (self.width() - icon_size) // 2
            y = (self.height() - icon_size) // 2
            
            # Clip Region
            progress_h = int(icon_size * min(1.0, max(0.0, self.progress)))
            clip_y = y + (icon_size - progress_h)
            
            painter.setClipRect(x, clip_y, icon_size, progress_h)
            painter.drawPixmap(x, y, colored)
            painter.end()