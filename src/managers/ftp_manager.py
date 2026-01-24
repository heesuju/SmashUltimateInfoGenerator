from PyQt6.QtCore import QObject, pyqtSignal, QThread
from src.core.ftp import SwitchFTP
import os
import traceback

class SyncThread(QThread):
    progress_log = pyqtSignal(str)
    progress_value = pyqtSignal(float)
    sync_results = pyqtSignal(int, int) # success, fail
    
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
            
            success_count, fail_count = ftp.sync_mod_folders(self.folders, on_progress)
            
            ftp.disconnect()
            self.progress_log.emit("Sync complete!")
            self.progress_value.emit(1.0) # Ensure 100%
            self.sync_results.emit(success_count, fail_count)
            
        except Exception as e:
            self.progress_log.emit(f"Error: {e}")
            traceback.print_exc()
            self.sync_results.emit(0, len(self.folders)) # Assume all failed if exception

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
    progress_log = pyqtSignal(str)
    progress_value = pyqtSignal(float)
    mod_progress = pyqtSignal(str, float) # mod_name, progress (0-1)
    sync_results = pyqtSignal(int, int) # success_count, fail_count
    
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
            success_count = 0
            fail_count = 0
            
            for folder, status in self.diff_map.items():
                mod_name = os.path.basename(folder)
                # ... (Safety checks are here in previous edits, assuming context is preserved) ...
                if not mod_name:
                    self.progress_log.emit(f"Skipping invalid folder path: {folder}")
                    processed += 1
                    fail_count += 1
                    self.progress_value.emit(processed / total_mods)
                    continue
                    
                remote_path = f"/ultimate/mods/{mod_name}"
                
                try:
                    if status == "MATCH":
                        self.progress_log.emit(f"Skipping {mod_name} (Up to date)")
                        processed += 1
                        success_count += 1
                        self.progress_value.emit(processed / total_mods)
                        continue
                    
                    if status == "REPLACE":
                        self.progress_log.emit(f"Replacing {mod_name}...")
                        self.mod_progress.emit(mod_name, 0.0)
                        
                        # 1. Delete Remote
                        ftp.delete_remote_dir(remote_path)
                        
                        # 2. Upload Fresh
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

                    success_count += 1
                    
                except Exception as e:
                    fail_count += 1
                    self.progress_log.emit(f"Error syncing {mod_name}: {e}")
                    traceback.print_exc()
                    
                processed += 1
                self.progress_value.emit(processed / total_mods)

            ftp.disconnect()
            self.progress_log.emit("Smart Sync Complete!")
            self.progress_value.emit(1.0)
            self.sync_results.emit(success_count, fail_count)
            
        except Exception as e:
            self.progress_log.emit(f"Critical Sync Error: {e}")
            traceback.print_exc()
            self.sync_results.emit(success_count, fail_count)

class ConfigSyncThread(QThread):
    progress_log = pyqtSignal(str)
    sync_result = pyqtSignal(bool)
    
    def __init__(self, cache_dir, known_ip=None, port=5000):
        super().__init__()
        self.cache_dir = cache_dir
        self.known_ip = known_ip
        self.port = port
        
    def run(self):
        try:
            from src.core.ftp import SwitchFTP
            self.progress_log.emit("Starting config sync...")
            ftp = SwitchFTP(port=self.port)
            ftp.connect(self.known_ip)
            
            self.progress_log.emit("Searching for remote config directory...")
            remote_config_dir = ftp.find_acropolis_config_dir()
            
            if not remote_config_dir:
                self.progress_log.emit("Could not find ARCropolis config directory on Switch.")
                self.finished_signal.emit(False)
                return
                
            self.progress_log.emit(f"Found config dir: {remote_config_dir}")
            ftp.sync_config_files(self.cache_dir, remote_config_dir, lambda msg: self.progress_log.emit(msg))
            
            ftp.disconnect()
            self.progress_log.emit("Config sync complete!")
            self.sync_result.emit(True)
        except Exception as e:
            self.progress_log.emit(f"Config sync error: {e}")
            import traceback
            traceback.print_exc()
            self.sync_result.emit(False)

