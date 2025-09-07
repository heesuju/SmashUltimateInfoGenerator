from PyQt6.QtWidgets import (
    QListView, QSizePolicy, QListWidget, QLabel
)
from functools import partial
from PyQt6.QtGui import QIcon, QPixmap, QPainter
from PyQt6.QtCore import Qt, QRect, QSize
from PyQt6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QWidget,
)
from PyQt6.QtCore import Qt, QSize, QPoint, QPointF
from PyQt6.QtGui import QPixmap, QColor, QPalette
from PyQt6.QtWidgets import QListWidget, QListView, QStyledItemDelegate, QStyleOptionViewItem, QGraphicsDropShadowEffect, QSizePolicy, QStyle
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget,
    QTreeWidgetItem, QCheckBox, QHeaderView
)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPainterPath, QImage, QBrush, QPen, QColor
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QRect, QSize
from src.ui.components.layout import HBox, VBox
from src.constants.enums import Fighter
from src.managers.data_manager import ButtonIcons, DataManager
from src.models.mod import Mod
from PyQt6.QtWidgets import QGraphicsOpacityEffect
from PyQt6.QtCore import QPropertyAnimation

class TreeItem(QTreeWidgetItem):
    def __init__(self, parent, mod:Mod, on_clicked:callable, on_enabled:callable):
        self.mod = mod
        self.on_clicked = on_clicked
        self.on_enabled = on_enabled
        self.animations = []
        super().__init__(["", "", "", "", "", "", ""])

        parent.addTopLevelItem(self)

        check_widget = QCheckBox()
        check_widget.setChecked(False)
        check_widget.stateChanged.connect(lambda state: self.on_enabled(self.mod) if self.on_enabled else None)
        name_widget = QLabel(self.mod.mod_name)
        category_widget = QLabel(self.mod.category)
        authors_widget = QLabel(self.mod.authors)
        slot_widget = QLabel("C01-02")

        icons_widget = QWidget()
        from PyQt6.QtWidgets import QHBoxLayout
        icons_layout = QHBoxLayout(icons_widget)
        icons_layout.setContentsMargins(0, 0, 0, 0)
        icons_layout.setSpacing(0)
        keys = self.mod.get_grouped_character_keys()
        character_icons = DataManager.get_character_icons([character for character in keys])
        for path in character_icons:
            icon_label = QLabel()
            icon_label.setPixmap(QPixmap(path).scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            icons_layout.addWidget(icon_label)
        icons_layout.addStretch()


        # item.setData(0, Qt.ItemDataRole.UserRole, icons)

        
        # # Add button widget to the last column
        btn = QPushButton()
        btn.setIcon(QIcon(QPixmap(ButtonIcons.ENABLE.value)))
        btn.setStyleSheet(("""QPushButton {
            border-radius: 0px;
            border: none;
        }"""))
        btn.setFixedHeight(20)  # keep it small to fit row
        btn.clicked.connect(partial(self.on_item_toggled, self.mod.mod_name, btn))
            
        parent.setItemWidget(self, 0, check_widget)  # <-- custom widget in column 0
        parent.setItemWidget(self, 1, name_widget)
        parent.setItemWidget(self, 2, category_widget)
        parent.setItemWidget(self, 3, authors_widget)
        parent.setItemWidget(self, 4, slot_widget)
        parent.setItemWidget(self, 5, icons_widget)
        parent.setItemWidget(self, 6, btn)
        self.widgets = [check_widget, name_widget, category_widget, authors_widget, slot_widget, icons_widget, btn]

    def on_item_toggled(self, name, btn):
        print(f"Button clicked for {name}")
        btn.setIcon(QIcon(QPixmap(ButtonIcons.DISABLE.value)))
        if self.on_enabled is not None:
            self.on_enabled(self.mod)

    def on_item_clicked(self, item, column):
        print(f"Item clicked: {item.text(0)} in column {column}")
        if self.on_clicked is not None:
            self.on_clicked(self.mod)

    def animate_in(self, duration=600):
        self.animations = []
        for widget in self.widgets:
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
            effect.setOpacity(0.0)
            animation = QPropertyAnimation(effect, b"opacity")
            animation.setDuration(duration)
            animation.setStartValue(0.0)
            animation.setEndValue(1.0)
            animation.start()
            self.animations.append(animation)