from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush

class LoadingSpinner(QWidget):
    def __init__(self, parent=None, size=40):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.timer.start(16)  # ~60 FPS

    def rotate(self):
        self.angle = (self.angle + 8) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center = QPointF(self.rect().center())
        radius = min(self.width(), self.height()) / 2 - 4
        
        # Draw track
        pen_track = QPen(QColor(255, 255, 255, 30))
        pen_track.setWidth(4)
        pen_track.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_track)
        painter.drawEllipse(center, radius, radius)
        
        # Draw spinner
        pen = QPen(QColor(100, 180, 255))
        pen.setWidth(4)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        # Draw arc
        rect = QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2)
        start_angle = -self.angle * 16
        span_angle = -100 * 16 # Fixed span for now
        painter.drawArc(rect, start_angle, span_angle)

class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False) # Block mouse events
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        self.setLayout(layout)
        
        # Spinner
        self.spinner = LoadingSpinner(size=48)
        layout.addWidget(self.spinner, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Loading Text
        self.label = QLabel("Loading...")
        self.label.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
                font-weight: 500;
                background-color: transparent;
                letter-spacing: 0.5px;
            }
        """)
        layout.addWidget(self.label, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Fade effect
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)
        
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.fade_in)
        self.current_opacity = 0
        
        self.hide()

    def paintEvent(self, event):
        # Draw semi-transparent background
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 180))

    def show_loading(self):
        if self.parent():
            self.resize(self.parent().size())
        self.raise_()
        self.show()
        self.current_opacity = 0
        self.opacity_effect.setOpacity(0)
        self.animation_timer.start(16)
        
    def hide_loading(self):
        self.hide()
        self.animation_timer.stop()
        
    def fade_in(self):
        self.current_opacity += 0.1
        if self.current_opacity >= 1.0:
            self.current_opacity = 1.0
            self.animation_timer.stop()
        self.opacity_effect.setOpacity(self.current_opacity)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Ensure it always covers parent
        if self.parent():
            self.resize(self.parent().size())
