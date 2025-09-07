from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QSizePolicy, QLabel, QFrame, QHBoxLayout, QPushButton
)
from PyQt6.QtGui import QPixmap, QColor, QPalette, QIcon, QFont
from PyQt6.QtCore import Qt, QSize, QPoint, QPointF
from src.ui.components.layout import HBox, VBox
from src.constants.styles import MAIN_BUTTON
from src.ui.components.side_panel import SidePanel
from src.ui.components.thumbnail_label import ThumbnailLabel
from src.ui.components.collapsible_label import CollapsibleLabel
from src.ui.components.toggle_button import ToggleButton
from src.managers.mod_manager import ModManager
from src.managers.data_manager import DataManager, ButtonIcons
from src.utils.file import open_folder
from src.constants.ui_params import BODY_FONT, BODY_FONT_SIZE, TITLE_FONT, TITLE_FONT_SIZE

class PreviewPanel(SidePanel):
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

        
        author_layout = QHBoxLayout()
        self.body.addLayout(author_layout)

        author_label = QLabel("Author:")
        author_label.setFixedWidth(60)
        body_font = QFont(BODY_FONT, BODY_FONT_SIZE)  # Set the font and font size
        author_label.setFont(body_font)
        author_layout.addWidget(author_label)
        self.author = QLabel("")
        body_font = QFont(BODY_FONT, BODY_FONT_SIZE)  # Set the font and font size
        self.author.setFont(body_font)
        author_layout.addWidget(self.author)
        author_layout.addStretch(1)
        
        version_layout = QHBoxLayout()
        self.body.addLayout(version_layout)
        version_label = QLabel("Version:")
        version_label.setFixedWidth(60)
        body_font = QFont(BODY_FONT, BODY_FONT_SIZE)  # Set the font and font size
        version_label.setFont(body_font)
        version_layout.addWidget(version_label)
        self.version = QLabel("1.0.0")
        body_font = QFont(BODY_FONT, BODY_FONT_SIZE)  # Set the font and font size
        self.version.setFont(body_font)
        version_layout.addWidget(self.version)
        version_layout.addStretch(1)

        version_layout = QHBoxLayout()
        self.body.addLayout(version_layout)
        wifi_label = QLabel("Wifi-Safe:")
        wifi_label.setFixedWidth(60)
        body_font = QFont(BODY_FONT, BODY_FONT_SIZE)  # Set the font and font size
        version_label.setFont(body_font)
        version_layout.addWidget(wifi_label)
        self.wifi = QLabel("")
        body_font = QFont(BODY_FONT, BODY_FONT_SIZE)  # Set the font and font size
        self.wifi.setFont(body_font)
        version_layout.addWidget(self.wifi)
        version_layout.addStretch(1)

        self.description = CollapsibleLabel("Description", "", self)
        self.body.addWidget(self.description)

        self.elements = CollapsibleLabel("Elements", "", self)
        self.body.addWidget(self.elements)
        
        self.body.addStretch(1)

        open_btn = QPushButton("Open")
        open_btn.clicked.connect(self.on_open_clicked)
        self.footer.addWidget(open_btn)

        edit = QPushButton("Edit")
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
        self.description.set_value(mod.description)
        self.wifi.setText(str(mod.wifi_safe))
        elements = [str(element) for element in mod.includes]
        text = "\n".join([f"- {item}" for item in elements])
        self.elements.set_value(text)
        self.elements.set_title(f"Elements ({len(mod.includes)})")

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