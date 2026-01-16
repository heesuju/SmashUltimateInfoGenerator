import threading
from PyQt6.QtCore import QThread, pyqtSignal
from src.managers.batch_manager import BatchManager, BatchTaskStatus
from src.core.web.gamebanana import search_mod, get_mod_info, process_mod_info, get_mod_description
from src.managers.data_manager import DataManager


class BatchWorker(QThread):
    """Worker thread for batch processing mods"""
    
    task_started = pyqtSignal(str)  # Emits mod hash
    task_progress = pyqtSignal(str, str)  # Emits mod hash, progress message
    task_complete = pyqtSignal(str)  # Emits mod hash
    task_error = pyqtSignal(str, str)  # Emits mod hash, error message
    all_complete = pyqtSignal()  # Emits when all tasks are done
    
    def __init__(self, batch_manager: BatchManager):
        super().__init__()
        self.batch_manager = batch_manager
        self.should_stop = False
    
    def run(self):
        """Process all pending tasks in the batch queue"""
        tasks = self.batch_manager.get_tasks()
        
        for task in tasks:
            if self.should_stop:
                break
            
            if task.status != BatchTaskStatus.PENDING:
                continue
            
            mod_hash = str(task.mod.hash)
            
            try:
                # Mark as processing
                self.task_started.emit(mod_hash)
                
                # Step 1: Get or search for GameBanana URL
                mod_id = None
                if task.mod.url:
                    # Extract mod ID from existing URL
                    import re
                    match = re.search(r"gamebanana\.com/mods/(\d+)", task.mod.url)
                    if match:
                        mod_id = match.group(1)
                        self.task_progress.emit(mod_hash, f"Using existing URL")
                
                if not mod_id:
                    # Search for URL
                    self.task_progress.emit(mod_hash, "Searching GameBanana...")
                    
                    # Build search query
                    mod_name = task.mod.mod_name.strip()
                    author_name = task.mod.authors.strip()
                    
                    # Append character names to search query (limit to 3)
                    if 0 < len(task.mod.characters) <= 3:
                        search_terms = set()
                        mod_name_lower = mod_name.lower()
                        
                        # for char in task.mod.characters:
                        #     fighter_key = char.fighter
                        #     group = DataManager.get_character_groups(fighter_key)
                        #     custom_name = DataManager.get_character_data(fighter_key, "Custom")
                            
                        #     term_to_add = None
                        #     if group:
                        #         term_to_add = group
                        #     elif custom_name:
                        #         term_to_add = custom_name[0] if isinstance(custom_name, list) else custom_name
                            
                        #     if term_to_add and term_to_add.lower() not in mod_name_lower:
                        #         search_terms.add(term_to_add)
                        
                        # if search_terms:
                        #     mod_name += " " + " ".join(search_terms)
                    
                    # Perform search
                    mod_id = search_mod(mod_name, author_name)
                    mod_id = str(mod_id.get("_idRow"))
                    if not mod_id:
                        self.task_error.emit(mod_hash, "Could not find mod on GameBanana")
                        continue
                
                # Step 2: Fetch mod info
                self.task_progress.emit(mod_hash, "Fetching mod data...")
                result = get_mod_info(mod_id)
                
                if not result:
                    self.task_error.emit(mod_hash, "Failed to fetch mod data")
                    continue
                
                # Step 3: Process mod info
                _, info = process_mod_info(result)

                # Step 4: Store fetched data in the task (this is safe as it's just data)
                task.fetched_url = f"https://gamebanana.com/mods/{mod_id}"
                task.fetched_mod_name = info.get("mod_name")
                task.fetched_authors = info.get("authors")
                task.fetched_version = info.get("version")
                task.fetched_preview_links = info.get("preview_links")
                task.fetched_preview_files = info.get("preview_files")
                task.fetched_is_wifi_safe = info.get("is_wifi_safe")
                task.fetched_is_moveset = info.get("is_moveset")
                task.fetched_is_final_smash = info.get("is_final_smash")
                
                # Fetch detailed description (separate API call)
                self.task_progress.emit(mod_hash, "Fetching description...")
                description = get_mod_description(mod_id)
                if description:
                    task.fetched_description = description
                
                task.status = BatchTaskStatus.COMPLETE
                task.progress_message = "Data fetched successfully"
                
                # Emit completion (UI will update via signal handler)
                self.task_complete.emit(mod_hash)
                
            except Exception as e:
                error_msg = str(e)
                task.status = BatchTaskStatus.ERROR
                task.error_message = error_msg
                self.task_error.emit(mod_hash, error_msg)
        
        # Emit completion signal
        self.all_complete.emit()
    
    def stop(self):
        """Request the worker to stop processing"""
        self.should_stop = True
