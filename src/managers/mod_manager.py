import os
import shutil
from typing import Union, List
from PyQt6.QtCore import QObject, pyqtSignal
from src.core.mod_loader import ModLoader
from src.core.mod_installer import ModInstaller
from src.managers.config_manager import ConfigManager
from src.managers.workspace_manager import WorkspaceManager
from src.models.mod import Mod
from src.utils.logger import output_log
from src.managers.cache_manager import CacheManager

class ModManager(QObject):
    # Signals
    selection_changed = pyqtSignal(list)
    install_started = pyqtSignal()
    install_finished = pyqtSignal()

    def __init__(self, config_manager:ConfigManager, workspace_manager:WorkspaceManager):
        super().__init__()
        self.config_manager = config_manager
        self.workspace_manager = workspace_manager
        self.mods = {}
        self.focused_id = ""
        self.selected_ids = []
        self.callback = None
        self.focus_callbacks = []
        self._current_loader = None # Prevent GC of active loader

        # Register callback for workspace changes
        self.workspace_manager.add_enabled_callback(self._on_workspace_enabled_changed)
        self.workspace_manager.workspace_changed.connect(self._on_workspace_changed)

    @property
    def favorite_ids(self):
        return self.config_manager.config.favorites

    @property
    def hidden_ids(self):
        return self.config_manager.config.hidden_folders

    @property
    def enabled_ids(self):
        return self.workspace_manager.get_enabled_ids()

    def set_callback(self, callback:callable):
        self.callback = callback

    def add_focus_callback(self, callback:callable):
        self.focus_callbacks.append(callback)

    def add_favorite_callback(self, callback:callable):
        if not hasattr(self, 'favorite_callbacks'):
            self.favorite_callbacks = []
        self.favorite_callbacks.append(callback)
    
    def _notify_favorite_changed(self, mod_id:str, is_favorite:bool):
        if hasattr(self, 'favorite_callbacks'):
            for callback in self.favorite_callbacks:
                callback(mod_id, is_favorite)

    def add_hidden_callback(self, callback:callable):
        if not hasattr(self, 'hidden_callbacks'):
            self.hidden_callbacks = []
        self.hidden_callbacks.append(callback)

    def _notify_hidden_changed(self, mod_id:str, is_hidden:bool):
        if hasattr(self, 'hidden_callbacks'):
            for callback in self.hidden_callbacks:
                callback(mod_id, is_hidden)

    def add_enabled_callback(self, callback:callable):
        if not hasattr(self, 'enabled_callbacks'):
            self.enabled_callbacks = []
        self.enabled_callbacks.append(callback)

    def _notify_enabled_changed(self, mod_id:str, is_enabled:bool):
        if hasattr(self, 'enabled_callbacks'):
            for callback in self.enabled_callbacks:
                callback(mod_id, is_enabled)
    
    def _on_workspace_enabled_changed(self, mod_id:str, is_enabled:bool):
        # Propagate to callbacks
        self._notify_enabled_changed(mod_id, is_enabled)

    def _on_workspace_changed(self):
        """Called when workspace is switched/reloaded"""
        if self.callback:
            self.callback()

    def scan(self, scan_target:Union[str, List[str]]):
        # Keep reference to prevent GC
        self._current_loader = ModLoader(scan_target)
        self._current_loader.load_mods(self.on_progress, self.on_complete)

    def scan_all(self):
        self.mods = {}
        root_dir = self.config_manager.config.root_dir
        
        if not root_dir:
            return 
        
        if os.path.exists(root_dir):
            mod_folders = [os.path.join(root_dir, name) for name in os.listdir(root_dir)]
            self.scan(mod_folders)

    def add_mod_from_path(self, path:Union[str, List[str]]):
        """Add mod(s) from folder(s) or zip file(s)"""
        root_dir = self.config_manager.config.root_dir
        if not root_dir:
            return
            
        output_log(f"Adding mod from: {path}")
        self.install_started.emit()
        # Keep reference to installer to prevent GC/early termination
        self._current_installer = ModInstaller(
            directory=path,
            root_dir=root_dir,
            on_finish=None
        )
        self._current_installer.install_finished.connect(self._on_mod_install_finish)
        self._current_installer.start()
    
    def _on_mod_install_finish(self, new_paths:List[str]):
        """Callback when ModInstaller finishes"""
        if not new_paths:
            self.install_finished.emit()
            return
            
        # Scan the newly added mods
        self._current_loader = ModLoader(new_paths)
        self._current_loader.load_mods(self.on_progress, self.on_complete)

    def on_progress(self, mod:Mod):
        if mod:
            self.mods[str(mod.hash)] = mod

    def on_complete(self):
        # Validate workspace to remove stale hashes
        current_hashes = list(self.mods.keys())
        self.workspace_manager.validate_enabled_mods(current_hashes)
        
        self.install_finished.emit()
        if self.callback:
            self.callback()

    def set_selection(self, id:str):
        self.focused_id = id
        if len(self.focus_callbacks) > 0:
            for callback in self.focus_callbacks:
                callback(id)

    def get_mods(self)->List[Mod]:
        return self.mods.values()

    def get_mods_dict(self)->dict[str, Mod]:
        return self.mods
    
    def get_mod(self, id:str)->Mod:
        return self.mods.get(id, None)
    
    def add_favorite(self, id:str):
        id = str(id) # Ensure ID is string
        if id not in self.favorite_ids:
            self.favorite_ids.append(id)
            self.config_manager.save()
            self._notify_favorite_changed(id, True)

    def remove_favorite(self, id:str):
        id = str(id) # Ensure ID is string
        if id in self.favorite_ids:
            self.favorite_ids.remove(id)
            self.config_manager.save()
            self._notify_favorite_changed(id, False)

    def add_enabled(self, id:str):
        self.workspace_manager.set_enabled(id, True)

    def remove_enabled(self, id:str):
        self.workspace_manager.set_enabled(id, False)
            
    def toggle_enabled(self, id:str):
        self.workspace_manager.toggle_enabled(id)

    def add_hidden(self, id:str):
        id = str(id)
        if id not in self.hidden_ids:
            self.hidden_ids.append(id)
            self.config_manager.save()
            self._notify_hidden_changed(id, True)

    def remove_hidden(self, id:str):
        id = str(id)
        if id in self.hidden_ids:
            self.hidden_ids.remove(id)
            self.config_manager.save()
            self._notify_hidden_changed(id, False)
    
    # Selection management methods

    def toggle_selection(self, id:str):
        """Toggle selection state of a mod"""
        if id in self.selected_ids:
            self.selected_ids.remove(id)
        else:
            self.selected_ids.append(id)
        self.selection_changed.emit(self.selected_ids)
    
    def add_selection(self, id:str):
        """Add a mod to selection"""
        if id not in self.selected_ids:
            self.selected_ids.append(id)
            self.selection_changed.emit(self.selected_ids)
    
    def remove_selection(self, id:str):
        """Remove a mod from selection"""
        if id in self.selected_ids:
            self.selected_ids.remove(id)
            self.selection_changed.emit(self.selected_ids)
    
    def clear_selection(self):
        """Clear all selections"""
        if self.selected_ids:
            self.selected_ids = []
            self.selection_changed.emit(self.selected_ids)
    
    def is_selected(self, id:str)->bool:
        """Check if a mod is selected"""
        return id in self.selected_ids
    
    def are_all_selected(self, ids:List[str])->bool:
        """Check if all provided IDs are selected"""
        return all(id in self.selected_ids for id in ids)
    
    def get_selected_ids(self)->List[str]:
        """Get all selected mod IDs"""
        return self.selected_ids

    def delete_mods(self, ids: List[str]):
        """Delete mods from file system and cache"""
        cache_manager = CacheManager()
        deleted_count = 0
        
        for id in ids:
            mod = self.mods.get(id)
            if mod:
                path = mod.path
                if os.path.exists(path) and os.path.isdir(path):
                    try:
                        shutil.rmtree(path)
                        cache_manager.remove_mod(path)
                        del self.mods[id]
                        deleted_count += 1
                        output_log(f"Deleted mod: {mod.mod_name} at {path}")
                    except Exception as e:
                        output_log(f"Failed to delete mod {mod.mod_name}: {e}")
        
        cache_manager.close()
        
        if deleted_count > 0:
            self.clear_selection()
            if self.callback:
                self.callback()

    def unload_mods(self, ids: List[str]):
        """Remove mods from memory (ModManager) without deleting files. Used for refreshing."""
        removed = False
        for id in ids:
            if id in self.mods:
                del self.mods[id]
                removed = True
        
        self.selected_ids = [s for s in self.selected_ids if s in self.mods]
        
        if removed and self.callback:
            self.callback()