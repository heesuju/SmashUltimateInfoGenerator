from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QTreeWidget,
    QTreeWidgetItem, QCheckBox, QLineEdit, QHeaderView, QFileDialog
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap
from src.ui.components.side_panel import SidePanel
from src.ui.components.input_button_widget import InputButtonWidget, InputButton
from src.ui.components.single_combobox import SingleComboBox
from src.managers.data_manager import ButtonIcons
from src.managers.config_manager import ConfigManager

FONT = "Arial"
FONT_SIZE = 10
BODY_FONT_SIZE = 8


class WorkspacePanel(SidePanel):
    def __init__(self, config_manager: ConfigManager):
        super().__init__("Workspace")
        self.config_manager = config_manager
        
        # Cache directory input with browse button
        self.cache_dir = InputButtonWidget(
            "Enter cache directory", 
            InputButton(text="", img=ButtonIcons.BROWSE, callback=self.choose_cache_dir)
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
            "Enter workspace path",
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
        
        # Action buttons
        self.add_footer_button("Restore", self.restore_workspaces)
        self.add_footer_button("Apply", self.apply, primary=True)
        
        # Load saved cache directory
        self.load_cache_dir()
    
    def choose_cache_dir(self):
        """Open file dialog to choose cache directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Cache Directory",
            self.cache_dir.get_text() or ""
        )
        if directory:
            self.cache_dir.set_text(directory)
    
    def load_cache_dir(self):
        """Load saved cache directory from config"""
        if hasattr(self.config_manager.config, 'cache_dir'):
            cache_dir = self.config_manager.config.cache_dir
            if cache_dir:
                self.cache_dir.set_text(cache_dir)
    
    def add_workspace(self):
        """Add a new workspace to the tree and combobox"""
        workspace_path = self.workspace_input.get_text().strip()
        if workspace_path:
            # Add to combobox
            self.workspace_selector.addItem(workspace_path)
            # Add to tree
            self.add_workspace_to_tree(workspace_path, is_default=False)
            # Clear input
            self.workspace_input.set_text("")
    
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
            # Could trigger loading of workspace-specific data here
            print(f"Selected workspace: {workspace_name}")
    
    def remove_single_workspace(self, item: QTreeWidgetItem):
        """Remove a single workspace item"""
        workspace_name = item.text(0)
        is_default = item.data(0, Qt.ItemDataRole.UserRole)
        
        # Don't remove default workspace
        if is_default:
            return
        
        # Remove from tree
        root = self.workspace_tree.invisibleRootItem()
        root.removeChild(item)
        
        # Remove from combobox
        combo_index = self.workspace_selector.findText(workspace_name)
        if combo_index >= 0:
            self.workspace_selector.removeItem(combo_index)
    
    def remove_workspace(self):
        """This method is no longer used but kept for compatibility"""
    
    def restore_workspaces(self):
        """Restore workspaces to saved state"""
        # Clear tree
        self.workspace_tree.clear()
        # Clear combobox
        self.workspace_selector.clear()
        
        # Re-add default workspace
        self.workspace_selector.addItem("Default")
        self.add_workspace_to_tree("Default", is_default=True)
        
        # Load from config if available
        # TODO: Add workspace list to config and load here
    
    def apply(self):
        """Apply workspace settings"""
        # Save cache directory to config
        cache_dir = self.cache_dir.get_text()
        if cache_dir:
            self.config_manager.config.cache_dir = cache_dir
            self.config_manager.save()
        
        # TODO: Save workspace list to config
        print("Workspace settings applied")
