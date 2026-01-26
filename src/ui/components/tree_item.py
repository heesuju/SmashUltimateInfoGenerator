from PyQt6.QtWidgets import QLabel, QWidget, QPushButton, QTreeWidgetItem, QCheckBox
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from src.managers.data_manager import ButtonIcons, DataManager
from src.models.mod import Mod, ModItem
from src.constants.colors import AppColors

from src.ui.components.toggle_button import ToggleButton

class TreeItem(QTreeWidgetItem):
    def __init__(self, parent, mod:ModItem, on_clicked:callable, on_enabled:callable, tree_list=None):
        self.mod = mod
        self.on_clicked = on_clicked
        self.on_enabled = on_enabled
        self.tree_list = tree_list  # Reference to TreeList widget
        self.animations = []
        super().__init__(["", "", "", "", "", "", ""]) # 7 Columns

        parent.addTopLevelItem(self)

        check_widget = QCheckBox()
        # Set initial checked state based on ModManager selection
        check_widget.setChecked(self.mod.selected)
        
        # Store reference in TreeList if available
        if tree_list and hasattr(tree_list, 'item_checkboxes'):
            tree_list.item_checkboxes[self.mod.id] = check_widget
        
        # Connect to selection manager
        def on_checkbox_changed(state):
            if tree_list and hasattr(tree_list, 'mod_manager'):
                from PyQt6.QtCore import Qt
                if state == Qt.CheckState.Checked.value:
                    tree_list.mod_manager.add_selection(self.mod.id)
                else:
                    tree_list.mod_manager.remove_selection(self.mod.id)
                
                # Update header checkbox via ModList
                parent = tree_list
                while parent is not None:
                    parent = parent.parent()
                    if hasattr(parent, 'update_header_checkbox_state'):
                        parent.update_header_checkbox_state()
                        break
            
            # Call user callback if provided
            if self.on_enabled:
                self.on_enabled(self.mod)
        
        check_widget.stateChanged.connect(on_checkbox_changed)
        
        self.fav_button = ToggleButton(
            ButtonIcons.FAV_ON.value, 
            ButtonIcons.FAV_OFF.value, 
            self.on_fav_on, 
            self.on_fav_off, 
            24,
            color_a=AppColors.BUTTON_YELLOW,
            color_b=AppColors.BUTTON_GRAY
        )
        self.fav_button.set_state(self.mod.favorited)
        
        name_widget = QLabel(self.mod.name)
        category_widget = QLabel(self.mod.category)
        authors_widget = QLabel(self.mod.authors)
        slot_widget = QLabel(self.mod.slots)

        icons_widget = QWidget()
        from PyQt6.QtWidgets import QHBoxLayout
        icons_layout = QHBoxLayout(icons_widget)
        icons_layout.setContentsMargins(0, 0, 0, 0)
        icons_layout.setSpacing(2)
        
        for i, path in enumerate(self.mod.character_icons):
            icon_label = QLabel()
            icon_label.setPixmap(QPixmap(path).scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            
            if i < len(self.mod.character_names):
                icon_label.setToolTip(self.mod.character_names[i])
            
            icons_layout.addWidget(icon_label)
        
        remaining = len(self.mod.character_names) - len(self.mod.character_icons)
        
        if remaining > 0:
            plus_label = QLabel(f"+{remaining}")
            plus_label.setStyleSheet("color: #888; font-size: 11px; padding-left: 4px;")
            omitted = self.mod.character_names[len(self.mod.character_icons):]
            plus_label.setToolTip("\n".join(omitted))    
            icons_layout.addWidget(plus_label)

        icons_layout.addStretch()
        
        # Actions Widget (Fav + Enable)
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(4)
        
        # Add Fav Button
        actions_layout.addWidget(self.fav_button)

        self.hide_button = ToggleButton(
            ButtonIcons.HIDE_ON.value, 
            ButtonIcons.HIDE_OFF.value, 
            self.on_vis_off, 
            self.on_vis_on, 
            24, 
            initial_state=self.mod.hidden,
            color_a=AppColors.BUTTON_GRAY,
            color_b=AppColors.BUTTON_CYAN
        )
        
        actions_layout.addWidget(self.hide_button)
        
        self.enable_button = ToggleButton(
            ButtonIcons.ENABLE.value,
            ButtonIcons.DISABLE.value,
            self.on_enable,
            self.on_disable,
            24,
            initial_state=self.mod.enabled,
            color_a=AppColors.BUTTON_GREEN,
            color_b=AppColors.BUTTON_GRAY
        )
        
        actions_layout.addWidget(self.enable_button)
        
        actions_layout.addStretch() # Push access to left
            
            
        parent.setItemWidget(self, 0, check_widget)     # Column 0: Checkbox
        parent.setItemWidget(self, 1, category_widget)  # Column 1: Category
        parent.setItemWidget(self, 2, name_widget)      # Column 2: Mod Name
        parent.setItemWidget(self, 3, authors_widget)   # Column 3: Authors
        parent.setItemWidget(self, 4, slot_widget)      # Column 4: Slot
        parent.setItemWidget(self, 5, icons_widget)     # Column 5: Characters
        parent.setItemWidget(self, 6, actions_widget)   # Column 6: Actions (Fav + Enabled)
        self.widgets = [check_widget, category_widget, name_widget, authors_widget, slot_widget, icons_widget, actions_widget]

    def on_item_toggled(self):
        pass

    def on_fav_on(self):
        if self.tree_list and hasattr(self.tree_list, 'mod_manager'):
            self.tree_list.mod_manager.add_favorite(self.mod.id)

    def on_fav_off(self):
        if self.tree_list and hasattr(self.tree_list, 'mod_manager'):
            self.tree_list.mod_manager.remove_favorite(self.mod.id)

    def on_vis_on(self):
        # Called when eye is toggled ON (Visible) -> Remove from hidden
        if self.tree_list and hasattr(self.tree_list, 'mod_manager'):
            self.tree_list.mod_manager.remove_hidden(self.mod.id)

    def on_vis_off(self):
        # Called when eye is toggled OFF (Hidden) -> Add to hidden
        if self.tree_list and hasattr(self.tree_list, 'mod_manager'):
            self.tree_list.mod_manager.add_hidden(self.mod.id)
    
    def update_enable_button_icon(self, is_enabled:bool):
        """Update the enable button icon based on enabled state"""
        self.enable_button.set_state(is_enabled)
    
    def on_enable(self):
        # Called when enabled (toggle ON)
        if self.tree_list and hasattr(self.tree_list, 'mod_manager'):
            self.tree_list.mod_manager.add_enabled(self.mod.id)
    
    def on_disable(self):
        # Called when disabled (toggle OFF)
        if self.tree_list and hasattr(self.tree_list, 'mod_manager'):
            self.tree_list.mod_manager.remove_enabled(self.mod.id)