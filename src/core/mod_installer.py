import os
import tempfile
import zipfile
import py7zr
import rarfile
from PyQt6.QtCore import QThread, pyqtSignal
from typing import Union

from src.utils.file import (
    is_valid_dir,
    is_valid_file,
    copy_directory_contents,
    rename_folder
)
from src.utils.string_helper import remove_spacing
from src.models.mod import Mod
from src.managers.data_manager import DataManager
from src.constants.enums import Fighter
from src.core.formatting import (
    group_char_name,
    format_slots,
    format_folder_name
)
from src.core.scanner import scan_mod
from src.utils.hash import get_hash
from src.utils.logger import output_log

# Configure rarfile to use 7-Zip if available
_7ZIP_PATH = r"C:\Program Files\7-Zip\7z.exe"
if os.path.exists(_7ZIP_PATH):
    # Set 7-Zip as the extraction tool
    rarfile.UNRAR_TOOL = "7z"
    rarfile.SEVENZIP_TOOL = _7ZIP_PATH
    rarfile.tool_setup()


ZIP_EXT = [
    ".zip", 
    ".7z",
    ".rar"
]

ROOT_CHILDREN = [
    "flags",
    "camera", 
    "effect", 
    "fighter", 
    "sound", 
    "stage", 
    "item", 
    "stream;", 
    "ui", 
    "config.json", 
    "plugin.nro", 
    "victory.toml", 
    "preview.webp", 
    "info.toml",
    "info.ini"
]

def extract_archive(archive_path: str, extract_to: str) -> None:
    """
    Extract archive using native Python libraries based on file extension.
    Supports .zip, .7z, and .rar formats.
    """
    ext = os.path.splitext(archive_path)[1].lower()
    
    try:
        if ext == ".zip":
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
        elif ext == ".7z":
            with py7zr.SevenZipFile(archive_path, 'r') as z:
                z.extractall(extract_to)
        elif ext == ".rar":
            with rarfile.RarFile(archive_path, 'r') as rar_ref:
                rar_ref.extractall(extract_to)
        else:
            raise ValueError(f"Unsupported archive format: {ext}")
    except (zipfile.BadZipFile, py7zr.exceptions.Bad7zFile) as e:
        raise ValueError(f"Corrupted or invalid archive file: {e}")
    except rarfile.BadRarFile as e:
        raise ValueError(f"Corrupted or invalid RAR file. The file may be incomplete or damaged: {e}")
    except rarfile.NeedFirstVolume:
        raise ValueError("This is a multi-part RAR archive. Please provide the first volume (.part1.rar)")
    except Exception as e:
        raise ValueError(f"Failed to extract archive: {e}")

def scan_for_mod_roots(root_path: str, current_depth: int = 0, max_depth: int = 3) -> list[str]:
    """
    Recursively scans for mod roots up to max_depth.
    Returns a list of all found mod root directories.
    """
    found_roots = []
    
    if not is_valid_dir(root_path):
        return []
    
    # Check if current directory is a mod root
    try:
        path_list = os.listdir(root_path)
    except OSError:
        return []

    is_root = False
    for name in path_list:
        if name.lower() in ROOT_CHILDREN:
            is_root = True
            break
            
    if is_root:
        return [root_path]
    
    # If not a root, and we haven't hit max depth, recurse
    if current_depth < max_depth:
        for name in path_list:
            child_path = os.path.join(root_path, name)
            if is_valid_dir(child_path):
                found_roots.extend(scan_for_mod_roots(child_path, current_depth + 1, max_depth))
                
    return found_roots

