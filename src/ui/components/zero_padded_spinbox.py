from PyQt6.QtWidgets import QSpinBox


class ZeroPaddedSpinBox(QSpinBox):
    """QSpinBox that displays values with zero-padding (e.g., 00, 01, 02)"""
    
    def textFromValue(self, value: int) -> str:
        return f"{value:02d}"
    
    def valueFromText(self, text: str) -> int:
        # Remove prefix and parse the number
        return int(text.lstrip('C'))
