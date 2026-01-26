from PyQt6.QtWidgets import QApplication, QFileDialog, QPushButton, QWidget, QVBoxLayout
from src.utils.logger import output_log

def choose_folder(parent:QWidget, default_dir:str=""):
    folder_path = QFileDialog.getExistingDirectory(
        parent,
        "Select a folder",
        default_dir
    )
    if folder_path:
        output_log(f"Selected folder: {folder_path}")
    
    return folder_path