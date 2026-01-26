from enum import Enum
from PyQt6.QtWidgets import QDialog, QMessageBox, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

class PopupType(Enum):
    CONFIRM = "confirm"
    PROMPT = "prompt"

class PopupDialog(QDialog):
    def __init__(self, title="", message="", dialog_type:PopupType=PopupType.CONFIRM, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(300, 120)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(QLabel(message))

        if dialog_type == PopupType.CONFIRM:
            self.buttons = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        else:
            self.buttons = QMessageBox.StandardButton.Ok

        self.result = None
        self.show_dialog()

    def show_dialog(self):
        self.activateWindow()
        self.raise_()
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(self.windowTitle())
        msg_box.setText(self.layout.itemAt(0).widget().text())
        msg_box.setStandardButtons(self.buttons)
        msg_box.setModal(True)
        msg_box.activateWindow()
        msg_box.raise_()
        ret = msg_box.exec()
        self.result = ret
        self.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)