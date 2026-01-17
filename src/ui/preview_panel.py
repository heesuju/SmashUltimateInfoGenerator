from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QSizePolicy, QLabel, QFrame, QHBoxLayout, QPushButton,
    QMenu
)
from PyQt6.QtGui import QPixmap, QColor, QPalette, QIcon, QFont, QAction, QDesktopServices
from PyQt6.QtCore import Qt, QSize, QPoint, QPointF, pyqtSignal, QUrl
from src.ui.components.layout import HBox, VBox
from src.ui.components.side_panel import SidePanel
from src.ui.components.thumbnail_label import ThumbnailLabel
from src.ui.components.toggle_button import ToggleButton
from src.ui.components.flow_layout import FlowLayout, ElementTag
from src.managers.mod_manager import ModManager
from src.managers.data_manager import DataManager, ButtonIcons
from src.utils.file import open_folder
from src.constants.ui_params import BODY_FONT, BODY_FONT_SIZE, TITLE_FONT, TITLE_FONT_SIZE

class PreviewPanel(SidePanel):
    edit_requested = pyqtSignal(str)  # Emits mod_id when edit is requested
    
    def __init__(self, mod_manager:ModManager, online_manager=None, download_manager=None):
        super().__init__("Preview")
        self.mod_manager = mod_manager
        self.online_manager = online_manager
        self.download_manager = download_manager
        self.is_online_mode = False
        self.current_online_details = {} # Cache for online mod details
        
        self.mod_manager.add_focus_callback(self.set_data)
        self.mod_manager.add_favorite_callback(self.on_favorite_changed)
        self.mod_manager.add_hidden_callback(self.on_hidden_changed)
        
        if self.online_manager:
            self.online_manager.add_focus_callback(self.set_online_data)
            self.online_manager.mod_details_ready.connect(self.update_online_details)

        self.header.addStretch()
        self.fav_button = ToggleButton(ButtonIcons.FAV_ON.value, ButtonIcons.FAV_OFF.value, self.on_fav_on, self.on_fav_off, 24)
        self.header.addWidget(self.fav_button)
        
        self.hide_button = ToggleButton(ButtonIcons.HIDE_ON.value, ButtonIcons.HIDE_OFF.value, self.on_vis_off, self.on_vis_on, 24)
        self.header.addWidget(self.hide_button)

        web_button = QPushButton()
        web_button.setIcon(QIcon(ButtonIcons.WEB.value))
        web_button.setFlat(True)
        web_button.setObjectName("obj")
        web_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        web_button.setFixedSize(QSize(24, 24))
        web_button.clicked.connect(self.open_web_page)
        self.header.addWidget(web_button)
        self.web_button = web_button

        menu_button = QPushButton()
        menu_button.setIcon(QIcon(QPixmap(ButtonIcons.MENU.value)))
        menu_button.setFlat(True)
        menu_button.setObjectName("obj")
        menu_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        menu_button.setFixedSize(QSize(24, 24))
        menu_button.clicked.connect(self.show_context_menu)
        self.header.addWidget(menu_button)
        self.menu_button = menu_button
        
        
        
        self.thumbnail = ThumbnailLabel()
        self.body.addWidget(self.thumbnail)

        # Author and Version on same row
        info_layout = QHBoxLayout()
        self.body.addLayout(info_layout)
        
        body_font = QFont(BODY_FONT, BODY_FONT_SIZE)
        
        self.author = QLabel("")
        self.author.setFont(body_font)
        info_layout.addWidget(self.author)
        
        info_layout.addStretch(1)
        
        self.version = QLabel("1.0.0")
        self.version.setFont(body_font)
        info_layout.addWidget(self.version)

        self.elements_container = FlowLayout(spacing=5)
        self.body.addWidget(self.elements_container)

        self.description_label = QLabel("")
        self.description_label.setWordWrap(True)
        self.description_label.setFont(QFont(BODY_FONT, BODY_FONT_SIZE))
        self.body.addWidget(self.description_label)        
        
        self.body.addStretch(1)

        self.open_btn = self.add_footer_button("Open", self.on_open_clicked)
        self.edit_btn = self.add_footer_button("Edit", self.on_edit_clicked)
        self.enable_btn = self.add_footer_button("Enable", self.on_enabled, primary=True)
        self.download_btn = self.add_footer_button("Download", self.on_download_clicked, primary=True)
        self.download_btn.hide()

    def set_online_data(self, id:str):
        """Handle online mod selection - show basic info immediately"""
        self.is_online_mode = True
        self.current_online_details = {} # Reset cache
        
        # Toggle buttons
        self.open_btn.hide()
        self.edit_btn.hide()
        self.enable_btn.hide()
        self.download_btn.show()
        # Disable download until details loaded
        self.download_btn.setEnabled(False)
        self.download_btn.setText("Loading...")
        
        mod = self.online_manager.get_mod(id)
        if not mod:
            return
            
        self.fav_button.hide()
        self.hide_button.hide()
        
        if self.title_label:
            self.title_label.setText(mod.name)
            
        self.thumbnail.set_thumbnail(mod.thumbnail)
        self.author.setText(mod.authors)
        self.version.setText(mod.version)
        self.description_label.setText("Loading details...")
        
        self.elements_container.clear()
        
        if mod.url and mod.url.startswith("http"):
            self.web_button.setEnabled(True)
            self.web_button.setToolTip(mod.url)
        else:
            self.web_button.setEnabled(False)

    def update_online_details(self, details:dict):
        """Update preview with full details from API"""
        if not self.is_online_mode:
            return
            
        self.current_online_details = details
        self.download_btn.setEnabled(True)
        self.download_btn.setText("Download")

        description = details.get('description', '')
        if description:
            self.description_label.setText(description)
        
        self.elements_container.clear()
        
        if details.get('is_wifi_safe'):
            wifi_tag = ElementTag("Wifi-Safe")
            self.elements_container.add_widget(wifi_tag)
        
        if details.get('is_moveset'):
            tag = ElementTag("Moveset")
            self.elements_container.add_widget(tag)
            
        if details.get('is_final_smash'):
            tag = ElementTag("Final Smash")
            self.elements_container.add_widget(tag)

    def set_data(self, id:str):
        """Handle installed mod selection"""
        self.is_online_mode = False
        # Toggle buttons
        self.open_btn.show()
        self.edit_btn.show()
        self.enable_btn.show()
        self.download_btn.hide()
        
        mod = self.mod_manager.get_mod(id)
        self.fav_button.show()
        self.hide_button.show()
        self.fav_button.set_state(str(mod.hash) in self.mod_manager.favorite_ids)
        self.hide_button.set_state(str(mod.hash) in self.mod_manager.hidden_ids)
        
        if self.title_label:
            self.title_label.setText(mod.mod_name)
            
        self.thumbnail.set_thumbnail(mod.thumbnail)
        self.author.setText(mod.authors)
        self.version.setText(mod.version)
        self.description_label.setText(mod.description)
        
        self.elements_container.clear()
        
        if str(mod.wifi_safe).lower() != "uncertain":
            wifi_text = "Wifi-Safe" if str(mod.wifi_safe).lower() == "safe" else "Not Wifi-Safe"
            wifi_tag = ElementTag(wifi_text)
            self.elements_container.add_widget(wifi_tag)
        
        for element in mod.includes:
            tag = ElementTag(str(element))
            self.elements_container.add_widget(tag)

        # Update Web Button State
        if mod.url and mod.url.startswith("http"):
            self.web_button.setEnabled(True)
            self.web_button.setToolTip(mod.url)
        else:
             self.web_button.setEnabled(False)
             self.web_button.setToolTip("No URL available")

    def on_open_clicked(self):
        id =self.mod_manager.focused_id
        mod = self.mod_manager.get_mod(id)
        open_folder(mod.path)
        
    def on_fav_on(self):
        id =self.mod_manager.focused_id
        mod = self.mod_manager.get_mod(id)
        self.mod_manager.add_favorite(mod.hash)

    def on_fav_off(self):
        id =self.mod_manager.focused_id
        mod = self.mod_manager.get_mod(id)
        self.mod_manager.remove_favorite(mod.hash)
        
    def on_favorite_changed(self, mod_id:str, is_favorite:bool):
        # Update UI if the changed mod is the currently displayed one
        if self.mod_manager.focused_id and self.mod_manager.get_mod(self.mod_manager.focused_id).hash == mod_id:
            self.fav_button.set_state(is_favorite)

    def on_vis_on(self):
        id =self.mod_manager.focused_id
        mod = self.mod_manager.get_mod(id)
        self.mod_manager.remove_hidden(mod.hash)
        
    def on_vis_off(self):
        id =self.mod_manager.focused_id
        mod = self.mod_manager.get_mod(id)
        self.mod_manager.add_hidden(mod.hash)

    def on_hidden_changed(self, mod_id:str, is_hidden:bool):
        # Update UI if the changed mod is the currently displayed one
        if self.mod_manager.focused_id and self.mod_manager.get_mod(self.mod_manager.focused_id).hash == mod_id:
            # Note: is_hidden=True means Hidden, Button State True = Hidden.
            self.hide_button.set_state(is_hidden)

    def on_enabled(self):
        id =self.mod_manager.focused_id
        mod = self.mod_manager.get_mod(id)
        self.mod_manager.add_enabled(mod.hash)

    def on_disabled(self):
        id =self.mod_manager.focused_id
        mod = self.mod_manager.get_mod(id)
        self.mod_manager.remove_enabled(mod.hash)
    
    def on_edit_clicked(self):
        """Emit signal to request edit mode for current mod"""
        self.edit_requested.emit(self.mod_manager.focused_id)

    def show_context_menu(self):
        """Show context menu for mod options"""
        menu = QMenu(self)
        
        action = QAction("Copy Mod ID", self)
        action.triggered.connect(lambda: None) # Todo implement copy
        title = QAction("Mod Options", self)
        title.setEnabled(False)
        menu.addAction(title)
        
        menu.exec(self.menu_button.mapToGlobal(QPoint(0, self.menu_button.height())))

    def open_web_page(self):
        """Open mod URL in browser"""
        if self.is_online_mode:
            id = self.online_manager.focused_id
            if id:
                mod = self.online_manager.get_mod(id)
                if mod and mod.url and mod.url.startswith("http"):
                    QDesktopServices.openUrl(QUrl(mod.url))
        else:
            id = self.mod_manager.focused_id
            if id:
                mod = self.mod_manager.get_mod(id)
                if mod.url and mod.url.startswith("http"):
                    QDesktopServices.openUrl(QUrl(mod.url))

    def on_download_clicked(self):
        """Handle download button click"""
        files = self.current_online_details.get("files", [])
        
        if not files:
            print("No files to download")
            return
            
        if len(files) == 1:
            # Single file - download directly
            # files[0]["name"] corresponds to _sFile from gamebanana.py
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
                # Pass Name (_sFile) if available
                action.triggered.connect(lambda checked, url=file_data["url"], fname=name: self.download_file(url, fname))
                menu.addAction(action)
                
            menu.addSeparator()
            
            download_all = QAction("Download All", self)
            download_all.triggered.connect(lambda: self.download_all_files(files))
            menu.addAction(download_all)
            
            # Show below button
            menu.exec(self.download_btn.mapToGlobal(QPoint(0, self.download_btn.height())))
            
    def download_file(self, url:str, filename:str=None):
        """Download file logic"""
        if self.download_manager:
            # Extract filename from URL or use default if not provided
            if not filename:
                filename = url.split("/")[-1]
                if "?" in filename:
                    filename = filename.split("?")[0]
            if not filename:
                filename = "download.zip"
            
            # Get mod name from details
            mod_name = self.current_online_details.get("mod_name", "Unknown Mod")
            # Get mod ID
            mod_id = self.online_manager.focused_id
            
            self.download_manager.start_download(url, filename, mod_name, mod_id, self.current_online_details)
        else:
            # Fallback
            QDesktopServices.openUrl(QUrl(url))
        
    def download_all_files(self, files:list):
        """Download all files"""
        print(f"Downloading {len(files)} files")
        for f in files:
             if f.get("url"):
                self.download_file(f.get("url"), f.get("name"))