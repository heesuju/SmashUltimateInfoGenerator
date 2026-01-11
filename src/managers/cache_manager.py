"""
cache_manager.py: Manages mod scan result caching to improve performance
"""

import os
import json
from typing import Optional
from src.utils.file import is_valid_dir
from src.utils.logger import output_log

CACHE_FILE = "data/cache/mod_scan_cache.json"

class CacheManager:
    def __init__(self):
        self.cache = self._load_cache()
    
    def _load_cache(self) -> dict:
        """Load cache from disk"""
        if not os.path.exists(CACHE_FILE):
            return {}
        
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            output_log(f"Failed to load scan cache: {e}")
            return {}
    
    def _save_cache(self):
        """Save cache to disk"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
            
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            output_log(f"Failed to save scan cache: {e}")
    
    def _get_mtime(self, mod_path: str) -> Optional[float]:
        """Get modification time of mod directory"""
        try:
            if is_valid_dir(mod_path):
                return os.path.getmtime(mod_path)
        except Exception:
            pass
        return None
    
    def is_cache_valid(self, mod_path: str) -> bool:
        """Check if cache entry is valid for given mod path"""
        if mod_path not in self.cache:
            return False
        
        cached_mtime = self.cache[mod_path].get('mtime')
        current_mtime = self._get_mtime(mod_path)
        
        if cached_mtime is None or current_mtime is None:
            return False
        
        # Cache is valid if modification times match
        return cached_mtime == current_mtime
    
    def get_cached_mod(self, mod_path: str) -> Optional[dict]:
        """
        Get cached mod data if valid
        Returns None if cache miss or invalid
        """
        if not self.is_cache_valid(mod_path):
            return None
        
        return self.cache[mod_path].get('scan_data')
    
    def set_cached_mod(self, mod_path: str, mod_data: dict):
        """Store mod scan result in cache"""
        mtime = self._get_mtime(mod_path)
        
        if mtime is None:
            return
        
        self.cache[mod_path] = {
            'mtime': mtime,
            'scan_data': mod_data
        }
        
        self._save_cache()
    
    def cleanup(self):
        """Remove cache entries for mods that no longer exist"""
        paths_to_remove = []
        
        for mod_path in self.cache.keys():
            if not is_valid_dir(mod_path):
                paths_to_remove.append(mod_path)
        
        for path in paths_to_remove:
            del self.cache[path]
        
        if paths_to_remove:
            output_log(f"Cleaned {len(paths_to_remove)} orphaned cache entries")
            self._save_cache()
    
    def clear_all(self):
        """Clear entire cache"""
        self.cache = {}
        self._save_cache()
        output_log("Scan cache cleared")
