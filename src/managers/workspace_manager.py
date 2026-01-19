import os
import re
import json
from PyQt6.QtCore import QObject, QThread
from src.utils.file import read_json, write_json, is_valid_file
from src.managers.config_manager import ConfigManager
from src.utils.logger import output_log
from src.core.sync_worker import SyncWorker
from src.models.mod import Mod

class WorkspaceManager(QObject):
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self.workspace_map = {} # Name -> Preset Filename
        self.current_workspace_name = "Default"
        self.enabled_mods = [] # List of mod hashes/IDs
        self.enabled_callbacks = []
        
        self.sync_thread = None
        self.sync_worker = None
        
        self.load()

    @property
    def cache_dir(self):
        return self.config_manager.config.cache_dir

    def load(self):
        if not self.cache_dir:
            return

        # Load workspace list mapping
        workspace_list_path = os.path.join(self.cache_dir, "workspace_list")
        if is_valid_file(workspace_list_path):
            self.workspace_map = read_json(workspace_list_path)
        else:
            # Initialize default if missing
            self.workspace_map = {"Default": "presets"}
            self.save_workspace_list()

        # Load active workspace name
        active_ws_path = os.path.join(self.cache_dir, "workspace")
        workspace_loaded = False
        
        if is_valid_file(active_ws_path):
            try:
                # Read as raw text, no JSON quotes
                with open(active_ws_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                if content:
                    self.current_workspace_name = content
                    workspace_loaded = True
            except:
                output_log("Failed to load active workspace, defaulting to Default")
        
        # Ensure current workspace exists in map, else default
        if self.current_workspace_name not in self.workspace_map:
            self.current_workspace_name = "Default"
            if "Default" not in self.workspace_map:
                self.workspace_map["Default"] = "presets"
            workspace_loaded = False # Force save if we reset
            
        # Create/Update workspace file if it wasn't loaded correctly
        if not workspace_loaded:
            self.save_active_workspace()
        
        self.load_enabled_mods()

    def load_enabled_mods(self):
        preset_filename = self.workspace_map.get(self.current_workspace_name, "presets")
        preset_path = os.path.join(self.cache_dir, preset_filename)
        
        if is_valid_file(preset_path):
            data = read_json(preset_path)
            if isinstance(data, list):
                # Ensure all IDs are strings
                self.enabled_mods = [str(x) for x in data]
            else:
                self.enabled_mods = []
        else:
            self.enabled_mods = []
            
        output_log(f"Loaded workspace '{self.current_workspace_name}' with {len(self.enabled_mods)} enabled mods")

    def _extract_number_from_preset(self, input_str: str) -> str:
        match = re.search(r'_preset(\d+)$', input_str)
        if match:
            return match.group(1)
        return ""

    def save_workspace_list(self):
        if not self.cache_dir: return
        workspace_list_path = os.path.join(self.cache_dir, "workspace_list")
        write_json(workspace_list_path, self.workspace_map)

    def save_active_workspace(self):
        if not self.cache_dir: return
        active_ws_path = os.path.join(self.cache_dir, "workspace")
        try:
            with open(active_ws_path, 'w', encoding='utf-8') as f:
                f.write(self.current_workspace_name)
        except Exception as e:
            output_log(f"Failed to save active workspace: {e}") 

    def save_enabled_mods(self):
        if not self.cache_dir: return
        preset_filename = self.workspace_map.get(self.current_workspace_name, "presets")
        preset_path = os.path.join(self.cache_dir, preset_filename)
        write_json(preset_path, self.enabled_mods)

    # --- Public API ---

    def get_enabled_ids(self) -> list[str]:
        return self.enabled_mods

    def is_enabled(self, mod_id: str) -> bool:
        return str(mod_id) in self.enabled_mods

    def set_enabled(self, mod_id: str, enabled: bool):
        mod_id = str(mod_id) # Ensure string type
        changed = False
        if enabled:
            if mod_id not in self.enabled_mods:
                self.enabled_mods.append(mod_id)
                changed = True
        else:
            if mod_id in self.enabled_mods:
                self.enabled_mods.remove(mod_id)
                changed = True
        
        if changed:
            self.save_enabled_mods()
            self._notify_enabled_changed(mod_id, enabled)

    def toggle_enabled(self, mod_id: str):
        is_enabled = self.is_enabled(mod_id)
        self.set_enabled(mod_id, not is_enabled)

    def add_workspace(self, name: str) -> bool:
        """Add a new workspace"""
        if name in self.workspace_map:
            return False
            
        # Generate filename from name (sanitize)
        clean_name = re.sub(r'[<>:"/\\|?*]', '', name).replace(' ', '_')
        filename = f"preset_{clean_name}"
        
        self.workspace_map[name] = filename
        self.save_workspace_list()
        
        # Create empty preset file
        preset_path = os.path.join(self.cache_dir, filename)
        write_json(preset_path, [])
        return True

    def remove_workspace(self, name: str):
        """Remove a workspace"""
        if name not in self.workspace_map:
            return
            
        filename = self.workspace_map.pop(name)
        self.save_workspace_list()
        
        if self.current_workspace_name == name:
            self.switch_workspace("Default") # Fallback to Default
            
        # Delete file
        preset_path = os.path.join(self.cache_dir, filename)
        if os.path.exists(preset_path):
            try:
                os.remove(preset_path)
            except Exception as e:
                output_log(f"Failed to delete preset file {filename}: {e}")

    def switch_workspace(self, name: str):
        """Switch current active workspace"""
        if name not in self.workspace_map:
            return
            
        self.current_workspace_name = name
        self.save_active_workspace()
        self.load_enabled_mods()
        self.workspace_changed.emit()

    def sync_mods(self, all_mods:dict[str, Mod]):
        """Sync enabled mods to export directory using SyncWorker"""
        enabled_mods_list = [mod for key, mod in all_mods.items() if key in self.enabled_mods]
        export_dir = self.config_manager.config.export_dir
        
        if not export_dir:
            output_log("Export directory not set, skipping sync")
            return
            
        output_log(f"Starting sync of {len(enabled_mods_list)} mods to {export_dir}")
        
        if self.sync_thread and self.sync_thread.isRunning():
            output_log("Sync already in progress")
            return

        self.sync_thread = QThread()
        self.sync_worker = SyncWorker(enabled_mods_list, export_dir)
        self.sync_worker.moveToThread(self.sync_thread)
        
        self.sync_thread.started.connect(self.sync_worker.run)
        # self.sync_thread.started.connect(self.sync_started.emit) # Removed to prevent race condition
        
        self.sync_worker.progress.connect(self.sync_progress.emit)
        self.sync_worker.finished.connect(self._on_sync_finished_internal)
        
        # Connect thread finish for safe cleanup
        self.sync_thread.finished.connect(self._on_thread_finished)
        self.sync_thread.finished.connect(self.sync_thread.deleteLater)
        
        self.sync_started.emit() # Manually emit before start to guarantee order
        self.sync_thread.start()

    def _on_sync_finished_internal(self):
        """Handle worker finish, emit signal, request thread stop"""
        self.sync_finished.emit()
        
        # Only signal the thread to quit, do NOT delete it here
        if self.sync_thread:
            self.sync_thread.quit()
            
        if self.sync_worker:
            self.sync_worker.deleteLater()
            self.sync_worker = None

    def _on_thread_finished(self):
        """Safe thread cleanup after it has truly stopped"""
        self.sync_thread = None

    # --- Signals ---
    from PyQt6.QtCore import pyqtSignal
    workspace_changed = pyqtSignal()
    sync_started = pyqtSignal()
    sync_finished = pyqtSignal()
    sync_progress = pyqtSignal(str, float)
    
    # --- Callbacks ---

    def add_enabled_callback(self, callback: callable):
        self.enabled_callbacks.append(callback)

    def _notify_enabled_changed(self, mod_id: str, is_enabled: bool):
        for callback in self.enabled_callbacks:
            callback(mod_id, is_enabled)
