from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QTreeWidget,
    QTreeWidgetItem, QCheckBox, QLineEdit, QHeaderView, QFileDialog, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap
from src.ui.components.side_panel import SidePanel
from src.ui.components.input_button_widget import InputButtonWidget, InputButton
from src.ui.components.single_combobox import SingleComboBox
from src.managers.data_manager import ButtonIcons
from src.managers.config_manager import ConfigManager
from src.managers.workspace_manager import WorkspaceManager
from src.managers.mod_manager import ModManager

FONT = "Arial"
FONT_SIZE = 10
BODY_FONT_SIZE = 8


class WorkspacePanel(SidePanel):
    def __init__(self, config_manager: ConfigManager, workspace_manager: WorkspaceManager, mod_manager: ModManager):
        super().__init__("Workspace")
        self.config_manager = config_manager
        self.workspace_manager = workspace_manager
        self.mod_manager = mod_manager
        
        # Cache directory input with browse button
        self.cache_dir = InputButtonWidget(
            "Enter cache directory", 
            InputButton(img=ButtonIcons.BROWSE, callback=self.choose_cache_dir)
        )
        self.body.addWidget(self.cache_dir)
        
        # Workspace selection combobox
        workspace_label_select = QLabel("Select Workspace:")
        workspace_label_select.setFont(QFont(FONT, BODY_FONT_SIZE))
        self.body.addWidget(workspace_label_select)
        
        self.workspace_selector = SingleComboBox()
        self.workspace_selector.addItem("Default")
        self.workspace_selector.currentIndexChanged.connect(self.on_workspace_selected)
        self.body.addWidget(self.workspace_selector)
        
        # Add workspace section
        add_workspace_label = QLabel("Add Workspace:")
        add_workspace_label.setFont(QFont(FONT, BODY_FONT_SIZE))
        self.body.addWidget(add_workspace_label)
        
        self.workspace_input = InputButtonWidget(
            "Enter new workspace name",
            InputButton(text="Add", highlight=True, callback=self.add_workspace)
        )
        self.body.addWidget(self.workspace_input)
        
        # Workspace tree list
        workspaces_list_label = QLabel("Workspaces:")
        workspaces_list_label.setFont(QFont(FONT, BODY_FONT_SIZE))
        self.body.addWidget(workspaces_list_label)
        
        self.workspace_tree = QTreeWidget()
        self.workspace_tree.setColumnCount(2)
        self.workspace_tree.setHeaderLabels(["Workspace", "Actions"])
        self.workspace_tree.header().setStretchLastSection(False)
        self.workspace_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.workspace_tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.workspace_tree.setColumnWidth(1, 60)
        self.workspace_tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid rgba(255, 255, 255, 0.1);
                background: rgba(0, 0, 0, 0.2);
                border-radius: 5px;
                outline: 0;
            }
            QTreeWidget::item {
                padding: 4px;
                border: none;
            }
            QTreeWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.08);
            }
            QTreeWidget::item:selected {
                background-color: rgba(100, 150, 255, 0.2);
            }
            QHeaderView::section {
                background-color: rgba(0, 0, 0, 0.3);
                color: white;
                padding: 4px;
                border: none;
                border-right: 1px solid rgba(255, 255, 255, 0.1);
                border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            }
        """)
        self.body.addWidget(self.workspace_tree)
        
        # Add default workspace
        self.add_workspace_to_tree("Default", is_default=True)
        
        self.body.addStretch(1)

        # Export Directory Input
        export_label = QLabel("Export Directory:")
        export_label.setFont(QFont(FONT, BODY_FONT_SIZE))
        self.body.addWidget(export_label)
        
        self.export_dir = InputButtonWidget(
            "Enter export directory",
            InputButton(img=ButtonIcons.BROWSE, callback=self.choose_export_dir)
        )
        self.body.addWidget(self.export_dir)
        
        # Connect inputs to realtime save
        self.cache_dir.input_box.editingFinished.connect(self.save_config)
        self.export_dir.input_box.editingFinished.connect(self.save_config)
        
        # Action buttons
        self.add_footer_button(
            "Export Enabled Mods", 
            self.on_sync_clicked, 
            primary=True,
            icon=ButtonIcons.EXPORT.value
        )
        
        # Load saved cache directory and export directory
        self.load_cache_dir()
        self.load_export_dir()
    
    def choose_cache_dir(self):
        """Open file dialog to choose cache directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Cache Directory",
            self.cache_dir.get_text() or ""
        )
        if directory:
            self.cache_dir.set_text(directory)
            self.save_config()
    
    def load_cache_dir(self):
        """Load saved cache directory from config"""
        if hasattr(self.config_manager.config, 'cache_dir'):
            cache_dir = self.config_manager.config.cache_dir
            if cache_dir:
                self.cache_dir.set_text(cache_dir)
                
    def choose_export_dir(self):
        """Open file dialog to choose export directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Export Directory",
            self.export_dir.get_text() or ""
        )
        if directory:
            self.export_dir.set_text(directory)
            self.save_config()

    def load_export_dir(self):
        """Load saved export directory from config"""
        if hasattr(self.config_manager.config, 'export_dir'):
            export_dir = self.config_manager.config.export_dir
            if export_dir:
                self.export_dir.set_text(export_dir)

    def save_config(self):
        """Save config settings (dirs) immediately"""
        changed = False
        
        # Save cache directory to config
        cache_dir = self.cache_dir.get_text()
        if cache_dir and cache_dir != self.config_manager.config.cache_dir:
            self.config_manager.config.cache_dir = cache_dir
            changed = True
            
        # Save export directory to config
        export_dir = self.export_dir.get_text()
        if export_dir and export_dir != self.config_manager.config.export_dir:
            self.config_manager.config.export_dir = export_dir
            changed = True

        if changed:
            self.config_manager.save()
            print("Config settings saved")

    def on_sync_clicked(self):
        """Trigger sync process"""
        # Ensure config is saved
        self.save_config()
        
        reply = QMessageBox.question(
            self, 
            "Sync Mods", 
            "This will delete any mods in the export folder that are disabled or removed, and copy all enabled mods.\nThis may take some time.\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # We will implement sync_mods with a callback or signal for progress later, 
            # for now just trigger it
            # TODO: Add progress feedback
            self.workspace_manager.sync_mods(self.mod_manager.get_mods())
    
    def add_workspace(self):
        """Add a new workspace"""
        workspace_name = self.workspace_input.get_text().strip()
        if workspace_name:
            if self.workspace_manager.add_workspace(workspace_name):
                # Refresh UI
                self.workspace_selector.addItem(workspace_name)
                self.add_workspace_to_tree(workspace_name, is_default=False)
                self.workspace_input.set_text("")
            else:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Error", f"Workspace '{workspace_name}' already exists.")

    def create_action_buttons(self, item: QTreeWidgetItem, is_default: bool = False):
        """Create action buttons widget for a tree item"""
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(2)
        
        # Remove button (only for non-default workspaces)
        if not is_default:
            remove_btn = QPushButton()
            remove_btn.setIcon(QIcon(QPixmap(ButtonIcons.CLEAR.value)))
            remove_btn.setFixedSize(24, 24)
            remove_btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    background: transparent;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 100, 100, 0.3);
                }
            """)
            remove_btn.clicked.connect(lambda: self.remove_single_workspace(item))
            actions_layout.addWidget(remove_btn)
        
        actions_layout.addStretch()
        return actions_widget
    
    def add_workspace_to_tree(self, workspace_name: str, is_default: bool = False):
        """Add a workspace item to the tree with action buttons"""
        item = QTreeWidgetItem(self.workspace_tree)
        item.setText(0, workspace_name)
        
        # Store if it's the default workspace
        item.setData(0, Qt.ItemDataRole.UserRole, is_default)
        
        # Add action buttons widget to second column
        actions_widget = self.create_action_buttons(item, is_default)
        self.workspace_tree.setItemWidget(item, 1, actions_widget)
    
    def on_workspace_selected(self, index: int):
        """Handle workspace selection from combobox"""
        if index >= 0:
            workspace_name = self.workspace_selector.currentText()
            if workspace_name != self.workspace_manager.current_workspace_name:
                self.workspace_manager.switch_workspace(workspace_name)
                print(f"Switched to workspace: {workspace_name}")
    
    def remove_single_workspace(self, item: QTreeWidgetItem):
        """Remove a single workspace item"""
        workspace_name = item.text(0)
        is_default = item.data(0, Qt.ItemDataRole.UserRole)
        
        # Don't remove default workspace
        if is_default:
            return
            
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete workspace '{workspace_name}'?\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Realtime remove
            self.workspace_manager.remove_workspace(workspace_name)
            
            # Remove from tree
            root = self.workspace_tree.invisibleRootItem()
            root.removeChild(item)
            
            # Remove from combobox
            combo_index = self.workspace_selector.findText(workspace_name)
            if combo_index >= 0:
                self.workspace_selector.removeItem(combo_index)
                
            # If we deleted current workspace, Manager switches to Default. UI should reflect that.
            if self.workspace_manager.current_workspace_name == "Default":
                default_idx = self.workspace_selector.findText("Default")
                if default_idx >= 0:
                    self.workspace_selector.setCurrentIndex(default_idx)
    
    def remove_workspace(self):
        """This method is no longer used but kept for compatibility"""
    
    def restore_workspaces(self):
        """Restore workspaces to saved state (Refresh UI)"""
        # Clear tree
        self.workspace_tree.clear()
        # Clear combobox
        self.workspace_selector.blockSignals(True)
        self.workspace_selector.clear()
        
        # Populate from manager
        for name in self.workspace_manager.workspace_map.keys():
            self.workspace_selector.addItem(name)
            is_default = (name == "Default")
            self.add_workspace_to_tree(name, is_default)
            
        # Select current
        current_idx = self.workspace_selector.findText(self.workspace_manager.current_workspace_name)
        if current_idx >= 0:
            self.workspace_selector.setCurrentIndex(current_idx)
            
        self.workspace_selector.blockSignals(False)
    
    def apply(self):
        """Deprecated method"""
        pass
