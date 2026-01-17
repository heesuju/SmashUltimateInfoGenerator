from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QProgressBar, QPushButton, 
    QHBoxLayout, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt
from src.ui.components.side_panel import SidePanel
from src.managers.download_manager import DownloadManager
from src.ui.components.layout import HBox, VBox

class DownloadItem(QFrame):
    def __init__(self, name: str, download_id: str):
        super().__init__()
        self.download_id = download_id
        
        self.setObjectName("download_item")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            #download_item {
                background-color: rgba(0, 0, 0, 0.2);
                border-radius: 5px;
            }
        """)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        layout = VBox(margin=10, spacing=5)
        self.setLayout(layout)
        
        # Header
        header = HBox()
        layout.addLayout(header)
        
        self.name_label = QLabel(name)
        self.name_label.setStyleSheet("color: white; font-weight: bold;")
        self.name_label.setWordWrap(True)
        header.addWidget(self.name_label)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(5)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Status
        self.status_label = QLabel("Waiting...")
        self.status_label.setStyleSheet("color: #aaa; font-size: 10px;")
        layout.addWidget(self.status_label)
        
    def update_progress(self, received, total):
        if total > 0:
            percent = int((received / total) * 100)
            self.progress_bar.setValue(percent)
            
            # Convert bytes to MB
            rec_mb = received / (1024 * 1024)
            tot_mb = total / (1024 * 1024)
            self.status_label.setText(f"{rec_mb:.1f} MB / {tot_mb:.1f} MB")
        else:
            self.progress_bar.setValue(0)
            self.status_label.setText("Starting...")
            
    def set_finished(self, success, message):
        if success:
            self.progress_bar.setValue(100)
            self.status_label.setText("Completed")
            self.status_label.setStyleSheet("color: #4ade80; font-size: 10px;") # Green
        else:
            self.progress_bar.setStyleSheet("""
                QProgressBar::chunk { background-color: #ef4444; }
            """)
            self.status_label.setText(f"Error: {message}")
            self.status_label.setStyleSheet("color: #ef4444; font-size: 10px;") # Red

class DownloadPanel(SidePanel):
    def __init__(self, download_manager: DownloadManager):
        super().__init__("Downloads")
        self.download_manager = download_manager
        
        self.items = {} # id -> DownloadItem
        
        # Connect signals
        self.download_manager.download_queued.connect(self.on_download_queued)
        self.download_manager.download_started.connect(self.on_download_started)
        self.download_manager.progress_updated.connect(self.on_progress_updated)
        self.download_manager.download_finished.connect(self.on_download_finished)
        
        self.add_footer_button("Clear Completed", self.clear_completed)
        
        # Add spacer to push items up
        self.body.addStretch(1)

    def on_download_queued(self, download_id, name):
        item = DownloadItem(name, download_id)
        item.status_label.setText("Pending...")
        item.status_label.setStyleSheet("color: #aaa; font-size: 10px;")
        
        # Insert at top
        self.body.insertWidget(0, item)
        self.items[download_id] = item
        
    def on_download_started(self, download_id, name):
        if download_id in self.items:
            item = self.items[download_id]
            item.status_label.setText("Starting...")
        else:
            item = DownloadItem(name, download_id)
            # Insert at top
            self.body.insertWidget(0, item)
            self.items[download_id] = item
        
    def on_progress_updated(self, download_id, received, total):
        if download_id in self.items:
            self.items[download_id].update_progress(received, total)
            
    def on_download_finished(self, download_id, success, message):
        if download_id in self.items:
            self.items[download_id].set_finished(success, message)
            
    def clear_completed(self):
        # Remove finished items (this logic is simple, ideally we track state better)
        to_remove = []
        for id, item in self.items.items():
            if item.status_label.text() == "Completed":
                to_remove.append(id)
                
        for id in to_remove:
            item = self.items.pop(id)
            item.deleteLater()
