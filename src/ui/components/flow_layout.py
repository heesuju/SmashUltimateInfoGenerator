from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class FlowLayout(QWidget):
    """A layout that arranges widgets in a flowing left-to-right, top-to-bottom manner"""
    
    def __init__(self, parent=None, margin=0, spacing=5):
        super().__init__(parent)
        self.margin = margin
        self.spacing = spacing
        self.items = []
        self.setContentsMargins(margin, margin, margin, margin)
    
    def add_widget(self, widget):
        """Add a widget to the flow layout"""
        self.items.append(widget)
        widget.setParent(self)
        self.update_layout()
    
    def clear(self):
        """Remove all widgets from the layout"""
        for item in self.items:
            item.deleteLater()
        self.items.clear()
        self.update_layout()
    
    def update_layout(self):
        """Recalculate and apply the layout"""
        if not self.items:
            self.setMinimumHeight(0)
            return
        
        x = self.margin
        y = self.margin
        line_height = 0
        
        width = self.width()
        
        for widget in self.items:
            widget.show()
            widget_width = widget.sizeHint().width()
            widget_height = widget.sizeHint().height()
            
            # Check if we need to wrap to next line
            if x + widget_width > width - self.margin and x > self.margin:
                x = self.margin
                y += line_height + self.spacing
                line_height = 0
            
            # Position the widget
            widget.move(x, y)
            
            # Update position for next widget
            x += widget_width + self.spacing
            line_height = max(line_height, widget_height)
        
        # Set minimum height to fit all widgets
        self.setMinimumHeight(y + line_height + self.margin)
    
    def resizeEvent(self, event):
        """Recalculate layout when widget is resized"""
        super().resizeEvent(event)
        self.update_layout()


class ElementTag(QLabel):
    """A styled tag/badge widget for displaying individual elements"""
    
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        
        # Styling
        self.setFont(QFont("Arial", 8))
        self.setStyleSheet("""
            QLabel {
                background-color: rgba(100, 150, 255, 0.2);
                border: 1px solid rgba(100, 150, 255, 0.5);
                border-radius: 10px;
                padding: 4px 10px;
                color: #5a9fff;
                font-weight: bold;
            }
        """)
        
        # Size policy
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.adjustSize()
