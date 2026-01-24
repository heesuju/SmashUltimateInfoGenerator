from PyQt6.QtCore import QObject, pyqtSignal, QThread
from ftp import SwitchFTP
import os
import traceback

class SyncThread(QThread):
    progress_log = pyqtSignal(str)
    progress_value = pyqtSignal(float)
    finished_signal = pyqtSignal()
    
    def __init__(self, folders, known_ip=None, port=5000):
        super().__init__()
        self.folders = folders
        self.known_ip = known_ip
        self.port = port
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
            
            ftp = SwitchFTP(port=self.port)
            
            switch_ip = self.known_ip
            if not switch_ip:
                subnet = ftp.get_local_subnet()
                self.progress_log.emit(f"Scanning subnet: {subnet} for port {self.port}...")
                switch_ip = ftp.find_switch(subnet, lambda msg: self.progress_log.emit(msg))
            
            self.progress_log.emit(f"Connecting to {switch_ip}:{self.port}...")
            
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

class ScanThread(QThread):
    progress_log = pyqtSignal(str)
    scan_finished = pyqtSignal(dict) # {mod_path: status}
    
    def __init__(self, folders, known_ip=None, port=5000):
        super().__init__()
        self.folders = folders
        self.known_ip = known_ip
        self.port = port
        
    def run(self):
        results = {}
        try:
            self.progress_log.emit("Connecting for scan...")
            ftp = SwitchFTP(port=self.port)
            
            # Connect
            ip = self.known_ip
            if not ip:
                subnet = ftp.get_local_subnet()
                ip = ftp.find_switch(subnet)
            
            if not ip:
                self.progress_log.emit("Could not find Switch.")
                self.scan_finished.emit({})
                return
                
            ftp.connect(ip)
            
            total = len(self.folders)
            for i, folder in enumerate(self.folders):
                mod_name = os.path.basename(folder)
                self.progress_log.emit(f"Scanning {mod_name} ({i+1}/{total})...")
                
                status = ftp.scan_mod_diff(folder, "/ultimate/mods")
                results[folder] = status
                
            ftp.disconnect()
            self.scan_finished.emit(results)
            
        except Exception as e:
            self.progress_log.emit(f"Scan Error: {e}")
            traceback.print_exc()
            self.scan_finished.emit({})

class SmartSyncThread(QThread):
    progress_log = pyqtSignal(str)
    progress_value = pyqtSignal(float)
    mod_progress = pyqtSignal(str, float) # mod_name, progress (0-1)
    finished_signal = pyqtSignal()
    
    def __init__(self, diff_map: dict, known_ip=None, port=5000):
        super().__init__()
        self.diff_map = diff_map
        self.known_ip = known_ip
        self.port = port
        
    def run(self):
        try:
            ftp = SwitchFTP(port=self.port)
            ip = self.known_ip
            if not ip:
                # Should be known by now, but fallback
                subnet = ftp.get_local_subnet()
                ip = ftp.find_switch(subnet)
                
            ftp.connect(ip)
            
            total_mods = len(self.diff_map)
            processed = 0
            
            for folder, status in self.diff_map.items():
                mod_name = os.path.basename(folder)
                remote_path = f"/ultimate/mods/{mod_name}"
                
                if status == "MATCH":
                    self.progress_log.emit(f"Skipping {mod_name} (Up to date)")
                    processed += 1
                    self.progress_value.emit(processed / total_mods)
                    continue
                
                if status == "REPLACE":
                    self.progress_log.emit(f"Replacing {mod_name}...")
                    self.mod_progress.emit(mod_name, 0.0)
                    
                    # 1. Delete Remote
                    ftp.delete_remote_dir(remote_path)
                    
                    # 2. Upload Fresh
                    # Count total files for progress
                    total_files = 0
                    for _, _, files in os.walk(folder):
                        total_files += len(files)
                    
                    processed_files = 0
                    
                    def on_file_prog(msg):
                        nonlocal processed_files
                        self.progress_log.emit(msg)
                        if "Syncing" in msg or "Skipped" in msg:
                            processed_files += 1
                            if total_files > 0:
                                self.mod_progress.emit(mod_name, processed_files / total_files)
                        
                    ftp.sync_dir(folder, remote_path, on_file_prog)
                    self.mod_progress.emit(mod_name, 1.0)
                    
                elif status in ["METADATA_ONLY", "MISSING"]:
                    action = "Updating metadata" if status == "METADATA_ONLY" else "Uploading"
                    self.progress_log.emit(f"{action} {mod_name}...")
                    self.mod_progress.emit(mod_name, 0.0)
                    
                    # Count total files
                    total_files = 0
                    for _, _, files in os.walk(folder):
                        total_files += len(files)
                        
                    processed_files = 0
                    
                    def on_file_prog(msg):
                        nonlocal processed_files
                        self.progress_log.emit(msg)
                        if "Syncing" in msg or "Skipped" in msg:
                            processed_files += 1
                            if total_files > 0:
                                self.mod_progress.emit(mod_name, processed_files / total_files)
                        
                    ftp.sync_dir(folder, remote_path, on_file_prog)
                    self.mod_progress.emit(mod_name, 1.0)

                processed += 1
                self.progress_value.emit(processed / total_mods)

            ftp.disconnect()
            self.progress_log.emit("Smart Sync Complete!")
            self.progress_value.emit(1.0)
            
        except Exception as e:
            self.progress_log.emit(f"Sync Error: {e}")
            traceback.print_exc()
        finally:
            self.finished_signal.emit()

