import os
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QFrame, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize, QUrl
from PyQt6.QtGui import QPixmap, QColor, QPalette, QIcon, QFont, QDesktopServices
from datetime import datetime
from src.ui.grid_item import GridListItem, GridListItemWidget
from src.models.mod import OnlineModItem, ModItem
from src.ui.components.layout import HBox, VBox
from src.ui.grid_item_button import Overlay
from src.utils.image_loader import ImageLoader
from src.managers.data_manager import ButtonIcons
from src.ui.components.toggle_button import ToggleButton

class OnlineGridListItem(GridListItem):
    def __init__(self, parent, mod: OnlineModItem, height:int=80, grid_list=None):
        super(GridListItem, self).__init__() 
        
        self.parent = parent
        self.mod = mod
        
        self.widget = OnlineGridListItemWidget(self.mod, height, grid_list=grid_list)
        self.setSizeHint(QSize(350, 110))
        
        parent.addItem(self)
        parent.setItemWidget(self, self.widget)

class OnlineGridListItemWidget(GridListItemWidget):
    def __init__(self, mod: OnlineModItem, height:int=80, grid_list=None):
        QWidget.__init__(self)
        
        self.mod = mod
        self.grid_list = grid_list
        self.image_path = mod.thumbnail
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.frame = QFrame()
        self.frame.setObjectName("gridItemFrame") 
        self.frame.setFrameShape(QFrame.Shape.NoFrame)
        self.frame.setAutoFillBackground(True)
        frame_layout = HBox(margin=4, spacing=4)
        self.frame.setLayout(frame_layout)
        
        palette = self.frame.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
        self.frame.setPalette(palette)
        
        # Thumbnail Handling
        is_url = self.image_path.startswith("http")
        initial_path = self.image_path if not is_url else ""
        overlay = Overlay(initial_path, self)
        self.overlay = overlay # Scanpy reference
        frame_layout.addWidget(overlay)
        
        # Async download
        if is_url:
            ImageLoader().load_image(self.image_path, self.access_overlay_image)
        
        # Info Column
        info_layout = QVBoxLayout()
        # Right Column
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Actions Row (Fav/Hide/Menu)
        action_layout = HBox()
        action_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        frame_layout.addLayout(info_layout)
        frame_layout.addStretch(1)

        frame_layout.addLayout(right_layout)
        right_layout.addLayout(action_layout)
        
        frame_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # -- Info Content --
        info_layout.addStretch(1)
        
        # Name
        line_text = QLabel(mod.name)
        line_text.setAlignment(Qt.AlignmentFlag.AlignLeft)
        info_layout.addWidget(line_text)
        
        # Author
        author_text = QLabel(mod.authors)
        author_text.setStyleSheet("color: #666;")
        author_text.setAlignment(Qt.AlignmentFlag.AlignLeft)
        info_layout.addWidget(author_text)
        
        # Stats Row (New!)
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(10)
        stats_layout.setContentsMargins(0, 2, 0, 0)
        stats_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Helper to create stat label with icon (or just text for now to keep it simple)
        # Icons would be nice but let's stick to text: "❤ 418  💬 64  👁 192k"
        
        def format_count(n):
            if n >= 1000:
                return f"{n/1000:.1f}k"
            return str(n)
            
        likes_label = QLabel(f"❤ {format_count(mod.like_count)}")
        likes_label.setStyleSheet("color: #ff5555; font-size: 11px;") # Red for heart
        
        posts_label = QLabel(f"💬 {format_count(mod.post_count)}")
        posts_label.setStyleSheet("color: #888; font-size: 11px;")
        
        views_label = QLabel(f"👁 {format_count(mod.view_count)}")
        views_label.setStyleSheet("color: #888; font-size: 11px;")
        
        stats_layout.addWidget(likes_label)
        stats_layout.addWidget(posts_label)
        stats_layout.addWidget(views_label)
        stats_layout.addStretch(1)
        
        info_layout.addLayout(stats_layout)
        
        # Helper for relative time
        def get_relative_time(timestamp: int) -> str:
            if not timestamp: return ""
            dt = datetime.fromtimestamp(timestamp)
            now = datetime.now()
            diff = now - dt
            days = diff.days
            if days < 0: return "Just now"
            if days == 0: return "Today"
            if days == 1: return "Yesterday"
            if days < 7: return f"{days} days ago"
            weeks = days // 7
            if weeks < 4: return f"{weeks} week{'s' if weeks > 1 else ''} ago"
            months = days // 30
            if months < 12: return f"{months} month{'s' if months > 1 else ''} ago"
            years = days // 365
            return f"{years} year{'s' if years > 1 else ''} ago"

        # Date Updated (New Row)
        if mod.date_updated:
            rel_date = get_relative_time(mod.date_updated)
            date_label = QLabel(rel_date)
            date_label.setStyleSheet("color: #aaa; font-size: 10px;")
            date_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            # Add to info_layout directly, below stats
            info_layout.addWidget(date_label)

        info_layout.setContentsMargins(0,0,0,0)
        info_layout.setSpacing(0) # Reduce spacing
        info_layout.addStretch(1)

        # -- Actions Content --
        # Browser Button
        self.browser_button = QPushButton()
        self.browser_button.setIcon(QIcon("assets/icons/buttons/web_16.svg"))
        self.browser_button.setFlat(True)
        self.browser_button.setFixedSize(24, 24)
        self.browser_button.clicked.connect(self.open_url)
        self.browser_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        action_layout.addWidget(self.browser_button)

        # Menu Button
        menu_button = QPushButton()
        menu_button.setIcon(QIcon(QPixmap(ButtonIcons.MENU.value)))
        menu_button.setFlat(True)
        menu_button.setFixedSize(QSize(24, 24))
        action_layout.addWidget(menu_button)
        
        right_layout.addStretch(1)
        
        # Version (Bottom Right)
        if mod.version:
            ver_label = QLabel(f"v{mod.version}")
            ver_label.setStyleSheet("color: #888; font-size: 10px; font-weight: bold;")
            ver_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            right_layout.addWidget(ver_label)
            
        # Initial style
        self.update_selection_style()
        
        layout.addWidget(self.frame)

    def update_selection_style(self):
        """Update the frame shadow to show selection state"""
        shadow = QGraphicsDropShadowEffect()
        
        if self.mod.selected:
            # Selected: Blue glowing shadow (no border)
            shadow.setBlurRadius(25)
            shadow.setOffset(0, 0)
            shadow.setColor(QColor(74, 144, 226, 220))
            
            self.frame.setStyleSheet("""
                QFrame#gridItemFrame {
                    border: none;
                    border-radius: 4px;
                }
            """)
        else:
            # Not selected: Subtle gray shadow
            shadow.setBlurRadius(10)
            shadow.setOffset(2, 2)
            shadow.setColor(QColor(0, 0, 0, 160))
            
            self.frame.setStyleSheet("""
                QFrame#gridItemFrame {
                    border: none;
                    border-radius: 4px;
                }
            """)
        
        self.frame.setGraphicsEffect(shadow)

    def mousePressEvent(self, event):
        from PyQt6.QtCore import Qt
        
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if self.grid_list and hasattr(self.grid_list, 'mod_manager'):
                manager = self.grid_list.mod_manager
                if hasattr(manager, 'toggle_selection'):
                    manager.toggle_selection(self.mod.id)
                    self.mod.selected = manager.is_selected(self.mod.id)
                    self.update_selection_style()
            return
        
        if self.grid_list and hasattr(self.grid_list, 'mod_manager'):
            manager = self.grid_list.mod_manager
            if hasattr(manager, 'set_focus'):
                print(f"[OnlineGridItem] Calling manager.set_focus({self.mod.id})")
                manager.set_focus(self.mod.id)
        
        super().mousePressEvent(event)

    def open_url(self):
        if self.mod.url:
            QDesktopServices.openUrl(QUrl(self.mod.url))

    def access_overlay_image(self, local_path):
        """Callback for ImageLoader"""
        if local_path and os.path.exists(local_path):
            self.overlay.update_image(local_path)

