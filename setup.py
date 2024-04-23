from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but they might need fine-tuning.
build_exe_options = {
    "include_files": ["cache", "data", "scraper", "ui", "utils", "cache"],
    "zip_include_packages": ["tomli_w", "Pillow", "requests", "beautifulsoup4", "selenium", "tomli"],
}

setup(
    name="Info Toml Generator",
    version="1.3",
    description="Info.toml generator for Smash Ultimate",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base="console")],
)