class ConnectionThread(QThread):
    connected = pyqtSignal(str) # ip
    failed = pyqtSignal()
    
    def __init__(self, target_ip=None, port=5000):
        super().__init__()
        self.target_ip = target_ip
        self.port = port
        
    def run(self):
        try:
            ftp = SwitchFTP(port=self.port)
            found_ip = None
            if self.target_ip:
                try:
                    ftp.connect(self.target_ip)
                    ftp.disconnect()
                    found_ip = self.target_ip
                except:found_ip = None
            
            if not found_ip and not self.target_ip:
                subnet = ftp.get_local_subnet()
                found_ip = ftp.find_switch(subnet)
                
            if found_ip:
                self.connected.emit(found_ip)
            else:
                self.failed.emit()
        except:
            self.failed.emit()

class FTPManager(QObject):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(float)
    mod_progress = pyqtSignal(str, float)
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
            
        config = self.config_manager.config
        target_ip = config.ftp_ip if config.ftp_ip else None
        port = config.ftp_port or 5000
        
        self.connection_status_changed.emit(False, "Searching..." if not target_ip else f"Connecting to {target_ip}...")
        self.conn_thread = ConnectionThread(target_ip=target_ip, port=port)
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

    def reset_progress(self):
        """Reset progress indicators (e.g. set nav button to -1)"""
        self.progress_signal.emit(-1.0)

    def start_sync(self, sync_all: bool = False):
        if self.thread and self.thread.isRunning():
            return
            
        # Get mods based on sync mode
        if sync_all:
            target_ids = list(self.mod_manager.mods.keys())
        else:
            target_ids = self.mod_manager.enabled_ids
            
        folders = []
        
        for mod_id in target_ids:
            mod = self.mod_manager.get_mod(mod_id)
            if mod and mod.path and os.path.exists(mod.path):
                folders.append(mod.path)
        
        if not folders:
            msg = "No mods found to sync." if sync_all else "No enabled mods to sync."
            self.log_signal.emit(msg)
            return

        port = self.config_manager.config.ftp_port or 5000
        self.thread = SyncThread(folders, known_ip=self.current_ip, port=port)
        self.thread.progress_log.connect(self.log_signal.emit)
        self.thread.progress_value.connect(self.progress_signal.emit)
        self.thread.finished_signal.connect(self.on_sync_finished)
        
        self.sync_started.emit()
        self.thread.start()
        
    def on_sync_finished(self):
        self.sync_finished.emit()
        self.thread = None
        
    # ---------- Smart Sync API ----------
    
    scan_complete = pyqtSignal(dict) # {folder: status}
    
    def start_scan(self, sync_all: bool = False):
        """Scan mods and return status for each"""
        if self.thread and self.thread.isRunning():
            self.log_signal.emit("Sync in progress, cannot scan.")
            return
            
        # Get target mods
        if sync_all:
            target_ids = list(self.mod_manager.mods.keys())
        else:
            target_ids = self.mod_manager.enabled_ids
            
        folders = []
        
        for mod_id in target_ids:
            mod = self.mod_manager.get_mod(mod_id)
            if mod and mod.path and os.path.exists(mod.path):
                folders.append(mod.path)
        
        if not folders:
            msg = "No mods found to scan." if sync_all else "No enabled mods to scan."
            self.log_signal.emit(msg)
            self.scan_complete.emit({})
            return
            
        port = self.config_manager.config.ftp_port or 5000
        self.thread = ScanThread(folders, known_ip=self.current_ip, port=port)
        self.thread.progress_log.connect(self.log_signal.emit)
        self.thread.scan_finished.connect(self._on_scan_finished)
        self.thread.start()
        
    def _on_scan_finished(self, results):
        self.scan_complete.emit(results)
        self.thread = None
        
    def start_smart_sync(self, diff_map: dict):
        """Execute smart sync based on pre-calculated diff map"""
        if self.thread and self.thread.isRunning():
            return
            
        if not diff_map:
            self.log_signal.emit("Nothing to sync.")
            return
            
        port = self.config_manager.config.ftp_port or 5000
        self.thread = SmartSyncThread(diff_map, known_ip=self.current_ip, port=port)
        self.thread.progress_log.connect(self.log_signal.emit)
        self.thread.progress_value.connect(self.progress_signal.emit)
        self.thread.mod_progress.connect(self.mod_progress.emit)
        self.thread.finished_signal.connect(self.on_sync_finished)
        
        self.sync_started.emit()
        self.thread.start()

