import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
import qdarktheme

from src.ui.main_menu import MainMenu
from src.managers.config_manager import ConfigManager

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("assets/icons/app_icon.svg"))
    config_manager = ConfigManager()

    qdarktheme.setup_theme(str(config_manager.config.theme))
    window = MainMenu(config_manager)
    window.show()
    sys.exit(app.exec())