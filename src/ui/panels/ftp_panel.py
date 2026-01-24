from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, 
                             QLabel, QProgressBar, QListWidget, QListWidgetItem,
                             QGroupBox, QComboBox, QLineEdit, QCheckBox)
from PyQt6.QtGui import QIntValidator, QIcon
from PyQt6.QtCore import Qt
from src.ui.components.side_panel import SidePanel
from src.ui.components.layout import VBox, HBox
from src.managers.ftp_manager import FTPManager
from src.managers.data_manager import ButtonIcons
from src.ui.components.collapsible_section import CollapsibleSection
import os
from PyQt6.QtGui import QPainter, QColor

class SyncItemWidget(QWidget):
    def __init__(self, text):
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        self.label = QLabel(text)
        self.label.setStyleSheet("background: transparent;") # Allow paintEvent to show through
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.progress = 0.0
        
    def set_progress(self, value: float):
        self.progress = value
        self.update() # Trigger repaint
        
    def paintEvent(self, event):
        painter = QPainter(self)
        if self.progress > 0:
            width = self.width() * self.progress
            rect = event.rect()
            rect.setWidth(int(width))
            # Semi-transparent green
            painter.fillRect(rect, QColor(76, 175, 80, 100)) # #4CAF50 at ~40% opacity
        
        super().paintEvent(event)

