from enum import Enum
from typing import Optional, Callable
from pydantic import BaseModel
from src.models.mod import Mod


class BatchTaskStatus(Enum):
    """Status of a batch processing task"""
    PENDING = "Pending"
    PROCESSING = "Processing"
    COMPLETE = "Complete"
    ERROR = "Error"


class BatchTask(BaseModel):
    """Represents a single task in the batch processing queue"""
    mod: Mod
    status: BatchTaskStatus = BatchTaskStatus.PENDING
    progress_message: str = ""
    error_message: str = ""
    
    # Original data from info.toml at time of task creation (read-only snapshot)
    original_mod_name: Optional[str] = None
    original_authors: Optional[str] = None
    original_version: Optional[str] = None
    original_url: Optional[str] = None
    original_wifi_safe: Optional[str] = None
    original_description: Optional[str] = None
    original_elements: Optional[list[str]] = None
    original_characters: Optional[list[dict]] = None  # [{fighter: str, slots: [int]}]
    original_thumbnail: Optional[str] = None
    original_display_name: Optional[str] = None
    original_folder_name: Optional[str] = None
    original_category: Optional[str] = None
    
    # Temporary data fetched from GameBanana (not applied until user clicks Apply)
    fetched_url: Optional[str] = None
    fetched_mod_name: Optional[str] = None
    fetched_authors: Optional[str] = None
    fetched_version: Optional[str] = None
    fetched_description: Optional[str] = None
    fetched_preview_links: Optional[list[str]] = None
    fetched_preview_files: Optional[list[str]] = None
    fetched_is_wifi_safe: Optional[bool] = None
    fetched_is_moveset: Optional[bool] = None
    fetched_is_final_smash: Optional[bool] = None
    
    class Config:
        arbitrary_types_allowed = True


