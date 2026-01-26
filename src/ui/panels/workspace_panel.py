from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QMessageBox
)
import os
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap
from src.ui.components.side_panel import SidePanel
from src.ui.components.workspace_list import WorkspaceList
from src.managers.data_manager import ButtonIcons
from src.managers.config_manager import ConfigManager
from src.managers.workspace_manager import WorkspaceManager
from src.managers.mod_manager import ModManager
from src.utils.logger import output_log
from src.constants.colors import AppColors
from src.constants.strings import AppStrings

class WorkspacePanel(SidePanel):
    from PyQt6.QtCore import pyqtSignal
    sync_started = pyqtSignal()
    
    def __init__(self, config_manager: ConfigManager, workspace_manager: WorkspaceManager, mod_manager: ModManager, on_open_config=None):
        super().__init__("Workspace")
        self.config_manager = config_manager
        self.workspace_manager = workspace_manager
        self.mod_manager = mod_manager
        self.on_open_config = on_open_config
        
        # Connect to manager signals
        self.workspace_manager.sync_started.connect(self.on_sync_start)
        self.workspace_manager.sync_finished.connect(self.on_sync_finish)
        self.workspace_manager.sync_progress.connect(self.on_sync_progress)
        
        # Config Warning
        self.config_warning = QLabel()
        self.config_warning.setText(AppStrings.WARN_CONFIG_DIRS.format(color=AppColors.TEXT_LINK))
        self.config_warning.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_ERROR};
                background-color: {AppColors.BG_ERROR};
                border: 1px solid {AppColors.BORDER_ERROR};
                border-radius: 4px;
                padding: 8px;
            }}
        """)
        self.config_warning.setOpenExternalLinks(False)
        self.config_warning.linkActivated.connect(self.on_config_link_clicked)
        self.config_warning.hide()
        self.body.insertWidget(0, self.config_warning)
        
        # Workspace List Component (Unified selection and creation)
        self.workspace_list = WorkspaceList(self.workspace_manager)
        self.body.addWidget(self.workspace_list)
        
        self.body.addStretch(1)
        
        # Action buttons
        self.export_btn = self.add_footer_button(
            AppStrings.LBL_EXPORT_BUTTON.format(count=0), 
            self.on_sync_clicked, 
            primary=True,
            icon=ButtonIcons.EXPORT.value
        )
        
        self.workspace_manager.workspace_changed.connect(self.update_export_btn_text)
        self.workspace_manager.add_enabled_callback(self.update_export_btn_text)
        self.update_export_btn_text()

    def showEvent(self, event):
        super().showEvent(event)
        self.check_config()

    def check_config(self):
        """Check if config dirs are set, show warning if not"""
        if not self.config_manager.config:
            return
            
        cache = self.config_manager.config.cache_dir
        export = self.config_manager.config.export_dir
        
        if not cache:
            self.config_warning.setVisible(True)
        else:
            self.config_warning.setVisible(False)
            
        # Validate export dir
        if export and os.path.isdir(export):
            self.export_btn.setEnabled(True)
            self.export_btn.setToolTip("")
        else:
            self.export_btn.setEnabled(False)
            self.export_btn.setToolTip(AppStrings.TOOLTIP_EXPORT_INVALID)
            
    def on_config_link_clicked(self, link):
        if self.on_open_config:
            self.on_open_config()
        
    def update_export_btn_text(self, *args):
        """Update export button text with enabled mod count"""
        count = len(self.workspace_manager.get_enabled_ids())
        self.export_btn.setText(AppStrings.LBL_EXPORT_BUTTON.format(count=count))

    def on_cache_changed(self):
        """Handle cache directory change"""
        self.check_config()
        self.workspace_manager.load()

    def on_sync_clicked(self):
        """Trigger sync process"""
        reply = QMessageBox.question(
            self, 
            AppStrings.DIALOG_TITLE_SYNC, 
            AppStrings.DIALOG_MSG_SYNC,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.workspace_manager.sync_mods(self.mod_manager.get_mods_dict())

    def on_sync_start(self):
        """Handle sync started event"""
        self.export_btn.setEnabled(False)
        self.export_btn.setText(AppStrings.STATUS_EXPORTING)
        self.sync_started.emit()

    def on_sync_finish(self):
        """Handle sync finished event"""
        self.check_config()
        self.update_export_btn_text()
        self.export_btn.repaint() # Force repaint
        
    def on_sync_progress(self, message: str, progress: float):
        """Handle sync progress event"""
        percent = int(progress * 100)
        self.export_btn.setText(AppStrings.STATUS_EXPORTING_PERCENT.format(percent=percent))
        
        # Failsafe: if 100% is reached, consider it finished
        if progress >= 1.0:
            self.on_sync_finish()