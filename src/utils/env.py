import os
import shutil
import platform
from typing import Optional

def find_executable(names: list[str], extra_paths: list[str] = []) -> Optional[str]:
    """
    Find an executable by trying multiple names and extra paths.
    """
    # 1. Search in PATH
    for name in names:
        path = shutil.which(name)
        if path:
            return path
            
    # 2. Search in extra paths
    for path in extra_paths:
        if os.path.exists(path):
            return path
            
    return None

def find_7z() -> Optional[str]:
    """
    Search for 7-Zip executable based on platform.
    """
    system = platform.system()
    
    if system == "Windows":
        # Common Windows names and paths
        names = ["7z", "7za", "7z.exe"]
        extra_paths = [
            r"C:\Program Files\7-Zip\7z.exe",
            r"C:\Program Files (x86)\7-Zip\7z.exe"
        ]
        return find_executable(names, extra_paths)
    else:
        # Linux / Unix
        names = ["7z", "7za", "p7zip"]
        return find_executable(names)
