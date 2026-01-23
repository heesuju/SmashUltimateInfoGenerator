from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel, QProgressBar
from src.ui.components.layout import VBox, HBox
from src.managers.ftp_manager import FTPManager

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
        self.sync_button.setText("Sync Enabled Mods")
        self.status_label.setText("Sync Complete")
