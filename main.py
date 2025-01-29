import sys
from PyQt6.QtWidgets import QApplication
import qdarktheme
from src.ui.main_widget import MainWidget

if __name__ == "__main__":
    app = QApplication(sys.argv)
    qdarktheme.setup_theme("dark")
    window = MainWidget()
    window.show()
    sys.exit(app.exec())