class ModInstaller(QThread):
    """
    Adds mods to working directory in another thread
    Can add folders, zip files containing the mod.
    """
    install_finished = pyqtSignal(list) # Emits list of new paths

    def __init__(
        self,
        directory:Union[str, list],
        root_dir:str,
        on_finish:callable, # Kept for compatibility but unused
        on_start:callable = None,
        on_progress:callable = None,
        on_dup_error:callable = None,
        on_per_error:callable = None
    ):
        super().__init__()
        self.directory = directory
        self.root_dir = root_dir
        self.on_finish = on_finish
        self.on_start = on_start
        self.on_progress = on_progress
        self.on_dup_error = on_dup_error
        self.on_per_error = on_per_error

    def run(self):
        try:
            paths = self.directory if isinstance(self.directory, list) else [self.directory]
            all_results = []
            
            for path in paths:
                if not path:
                    continue
                    
                if path.lower().endswith(tuple(ZIP_EXT)) and is_valid_file(path):
                    results = self.unzip_and_install(path)
                    all_results.extend(results)
                else:
                    mod_roots = scan_for_mod_roots(path)
                    
                    # If empty, treat the directory itself as the mod root (Fallback)
                    if not mod_roots and is_valid_dir(path):
                        mod_roots = [path]

                    if mod_roots:
                        for root in mod_roots:
                            # Using folder name if no specific fallback needed
                            mod = self.process_mod(root)
                            if mod:
                                result = self.add_mod(mod)
                                if result:
                                    all_results.append(result)
                    else:
                        output_log(f"No valid mod found in {path}")
            
            self.install_finished.emit(all_results)
            
        except Exception as e:
            output_log(f"Error in ModInstaller: {e}")
            self.install_finished.emit([])

    def process_mod(self, path:str, fallback_name:str=None) -> Mod:
        """Scan a single mod directory synchronously"""
        # Retrieve name from folder
        mod_name = os.path.basename(path)
        
        # If fallback name provided (e.g. from zip file), use it if we are at the root
        if fallback_name:
            mod_name = fallback_name
        
        # scan_mod expects a Mod object
        mod = Mod()
        mod.path = path
        mod.display_name = mod_name
        mod.mod_name = mod_name
        mod.hash = get_hash(mod_name)
        
        return scan_mod(mod)

    def unzip_and_install(self, path:str) -> list[str]:
        results = []
        # Get zip filename without extension to use as fallback mod name
        zip_name = os.path.splitext(os.path.basename(path))[0]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                extract_archive(path, temp_dir)
                
                # Check contents recursively for mods
                mod_roots = scan_for_mod_roots(temp_dir)
                
                # Fallback: if no roots found, use the temp dir itself as the mod root
                fallback_used = False
                if not mod_roots:
                    mod_roots = [temp_dir]
                    fallback_used = True
                
                for root in mod_roots:
                    # Check if the root found IS the temp dir
                    fallback = None
                    # Use fallback name if we are using the temp root (either forced fallback or just happened to be files at root)
                    if fallback_used or os.path.abspath(root) == os.path.abspath(temp_dir):
                        fallback = zip_name
                        
                    mod = self.process_mod(root, fallback_name=fallback)
                    if mod:
                        res = self.add_mod(mod)
                        if res:
                            results.append(res)
                            
            except Exception as e:
                output_log(f"Unzip error: {e}")
        return results

    def add_mod(self, mod:Mod)->str:
        if mod is None:
            return ""
    
        mod_path = mod.path
        
        # Reconstruct character data
        keys = mod.get_character_keys()
        slots = mod.get_character_slots()
        
        names = []
        groups = []
        
        for key in keys:
            try:
                fighter = Fighter(key)
                names.append(DataManager.get_character_names(fighter))
                groups.append(DataManager.get_character_groups(fighter))
            except ValueError:
                # Handle unknown fighter keys if necessary
                names.append(key)
                groups.append("")

        folder_name = format_folder_name(
            remove_spacing(group_char_name(names, groups)),
            remove_spacing(format_slots(slots)),
            remove_spacing(mod.mod_name),
            remove_spacing(mod.category)
        )
        
        # Ensure we don't overwrite
        new_dir = os.path.join(self.root_dir, folder_name)
        new_name = folder_name

        if os.path.exists(new_dir): 
            num = 0
            while os.path.exists(new_dir): 
                num+=1
                new_name = f"{folder_name}{num}"
                new_dir = os.path.join(self.root_dir, new_name)
        try:
            copy_directory_contents(mod_path, self.root_dir, new_name)
            output_log(f"successfully added dir: {mod_path}")
            return new_dir
        except PermissionError:
            output_log(f"PermissionError: You do not have the required permissions to copy to '{new_dir}'.")
            return ""
        except Exception as e:
            output_log(f"An unexpected error occurred: {e}")
            return ""