class BatchManager:
    """Manages the batch processing queue and state"""
    
    def __init__(self):
        self.tasks: list[BatchTask] = []
        self.callbacks: list[Callable] = []
    
    def add_task(self, mod: Mod) -> BatchTask:
        """Add a mod to the batch processing queue"""
        # Capture original info.toml data as read-only snapshot
        original_wifi = None
        original_elements = None
        original_characters = None
        original_category = None
        
        if mod.contains_info:
            if mod.wifi_safe:
                original_wifi = mod.wifi_safe.value if hasattr(mod.wifi_safe, 'value') else str(mod.wifi_safe)
            if mod.includes:
                original_elements = [el.value if hasattr(el, 'value') else str(el) for el in mod.includes]
            if mod.characters:
                original_characters = [
                    {"fighter": c.fighter, "slots": c.slots} for c in mod.characters
                ]
            if mod.category:
                original_category = mod.category.value if hasattr(mod.category, 'value') else str(mod.category)
        
        task = BatchTask(
            mod=mod,
            original_mod_name=mod.mod_name if mod.contains_info else None,
            original_authors=mod.authors if mod.contains_info else None,
            original_version=mod.version if mod.contains_info else None,
            original_url=mod.url if mod.contains_info else None,
            original_wifi_safe=original_wifi,
            original_description=mod.description if mod.contains_info else None,
            original_elements=original_elements,
            original_characters=original_characters,
            original_thumbnail=mod.thumbnail if mod.contains_info else None,
            original_display_name=mod.display_name if mod.contains_info else None,
            original_folder_name=mod.folder_name if mod.contains_info else None,
            original_category=original_category
        )
        self.tasks.append(task)
        self._notify_callbacks()
        return task
    
    def add_tasks(self, mods: list[Mod]) -> list[BatchTask]:
        """Add multiple mods to the batch processing queue"""
        new_tasks = []
        for mod in mods:
            # Capture original info.toml data as read-only snapshot
            original_wifi = None
            original_elements = None
            original_characters = None
            original_category = None
            
            if mod.contains_info:
                if mod.wifi_safe:
                    original_wifi = mod.wifi_safe.value if hasattr(mod.wifi_safe, 'value') else str(mod.wifi_safe)
                if mod.includes:
                    original_elements = [el.value if hasattr(el, 'value') else str(el) for el in mod.includes]
                if mod.characters:
                    original_characters = [
                        {"fighter": c.fighter, "slots": c.slots} for c in mod.characters
                    ]
                if mod.category:
                    original_category = mod.category.value if hasattr(mod.category, 'value') else str(mod.category)
            
            task = BatchTask(
                mod=mod,
                original_mod_name=mod.mod_name if mod.contains_info else None,
                original_authors=mod.authors if mod.contains_info else None,
                original_version=mod.version if mod.contains_info else None,
                original_url=mod.url if mod.contains_info else None,
                original_wifi_safe=original_wifi,
                original_description=mod.description if mod.contains_info else None,
                original_elements=original_elements,
                original_characters=original_characters,
                original_thumbnail=mod.thumbnail if mod.contains_info else None,
                original_display_name=mod.display_name if mod.contains_info else None,
                original_folder_name=mod.folder_name if mod.contains_info else None,
                original_category=original_category
            )
            self.tasks.append(task)
            new_tasks.append(task)
        self._notify_callbacks()
        return new_tasks
    
    def remove_task(self, mod_hash: str):
        """Remove a task from the queue by mod hash"""
        self.tasks = [t for t in self.tasks if str(t.mod.hash) != mod_hash]
        self._notify_callbacks()
    
    def get_task(self, mod_hash: str) -> Optional[BatchTask]:
        """Get a task by mod hash"""
        for task in self.tasks:
            if str(task.mod.hash) == mod_hash:
                return task
        return None
    
    def get_tasks(self) -> list[BatchTask]:
        """Get all tasks in the queue"""
        return self.tasks
    
    def clear_queue(self):
        """Clear all tasks from the queue"""
        self.tasks = []
        self._notify_callbacks()
    
    def update_task_status(self, mod_hash: str, status: BatchTaskStatus, message: str = "", notify: bool = True):
        """Update the status of a task"""
        task = self.get_task(mod_hash)
        if task:
            task.status = status
            task.progress_message = message
            if notify:
                self._notify_callbacks()
    
    def update_task_error(self, mod_hash: str, error: str, notify: bool = True):
        """Update task with error status and message"""
        task = self.get_task(mod_hash)
        if task:
            task.status = BatchTaskStatus.ERROR
            task.error_message = error
            if notify:
                self._notify_callbacks()
    
    def update_task_data(self, mod_hash: str, data: dict, notify: bool = True):
        """Update task with fetched GameBanana data"""
        task = self.get_task(mod_hash)
        if task:
            task.fetched_url = data.get("url")
            task.fetched_mod_name = data.get("mod_name")
            task.fetched_authors = data.get("authors")
            task.fetched_version = data.get("version")
            task.fetched_description = data.get("description")
            task.fetched_preview_links = data.get("preview_links")
            task.fetched_preview_files = data.get("preview_files")
            task.fetched_is_wifi_safe = data.get("is_wifi_safe")
            task.fetched_is_moveset = data.get("is_moveset")
            task.fetched_is_final_smash = data.get("is_final_smash")
            if notify:
                self._notify_callbacks()
    
    def add_callback(self, callback: Callable):
        """Add a callback to be notified when queue changes"""
        self.callbacks.append(callback)
    
    def _notify_callbacks(self):
        """Notify all registered callbacks of queue changes"""
        for callback in self.callbacks:
            callback()
    
    def get_pending_count(self) -> int:
        """Get count of pending tasks"""
        return sum(1 for t in self.tasks if t.status == BatchTaskStatus.PENDING)
    
    def get_processing_count(self) -> int:
        """Get count of processing tasks"""
        return sum(1 for t in self.tasks if t.status == BatchTaskStatus.PROCESSING)
    
    def get_complete_count(self) -> int:
        """Get count of completed tasks"""
        return sum(1 for t in self.tasks if t.status == BatchTaskStatus.COMPLETE)
    
    def get_error_count(self) -> int:
        """Get count of errored tasks"""
        return sum(1 for t in self.tasks if t.status == BatchTaskStatus.ERROR)
