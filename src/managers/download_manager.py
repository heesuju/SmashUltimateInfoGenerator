from PyQt6.QtCore import QObject, pyqtSignal, QUrl, QFile, QIODevice
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
import os
import shutil
from collections import deque
from src.managers.config_manager import ConfigManager
from src.core.mod_installer import ModInstaller
from src.utils.toml import dump_toml, load_toml
from pathlib import Path
from src.core.scanner import scan_mod
from src.models.mod import Mod
from src.core.formatting import (
    format_folder_name, 
    format_display_name, 
    format_slots, 
    format_character_names_for_display, 
    format_character_names_for_folder, 
    get_mod_name,
    clean_version
)
from src.utils.string_helper import SPECIAL_CHARS, remove_redundant_spacing
from src.constants.enums import Fighter
from src.managers.data_manager import DataManager

class DownloadManager(QObject):
    # Signals
    download_queued = pyqtSignal(str, str) # id, name
    download_started = pyqtSignal(str, str) # id, name
    progress_updated = pyqtSignal(str, int, int) # id, received, total
    download_finished = pyqtSignal(str, bool, str) # id, success, message
    install_finished = pyqtSignal(str) # path
    thumbnail_updated = pyqtSignal(str) # path
    
    def __init__(self, config_manager: ConfigManager, max_concurrent=3):
        super().__init__()
        self.manager = QNetworkAccessManager()
        self.config_manager = config_manager
        self.max_concurrent_downloads = max_concurrent
        
        self.download_queue = deque()
        self.active_downloads = {} # id -> reply
        self.download_meta = {} # id -> dict (metadata for post-processing)
        self.download_files = {} # id -> QFile
        self.active_installers = [] # Prevent GC of installers
        
        # Default download path
        self.download_path = os.path.join(os.getcwd(), "downloads")
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)
            
    def start_download(self, url: str, filename: str, mod_name: str, mod_id_str: str, mod_data: dict = None):
        """Queue a download"""
        # Create a unique ID
        import time
        download_id = f"{mod_name}_{filename}_{int(time.time())}"
        
        # Check if multiple files exist and append suffix
        if mod_data:
            files = mod_data.get("files", [])
            if len(files) > 1:
                 # Find matching file logic
                 matching_file = next((f for f in files if f.get("url") == url), None)
                 if matching_file:
                    desc = matching_file.get("description", "")
                    if desc:
                        import re
                        clean_desc = re.sub(r'[()\[\]{}]', '', desc)
                        for char in SPECIAL_CHARS:
                            clean_desc = clean_desc.replace(char, "")
                        clean_desc = remove_redundant_spacing(clean_desc).strip()
                        if clean_desc:
                            mod_name = f"{mod_name} ({clean_desc})"

        task = {
            "id": download_id,
            "url": url,
            "filename": filename,
            "mod_name": mod_name,
            "mod_id_str": mod_id_str,
            "mod_data": mod_data
        }
        
        self.download_queue.append(task)
        self.download_queued.emit(download_id, mod_name)
        self.process_queue()
        return download_id

    def process_queue(self):
        """Process the download queue"""
        while len(self.active_downloads) < self.max_concurrent_downloads and self.download_queue:
            task = self.download_queue.popleft()
            self._start_download_task(task)
            
    def _start_download_task(self, task):
        download_id = task["id"]
        url_str = task["url"]
        filename = task["filename"]
        mod_name = task["mod_name"]
        
        # Store metadata for post-processing
        self.download_meta[download_id] = task
        
        # Start Request
        request = QNetworkRequest(QUrl(url_str))
        request.setAttribute(QNetworkRequest.Attribute.RedirectPolicyAttribute, True)
        
        # Spoof User Agent
        request.setRawHeader(b"User-Agent", b"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        reply = self.manager.get(request)
        self.active_downloads[download_id] = reply
        
        # Connect signals
        reply.downloadProgress.connect(lambda recv, tot, id=download_id: self._on_progress(id, recv, tot))
        reply.finished.connect(lambda id=download_id: self._on_finished(id))
        reply.readyRead.connect(lambda id=download_id: self._on_ready_read(id))
        reply.metaDataChanged.connect(lambda id=download_id: self._on_metadata_changed(id))
        
        self.download_started.emit(download_id, mod_name)
        
    def _on_metadata_changed(self, download_id):
        reply = self.active_downloads.get(download_id)
        if not reply or download_id in self.download_files:
            return
            
        # Determine filename from Content-Disposition or fallback
        filename = self.download_meta[download_id]["filename"]
        try:
            content_disp = reply.header(QNetworkRequest.KnownHeaders.ContentDispositionHeader)
            if content_disp:
                import re
                match = re.search(r'filename="?([^";]+)"?', content_disp)
                if match:
                    filename = match.group(1)
        except Exception as e:
            print(f"Error parsing headers: {e}")
        
        file_path = os.path.join(self.download_path, filename)
        
        file = QFile(file_path)
        if file.open(QIODevice.OpenModeFlag.WriteOnly):
            self.download_files[download_id] = file
        else:
            print(f"Failed to open file: {filename}")
            # Will fail in readyRead or finished

    def _on_ready_read(self, download_id):
        reply = self.active_downloads.get(download_id)
        
        # Ensure file exists (lazy open fallback if metadata didn't fire/work)
        if download_id not in self.download_files:
            self._on_metadata_changed(download_id)
            
        file = self.download_files.get(download_id)
        if reply and file:
            data = reply.readAll()
            file.write(data)
            
    def _on_progress(self, download_id, received, total):
        self.progress_updated.emit(download_id, received, total)
        
    def _on_finished(self, download_id):
        reply = self.active_downloads.pop(download_id, None)
        file = self.download_files.pop(download_id, None)
        meta = self.download_meta.pop(download_id, None)
        
        if file:
            file.close()
            
        if reply:
            err = reply.error()
            if err == QNetworkReply.NetworkError.NoError:
                # Success - Start Post Processing
                if meta:
                   self._process_install(meta, file.fileName())
                else: 
                   self.download_finished.emit(download_id, True, "Download Complete")
            else:
                self.download_finished.emit(download_id, False, reply.errorString())
            reply.deleteLater()
            
        # Process next
        self.process_queue()
        
    def _process_install(self, meta: dict, downloaded_path: str):
        """Use ModInstaller to install the downloaded file"""
        mod_root = self.config_manager.config.root_dir
        if not mod_root or not os.path.exists(mod_root):
             self.download_finished.emit(meta["id"], False, "Mod root directory not configured")
             return

        # Create Installer
        installer = ModInstaller(
            directory=downloaded_path,
            root_dir=mod_root,
            on_finish=None
        )
        
        # Connect signals passing metadata closure
        installer.install_finished.connect(
            lambda paths: self._on_installer_finished(installer, paths, meta, downloaded_path)
        )
        
        # Keep reference and start
        self.active_installers.append(installer)
        installer.start()
        
    def _on_installer_finished(self, installer, new_paths, meta, downloaded_path):
        """Callback when ModInstaller finishes"""
        if installer in self.active_installers:
            self.active_installers.remove(installer)
            
        if not new_paths:
            # Installation failed or no valid mod found
            # Maybe it's a simple file that needs manual handling? 
            # ModInstaller fallback handles dirs, but maybe not single files properly if not recognized?
            # For now, assume failure if empty
            # BUT: If ModInstaller failed, it might be because it's just a loose file we should move manually?
            # Let's try the manual move as fallback if ModInstaller returned nothing and it wasn't a zip
            if not downloaded_path.lower().endswith(('.zip', '.7z', '.rar')):
                 self._manual_install_fallback(meta, downloaded_path)
                 return

            # self.download_finished.emit(meta["id"], False, "Installation failed (No mod root found)") # Don't double emit finish
            return

        # Process paths (usually just one)
        for path in new_paths:
            final_path = self._write_metadata(path, meta)
            self.install_finished.emit(final_path)
            
        self.download_finished.emit(meta["id"], True, "Installation Complete")

    def _manual_install_fallback(self, meta, downloaded_path):
        """Fallback for loose files not handled by ModInstaller"""
        try:
            mod_root = self.config_manager.config.root_dir
            folder_name = "".join([c for c in meta["mod_name"] if c.isalpha() or c.isdigit() or c in (' ', '.', '_', '-')]).rstrip()
            target_dir = os.path.join(mod_root, folder_name)
            
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
                
            filename = meta["filename"]
            target_path = os.path.join(target_dir, filename)
            
            if os.path.exists(target_path):
                os.remove(target_path)
            
            if os.path.exists(downloaded_path):
                shutil.move(downloaded_path, target_path)
                
            final_path = self._write_metadata(target_dir, meta)
            self.install_finished.emit(final_path)
            self.download_finished.emit(meta["id"], True, "Installation Complete")
            
        except Exception as e:
            print(f"Manual fallback error: {e}")

    def _write_metadata(self, target_dir: str, meta: dict) -> str:
        """Generate info.toml and download thumbnail. Returns final directory path."""
        try:
            mod_data = meta.get("mod_data")
            if not mod_data:
                return target_dir
            
            # Step 1: Scan the mod directory to detect characters, slots, etc.
            mod = Mod()
            mod.path = target_dir
            mod.display_name = mod_data.get("mod_name", "")
            mod.mod_name = mod_data.get("mod_name", "")
            mod.folder_name = os.path.basename(target_dir)
            
            # Perform Local Scan
            mod = scan_mod(mod)
            
            # --- START FORMATTING LOGIC ---
            # Extract Components
            char_keys = mod.get_character_keys()
            slots_list = mod.get_character_slots()
            category_str = str(mod.category.value)
            
            # Format Components
            name_rules = self.config_manager.config.name_rules
            
            slots_str_display = format_slots(slots_list, name_rules.cap_slots_display)
            slots_str_folder = format_slots(slots_list, name_rules.cap_slots_folder)
            
            # Convert keys to custom names for proper grouping/display
            char_names = []
            for key in char_keys:
                try:
                    name = DataManager.get_character_names(Fighter(key))
                    if name:
                        char_names.append(name)
                    else:
                        char_names.append(key)
                except:
                    char_names.append(key)

            chars_str_display = format_character_names_for_display(char_names)
            chars_str_folder = format_character_names_for_folder(char_names)
            
            # Clean Mod Name (Remove redundant chars/slots from title)
            # Use name from meta which was processed in start_download
            online_name = meta.get("mod_name", mod_data.get("mod_name", ""))
            
            mod.mod_name = online_name
            
            # Generate Final Names
            final_display_name = format_display_name(chars_str_display, slots_str_display, online_name, category_str)
            final_folder_name = format_folder_name(chars_str_folder, slots_str_folder, online_name, category_str)
            
            mod.display_name = final_display_name
            mod.folder_name = final_folder_name
            
            # Rename Folder on Disk
            parent_dir = os.path.dirname(target_dir)
            new_target_dir = os.path.join(parent_dir, final_folder_name)
            
            if new_target_dir != target_dir:
                try:
                    # Handle collision
                    counter = 1
                    base_new_dir = new_target_dir
                    while os.path.exists(new_target_dir):
                         new_target_dir = f"{base_new_dir}_{counter}"
                         counter += 1
                         
                    os.rename(target_dir, new_target_dir)
                    target_dir = new_target_dir
                    mod.path = target_dir
                    mod.folder_name = os.path.basename(target_dir) # Update in case of counter
                except Exception as e:
                    print(f"Failed to rename folder: {e}")
            
            # --- END FORMATTING LOGIC ---
            
            # Load existing info.toml to check for description and other fields
            existing_desc = ""
            existing_authors = ""
            existing_version = ""
            existing_category = ""

            existing_data = load_toml(mod.path)
            if existing_data:
                existing_desc = existing_data.get("description", "")
                existing_authors = existing_data.get("authors", "")
                existing_version = existing_data.get("version", "")
                existing_category = existing_data.get("category", "")

            # Step 2: Overlay Online Metadata
            
            # Description
            if existing_desc:
                mod.description = existing_desc
                print(f"Preserving existing description for {mod.mod_name}")
            else:
                mod.description = mod_data.get("description", "")
            
            # Authors
            if existing_authors:
                mod.authors = existing_authors
            else:
                mod.authors = mod_data.get("authors", "")

            # Version
            if existing_version:
                mod.version = clean_version(existing_version)
            else:
                mod.version = clean_version(mod_data.get("version", "1.0.0"))

            mod.url = f"https://gamebanana.com/mods/{meta.get('mod_id_str')}"
            
            # Use original URL if available in data
            if "url" in mod_data and mod_data["url"]:
                 mod.url = mod_data["url"]
            
            # Step 3: Write merged data to info.toml
            toml_data = mod.to_dict()
            dump_toml(target_dir, toml_data)
            
            # Step 4: Handle Thumbnail
            # Check for preview_links if thumbnail key is missing
            thumb_url = mod_data.get("thumbnail")
            if not thumb_url:
                previews = mod_data.get("preview_links", [])
                if previews and len(previews) > 0:
                    thumb_url = previews[0]
            
            if thumb_url:
                preview_path = os.path.join(target_dir, "preview.webp")
                if not os.path.exists(preview_path):
                    self._download_thumbnail(thumb_url, target_dir)
            
            return target_dir # Return the final (potentially renamed) path

        except Exception as e:
            print(f"Metadata write error: {e}")
            return target_dir # Return original path on error call logic continues

    def _download_thumbnail(self, url: str, target_dir: str):
        req = QNetworkRequest(QUrl(url))
        reply = self.manager.get(req)
        reply.finished.connect(lambda: self._save_thumbnail(reply, target_dir))
        
    def _save_thumbnail(self, reply, target_dir):
        if reply.error() == QNetworkReply.NetworkError.NoError:
            data = reply.readAll()
            path = os.path.join(target_dir, "preview.webp")
            f = QFile(path)
            if f.open(QIODevice.OpenModeFlag.WriteOnly):
                f.write(data)
                f.close()
            
            # Emit signal that thumbnail is ready
            self.thumbnail_updated.emit(target_dir)

        reply.deleteLater()
            
    def cancel_download(self, download_id):
        reply = self.active_downloads.get(download_id)
        if reply:
            reply.abort()