class StaleScanThread(QThread):
    progress_log = pyqtSignal(str)
    scan_finished = pyqtSignal(list) # list of stale folder names
    
    def __init__(self, known_mod_names, known_ip=None, port=5000):
        super().__init__()
        self.known_mod_names = set(known_mod_names) # Set for faster lookup
        self.known_ip = known_ip
        self.port = port
        
    def run(self):
        stale_mods = []
        try:
            self.progress_log.emit("Connecting to check for stale mods...")
            ftp = SwitchFTP(port=self.port)
            
            ip = self.known_ip
            if not ip:
                subnet = ftp.get_local_subnet()
                ip = ftp.find_switch(subnet)
            
            if not ip:
                self.progress_log.emit("Could not find Switch.")
                self.scan_finished.emit([])
                return

            ftp.connect(ip)
            
            self.progress_log.emit("Listing remote mods in /ultimate/mods/...")
            
            try:
                # 1. List all folders in /ultimate/mods
                remote_items = []
                try:
                    remote_items = list(ftp.ftp.mlsd("/ultimate/mods"))
                except:
                    # Fallback
                    names = ftp.ftp.nlst("/ultimate/mods")
                    remote_items = [(n, {'type': 'unknown'}) for n in names]

                for name, facts in remote_items:
                    if name in [".", ".."]: continue
                    
                    # Heuristic: If unknown type, treat as potential mod folder
                    is_dir = facts.get('type') == 'dir' or facts.get('type') == 'unknown'
                    
                    if is_dir:
                        # 2. Check if in known list
                        if name not in self.known_mod_names:
                            stale_mods.append(name)
                            
            except Exception as e:
                self.progress_log.emit(f"Error listing remote directory: {e}")

            ftp.disconnect()
            self.progress_log.emit(f"Scan complete. Found {len(stale_mods)} stale mods.")
            self.scan_finished.emit(stale_mods)
            
        except Exception as e:
            self.progress_log.emit(f"Stale Scan Error: {e}")
            import traceback
            traceback.print_exc()
            self.scan_finished.emit([])

class StaleCleanupThread(QThread):
    progress_log = pyqtSignal(str)
    progress_value = pyqtSignal(float)
    cleanup_finished = pyqtSignal(int, int) # success, fail
    
    def __init__(self, folders_to_delete, known_ip=None, port=5000):
        super().__init__()
        self.folders_to_delete = folders_to_delete
        self.known_ip = known_ip
        self.port = port
        
    def run(self):
        success = 0
        fail = 0
        try:
            self.progress_log.emit("Connecting for cleanup...")
            ftp = SwitchFTP(port=self.port)
            ftp.connect(self.known_ip)
            
            total = len(self.folders_to_delete)
            
            for i, folder_name in enumerate(self.folders_to_delete):
                self.progress_log.emit(f"Deleting {folder_name} ({i+1}/{total})...")
                remote_path = f"/ultimate/mods/{folder_name}"
                
                try:
                    ftp.delete_remote_dir(remote_path)
                    success += 1
                except Exception as e:
                    self.progress_log.emit(f"Failed to delete {folder_name}: {e}")
                    fail += 1
                
                self.progress_value.emit((i + 1) / total)
                
            ftp.disconnect()
            self.progress_log.emit("Cleanup complete!")
            self.cleanup_finished.emit(success, fail)
            
        except Exception as e:
            self.progress_log.emit(f"Cleanup Error: {e}")
            self.cleanup_finished.emit(success, len(self.folders_to_delete) - success)

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
                except:
                    found_ip = None
            
            if not found_ip and not self.target_ip:
                subnet = ftp.get_local_subnet()
                found_ip = ftp.find_switch(subnet)
                
            if found_ip:
                self.connected.emit(found_ip)
            else:
                self.failed.emit()
        except:
            self.failed.emit()

class MonitorThread(QThread):
    status_changed = pyqtSignal(bool, str) # connected, ip/msg
    
    def __init__(self, manager, interval=15):
        super().__init__()
        self.manager = manager
        self.interval = interval
        self.is_running = True
        
    def run(self):
        import time
        while self.is_running:
            try:
                # Sleep first
                for _ in range(self.interval):
                    if not self.is_running: return
                    time.sleep(1)
                    
                if (self.manager.thread and self.manager.thread.isRunning()) or \
                   (self.manager.conn_thread and self.manager.conn_thread.isRunning()):
                    continue
                    
                # Check connection
                config = self.manager.config_manager.config
                target_ip = self.manager.current_ip or config.ftp_ip
                port = config.ftp_port or 5000
                
                if not target_ip:
                    continue
                    
                # Efficient check
                if SwitchFTP.is_reachable(target_ip, port=port, timeout=2.0):
                     self.status_changed.emit(True, target_ip)
                else:
                     self.status_changed.emit(False, "Connection Lost")
                    
            except Exception:
                pass
    
    def stop(self):
        self.is_running = False
        self.wait()

    def __del__(self):
        self.wait()

