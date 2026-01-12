from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QToolButton
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QFont


class CollapsibleSection(QWidget):
    """A collapsible section widget with a disclosure triangle header."""
    
    def __init__(self, title: str = "", font_name: str = "Arial", font_size: int = 10, 
                 expanded: bool = True, parent=None):
        super().__init__(parent)
        
        self.title = title
        self.is_expanded = expanded
        self._status_text = ""
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header section (clickable)
        self.header = QWidget()
        self.header.setCursor(Qt.CursorShape.PointingHandCursor)
        self.header.mousePressEvent = self.toggle
        
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(0, 5, 0, 5)
        header_layout.setSpacing(5)
        
        # Disclosure triangle
        self.toggle_button = QToolButton()
        self.toggle_button.setStyleSheet("""
            QToolButton {
                border: none;
                background: transparent;
            }
        """)
        self.toggle_button.setArrowType(Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow)
        self.toggle_button.setFixedSize(16, 16)
        self.toggle_button.clicked.connect(self.toggle)
        header_layout.addWidget(self.toggle_button)
        
        # Title label
        self.title_label = QLabel(title)
        title_font = QFont(font_name, font_size)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        header_layout.addWidget(self.title_label)
        
        # Status label (optional, for showing active filter count)
        self.status_label = QLabel()
        status_font = QFont(font_name, font_size - 1)
        self.status_label.setFont(status_font)
        self.status_label.setStyleSheet("color: #888;")
        header_layout.addWidget(self.status_label)
        
        header_layout.addStretch()
        
        main_layout.addWidget(self.header)
        
        # Content container
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 5, 0, 10)
        self.content_layout.setSpacing(5)
        
        main_layout.addWidget(self.content_widget)
        
        # Set initial state without animation
        if not expanded:
            self.content_widget.setMaximumHeight(0)
            self.content_widget.setVisible(False)
    
    def add_widget(self, widget: QWidget):
        """Add a widget to the collapsible content area."""
        self.content_layout.addWidget(widget)
    
    def add_layout(self, layout):
        """Add a layout to the collapsible content area."""
        self.content_layout.addLayout(layout)
    
    def add_stretch(self, stretch: int = 1):
        """Add stretch to the collapsible content area."""
        self.content_layout.addStretch(stretch)
    
    def set_status(self, text: str):
        """Set the status text shown next to the title (e.g., '5 active')."""
        self._status_text = text
        self.status_label.setText(f"({text})" if text else "")
    
    def toggle(self, event=None):
        """Toggle the collapsed/expanded state."""
        self.is_expanded = not self.is_expanded
        
        # Update arrow direction
        if self.is_expanded:
            self.toggle_button.setArrowType(Qt.ArrowType.DownArrow)
        else:
            self.toggle_button.setArrowType(Qt.ArrowType.RightArrow)
        
        # Animate the content widget
        if self.is_expanded:
            self.content_widget.setVisible(True)
            self.content_widget.setMaximumHeight(16777215)  # Remove max height constraint
        else:
            self.content_widget.setMaximumHeight(0)
            self.content_widget.setVisible(False)
    
    def set_expanded(self, expanded: bool):
        """Programmatically set the expanded state."""
        if self.is_expanded != expanded:
            self.toggle()