class FTPPanel(SidePanel):
    def __init__(self, ftp_manager: FTPManager):
        super().__init__("FTP Sync")
        self.ftp_manager = ftp_manager
        
        self.status_text = QLabel("Idle")
        self.status_text.setStyleSheet("color: #ccc; font-size: 12px;")
        self.status_text.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.header.addWidget(self.status_text, 0, Qt.AlignmentFlag.AlignVCenter)
        
        self.status_indicator = QLabel()
        self.status_indicator.setFixedSize(12, 12)
        self.status_indicator.setStyleSheet("background-color: #777; border-radius: 6px;")
        self.status_indicator.setToolTip("Status: Idle")
        self.header.addWidget(self.status_indicator, 0, Qt.AlignmentFlag.AlignVCenter)

        # --- Fixed Top Section (Inputs, Progress, Log) ---
        self.top_widget = QWidget()
        top_layout = VBox(margin=(10, 0, 10, 0), spacing=10)
        self.top_widget.setLayout(top_layout)
        
        # Connection Settings (IP:Port)
        conn_layout = HBox()
        conn_layout.setSpacing(0)
        
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("IP Address")
        self.ip_input.setStyleSheet("""
            QLineEdit {
                background-color: #2b2b2b; 
                color: white; 
                border: 1px solid #444; 
                border-top-left-radius: 5px; 
                border-bottom-left-radius: 5px;
                border-top-right-radius: 0px; 
                border-bottom-right-radius: 0px;
                padding: 4px;
            }
        """)
        conn_layout.addWidget(self.ip_input)
        
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Port")
        self.port_input.setValidator(QIntValidator(1, 65535))
        self.port_input.setFixedWidth(60)
        self.port_input.setStyleSheet("""
            QLineEdit {
                background-color: #2b2b2b; 
                color: white; 
                border: 1px solid #444; 
                border-left: 0px;
                border-radius: 0px;
                padding: 4px;
            }
        """)
        conn_layout.addWidget(self.port_input)
        
        # Retry/Refresh Button
        self.retry_button = QPushButton()
        self.retry_button.setIcon(QIcon(ButtonIcons.REFRESH.value))
        self.retry_button.setToolTip("Refresh Connection")
        self.retry_button.setFixedSize(28, 28) # Height matches inputs roughly
        self.retry_button.setFlat(True)
        self.retry_button.clicked.connect(self.on_retry_clicked)
        self.retry_button.setStyleSheet("""
             QPushButton {
                background-color: #2b2b2b;
                border: 1px solid #444;
                border-left: 0px;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
                border-top-left-radius: 0px; 
                border-bottom-left-radius: 0px;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #3b3b3b;
            }
        """)
        conn_layout.addWidget(self.retry_button)
        
        top_layout.addLayout(conn_layout)
        
        # --- Sync Options Group ---
        self.options_group = QGroupBox("Sync Options")
        self.options_group.setStyleSheet("""
            QGroupBox {
                color: #ccc;
                font-weight: bold;
                border: 1px solid #444;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
        """)
        options_layout = HBox(margin=(5, 5, 5, 5), spacing=15)
        
        # Mode Combo
        mode_layout = VBox(spacing=2)
        mode_label = QLabel("Sync Mode:")
        mode_label.setStyleSheet("color: #888; font-size: 11px;")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Enabled Only", "All"])
        self.mode_combo.setStyleSheet("""
            QComboBox {
                padding: 0px 10px;
                border-radius: 5px;
                border: 1px solid #444;
                background-color: #2b2b2b;
                color: white;
                min-height: 24px;
            }
            QComboBox:hover {
                border-color: #666;
            }
        """)
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        options_layout.addLayout(mode_layout)
        
        # Config Check
        self.sync_configs_check = QCheckBox("Sync Configs")
        self.sync_configs_check.setStyleSheet("color: white;")
        self.sync_configs_check.setChecked(True)
        options_layout.addWidget(self.sync_configs_check, 0, Qt.AlignmentFlag.AlignBottom)
        
        options_layout.addStretch()
        self.options_group.setLayout(options_layout)
        top_layout.addWidget(self.options_group)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        top_layout.addWidget(self.progress_bar)
        
        # Log Output (Collapsible)
        self.log_section = CollapsibleSection("Activity Log", expanded=True)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("font-family: Consolas, monospace; font-size: 12px;")
        self.log_output.setMinimumHeight(150)
        self.log_output.setMaximumHeight(1000)
        self.log_section.add_widget(self.log_output)
        top_layout.addWidget(self.log_section)
        
        self.root.insertWidget(1, self.top_widget)
        
        
        # Load Config
        config = self.ftp_manager.config_manager.config
        self.ip_input.setText(config.ftp_ip)
        self.port_input.setText(str(config.ftp_port))
        
        # Connect signals
        self.ip_input.editingFinished.connect(self.on_config_changed)
        self.port_input.editingFinished.connect(self.on_config_changed)
        
        
        # Sync Button (Footer) - Now defaults to Scan/Preview
        self.sync_button = self.add_footer_button(
            text="Start Sync",
            callback=self.on_scan_clicked,
            primary=True,
            icon=ButtonIcons.SYNC.value
        )
        
        # Clean Stale Mods Button (Footer)
        self.stale_button = self.add_footer_button(
            text="Clean Stale",
            callback=self.on_stale_clicked,
            icon=ButtonIcons.BATCH_REMOVE.value
        )
        self.stale_button.setStyleSheet("color: #ff6666;") # Red text hint

        # Confirm & Cancel Buttons (Footer - Initially Hidden)
        self.cancel_preview_button = self.add_footer_button(
            text="Cancel",
            callback=self.on_cancel_preview_clicked,
            danger=True
        )
        self.cancel_preview_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_preview_button.hide()

        self.confirm_button = self.add_footer_button(
            text="Confirm",
            callback=self.on_confirm_sync_clicked,
            primary=True,
            icon=ButtonIcons.SYNC.value
        )
        self.confirm_button.setCursor(Qt.CursorShape.PointingHandCursor)
        # Override to Green for confirmation distinction
        self.confirm_button.setStyleSheet("""
            QPushButton {
                 background-color: #4CAF50;
                 color: white;
                 font-weight: bold;
                 border-radius: 5px;
                 padding: 5px 10px;
            }
            QPushButton:hover {
                 background-color: #45a049;
            }
             QPushButton:pressed {
                background-color: #388E3C; 
            }
            QPushButton:disabled {
                background-color: #2E2E32;
                color: #666;
                border: 1px solid #444;
            }
        """)
        self.confirm_button.hide()
        
        # Done Button (Footer - Shown after sync)
        self.done_button = self.add_footer_button(
            text="Done",
            callback=self.on_done_clicked,
            primary=True
        )
        self.done_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.done_button.hide()
        
        # --- Scrollable Body Content (Preview) ---
        
        # Preview Container (initially hidden)
        self.preview_container = QWidget()
        preview_layout = VBox()
        preview_layout.setContentsMargins(0, 0, 0, 0)
        
        # Categories
        self.match_list = QListWidget()
        self.match_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.replace_list = QListWidget()
        self.replace_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.metadata_list = QListWidget()
        self.metadata_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.missing_list = QListWidget()
        self.missing_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.stale_list = QListWidget()
        self.stale_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Add lists with Collapsible Sections
        self.match_box = CollapsibleSection("✓ Up to Date", expanded=False)
        self.match_box.add_widget(self.match_list)
        preview_layout.addWidget(self.match_box)
        
        self.replace_box = CollapsibleSection("🔄 Replace (Full Re-upload)", expanded=True)
        self.replace_box.add_widget(self.replace_list)
        preview_layout.addWidget(self.replace_box)
        
        self.metadata_box = CollapsibleSection("📝 Update Metadata Only", expanded=True)
        self.metadata_box.add_widget(self.metadata_list)
        preview_layout.addWidget(self.metadata_box)
        
        self.missing_box = CollapsibleSection("➕ New Mods", expanded=True)
        self.missing_box.add_widget(self.missing_list)
        preview_layout.addWidget(self.missing_box)
        
        self.stale_box = CollapsibleSection("🗑️ Stale / To Delete", expanded=True)
        self.stale_box.add_widget(self.stale_list)
        self.stale_box.hide() # Hidden by default
        preview_layout.addWidget(self.stale_box)
        
        self.preview_container.setLayout(preview_layout)
        self.preview_container.hide()
        self.body.addWidget(self.preview_container)
        
        # Connect signals
        self.ftp_manager.log_signal.connect(self.append_log)
        self.ftp_manager.progress_signal.connect(self.update_progress)
        self.ftp_manager.sync_started.connect(self.on_sync_started)
        self.ftp_manager.sync_finished.connect(self.on_sync_finished)
        self.ftp_manager.connection_status_changed.connect(self.on_connection_status_changed)
        self.ftp_manager.scan_complete.connect(self.on_scan_complete)
        self.ftp_manager.mod_progress.connect(self.on_mod_progress)
        self.ftp_manager.config_sync_finished.connect(self.on_config_sync_finished)
        self.ftp_manager.stale_scan_complete.connect(self.on_stale_scan_complete)
        
        # Store diff map for confirmation
        self.current_diff_map = {}
        self.stale_mods_list = [] # List of strings
        
        # Align content to top
        self.body.addStretch()
        
    def on_config_changed(self):
        new_ip = self.ip_input.text().strip()
        port_text = self.port_input.text().strip()
        new_port = int(port_text) if port_text else 5000
        
        config = self.ftp_manager.config_manager.config
        
        if config.ftp_ip != new_ip or config.ftp_port != new_port:
            self.append_log(f"Config changed: IP={new_ip if new_ip else 'Auto Scan'}, Port={new_port}. Reconnecting...")
            config.ftp_ip = new_ip
            config.ftp_port = new_port
            self.ftp_manager.config_manager.save()
            self.ftp_manager.check_connection()
        
    def on_connection_status_changed(self, connected: bool, msg: str):
        self.sync_button.setEnabled(connected)
        self.stale_button.setEnabled(connected)
        
        # Update Status Indicator
        # Green = Connected
        # Yellow = Searching/Connecting
        # Red = Error/Not Found
        # Grey = Idle
        
        color = "#9E9E9E" # Grey
        if connected:
            color = "#4CAF50" # Green
        elif msg == "Searching..." or "Connecting" in msg:
             color = "#FFC107" # Amber
        elif "Not Found" in msg or "Error" in msg:
             color = "#F44336" # Red
             
        self.status_indicator.setStyleSheet(f"background-color: {color}; border-radius: 6px;")
        self.status_indicator.setToolTip(f"Status: {msg}")
        self.status_text.setText(msg)
             
    def on_retry_clicked(self):
        self.ftp_manager.check_connection()
        
    def on_scan_clicked(self):
        self.log_output.clear()
        self.append_log("Starting scan...")
        self.sync_button.setEnabled(False)
        self.stale_button.setEnabled(False)
        self.mode_combo.setEnabled(False)
        
        sync_all = self.mode_combo.currentIndex() == 1
        self.ftp_manager.start_scan(sync_all=sync_all)
        self.options_group.hide()

    def on_stale_clicked(self):
        self.log_output.clear()
        self.append_log("Scanning for stale mods...")
        self.sync_button.setEnabled(False)
        self.stale_button.setEnabled(False)
        self.mode_combo.setEnabled(False)
        
        self.ftp_manager.start_stale_scan()
        self.options_group.hide()
        
    def append_log(self, msg: str):
        self.log_output.append(msg)
        # Scroll to bottom
        cursor = self.log_output.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_output.setTextCursor(cursor)
        
    def update_progress(self, value: float):
        self.progress_bar.setValue(int(value * 100))
        
    def on_sync_started(self):
        self.sync_button.setEnabled(False)
        self.stale_button.setEnabled(False)
        self.sync_button.setText("Syncing...")
        self.progress_bar.setValue(0)
        self.mode_combo.setEnabled(False)
        
    def on_sync_finished(self, success=0, failed=0):
        if hasattr(self, 'sync_configs_pending') and self.sync_configs_pending:
            self.sync_configs_pending = False
            self.append_log("Proceeding to config sync...")
            self.ftp_manager.start_config_sync()
            return

        if hasattr(self, 'is_stale_cleanup') and self.is_stale_cleanup:
            self.is_stale_cleanup = False
            # Special message for cleanup
            total = success + failed
            briefing = f"\n=== Cleanup Completed ===\nDeleted: {success}\nFailed: {failed}"
            self.append_log(briefing)
        else: 
            self.done_button.setVisible(True)
            self.sync_button.setVisible(False)
            self.mode_combo.setVisible(False)
            self.stale_button.setVisible(False)
            self.progress_bar.setValue(100) # Ensure it shows full
            
            # Briefing
            total = success + failed
            briefing = f"\n=== Sync Completed ===\nTotal: {total}\nSuccess: {success}\nFailed: {failed}"
            self.append_log(briefing)
            
        self.done_button.setVisible(True)
        self.sync_button.setVisible(False)
        self.stale_button.setVisible(False)
        self.mode_combo.setVisible(False)
        
        if failed > 0:
            self.append_log("Check log above for error details.")
        
    def on_done_clicked(self):
        # Reset UI
        self.done_button.hide()
        self.sync_button.setVisible(True)
        self.sync_button.setEnabled(True)
        self.sync_button.setText("Start Sync")
        
        self.stale_button.setVisible(True)
        self.stale_button.setEnabled(True)
        
        self.options_group.show()
        
        self.mode_combo.setVisible(True)
        self.mode_combo.setEnabled(True)
        
        # Clear Data
        self.current_diff_map = {}
        self.stale_mods_list = []
        self.match_list.clear() # This clears items + widgets
        self.replace_list.clear()
        self.metadata_list.clear()
        self.missing_list.clear()
        self.stale_list.clear()
        self.list_items.clear()
        
        self.preview_container.hide()
        self.progress_bar.setValue(0)
        self.log_output.clear()
        
        # Clear navigation button progress
        self.ftp_manager.reset_progress()
    
    def on_stale_scan_complete(self, stale_mods: list):
        self.stale_mods_list = stale_mods
        self.sync_button.setVisible(False)
        self.stale_button.setVisible(False)
        self.mode_combo.setVisible(False)
        
        self.confirm_button.setVisible(True)
        self.confirm_button.setText("Delete All") # Change text for clarity
        self.confirm_button.setStyleSheet("""
             QPushButton {
                  background-color: #F44336;
                  color: white;
                  font-weight: bold;
                  border-radius: 5px;
                  padding: 5px 10px;
             }
             QPushButton:hover {
                  background-color: #D32F2F;
             }
        """)
        
        self.cancel_preview_button.setVisible(True)
        
        # Clear other lists
        self.match_list.clear()
        self.replace_list.clear()
        self.metadata_list.clear()
        self.missing_list.clear()
        self.stale_list.clear()
        
        # Populate Stale List
        for mod_name in stale_mods:
            item = QListWidgetItem()
            widget = SyncItemWidget(mod_name)
            self.stale_list.addItem(item)
            self.stale_list.setItemWidget(item, widget)
            
        self.resize_list_to_content(self.stale_list)
        
        # Hide standard boxes, show stale box
        self.match_box.hide()
        self.replace_box.hide()
        self.metadata_box.hide()
        self.missing_box.hide()
        self.stale_box.show()
        
        self.stale_box.set_expanded(True)
        self.stale_box.set_status(f"{len(stale_mods)} mods")
        
        self.preview_container.show()
        
        if not stale_mods:
            self.append_log("No stale mods found.")
            # Auto-done or let user see log?
            self.confirm_button.setEnabled(False) # Nothing to delete

    def on_scan_complete(self, diff_map: dict):
        self.current_diff_map = diff_map
        self.sync_button.setVisible(False)
        self.stale_button.setVisible(False)
        self.mode_combo.setVisible(False)
        self.done_button.hide() # Ensure hidden on new scan
        
        # Reset confirm button style
        self.confirm_button.setText("Confirm")
        self.confirm_button.setStyleSheet("""
            QPushButton {
                 background-color: #4CAF50;
                 color: white;
                 font-weight: bold;
                 border-radius: 5px;
                 padding: 5px 10px;
            }
            QPushButton:hover {
                 background-color: #45a049;
            }
             QPushButton:pressed {
                background-color: #388E3C; 
            }
        """)
        self.confirm_button.setEnabled(True)
        
        # Show confirm controls
        self.confirm_button.setVisible(True)
        self.cancel_preview_button.setVisible(True)
        
        if not diff_map:
            self.append_log("Scan failed or no mods found.")
            return
            
        # Clear lists
        self.match_list.clear()
        self.replace_list.clear()
        self.metadata_list.clear()
        self.missing_list.clear()
        self.stale_list.clear()
        
        # Categorize
        self.list_items = {} # Map mod_name -> SyncItemWidget
        
        for folder, status in diff_map.items():
            mod_name = os.path.basename(folder)
            item = QListWidgetItem()
            widget = SyncItemWidget(mod_name)
            
            # Keep track for updates
            self.list_items[mod_name] = widget
            
            if status == "MATCH":
                self.match_list.addItem(item)
                self.match_list.setItemWidget(item, widget)
            elif status == "REPLACE":
                self.replace_list.addItem(item)
                self.replace_list.setItemWidget(item, widget)
            elif status == "METADATA_ONLY":
                self.metadata_list.addItem(item)
                self.metadata_list.setItemWidget(item, widget)
            elif status == "MISSING":
                self.missing_list.addItem(item)
                self.missing_list.setItemWidget(item, widget)
                
        # Adjust heights based on content
        
        # Adjust heights based on content
        self.resize_list_to_content(self.match_list)
        self.resize_list_to_content(self.replace_list)
        self.resize_list_to_content(self.metadata_list)
        self.resize_list_to_content(self.missing_list)
                
        # Show preview
        self.preview_container.show()
        self.match_box.show()
        self.replace_box.show()
        self.metadata_box.show()
        self.missing_box.show()
        self.stale_box.hide()
        
        # Update Collapsible States
        self.match_box.set_expanded(self.match_list.count() > 0)
        self.match_box.set_status(f"{self.match_list.count()} mods")
        
        self.replace_box.set_expanded(self.replace_list.count() > 0)
        self.replace_box.set_status(f"{self.replace_list.count()} mods")
        
        self.metadata_box.set_expanded(self.metadata_list.count() > 0)
        self.metadata_box.set_status(f"{self.metadata_list.count()} mods")
        
        self.missing_box.set_expanded(self.missing_list.count() > 0)
        self.missing_box.set_status(f"{self.missing_list.count()} mods")
        
        self.append_log(f"Scan complete. {len(diff_map)} mods analyzed.")
        
    def on_confirm_sync_clicked(self):
        # Hide preview controls, show sync button (for status)
        self.confirm_button.setVisible(False)
        self.cancel_preview_button.setVisible(False)
        # self.preview_container.hide() # Keep visible for progress
        self.log_output.clear()
        
        # Re-show sync button so on_sync_started can update it
        self.sync_button.setVisible(True)
        self.mode_combo.setVisible(True)
        self.mode_combo.setEnabled(False) 
        self.sync_configs_check.setEnabled(False)
        
        if self.stale_mods_list:
            # Stale Cleanup Mode
            self.is_stale_cleanup = True
            self.ftp_manager.start_stale_cleanup(self.stale_mods_list)
        else:
            # Normal Sync Mode
            self.is_stale_cleanup = False
            self.sync_configs_pending = self.sync_configs_check.isChecked()
            self.ftp_manager.start_smart_sync(self.current_diff_map)

    def on_config_sync_finished(self, success: bool):
        self.on_sync_finished(success=1 if success else 0, failed=0 if success else 1)
        self.sync_configs_check.setEnabled(True)
        
    def on_cancel_preview_clicked(self):
        self.preview_container.hide()
        self.confirm_button.setVisible(False)
        self.cancel_preview_button.setVisible(False)
        
        self.sync_button.setVisible(True)
        self.stale_button.setVisible(True)
        self.mode_combo.setVisible(True)
        self.sync_button.setEnabled(True)
        self.stale_button.setEnabled(True)
        self.mode_combo.setEnabled(True)
        
        self.options_group.show()
        self.append_log("Preview canceled.")
        self.stale_mods_list = [] # clear stale list
        self.current_diff_map = {}

    def resize_list_to_content(self, list_widget: QListWidget):
        # Calculate total height
        count = list_widget.count()
        if count == 0:
            list_widget.setFixedHeight(0)
            return

        row_height = list_widget.sizeHintForRow(0)
        if row_height < 0: row_height = 20 # Fallback
            
        total_height = (count * row_height) + (2 * list_widget.frameWidth()) + 5 # + padding
        
        list_widget.setFixedHeight(total_height)
        
    def on_mod_progress(self, mod_name: str, progress: float):
        if mod_name in self.list_items:
            self.list_items[mod_name].set_progress(progress)
