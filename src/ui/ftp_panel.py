from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QPushButton, 
                             QLabel, QProgressBar, QListWidget, QListWidgetItem,
                             QGroupBox)
from src.ui.components.layout import VBox, HBox
from src.managers.ftp_manager import FTPManager
import os

class FTPPanel(QWidget):
    def __init__(self, ftp_manager: FTPManager):
        super().__init__()
        self.ftp_manager = ftp_manager
        
        layout = VBox()
        
        # Header / Status
        self.status_label = QLabel("FTP Sync")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(self.status_label)
        
        # Controls
        controls = HBox()
        
        self.preview_button = QPushButton("Preview Sync")
        self.preview_button.clicked.connect(self.on_preview_clicked)
        self.preview_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #aaa;
            }
        """)
        controls.addWidget(self.preview_button)
        
        self.sync_button = QPushButton("Sync Enabled Mods")
        self.sync_button.clicked.connect(self.on_sync_clicked)
        # Style the button a bit
        self.sync_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #aaa;
            }
        """)
        controls.addWidget(self.sync_button)
        controls.addStretch()
        layout.addLayout(controls)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
        # Preview Container (initially hidden)
        self.preview_container = QGroupBox("Sync Preview")
        preview_layout = VBox()
        
        # Categories
        self.match_list = QListWidget()
        self.replace_list = QListWidget()
        self.metadata_list = QListWidget()
        self.missing_list = QListWidget()
        
        # Add lists with labels
        match_box = QGroupBox("✓ Up to Date")
        match_box_layout = VBox()
        match_box_layout.addWidget(self.match_list)
        match_box.setLayout(match_box_layout)
        preview_layout.addWidget(match_box)
        
        replace_box = QGroupBox("🔄 Replace (Full Re-upload)")
        replace_box_layout = VBox()
        replace_box_layout.addWidget(self.replace_list)
        replace_box.setLayout(replace_box_layout)
        preview_layout.addWidget(replace_box)
        
        metadata_box = QGroupBox("📝 Update Metadata Only")
        metadata_box_layout = VBox()
        metadata_box_layout.addWidget(self.metadata_list)
        metadata_box.setLayout(metadata_box_layout)
        preview_layout.addWidget(metadata_box)
        
        missing_box = QGroupBox("➕ New Mods")
        missing_box_layout = VBox()
        missing_box_layout.addWidget(self.missing_list)
        missing_box.setLayout(missing_box_layout)
        preview_layout.addWidget(missing_box)
        
        # Confirm button
        confirm_controls = HBox()
        self.confirm_button = QPushButton("Confirm & Start Sync")
        self.confirm_button.clicked.connect(self.on_confirm_sync_clicked)
        self.confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        confirm_controls.addWidget(self.confirm_button)
        
        self.cancel_preview_button = QPushButton("Cancel")
        self.cancel_preview_button.clicked.connect(self.on_cancel_preview_clicked)
        confirm_controls.addWidget(self.cancel_preview_button)
        confirm_controls.addStretch()
        preview_layout.addLayout(confirm_controls)
        
        self.preview_container.setLayout(preview_layout)
        self.preview_container.hide()
        layout.addWidget(self.preview_container)
        
        # Log Output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("font-family: Consolas, monospace; font-size: 12px;")
        layout.addWidget(self.log_output)
        
        self.setLayout(layout)
        
        # Retry Button (initially hidden or visible?)
        self.retry_button = QPushButton("Retry Connection")
        self.retry_button.clicked.connect(self.on_retry_clicked)
        self.retry_button.setStyleSheet("""
             QPushButton {
                background-color: #607D8B;
                color: white;
                padding: 4px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #546E7A;
            }
        """)
        self.retry_button.hide()
        controls.addWidget(self.retry_button)
        
        # Connect signals
        self.ftp_manager.log_signal.connect(self.append_log)
        self.ftp_manager.progress_signal.connect(self.update_progress)
        self.ftp_manager.sync_started.connect(self.on_sync_started)
        self.ftp_manager.sync_finished.connect(self.on_sync_finished)
        self.ftp_manager.connection_status_changed.connect(self.on_connection_status_changed)
        self.ftp_manager.scan_complete.connect(self.on_scan_complete)
        
        # Store diff map for confirmation
        self.current_diff_map = {}
        
    def on_connection_status_changed(self, connected: bool, msg: str):
        self.status_label.setText(f"Status: {msg}")
        self.sync_button.setEnabled(connected)
        
        if not connected and msg != "Searching...":
             self.retry_button.show()
             self.sync_button.setText("Sync Enabled Mods (Offline)")
        elif connected:
             self.retry_button.hide()
             self.sync_button.setText("Sync Enabled Mods")
        else: # Searching
             self.retry_button.hide()
             self.sync_button.setEnabled(False)
             
    def on_retry_clicked(self):
        self.ftp_manager.check_connection()
        
    def on_sync_clicked(self):
        self.log_output.clear()
        self.ftp_manager.start_sync()
        
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
        self.sync_button.setText("Syncing...")
        self.status_label.setText("Syncing with Switch...")
        self.progress_bar.setValue(0)
        
    def on_sync_finished(self):
        self.sync_button.setEnabled(True)
        self.preview_button.setEnabled(True)
        self.sync_button.setText("Sync Enabled Mods")
        self.status_label.setText("Sync Complete")
        
    def on_preview_clicked(self):
        self.log_output.clear()
        self.append_log("Starting scan...")
        self.preview_button.setEnabled(False)
        self.sync_button.setEnabled(False)
        self.ftp_manager.start_scan()
        
    def on_scan_complete(self, diff_map: dict):
        self.current_diff_map = diff_map
        self.preview_button.setEnabled(True)
        self.sync_button.setEnabled(True)
        
        if not diff_map:
            self.append_log("Scan failed or no mods found.")
            return
            
        # Clear lists
        self.match_list.clear()
        self.replace_list.clear()
        self.metadata_list.clear()
        self.missing_list.clear()
        
        # Categorize
        for folder, status in diff_map.items():
            mod_name = os.path.basename(folder)
            
            if status == "MATCH":
                self.match_list.addItem(mod_name)
            elif status == "REPLACE":
                self.replace_list.addItem(mod_name)
            elif status == "METADATA_ONLY":
                self.metadata_list.addItem(mod_name)
            elif status == "MISSING":
                self.missing_list.addItem(mod_name)
                
        # Show preview
        self.preview_container.show()
        self.append_log(f"Scan complete. {len(diff_map)} mods analyzed.")
        
    def on_confirm_sync_clicked(self):
        # Hide preview, start sync
        self.preview_container.hide()
        self.log_output.clear()
        self.ftp_manager.start_smart_sync(self.current_diff_map)
        
    def on_cancel_preview_clicked(self):
        self.preview_container.hide()
        self.append_log("Preview canceled.")
