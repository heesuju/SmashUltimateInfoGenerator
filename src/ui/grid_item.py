from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QSizePolicy, QListWidget, QListWidgetItem, QFrame
)
from PyQt6.QtGui import QPixmap, QColor, QPalette, QIcon
from PyQt6.QtCore import Qt, QSize, QPoint, QPointF
from src.utils.image_utils import create_image_overlay, add_text_to_image
from PyQt6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QWidget,
)
from PyQt6.QtWidgets import QGraphicsOpacityEffect
from PyQt6.QtCore import QPropertyAnimation

from src.ui.components.image_overlay import ImageOverlayWidget
from src.ui.components.layout import HBox, VBox
from src.ui.grid_item_button import Overlay
from src.models.mod import Mod, ModItem
from src.managers.data_manager import DataManager, ButtonIcons
from src.ui.components.toggle_button import ToggleButton

ICON_ELLIPSIS = "assets/icons/ui/ellipsis.png"
ICON_FAVORITE = "assets/icons/menu/favorite.png"
ICON_HIDE = "assets/icons/menu/visible.png"
ICON_OFF = "assets/icons/cartridge_off"
ICON_ON = "assets/icons/cartridge_off"

class GridListItem(QListWidgetItem):
    def __init__(self, parent, mod:ModItem, height:int=80, grid_list=None):
        super().__init__()
        self.parent = parent
        self.mod=mod
        self.widget = GridListItemWidget(self.mod, height, grid_list=grid_list)
        self.setSizeHint(QSize(350, 110))
        parent.addItem(self)
        parent.setItemWidget(self, self.widget)

