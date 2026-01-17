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
    
    def __init__(self, mod_manager:ModManager):
        super().__init__("Preview")
        self.mod_manager = mod_manager
        self.mod_manager.add_focus_callback(self.set_data)
        self.mod_manager.add_favorite_callback(self.on_favorite_changed)
        self.mod_manager.add_hidden_callback(self.on_hidden_changed)

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

        self.add_footer_button("Open", self.on_open_clicked)
        self.add_footer_button("Edit", self.on_edit_clicked)
        self.add_footer_button("Enable", self.on_enabled, primary=True)

    def set_data(self, id:str):
        mod = self.mod_manager.get_mod(id)
        self.fav_button.set_state(str(mod.hash) in self.mod_manager.favorite_ids)
        self.hide_button.set_state(str(mod.hash) in self.mod_manager.hidden_ids)
        
        # Use standard title label
        if self.title_label:
            self.title_label.setText(mod.mod_name)
            
        self.thumbnail.set_thumbnail(mod.thumbnail)
        self.author.setText(mod.authors)
        self.version.setText(mod.version)
        self.description_label.setText(mod.description)
        
        # Clear and repopulate element tags
        self.elements_container.clear()
        
        # Add wifi-safe tag if not uncertain
        if str(mod.wifi_safe).lower() != "uncertain":
            wifi_text = "Wifi-Safe" if str(mod.wifi_safe).lower() == "safe" else "Not Wifi-Safe"
            wifi_tag = ElementTag(wifi_text)
            self.elements_container.add_widget(wifi_tag)
        
        # Add element tags
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
        id = self.mod_manager.focused_id
        if id:
            mod = self.mod_manager.get_mod(id)
            if mod.url and mod.url.startswith("http"):
                QDesktopServices.openUrl(QUrl(mod.url))