class FTPManager(QObject):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(float)
    mod_progress = pyqtSignal(str, float)
    sync_started = pyqtSignal()
    sync_finished = pyqtSignal(int, int)
    
    config_sync_started = pyqtSignal()
    config_sync_finished = pyqtSignal(bool)
    
    # Connection signals
    connection_status_changed = pyqtSignal(bool, str) # connected, ip/msg
    
    def __init__(self, config_manager, mod_manager):
        super().__init__()
        self.config_manager = config_manager
        self.mod_manager = mod_manager
        self.thread = None
        self.conn_thread = None
        self.current_ip = None
        self.monitor_thread = None
        self._temp_result = None
        
        # Auto-connect on startup
        self.check_connection()
        
        # Start Monitor
        self.monitor_thread = MonitorThread(self)
        self.monitor_thread.status_changed.connect(self.on_monitor_status)
        self.monitor_thread.start()

    def on_monitor_status(self, connected, msg):
        if not connected:
            self.current_ip = None
        self.connection_status_changed.emit(connected, msg)

    def stop(self):
        """Stop all background operations"""
        if self.monitor_thread:
            self.monitor_thread.stop()
        if self.thread and self.thread.isRunning():
            self.thread.terminate() # Risky but needed on hard exit
            self.thread.wait()

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
        
    def _cleanup_thread(self):
        """Generic cleanup for main worker thread"""
        if self.thread:
            self.thread = None
            
    def _store_sync_results(self, s, f):
        self._temp_result = (s, f)
        
    def _finalize_sync(self):
        self._cleanup_thread()
        if self._temp_result:
            self.sync_finished.emit(*self._temp_result)
        else:
            self.sync_finished.emit(0, 0)
        self._temp_result = None

    def _store_scan_results(self, r):
        self._temp_result = r

    def _finalize_scan(self):
        self._cleanup_thread()
        if self._temp_result is not None:
            self.scan_complete.emit(self._temp_result)
        else:
            self.scan_complete.emit({})
        self._temp_result = None

    def _store_config_result(self, s):
        self._temp_result = s
        
    def _finalize_config_sync(self):
        self._cleanup_thread()
        if self._temp_result is not None:
            self.config_sync_finished.emit(self._temp_result)
        else:
            self.config_sync_finished.emit(False)
        self._temp_result = None

    def _cleanup_conn_thread(self):
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
        # Use built-in finished for cleanup, custom signal for result
        self.thread.sync_results.connect(self._store_sync_results)
        self.thread.finished.connect(self._finalize_sync)
        
        self.sync_started.emit()
        self.thread.start()
        
    # ---------- Smart Sync API ----------
    
    scan_complete = pyqtSignal(dict) # {folder: status}
    stale_scan_complete = pyqtSignal(list) # [folder_names]
    
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
        self.thread.scan_finished.connect(self._store_scan_results)
        self.thread.finished.connect(self._finalize_scan)
        self.thread.start()

    def start_stale_scan(self):
        """Start scanning for stale mods (remote folders not in local enabled list)"""
        if self.thread and self.thread.isRunning():
            self.log_signal.emit("Another operation in progress.")
            return

        # 1. Gather all local mod folder names
        all_mod_ids = self.mod_manager.mods.keys()
        known_names = []
        for mod_id in all_mod_ids:
            mod = self.mod_manager.get_mod(mod_id)
            if mod:
                if mod.path:
                    known_names.append(os.path.basename(mod.path))

        port = self.config_manager.config.ftp_port or 5000
        self.thread = StaleScanThread(known_names, known_ip=self.current_ip, port=port)
        self.thread.progress_log.connect(self.log_signal.emit)
        
        self.thread.scan_finished.connect(self._store_stale_results)
        self.thread.finished.connect(self._finalize_stale_scan)
        self.thread.start()

    def start_stale_cleanup(self, folders_to_delete: list):
        """Start deleting specified stale folders"""
        if self.thread and self.thread.isRunning():
            self.log_signal.emit("Another operation in progress.")
            return
            
        port = self.config_manager.config.ftp_port or 5000
        self.thread = StaleCleanupThread(folders_to_delete, known_ip=self.current_ip, port=port)
        self.thread.progress_log.connect(self.log_signal.emit)
        self.thread.progress_value.connect(self.progress_signal.emit)
        self.thread.cleanup_finished.connect(self._store_sync_results) # Reuse sync results (success/fail ints)
        self.thread.finished.connect(self._finalize_sync) # Reuse finalize sync
        
        self.sync_started.emit() # Re-use sync started signal to lock UI
        self.thread.start()

    def _store_stale_results(self, r):
        self._temp_result = r
        
    def _finalize_stale_scan(self):
        self._cleanup_thread()
        if self._temp_result is not None:
            self.stale_scan_complete.emit(self._temp_result)
        else:
            self.stale_scan_complete.emit([])
        self._temp_result = None
        
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
        self.thread.sync_results.connect(self._store_sync_results)
        self.thread.finished.connect(self._finalize_sync)
        
        self.sync_started.emit()
        self.thread.start()

    def start_config_sync(self):
        """Sync configuration files (presets, workspaces)"""
        if self.thread and self.thread.isRunning():
            self.log_signal.emit("Another operation in progress.")
            return

        cache_dir = self.config_manager.config.cache_dir
        if not cache_dir:
            self.log_signal.emit("Cache directory not set.")
            return

        port = self.config_manager.config.ftp_port or 5000
        self.thread = ConfigSyncThread(cache_dir, known_ip=self.current_ip, port=port)
        self.thread.progress_log.connect(self.log_signal.emit)
        self.thread.sync_result.connect(self._store_config_result)
        self.thread.finished.connect(self._finalize_config_sync)
        
        self.config_sync_started.emit()
        self.thread.start()
