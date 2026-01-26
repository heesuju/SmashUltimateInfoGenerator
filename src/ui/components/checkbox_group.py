from typing import List, Dict
from PyQt6.QtWidgets import QGroupBox, QHBoxLayout, QCheckBox
from PyQt6.QtCore import pyqtSlot, Qt

class CheckboxGroup(QGroupBox):
    def __init__(self, title:str, checkboxes:List[str], defaults:List[bool]=[], allow_multiple: bool = True, parent=None):
        """
        A custom QGroupBox that ensures at least one checkbox remains checked.
        """
        super().__init__(title, parent)
        self.checkboxes = []
        self.defaults = defaults
        self.allow_multiple = allow_multiple

        layout = QHBoxLayout()
        self.setLayout(layout)

        for n, label in enumerate(checkboxes):
            checkbox = QCheckBox(label)
            checkbox.stateChanged.connect(self.on_checkbox_state_changed)
            layout.addWidget(checkbox)
            self.checkboxes.append(checkbox)
            if n < len(defaults):
                checkbox.setChecked(defaults[n])
                checkbox.setCheckState(Qt.CheckState.Checked if defaults[n] else Qt.CheckState.Unchecked)

        layout.addStretch()

    @pyqtSlot()
    def on_checkbox_state_changed(self):
        """
        Slot to ensure at least one checkbox remains checked.
        """
        
        sender = self.sender()
        if not isinstance(sender, QCheckBox):
            return
        
        if not self.allow_multiple:
            if sender.isChecked():
                for cb in self.checkboxes:
                    if cb != sender:
                        cb.setChecked(False)
                        cb.setCheckState(Qt.CheckState.Unchecked)

        checked_boxes = [cb for cb in self.checkboxes if cb.isChecked()]
        if len(checked_boxes) == 0: 
            sender.setChecked(True) 
            sender.setCheckState(Qt.CheckState.Checked)

    def get_checkbox_states(self) -> Dict[str, bool]:
        """
        Returns the state of all checkboxes as a dictionary.
        """
        return {checkbox.text(): checkbox.isChecked() for checkbox in self.checkboxes}
    
    def get_value(self):
        for checkbox in self.checkboxes:
            if checkbox.isChecked():
                return checkbox.text()
    
    def reset(self):
        """
        Resets all checkboxes to their default state.
        """
        for n, checkbox in enumerate(self.checkboxes):
            if n < len(self.defaults):
                checkbox.setChecked(self.defaults[n])
                checkbox.setCheckState(Qt.CheckState.Checked if self.defaults[n] else Qt.CheckState.Unchecked)
            else:
                checkbox.setChecked(False)
                checkbox.setCheckState(Qt.CheckState.Unchecked)