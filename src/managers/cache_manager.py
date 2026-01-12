"""
cache_manager.py: Manages mod scan result caching using SQLite
"""

import os
import json
import sqlite3
from typing import Optional
from src.utils.file import is_valid_dir
from src.utils.logger import output_log

CACHE_DB = "data/cache/mod_scan_cache.db"

class CacheManager:
    def __init__(self):
        self._init_database()
        self.cleanup()  # Remove stale entries on startup
    
    def _init_database(self):
        """Initialize SQLite database with proper schema"""
        # Ensure directory exists
        os.makedirs(os.path.dirname(CACHE_DB), exist_ok=True)
        
        # Connect to database
        self.conn = sqlite3.connect(CACHE_DB, check_same_thread=False)
        
        # Enable WAL mode for better concurrent access
        self.conn.execute("PRAGMA journal_mode=WAL")
        
        # Create table if it doesn't exist
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS mod_cache (
                mod_path TEXT PRIMARY KEY,
                mtime REAL NOT NULL,
                scan_data TEXT NOT NULL
            )
        """)
        
        # Create index for faster mtime lookups
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_mtime ON mod_cache(mtime)
        """)
        
        self.conn.commit()
        output_log("Cache database initialized")
    
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
        try:
            cursor = self.conn.execute(
                "SELECT mtime FROM mod_cache WHERE mod_path = ?",
                (mod_path,)
            )
            row = cursor.fetchone()
            
            if row is None:
                return False
            
            cached_mtime = row[0]
            current_mtime = self._get_mtime(mod_path)
            
            if cached_mtime is None or current_mtime is None:
                return False
            
            # Cache is valid if modification times match
            return cached_mtime == current_mtime
            
        except Exception as e:
            output_log(f"Error checking cache validity: {e}")
            return False
    
    def get_cached_mod(self, mod_path: str) -> Optional[dict]:
        """
        Get cached mod data if valid
        Returns None if cache miss or invalid
        """
        if not self.is_cache_valid(mod_path):
            return None
        
        try:
            cursor = self.conn.execute(
                "SELECT scan_data FROM mod_cache WHERE mod_path = ?",
                (mod_path,)
            )
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            return json.loads(row[0])
            
        except Exception as e:
            output_log(f"Error retrieving cached mod: {e}")
            return None
    
    def set_cached_mod(self, mod_path: str, mod_data: dict):
        """Store mod scan result in cache"""
        mtime = self._get_mtime(mod_path)
        
        if mtime is None:
            return
        
        try:
            self.conn.execute(
                "INSERT OR REPLACE INTO mod_cache (mod_path, mtime, scan_data) VALUES (?, ?, ?)",
                (mod_path, mtime, json.dumps(mod_data))
            )
            self.conn.commit()
            
        except Exception as e:
            output_log(f"Error caching mod data: {e}")
    
    def cleanup(self):
        """Remove cache entries for mods that no longer exist"""
        try:
            cursor = self.conn.execute("SELECT mod_path FROM mod_cache")
            all_paths = [row[0] for row in cursor.fetchall()]
            
            paths_to_remove = [path for path in all_paths if not is_valid_dir(path)]
            
            if paths_to_remove:
                for path in paths_to_remove:
                    self.conn.execute("DELETE FROM mod_cache WHERE mod_path = ?", (path,))
                
                self.conn.commit()
                output_log(f"Cleaned {len(paths_to_remove)} orphaned cache entries")
                
        except Exception as e:
            output_log(f"Error during cache cleanup: {e}")
    
    def clear_all(self):
        """Clear entire cache"""
        try:
            self.conn.execute("DELETE FROM mod_cache")
            self.conn.commit()
            output_log("Scan cache cleared")
            
        except Exception as e:
            output_log(f"Error clearing cache: {e}")
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        try:
            cursor = self.conn.execute("SELECT COUNT(*) FROM mod_cache")
            total_entries = cursor.fetchone()[0]
            
            # Get database file size
            db_size = os.path.getsize(CACHE_DB) if os.path.exists(CACHE_DB) else 0
            
            return {
                'total_entries': total_entries,
                'db_size_mb': db_size / (1024 * 1024)
            }
        except Exception as e:
            output_log(f"Error getting cache stats: {e}")
            return {'total_entries': 0, 'db_size_mb': 0}
    
    def close(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()
