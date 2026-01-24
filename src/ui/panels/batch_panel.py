from PyQt6.QtWidgets import QScrollArea, QPushButton, QMessageBox, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from src.ui.components.side_panel import SidePanel
from src.ui.components.layout import VBox
from src.ui.components.batch_task_item import BatchTaskItem
from src.managers.batch_manager import BatchManager, BatchTaskStatus
from src.core.batch_worker import BatchWorker
import os
import shutil
import requests
import tempfile
from src.core.data import generate_toml
from src.utils.file import get_parent_dir
from src.managers.cache_manager import CacheManager
from src.managers.data_manager import ButtonIcons
from src.ui.components.thumbnail_label import ImageCache
from src.constants.enums import Wifi, Element, Category
from src.core.formatting import (
    format_display_name, 
    format_character_names_for_display, 
    format_slots
)
from src.managers.data_manager import DataManager

class BatchPanel(SidePanel):
    """Panel for managing batch processing tasks"""
    
    apply_requested = pyqtSignal()
    queue_updated = pyqtSignal() # Signal to bridge background thread updates to main UI thread
    
    def __init__(self, batch_manager: BatchManager):
        super().__init__("Batch Processing")
        self.batch_manager = batch_manager
        self.worker = None
        self.task_widgets = {}  # Map mod_hash -> BatchTaskItem widget
        
        # Override width to be twice as wide for comparison columns
        self.width = 680
        self.setFixedWidth(self.width)
        
        # Add info label
        info_label = QLabel("Selected mods will be processed to fetch GameBanana data.\nChanges will not be applied until you click 'Apply'.")
        info_font = QFont("Arial", 8)
        info_label.setFont(info_font)
        info_label.setStyleSheet("color: #666; padding: 5px;")
        info_label.setWordWrap(True)
        self.body.addWidget(info_label)
        
        # Stats section
        self.stats_label = QLabel("Queue: 0 tasks")
        stats_font = QFont("Arial", 9)
        stats_font.setBold(True)
        self.stats_label.setFont(stats_font)
        self.stats_label.setStyleSheet("padding: 5px;")
        self.body.addWidget(self.stats_label)
        
        from PyQt6.QtWidgets import QWidget as QWidgetContainer, QSizePolicy
        task_list_widget = QWidgetContainer()
        self.task_container = VBox(spacing=5)
        self.task_container.setAlignment(Qt.AlignmentFlag.AlignTop)  # Anchor items to top
        task_list_widget.setLayout(self.task_container)
        
        task_list_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self.body.addWidget(task_list_widget)
        self.body.addStretch()
        
        self.clear_button = self.add_footer_button("Clear", self.on_clear_queue, icon=ButtonIcons.CLEAR.value)
        self.fetch_button = self.add_footer_button("Fetch", self.start_processing, icon=ButtonIcons.WEB.value)
        self.apply_button = self.add_footer_button("Apply", self.on_apply, primary=True, icon=ButtonIcons.BATCH_ENABLE.value)
        
        # Connect to batch manager updates via Signal to ensure Main Thread execution
        self.queue_updated.connect(self.refresh_task_list)
        self.batch_manager.add_callback(self.queue_updated.emit)
    
    def refresh_task_list(self):
        """Refresh the task list display incrementally to avoid UI freeze"""
        tasks = self.batch_manager.get_tasks()
        current_hashes = set()
        
        # 1. Remove widgets for deleted tasks
        for task in tasks:
            current_hashes.add(str(task.mod.hash))
            
        hashes_to_remove = [h for h in self.task_widgets.keys() if h not in current_hashes]
        for h in hashes_to_remove:
            widget = self.task_widgets[h]
            self.task_container.removeWidget(widget)
            widget.setParent(None)
            widget.deleteLater()
            del self.task_widgets[h]
            
        # Check for stretch item at the end
        has_stretch = False
        count = self.task_container.count()
        if count > 0:
            last_item = self.task_container.itemAt(count - 1)
            if last_item.spacerItem():
                has_stretch = True
        
        # 2. Add widgets for new tasks and valid updates
        for task in tasks:
            mod_hash = str(task.mod.hash)
            
            if mod_hash in self.task_widgets:
                # Update status of existing widget
                self.task_widgets[mod_hash].update_status_display()
            else:
                # Add new widget
                task_widget = BatchTaskItem(task)
                task_widget.remove_requested.connect(self.on_remove_task)
                
                if has_stretch:
                    self.task_container.insertWidget(self.task_container.count() - 1, task_widget)
                else:
                    self.task_container.addWidget(task_widget)
                
                self.task_widgets[mod_hash] = task_widget
        
        # Ensure stretch item exists at the bottom
        if not has_stretch:
            self.task_container.addStretch()
            
        # Update stats UI
        self.update_stats_ui()
    
    def start_processing(self):
        """Start the batch processing worker"""
        if self.worker and self.worker.isRunning():
            return  # Already processing
        
        self.worker = BatchWorker(self.batch_manager)
        
        # Connect worker signals
        self.worker.task_started.connect(self.on_task_started)
        self.worker.task_progress.connect(self.on_task_progress)
        self.worker.task_complete.connect(self.on_task_complete)
        self.worker.task_error.connect(self.on_task_error)
        self.worker.all_complete.connect(self.on_all_complete)
        
        self.worker.start()
    
    def update_stats_ui(self):
        """Update just the stats label without rebuilding list"""
        tasks = self.batch_manager.get_tasks()
        total = len(tasks)
        pending = self.batch_manager.get_pending_count()
        processing = self.batch_manager.get_processing_count()
        complete = self.batch_manager.get_complete_count()
        error = self.batch_manager.get_error_count()
        
        self.stats_label.setText(
            f"Queue: {total} tasks | "
            f"Pending: {pending} | "
            f"Processing: {processing} | "
            f"Complete: {complete} | "
            f"Errors: {error}"
        )
        
        # Update buttons
        self.fetch_button.setEnabled(pending > 0 and processing == 0)
        self.apply_button.setEnabled(total > 0 and processing == 0)
        self.clear_button.setEnabled(total > 0 and processing == 0)

    def on_task_started(self, mod_hash: str):
        """Handle task started signal"""
        # Update BatchManager with notification to trigger MainMenu progress update
        self.batch_manager.update_task_status(
            mod_hash, 
            BatchTaskStatus.PROCESSING, 
            "Starting...", 
            notify=True
        )
        
        self.update_stats_ui()
        
        widget = self.task_widgets.get(mod_hash)
        if widget:
            widget.update_status(BatchTaskStatus.PROCESSING, "Fetching data...")
    
    def on_task_progress(self, mod_hash: str, message: str):
        """Handle task progress signal"""
        # Silent update to BatchManager (no notify) to key data in sync but avoid UI rebuild
        self.batch_manager.update_task_status(
            mod_hash,
            BatchTaskStatus.PROCESSING,
            message,
            notify=False
        )
        
        widget = self.task_widgets.get(mod_hash)
        if widget:
            widget.update_status(BatchTaskStatus.PROCESSING, message)
    
    def on_task_complete(self, mod_hash: str):
        """Handle task complete signal"""
        # Notify BatchManager of completion
        self.batch_manager.update_task_status(
            mod_hash, 
            BatchTaskStatus.COMPLETE, 
            "Data fetched successfully", 
            notify=True
        )
        
        widget = self.task_widgets.get(mod_hash)
        if widget:
            # Get task with fetched data
            task = self.batch_manager.get_task(mod_hash)
            
            # Update the editable fields with fetched data
            widget.update_new_data(
                mod_name=task.fetched_mod_name,
                authors=task.fetched_authors,
                version=task.fetched_version,
                url=task.fetched_url,
                description=task.fetched_description,
                preview_links=task.fetched_preview_links,
                wifi_safe=task.fetched_is_wifi_safe,
                is_moveset=task.fetched_is_moveset,
                is_final_smash=task.fetched_is_final_smash
            )
            
            # Update status display
            widget.update_status(BatchTaskStatus.COMPLETE)
        
        self.update_stats_ui()
    
    def on_task_error(self, mod_hash: str, error: str):
        """Handle task error signal"""
        self.batch_manager.update_task_error(mod_hash, error, notify=True)
        
        widget = self.task_widgets.get(mod_hash)
        if widget:
            widget.update_status(BatchTaskStatus.ERROR, "", error)
        self.update_stats_ui()
    
    def on_all_complete(self):
        """Handle all tasks complete signal"""
        self.update_stats_ui()
    
    def on_remove_task(self, mod_hash: str):
        """Remove a task from the queue"""
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "Processing", "Cannot remove tasks while processing.")
            return
        
        self.batch_manager.remove_task(mod_hash)
    
    def on_clear_queue(self):
        """Clear all tasks from the queue"""
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "Processing", "Cannot clear queue while processing.")
            return
        
        self.batch_manager.clear_queue()
    
    def on_apply(self):
        """Apply all tasks - saves current mod data to info.toml"""
        tasks = self.batch_manager.get_tasks()
        
        if not tasks:
            return
        
        # Confirm with user
        total_count = len(tasks)
        reply = QMessageBox.question(
            self,
            "Apply Changes",
            f"Apply changes to {total_count} mods?\n\n"
            "This will:\n"
            "• Update mod metadata\n"
            "• Generate info.toml files\n"
            "• Copy thumbnails if changed\n"
            "• Rename mod folders if needed",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Import needed modules
        from src.models.mod import Character
        from src.constants.enums import Fighter
        
        # Apply each task using data from widgets
        applied_count = 0
        error_count = 0
        
        for task in tasks:
            try:
                mod = task.mod
                mod_hash = str(mod.hash)
                widget = self.task_widgets.get(mod_hash)
                
                if widget:
                    # Explicitly read text fields from widget to ensure latest values (failsafe)
                    if "mod_name" in widget.input_fields:
                        mod.mod_name = widget.input_fields["mod_name"].text()
                    if "authors" in widget.input_fields:
                        mod.authors = widget.input_fields["authors"].text()
                    if "version" in widget.input_fields:
                        mod.version = widget.input_fields["version"].text()
                    if "url" in widget.input_fields:
                        mod.url = widget.input_fields["url"].text()
                    if "description" in widget.input_fields:
                        mod.description = widget.input_fields["description"].toPlainText()
                    if "display_name" in widget.input_fields:
                        mod.display_name = widget.input_fields["display_name"].text()
                    if "folder_name" in widget.input_fields:
                        mod.folder_name = widget.input_fields["folder_name"].text()
                    if "category" in widget.input_fields:
                        try:
                            mod.category = Category(widget.input_fields["category"].currentText())
                        except:
                            pass
                    if "wifi_safe" in widget.input_fields:
                        try:
                            mod.wifi_safe = Wifi(widget.input_fields["wifi_safe"].currentText())
                        except:
                            pass

                    # Read Characters and Slots from widget multi-selects
                    selected_chars = widget.get_selected_characters()
                    selected_slots = widget.get_selected_slots()
                    
                    # Build new characters list
                    new_chars = []
                    for char_name in selected_chars:
                        fighter_key = DataManager.get_character_by_custom(char_name)
                        if fighter_key:
                            new_chars.append(Character(fighter=fighter_key, slots=selected_slots))
                    mod.characters = new_chars
                    
                    # Read Elements from widget
                    selected_elements = widget.get_selected_elements()
                    mod.includes = []
                    for el_name in selected_elements:
                        try:
                            mod.add_to_included(Element(el_name))
                        except:
                            pass
                    
                    # Handle pending thumbnail from widget
                    pending_thumb = widget.get_pending_thumbnail()
                    if pending_thumb:
                        try:
                            dest = os.path.join(mod.path, "preview.webp")
                            
                            if pending_thumb.startswith("http"):
                                # It's a URL (fetched preview), download it
                                with requests.Session() as session:
                                    session.trust_env = False
                                    response = session.get(pending_thumb, stream=True)
                                
                                if response.status_code == 200:
                                    with open(dest, 'wb') as f:
                                        for chunk in response.iter_content(chunk_size=8192):
                                            f.write(chunk)
                                    ImageCache().remove(dest)
                                    mod.thumbnail = dest
                            else:
                                # It's a local file
                                shutil.copy2(pending_thumb, dest)
                                ImageCache().remove(dest)
                                mod.thumbnail = dest
                        except Exception as e:
                            print(f"Error copying/downloading thumbnail: {e}")
                
                # Download preview image if fetched (and no pending thumbnail)
                if not (widget and widget.get_pending_thumbnail()):
                    if task.fetched_preview_links and len(task.fetched_preview_links) > 0:
                        try:
                            preview_url = task.fetched_preview_links[0]
                            with requests.Session() as session:
                                session.trust_env = False
                                response = session.get(preview_url, stream=True)
                                
                            if response.status_code == 200:
                                dest = os.path.join(mod.path, "preview.webp")
                                with open(dest, 'wb') as f:
                                    shutil.copyfileobj(response.raw, f)
                                ImageCache().remove(dest)
                                mod.thumbnail = dest
                        except Exception as e:
                            print(f"Error downloading preview: {e}")
                
                # Generate TOML with current mod data
                generate_toml(mod)
                
                # Rename folder if needed
                old_path = mod.path
                new_dir = os.path.join(get_parent_dir(mod.path), mod.folder_name)
                if old_path != new_dir and not os.path.exists(new_dir):
                    try:
                        os.rename(old_path, new_dir)
                        mod.path = new_dir
                        mod.thumbnail = os.path.join(new_dir, "preview.webp")
                    except Exception as e:
                        print(f"Error renaming folder: {e}")
                elif os.path.exists(new_dir) and old_path != new_dir:
                    print(f"Could not rename {old_path} to {new_dir}: destination already exists")
                
                # Update cache
                cache_data = mod.model_dump(mode='json', exclude={'is_selected', 'path', 'hash'})
                CacheManager().set_cached_mod(mod.path, cache_data)
                
                applied_count += 1
                
            except Exception as e:
                print(f"Error applying task for {task.mod.mod_name}: {e}")
                error_count += 1
        
        # Show result
        if applied_count > 0:
            QMessageBox.information(
                self,
                "Success",
                f"Successfully applied {applied_count} tasks.\n"
                f"Errors: {error_count}"
            )
        
        # Clear queue and refresh
        self.batch_manager.clear_queue()
        self.apply_requested.emit()

