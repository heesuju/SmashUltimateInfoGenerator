import os
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QFrame, QSizePolicy, QGraphicsDropShadowEffect, QMenu
)
from PyQt6.QtCore import Qt, QSize, QUrl, QPoint
from PyQt6.QtGui import QPixmap, QColor, QPalette, QIcon, QFont, QDesktopServices, QAction
from datetime import datetime

from src.models.mod import OnlineModItem, ModItem
from src.managers.data_manager import ButtonIcons

from src.ui.components.grid_item import GridListItem, GridListItemWidget
from src.ui.components.layout import HBox, VBox
from src.ui.components.grid_item_button import Overlay
from src.ui.components.toggle_button import ToggleButton

from src.utils.image_loader import ImageLoader
from src.utils.image_utils import tint_pixmap
from src.constants.colors import ButtonColor

class OnlineGridListItem(GridListItem):
    def __init__(self, parent, mod: OnlineModItem, height:int=80, grid_list=None, online_manager=None, download_manager=None):
        super(GridListItem, self).__init__() 
        
        self.parent = parent
        self.mod = mod
        
        self.widget = OnlineGridListItemWidget(self.mod, height, grid_list=grid_list, online_manager=online_manager, download_manager=download_manager)
        self.setSizeHint(QSize(350, 110))
        
        parent.addItem(self)
        parent.setItemWidget(self, self.widget)

class OnlineGridListItemWidget(GridListItemWidget):
    def __init__(self, mod: OnlineModItem, height:int=80, grid_list=None, online_manager=None, download_manager=None):
        QWidget.__init__(self)
        
        self.mod = mod
        self.grid_list = grid_list
        self.online_manager = online_manager
        self.download_manager = download_manager
        self.image_path = mod.thumbnail
        self.mod_details = {}
        self.pending_download = False
        
        if self.online_manager:
            self.online_manager.mod_details_ready.connect(self.on_mod_details_ready)
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
        
        has_thumbnail = bool(initial_path and os.path.exists(initial_path) and os.path.isfile(initial_path))
        category = mod.category if mod.category else "Misc"
        
        download_icon_path = ButtonIcons.DOWNLOAD_OVERLAY.value
        
        overlay = Overlay(
            initial_path, 
            self, 
            category=category, 
            has_thumbnail=has_thumbnail, 
            overlay_mode="action",
            hover_icon=download_icon_path,
            on_toggle_callback=self.on_download_clicked
        )
        self.overlay = overlay # Scanpy reference
        frame_layout.addWidget(overlay)
        
        # Async download
        if is_url:
            try:
                ImageLoader.instance().load_image(self.image_path, self.access_overlay_image, widget=self)
            except Exception as e:
                print(f"Failed to load image: {e}")
        
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
        self.browser_button = QPushButton()
        web_pixmap = tint_pixmap(QPixmap(ButtonIcons.WEB.value), QColor(ButtonColor.CYAN.value))
        self.browser_button.setIcon(QIcon(web_pixmap))
        self.browser_button.setFlat(True)
        self.browser_button.setFixedSize(24, 24)
        self.browser_button.clicked.connect(self.open_url)
        self.browser_button.setCursor(Qt.CursorShape.PointingHandCursor)
        action_layout.addWidget(self.browser_button)

        self.download_button = QPushButton()
        download_pixmap = tint_pixmap(QPixmap(ButtonIcons.DOWNLOAD.value), QColor(ButtonColor.GREEN.value))
        self.download_button.setIcon(QIcon(download_pixmap))
        self.download_button.setFlat(True)
        self.download_button.setFixedSize(24, 24)
        self.download_button.clicked.connect(self.on_download_clicked)
        self.download_button.setCursor(Qt.CursorShape.PointingHandCursor)
        action_layout.addWidget(self.download_button)
        
        right_layout.addStretch(1)
        
        # Version (Bottom Right)
        if mod.version:
            ver_label = QLabel(str(mod.version))
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
    
    def on_mod_details_ready(self, details: dict):
        """Cache mod details when received from OnlineManager"""
        details_mod_id = details.get("_mod_id", "")
        if details_mod_id != self.mod.id:
            return
        
        if self.online_manager:
            is_focused = self.online_manager.focused_id == self.mod.id
            is_pending = self.pending_download
            
            if is_focused or is_pending:
                self.mod_details = details
        
                if self.pending_download:
                    self.pending_download = False
                    self._execute_download()
    
    def on_download_clicked(self):
        """Handle download button click"""
        if not self.mod_details:
            # Request details and queue download
            if self.online_manager:
                self.pending_download = True
                self.online_manager.set_focus(self.mod.id)
            return
        
        self._execute_download()
    
    def _execute_download(self):
        """Execute the download with cached mod details"""
        if not self.download_manager:
            # Fallback to opening URL in browser
            if self.mod.url:
                QDesktopServices.openUrl(QUrl(self.mod.url))
            return
        
        files = self.mod_details.get("files", [])
        
        if not files:
            print("No files to download")
            return
        
        if len(files) == 1:
            # Single file - download directly
            self.download_file(files[0]["url"], files[0].get("name"))
        else:
            # Multiple files - show menu
            menu = QMenu(self)
            
            for file_data in files:
                name = file_data.get("name", "Unknown")
                desc = file_data.get("description", "")
                label = f"{name}"
                if desc:
                    label += f" - {desc}"
                
                action = QAction(label, self)
                # Use closure to capture loop variable
                action.triggered.connect(lambda checked, url=file_data["url"], fname=name: self.download_file(url, fname))
                menu.addAction(action)
            
            menu.addSeparator()
            
            download_all = QAction("Download All", self)
            download_all.triggered.connect(lambda: self.download_all_files(files))
            menu.addAction(download_all)
            
            # Show menu below button
            menu.exec(self.download_button.mapToGlobal(QPoint(0, self.download_button.height())))
    
    def download_file(self, url: str, filename: str = None):
        """Download a single file"""
        if not self.download_manager:
            return
        
        # Extract filename from URL if not provided
        if not filename:
            filename = url.split("/")[-1]
            if "?" in filename:
                filename = filename.split("?")[0]
        if not filename:
            filename = "download.zip"
        
        # Get mod name from details
        mod_name = self.mod_details.get("mod_name", self.mod.name)
        
        self.download_manager.start_download(url, filename, mod_name, self.mod.id, self.mod_details)
    
    def download_all_files(self, files: list):
        """Download all files"""
        print(f"Downloading {len(files)} files")
        for f in files:
            if f.get("url"):
                self.download_file(f.get("url"), f.get("name"))

