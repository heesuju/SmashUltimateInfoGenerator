from PyQt6.QtWidgets import (
    QWidget, 
    QHBoxLayout, 
    QLabel, 
    QSizePolicy, 
    QFrame,
    QScrollArea,
    QPushButton,
    QScrollBar
)
from PyQt6.QtCore import Qt, QSize, QPoint, QPointF, QEvent
from PyQt6.QtGui import QFont, QIcon, QPixmap
from src.ui.components.layout import VBox, HBox
from src.constants.styles import MAIN_BUTTON, DANGER_BUTTON, SECONDARY_BUTTON

FONT = "Arial"
FONT_SIZE = 10
BODY_FONT_SIZE = 8

class SidePanel(QWidget):
    def __init__(self, title:str):
        super().__init__()
        self.width = 340
        layout = VBox()
        self.setLayout(layout)
        self.setFixedWidth(self.width)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        
        self.frame = QFrame()
        self.frame.setFrameShape(QFrame.Shape.NoFrame)
        self.frame.setAutoFillBackground(True)
        self.root = VBox(margin=0, spacing=10)
        self.frame.setLayout(self.root)

        self.header = HBox(margin=(10, 10, 10, 0), spacing=10)
        self.root.addLayout(self.header)
        
        # Standard Title Label
        if title:
            self.title_label = QLabel(title)
            title_font = QFont(FONT, 10) # Slightly larger for header
            title_font.setBold(True)
            self.title_label.setFont(title_font)
            # Add to header
            self.header.addWidget(self.title_label)
        else:
             self.title_label = None

        spacer = QWidget()
        spacer.setFixedSize(0, 26)
        self.header.addWidget(spacer)

        self.scroll = QScrollArea()
        self.scroll.setStyleSheet("""
            QScrollArea { 
                border: none; 
            }
        """)
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.root.addWidget(self.scroll, stretch=1)

        self.body_frame = QFrame()
        self.body_frame.setStyleSheet("QFrame { border: 0px; }")
        self.body_frame.setContentsMargins(0,0,0,0)
        self.body_frame.setFrameShape(QFrame.Shape.NoFrame)
        self.body = VBox(margin=(10, 0, 10, 10), spacing=10)
        self.body_frame.setLayout(self.body)
        self.scroll.setWidget(self.body_frame)
        
        # Custom Overlay ScrollBar
        self.scroll_bar = QScrollBar(Qt.Orientation.Vertical, self.scroll)
        self.scroll_bar.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.2);
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.3);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        self.scroll_bar.hide()
        
        # Sync external scrollbar with internal one
        vbar = self.scroll.verticalScrollBar()
        vbar.rangeChanged.connect(self.update_scroll_bar)
        vbar.valueChanged.connect(self.scroll_bar.setValue)
        self.scroll_bar.valueChanged.connect(vbar.setValue)
        
        self.scroll.installEventFilter(self)

        self.footer = QHBoxLayout()
        self.footer.setContentsMargins(10, 0, 10, 10)
        self.footer.setSpacing(10)
        self.root.addLayout(self.footer)

        layout.addWidget(self.frame)

    def eventFilter(self, obj, event):
        if obj == self.scroll and event.type() == QEvent.Type.Resize:
            self.update_scroll_layout()
        return super().eventFilter(obj, event)

    def update_scroll_bar(self, min_val, max_val):
        self.scroll_bar.setMinimum(min_val)
        self.scroll_bar.setMaximum(max_val)
        self.scroll_bar.setPageStep(self.scroll.verticalScrollBar().pageStep())
        self.scroll_bar.setVisible(max_val > min_val)
        
    def update_scroll_layout(self):
        w = 10 # Width of scrollbar
        self.scroll_bar.setGeometry(self.scroll.width() - w, 0, w, self.scroll.height())

    def add_footer_button(self, text: str, callback, primary: bool = False, danger: bool = False, icon: str = None) -> QPushButton:
        """Add a consistent button to the footer"""
        btn = QPushButton(text)
        if icon:
            if isinstance(icon, str):
                btn.setIcon(QIcon(QPixmap(icon)))
            else:
                btn.setIcon(icon)
            
        if primary:
            btn.setStyleSheet(MAIN_BUTTON)
        elif danger:
            btn.setStyleSheet(DANGER_BUTTON)
        else:
            btn.setStyleSheet(SECONDARY_BUTTON)
            
        btn.setFixedHeight(26)
        btn.clicked.connect(callback)
        self.footer.addWidget(btn)
        return btn