class GridListItemWidget(QWidget):
    # Static cache for scaled character icons
    _icon_cache = {}

    def __init__(self, mod:ModItem, height:int=80, grid_list=None):
        super().__init__()
        self.mod = mod
        self.grid_list = grid_list
        self.image_path = mod.thumbnail
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.frame = QFrame()
        self.frame.setObjectName("gridItemFrame")  # Set unique name for CSS targeting
        self.frame.setFrameShape(QFrame.Shape.NoFrame)
        self.frame.setAutoFillBackground(True)
        frame_layout = HBox(margin=4, spacing=4)
        self.frame.setLayout(frame_layout)

        
        palette = self.frame.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))  # White background
        self.frame.setPalette(palette)
        
        # Set initial border style based on selection state (will be set by update_selection_style)
        # update_selection_style() will be called after frame is built
        
        self.overlay = Overlay(self.image_path, self, initial_enabled=mod.enabled, on_toggle_callback=self.on_overlay_toggle)

        frame_layout.addWidget(self.overlay)
        
        info_layout = QVBoxLayout()

        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        action_layout = HBox()
        # action_layout.addStretch(1)
        action_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        frame_layout.addLayout(info_layout)
        frame_layout.addStretch(1)
        frame_layout.addLayout(right_layout)
        right_layout.addLayout(action_layout)
        frame_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        info_layout.addStretch(1)
        line_text = QLabel(mod.name)
        
        line_text.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Align text to the left

        author_text = QLabel(mod.authors)
        
        author_text.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Align text to the left

        info_layout.addWidget(line_text)
        info_layout.addWidget(author_text)
        slot_text = QLabel(mod.slots)
        slot_text.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Align text to the left
        info_layout.addWidget(slot_text)

        info_layout.setContentsMargins(0,0,0,0)
        info_layout.setSpacing(0)
        
        

        icon_layout = QHBoxLayout()
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        icon_layout.setContentsMargins(0,0,0,0)
        icon_layout.setSpacing(4)
        info_layout.addLayout(icon_layout)
        
        info_layout.addStretch(1)
        
        for char_img in mod.character_icons:
            img_label = QLabel()
            
            # Use cached icon if available
            if char_img in GridListItemWidget._icon_cache:
                char_icon = GridListItemWidget._icon_cache[char_img]
            else:
                # Load and scale, then cache
                char_icon = QPixmap(char_img).scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                GridListItemWidget._icon_cache[char_img] = char_icon
            
            img_label.setPixmap(char_icon)
            icon_layout.addWidget(img_label)

        self.fav_button = ToggleButton(ButtonIcons.FAV_ON.value, ButtonIcons.FAV_OFF.value, self.on_fav_on, self.on_fav_off, 24)
        self.fav_button.set_state(self.mod.favorited)
        action_layout.addWidget(self.fav_button)
        
        self.hide_button = ToggleButton(ButtonIcons.HIDE_ON.value, ButtonIcons.HIDE_OFF.value, self.on_vis_off, self.on_vis_on, 24)
        self.hide_button.set_state(self.mod.hidden)
        action_layout.addWidget(self.hide_button)


        menu_button = QPushButton()
        menu_button.setIcon(QIcon(QPixmap(ButtonIcons.MENU.value)))
        menu_button.setFlat(True)
        menu_button.setObjectName("obj")
        menu_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        menu_button.setFixedSize(QSize(24, 24))
        action_layout.addWidget(menu_button)

        
        
        right_layout.addStretch(1)

        version_text = QLabel(mod.version)
        version_text.setAlignment(Qt.AlignmentFlag.AlignRight)  # Align text to the left
        right_layout.addWidget(version_text)

        # Set initial selection style (shadow will be applied here)
        self.update_selection_style()
        
        layout.addWidget(self.frame)
    
    def update_selection_style(self):
        """Update the frame shadow to show selection state"""
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        from PyQt6.QtGui import QColor
        
        shadow = QGraphicsDropShadowEffect()
        
        if self.mod.selected:
            # Selected: Blue glowing shadow (no border)
            shadow.setBlurRadius(25)  # Increased for better visibility
            shadow.setOffset(0, 0)  # No offset for glow effect
            shadow.setColor(QColor(74, 144, 226, 220))  # #4A90E2 with higher alpha
            
            # No border - just the glow
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
            shadow.setColor(QColor(0, 0, 0, 160))  # Semi-transparent black
            
            # No border
            self.frame.setStyleSheet("""
                QFrame#gridItemFrame {
                    border: none;
                    border-radius: 4px;
                }
            """)
        
        self.frame.setGraphicsEffect(shadow)

        self.fav_button.set_state(self.mod.favorited)

    def mousePressEvent(self, event):
        from PyQt6.QtCore import Qt
        
        # Check if Ctrl is held down
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Ctrl+Click: Toggle selection
            if self.grid_list and hasattr(self.grid_list, 'mod_manager'):
                self.grid_list.mod_manager.toggle_selection(self.mod.id)
                self.mod.selected = self.grid_list.mod_manager.is_selected(self.mod.id)
                self.update_selection_style()
                
                # Update header checkbox
                parent = self
                while parent is not None:
                    parent = parent.parent()
                    if hasattr(parent, 'update_header_checkbox_state'):
                        parent.update_header_checkbox_state()
                        break
            return
        
        # Normal click: show preview (default behavior)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # self.frame.setStyleSheet(self.default_style)
        
        super().mouseReleaseEvent(event)

    def on_fav_on(self):
        if self.grid_list and hasattr(self.grid_list, 'mod_manager'):
            self.grid_list.mod_manager.add_favorite(self.mod.id)
    
    def on_fav_off(self):
        if self.grid_list and hasattr(self.grid_list, 'mod_manager'):
            self.grid_list.mod_manager.remove_favorite(self.mod.id)

    def on_vis_on(self):
        if self.grid_list and hasattr(self.grid_list, 'mod_manager'):
            self.grid_list.mod_manager.remove_hidden(self.mod.id)
    
    def on_vis_off(self):
        if self.grid_list and hasattr(self.grid_list, 'mod_manager'):
            self.grid_list.mod_manager.add_hidden(self.mod.id)
    
    def on_overlay_toggle(self):
        """Called when the overlay cartridge is clicked"""
        if self.grid_list and hasattr(self.grid_list, 'mod_manager'):
            # Toggle the enabled state through mod manager
            if self.mod.id in self.grid_list.mod_manager.enabled_ids:
                self.grid_list.mod_manager.remove_enabled(self.mod.id)
            else:
                self.grid_list.mod_manager.add_enabled(self.mod.id)