from PyQt6.QtCore import QObject, pyqtSignal, QThread
from ftp import SwitchFTP
import os
import traceback

class SyncThread(QThread):
    progress_log = pyqtSignal(str)
    progress_value = pyqtSignal(float)
    finished_signal = pyqtSignal()
    
    def __init__(self, folders, known_ip=None):
        super().__init__()
        self.folders = folders
        self.known_ip = known_ip
        self.is_running = True
        
    def run(self):
        try:
            self.progress_log.emit("Preparing to sync...")
            
            # Count total files for progress calculation
            total_files = 0
            for folder in self.folders:
                if os.path.exists(folder):
                    for _, _, files in os.walk(folder):
                        total_files += len(files)
            
            if total_files == 0:
                self.progress_log.emit("No files to sync.")
                self.finished_signal.emit()
                return

            self.progress_log.emit(f"Found {total_files} files to check.")
            
            ftp = SwitchFTP()
            
            switch_ip = self.known_ip
            if not switch_ip:
                subnet = ftp.get_local_subnet()
                self.progress_log.emit(f"Scanning subnet: {subnet} for port 5000...")
                switch_ip = ftp.find_switch(subnet, lambda msg: self.progress_log.emit(msg))
            
            self.progress_log.emit(f"Connecting to {switch_ip}...")
            
            ftp.connect(switch_ip)
            
            processed_files = 0
            
            def on_progress(msg):
                nonlocal processed_files
                self.progress_log.emit(msg)
                if "Syncing" in msg or "Skipped" in msg:
                    processed_files += 1
                    self.progress_value.emit(processed_files / total_files)
            
            ftp.sync_mod_folders(self.folders, on_progress)
            
            ftp.disconnect()
            self.progress_log.emit("Sync complete!")
            self.progress_value.emit(1.0) # Ensure 100%
            
        except Exception as e:
            self.progress_log.emit(f"Error: {e}")
            traceback.print_exc()
        finally:
            self.finished_signal.emit()

class ConnectionThread(QThread):
    connected = pyqtSignal(str) # ip
    failed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
    def run(self):
        try:
            ftp = SwitchFTP()
            subnet = ftp.get_local_subnet()
            switch_ip = ftp.find_switch(subnet)
            if switch_ip:
                self.connected.emit(switch_ip)
            else:
                self.failed.emit()
        except:
            self.failed.emit()

class FTPManager(QObject):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(float)
    sync_started = pyqtSignal()
    sync_finished = pyqtSignal()
    
    # Connection signals
    connection_status_changed = pyqtSignal(bool, str) # connected, ip/msg
    
    def __init__(self, config_manager, mod_manager):
        super().__init__()
        self.config_manager = config_manager
        self.mod_manager = mod_manager
        self.thread = None
        self.conn_thread = None
        self.current_ip = None
        
        # Auto-connect on startup
        self.check_connection()

    def check_connection(self):
        """Start background connection check"""
        if self.conn_thread and self.conn_thread.isRunning():
            return
            
        self.connection_status_changed.emit(False, "Searching...")
        self.conn_thread = ConnectionThread()
        self.conn_thread.connected.connect(self.on_connected)
        self.conn_thread.failed.connect(self.on_connection_failed)
        self.conn_thread.start()
        
    def on_connected(self, ip):
        self.current_ip = ip
        self.connection_status_changed.emit(True, ip)
        self.conn_thread = None
        
    def on_connection_failed(self):
        self.current_ip = None
        self.connection_status_changed.emit(False, "Not Found")
        self.conn_thread = None

    def start_sync(self):
        if self.thread and self.thread.isRunning():
            return
            
        # Get enabled mods from WorkspaceManager via ModManager
        enabled_ids = self.mod_manager.enabled_ids
        folders = []
        
        for mod_id in enabled_ids:
            mod = self.mod_manager.get_mod(mod_id)
            if mod and mod.path and os.path.exists(mod.path):
                folders.append(mod.path)
        
        if not folders:
            self.log_signal.emit("No enabled mods to sync.")
            return

        self.thread = SyncThread(folders, known_ip=self.current_ip)
        self.thread.progress_log.connect(self.log_signal.emit)
        self.thread.progress_value.connect(self.progress_signal.emit)
        self.thread.finished_signal.connect(self.on_sync_finished)
        
        self.sync_started.emit()
        self.thread.start()
        
    def on_sync_finished(self):
        self.sync_finished.emit()
        self.thread = None
