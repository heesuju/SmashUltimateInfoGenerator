from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but they might need fine-tuning.
build_exe_options = {
    "packages": ["tkinter", "tkinterdnd2"],
    "includes": ["tkinterdnd2"],    
    "include_files": ["cache", "data", "ui", "utils"],
    "zip_include_packages": ["tomli_w", "Pillow", "requests", "beautifulsoup4", "selenium", "tomli", "webdriver_manager"],
}

# change base to console to show console logs
setup(
    name="Info Toml Generator",
    version="1.6.1",
    description="Info.toml Generator for Smash Ultimate",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base="Win32GUI")],
)