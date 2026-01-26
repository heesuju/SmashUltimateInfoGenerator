from pydantic import BaseModel
from typing import Union, List
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
    QLineEdit
)
from PyQt6.QtGui import QPixmap, QColor, QPalette, QIcon
from src.managers.data_manager import ButtonIcons

class InputButton(BaseModel):
    text:str=""
    img:ButtonIcons=None
    callback:callable=None
    highlight:bool=False
    
    model_config = {
        "arbitrary_types_allowed": True
    }

class InputButtonWidget(QWidget):
    def __init__(self, placeholder_text:str, buttons:Union[List[InputButton], InputButton], on_submit:callable=None):
        super().__init__()
        
        hbox = QHBoxLayout()
        hbox.setSpacing(0)
        hbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(hbox)

        self.input_box = QLineEdit()
        self.input_box.setStyleSheet("""
            QLineEdit {
                border-top-left-radius: 5px;
                border-bottom-left-radius: 5px;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
            }
        """)
        self.input_box.setPlaceholderText(placeholder_text)
        if on_submit is not None:
            self.input_box.returnPressed.connect(on_submit)

        hbox.addWidget(self.input_box)
        
        if not isinstance(buttons, list):
            buttons = [buttons]

        for n, data in enumerate(buttons):
            button = QPushButton(data.text)
            if data.img is not None:
                button.setIcon(QIcon(QPixmap(str(data.img.value))))
            if data.callback is not None:
                button.clicked.connect(data.callback)

            style = ""
            borders = ""

            if n >= len(buttons) - 1:
                borders = """border-top-left-radius: 0px;
                    border-bottom-left-radius: 0px;
                    border-top-right-radius: 5px;
                    border-bottom-right-radius: 5px;"""
            else:
                borders = """border-top-left-radius: 0px;
                    border-bottom-left-radius: 0px;
                    border-top-right-radius: 0px;
                    border-bottom-right-radius: 0px;"""

            if data.highlight:
                style = """QPushButton {
                    background-color: #6563FF;
                    color: white;
                    font-weight: bold;
                    {0}
                }
                QPushButton:hover {
                    background-color: #8481FF;
                }
                QPushButton:pressed {
                    background-color: #4B4BFF; 
                }""".replace("{0}", borders)
            else:
                style = """QPushButton {
                    {0}
                }""".replace("{0}", borders)
            
            button.setStyleSheet(style)
            hbox.addWidget(button)

    def set_text(self, text:str):
        self.input_box.setText(text)

    def get_text(self):
        current_text = self.input_box.text()
        return current_text
    
    def set_border_color(self, color:str=""):
        if color:
            input_style = """QLineEdit {
                border: 1px solid {0};
                border-top-left-radius: 5px;
                border-bottom-left-radius: 5px;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
            }""".replace("{0}", color)
        else:
            input_style = """QLineEdit {
                border-top-left-radius: 5px;
                border-bottom-left-radius: 5px;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
            }"""
        
        self.input_box.setStyleSheet(input_style)