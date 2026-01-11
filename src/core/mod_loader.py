"""
mod_loader.py: class that scans mod folders to automatically find
included elements
"""

import os
import copy
from PyQt6.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool
from concurrent.futures import ThreadPoolExecutor
from typing import Union, List
from src.utils.file import is_valid_dir, get_base_name
from src.utils.toml import load_toml
from src.utils.hash import get_hash
from src.models.mod import Mod
from .scanner import scan_mod
from src.utils.logger import output_log
from src.managers.cache_manager import CacheManager

# Worker Signals
class ModWorkerSignals(QObject):
    finished = pyqtSignal(Mod)  # Emit each mod when done
    error = pyqtSignal(str)     # Emit error messages if needed

# Worker Runnable
class ModWorker(QRunnable):
    def __init__(self, mod_name:str, mod_path:str, cache_manager:CacheManager):
        super().__init__()
        self.mod_name = mod_name
        self.mod_path = mod_path
        self.cache_manager = cache_manager
        self.signals = ModWorkerSignals()

    def run(self):
        try:
            if not is_valid_dir(self.mod_path):
                return

            # Try to load from cache first
            cached_data = self.cache_manager.get_cached_mod(self.mod_path)
            
            if cached_data is not None:
                # Cache hit - load from cache
                try:
                    mod = Mod(**cached_data)
                    mod.path = self.mod_path
                    mod.hash = get_hash(self.mod_name)
                    self.signals.finished.emit(mod)
                    return
                except Exception as e:
                    output_log(f"Error loading from cache for {self.mod_name}: {e}")
                    # Fall through to regular scan
            
            # Cache miss or invalid - perform full scan
            data = load_toml(self.mod_path)
            mod = Mod()
            
            if data is not None:
                try:
                    mod = Mod(**data)
                    mod.contains_info = True
                except Exception as e:
                    output_log(f"Error loading mod info for {self.mod_name}: {e}")
            
            mod.display_name = self.mod_name
            mod.path = self.mod_path
            mod.hash = get_hash(self.mod_name)
            mod.folder_name = self.mod_name
            
            mod = scan_mod(mod)
            
            # Store in cache for next time
            cache_data = mod.model_dump(exclude={'is_selected', 'path', 'hash'})
            self.cache_manager.set_cached_mod(self.mod_path, cache_data)
            
            self.signals.finished.emit(mod)
        except Exception as e:
            self.signals.error.emit(f"Error loading mod {self.mod_name}: {e}")


# ModLoader with ThreadPool
class ModLoader(QObject):
    all_finished = pyqtSignal()

    def __init__(self, directory: Union[str, List[str]]):
        super().__init__()
        self.directory = directory
        if isinstance(self.directory, str):
            self.directory = [self.directory]
        self.thread_pool = QThreadPool()
        # Optimize for HDD: limit to 4 threads to reduce disk seek overhead
        self.thread_pool.setMaxThreadCount(4)
        self.cache_manager = CacheManager()
        self.pending = len(self.directory) 
        self.total = len(self.directory)
        self.success = 0

    def _worker_done(self, *_):
        self.pending -= 1
        self.success += 1
        if self.pending == 0:
            output_log("Scan complete: {0} mods found".format(self.success))
            self.all_finished.emit()

    def _worker_failed(self, error_msg=None):
        self.pending -= 1
        if error_msg:
            output_log(f"Mod scan error: {error_msg}")
            
        if self.pending == 0:
            output_log("Scan complete: {0} mods found".format(self.success))
            self.all_finished.emit()

    def load_mods(self, on_progress:callable, on_complete:callable=None):
        """
        Scans mods asynchronously and sends each scanned mod via callback
        """
        if on_complete:
            self.all_finished.connect(on_complete)

        if self.pending == 0:
            self.all_finished.emit()
            return

        # Cleanup orphaned cache entries before scanning
        self.cache_manager.cleanup()
        
        for mod_path in self.directory:
            if not is_valid_dir(mod_path):
                output_log(f"Invalid mod directory: {mod_path}")
                on_progress(None)

            mod_name = get_base_name(mod_path)
            worker = ModWorker(mod_name, mod_path, self.cache_manager)
            worker.signals.finished.connect(on_progress)  # send each mod to UI
            worker.signals.finished.connect(lambda *_: self._worker_done())
            worker.signals.error.connect(self._worker_failed)
            self.thread_pool.start(worker)
