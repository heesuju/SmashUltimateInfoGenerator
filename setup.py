import sys
import os
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["os", "sys", "json", "requests", "PIL", "tomli", "qdarktheme", 
                 "pyglet", "py7zr", "rarfile", "pydantic", "PyQt6", "PyQt6.QtMultimedia", "PyQt6.QtSvg", "certifi", "ssl",
                 "urllib3", "idna", "charset_normalizer"],
    "excludes": [],
    "include_files": [
        ("assets", "assets"),
        ("data/character_data.csv", "data/character_data.csv"),
        ("data/item_names.csv", "data/item_names.csv"),
        ("LICENSE", "LICENSE"),
    ]
}

base = None
if sys.platform == "win32":
   base = "Win32GUI"

setup(
    name="SmashUltimateInfoGenerator",
    version="2.0.0",
    description="Smash Ultimate Info Generator",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base, icon="assets/icons/app_icon.ico")]
)
