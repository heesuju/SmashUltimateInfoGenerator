import os
import shutil
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from src.models.mod import Mod
from src.utils.file import is_valid_dir
from src.utils.logger import output_log

class SyncWorker(QObject):
    progress = pyqtSignal(str, float) # Status message, progress %
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, mods_to_sync: list[Mod], export_dir: str):
        super().__init__()
        self.mods_to_sync = mods_to_sync
        self.export_dir = export_dir
        self.is_running = True

    def run(self):
        try:
            if not is_valid_dir(self.export_dir):
                self.error.emit(f"Invalid export directory: {self.export_dir}")
                self.finished.emit()
                return

            # 1. Map enabled mods by their destination folder name
            enabled_map = {mod.folder_name: mod for mod in self.mods_to_sync}
            
            # 2. Map existing folders in export directory
            try:
                existing_folders = [f for f in os.listdir(self.export_dir) if os.path.isdir(os.path.join(self.export_dir, f))]
            except Exception as e:
                self.error.emit(f"Failed to scan export directory: {str(e)}")
                self.finished.emit()
                return

            # 3. Calculate Diff
            to_delete = [f for f in existing_folders if f not in enabled_map]
            to_copy = [mod for name, mod in enabled_map.items() if name not in existing_folders]
            
            total_ops = len(to_delete) + len(to_copy)
            current_op = 0

            # 4. Perform Deletions
            for folder in to_delete:
                if not self.is_running: break
                
                full_path = os.path.join(self.export_dir, folder)
                self.progress.emit(f"Removing unused: {folder}", current_op / total_ops if total_ops > 0 else 0)
                try:
                    shutil.rmtree(full_path)
                except Exception as e:
                    output_log(f"Failed to delete {full_path}: {e}")
                
                current_op += 1

            # 5. Perform Copies
            for mod in to_copy:
                if not self.is_running: break
                
                dest_path = os.path.join(self.export_dir, mod.folder_name)
                src_path = mod.path
                
                self.progress.emit(f"Copying: {mod.display_name}", current_op / total_ops if total_ops > 0 else 0)
                
                try:
                    # ignore=.git etc if needed
                    shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
                except Exception as e:
                    output_log(f"Failed to copy {mod.mod_name}: {e}")
                    
                current_op += 1

            self.progress.emit("Sync Complete!", 1.0)
            self.finished.emit()

        except Exception as e:
            self.error.emit(f"Sync failed: {str(e)}")
            self.finished.emit()

    def stop(self):
        self.is_running = False
