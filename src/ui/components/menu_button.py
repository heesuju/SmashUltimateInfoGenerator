from typing import Union
from PyQt6.QtWidgets import QWidget, QPushButton, QSizePolicy
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtCore import QSize, QRect, Qt, QEvent
from src.utils.image_utils import tint_pixmap

ICON_SIZE = 32

class MenuButton(QPushButton):
    def __init__(self, icon:Union[str, QIcon, QPixmap], width:int, height:int, parent=None):
        self._original_pixmap = None
        icon_ref = None
        
        if isinstance(icon, str):
            self._original_pixmap = QPixmap(icon)
            icon_ref = QIcon(self._original_pixmap)
        elif isinstance(icon, QPixmap):
            self._original_pixmap = icon
            icon_ref = QIcon(icon)
        elif isinstance(icon, QIcon):
            icon_ref = icon
            self._original_pixmap = icon.pixmap(ICON_SIZE, ICON_SIZE)
        
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

        # Initial Color Update
        self.update_icon_color()
        self.toggled.connect(self._update_icon_state)

    def set_progress(self, value: float):
        """Set progress value (0.0 to 1.0). -1 to disable."""
        self.progress = value
        self._update_icon_state()
        self.update()

    def changeEvent(self, event):
        if event.type() == QEvent.Type.PaletteChange or event.type() == QEvent.Type.StyleChange:
            self.update_icon_color()
        super().changeEvent(event)
    
    def enterEvent(self, event):
        self._update_icon_state(hover=True)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self._update_icon_state(hover=False)
        super().leaveEvent(event)
        
    def _update_icon_state(self, hover=None):
        if self.progress >= 0:
            self.setIcon(QIcon())
            return

        is_hover = hover if hover is not None else self.underMouse()
        
        if self.isChecked() or is_hover:
            if hasattr(self, '_full_icon'):
                self.setIcon(self._full_icon)
        else:
            if hasattr(self, '_dim_icon'):
                self.setIcon(self._dim_icon)

    def update_icon_color(self):
        if self._original_pixmap and not self._original_pixmap.isNull():
            text_color = self.palette().text().color()
            
            full_pixmap = tint_pixmap(self._original_pixmap, text_color)
            
            dim_color = QColor(text_color)
            dim_color.setAlpha(100) # ~40% opacity
            dim_pixmap = tint_pixmap(self._original_pixmap, dim_color)
            
            self._full_icon = QIcon(full_pixmap)
            self._dim_icon = QIcon(dim_pixmap)
            
            self._update_icon_state()

    def set_status_color(self, color: QColor):
        """Set a status indicator color. Pass None to remove."""
        self.status_color = color
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        
        # Draw Progress Overlay if active
        if self.progress >= 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            if hasattr(self, '_dim_icon') and not self._dim_icon.isNull():
                bg_icon = self._dim_icon
            else:
                bg_icon = QIcon(self._original_pixmap) if self._original_pixmap else QIcon()

            if bg_icon.isNull():
                return
                
            icon_size = ICON_SIZE
            
            rect = self.contentsRect()
            x = rect.x() + (rect.width() - icon_size) // 2
            y = rect.y() + (rect.height() - icon_size) // 2
            
            # Draw dimmed background manually
            bg_pixmap = bg_icon.pixmap(icon_size, icon_size)
            painter.drawPixmap(x, y, bg_pixmap)
            
            # Create a green version of the pixmap for the fill
            # We use the FULL strength icon source for the fill color mask if available, or just the current
            if hasattr(self, '_full_icon') and not self._full_icon.isNull():
                fill_source = self._full_icon.pixmap(icon_size, icon_size)
            else:
                fill_source = bg_pixmap

            colored = QPixmap(fill_source.size())
            colored.fill(Qt.GlobalColor.transparent)
            
            p = QPainter(colored)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.drawPixmap(0, 0, fill_source)
            p.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
            p.fillRect(colored.rect(), QColor("#4CAF50")) # Green fill for progress
            p.end()
            
            padding = 4
            available_h = icon_size - (padding * 2)
            
            # Clamp progress
            prog = min(1.0, max(0.0, self.progress))
            
            fill_height = int(available_h * prog)
            fill_top = (icon_size - padding) - fill_height
            
            # Clip Rect in Widget Coordinates
            clip_y = y + fill_top
            clip_h = icon_size - fill_top 
            
            painter.setClipRect(x, clip_y, icon_size, clip_h)
            painter.drawPixmap(x, y, colored)
            painter.end()
            
        # Draw Status Indicator Circle if active (and not progressing)
        elif hasattr(self, 'status_color') and self.status_color:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            indicator_size = 8
            rect = self.contentsRect()
             # Position close to icon bottom right
            icon_rect_x = rect.x() + (rect.width() - ICON_SIZE) // 2
            icon_rect_y = rect.y() + (rect.height() - ICON_SIZE) // 2
            
            # Draw at bottom right of icon area
            x = icon_rect_x + ICON_SIZE - indicator_size + 2
            y = icon_rect_y + ICON_SIZE - indicator_size + 2
            
            painter.setBrush(self.status_color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(x, y, indicator_size, indicator_size)
            painter.end()