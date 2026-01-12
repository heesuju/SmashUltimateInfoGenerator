from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QSizePolicy, QLabel, QFrame, QHBoxLayout, QPushButton
)
from PyQt6.QtGui import QPixmap, QColor, QPalette, QIcon, QFont
from PyQt6.QtCore import Qt, QSize, QPoint, QPointF, pyqtSignal
from src.ui.components.layout import HBox, VBox
from src.constants.styles import MAIN_BUTTON
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

        self.mod_name = QLabel("")
        title_font = QFont(TITLE_FONT, TITLE_FONT_SIZE)  # Set the font and font size
        title_font.setBold(True)
        self.mod_name.setFont(title_font)
        self.header.addWidget(self.mod_name)

        self.header.addStretch()
        self.fav_button = ToggleButton(ButtonIcons.FAV_ON.value, ButtonIcons.FAV_OFF.value, self.on_fav_on, self.on_fav_off, 24)
        self.header.addWidget(self.fav_button)
        
        self.hide_button = ToggleButton(ButtonIcons.HIDE_ON.value, ButtonIcons.HIDE_OFF.value, self.on_vis_off, self.on_vis_on, 24)
        self.header.addWidget(self.hide_button)

        menu_button = QPushButton()
        menu_button.setIcon(QIcon(QPixmap(ButtonIcons.MENU.value)))
        menu_button.setFlat(True)
        menu_button.setObjectName("obj")
        menu_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        menu_button.setFixedSize(QSize(24, 24))
        self.header.addWidget(menu_button)
        
        
        
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

        open_btn = QPushButton("Open")
        open_btn.clicked.connect(self.on_open_clicked)
        self.footer.addWidget(open_btn)

        edit = QPushButton("Edit")
        edit.clicked.connect(self.on_edit_clicked)
        self.footer.addWidget(edit)

        save_button = QPushButton("Enable")
        save_button.setStyleSheet(MAIN_BUTTON)
        self.footer.addWidget(save_button)

    def set_data(self, id:str):
        mod = self.mod_manager.get_mod(id)
        self.fav_button.set_state(mod.hash in self.mod_manager.favorite_ids)
        self.hide_button.set_state(mod.hash in self.mod_manager.hidden_ids)
        self.mod_name.setText(mod.mod_name)
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

    def on_vis_on(self):
        id =self.mod_manager.focused_id
        mod = self.mod_manager.get_mod(id)
        self.mod_manager.remove_hidden(mod.hash)

    def on_vis_off(self):
        id =self.mod_manager.focused_id
        mod = self.mod_manager.get_mod(id)
        self.mod_manager.add_hidden(mod.hash)
        print()

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