from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, 
    QPushButton, QLabel, QFrame, QHeaderView, QTreeWidget, QTreeWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QEvent, QSize, QTimer
from PyQt6.QtGui import QFont, QIcon
from src.ui.components.multi_combobox import CheckableComboBox
from src.ui.components.batch_task_styles import CELL_COMBO_STYLE

class AssignmentRowWidget(QWidget):
    """
    Custom widget for each row in the assignment list.
    Contains:
    - Entity Selector (CheckableComboBox)
    - Slot Selector (CheckableComboBox)
    - Remove Button
    """
    def __init__(self, entities: dict, slot_options: list, default_entity=None, default_slots=None, slot_formatter=None, slot_sorter=None, parent=None):
        super().__init__(parent)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(4, 2, 4, 2)
        self.layout.setSpacing(5)
        self.entity_combo = CheckableComboBox(include_all=False, placeholder_text="Select Entity")
        self.entity_combo.setStyleSheet(CELL_COMBO_STYLE)
        self.entity_map = {}
        
        items = []
        if isinstance(entities, dict):
            # Sort by display name
            sorted_items = sorted(entities.items(), key=lambda x: x[1])
            for key, name in sorted_items:
                items.append(name)
                self.entity_map[name] = key
        else:
            items = sorted(entities)
            for name in items:
                self.entity_map[name] = name
                 
        self.entity_combo.add_items(items)
        if default_entity:
            keys_to_check = default_entity if isinstance(default_entity, list) else [default_entity]
            
            display_names = []
            for k in keys_to_check:
                for d_name, d_key in self.entity_map.items():
                    if d_key == k:
                        display_names.append(d_name)
                        
            for d_name in display_names:
                # Find item index? CheckableComboBox needs manual check
                model = self.entity_combo.model()
                for i in range(model.rowCount()):
                    if model.item(i).text() == d_name:
                        model.item(i).setCheckState(Qt.CheckState.Checked)
            self.entity_combo.update_display()

        # Slots Selector
        self.slots_combo = CheckableComboBox(include_all=False, placeholder_text="Select Slots", formatter=slot_formatter, sorter=slot_sorter)
        self.slots_combo.setStyleSheet(CELL_COMBO_STYLE)
        self.slots_combo.add_items(slot_options)
        if default_slots:
            default_set = set(default_slots)
            model = self.slots_combo.model()
            for i in range(model.rowCount()):
                if model.item(i).text() in default_set:
                    model.item(i).setCheckState(Qt.CheckState.Checked)
            self.slots_combo.update_display()
             
        self.layout.addWidget(self.entity_combo, 1) # Stretch 1
        self.layout.addWidget(self.slots_combo, 1)  # Stretch 1
        
        # Remove Button
        self.remove_btn = QPushButton("-")
        self.remove_btn.setFixedSize(20, 20)
        self.remove_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                border-radius: 3px;
                color: #ff5555;
                font-weight: bold;
                padding-bottom: 2px;
            }
            QPushButton:hover {
                background-color: rgba(255, 100, 100, 0.3);
            }
        """)
        self.layout.addWidget(self.remove_btn)

    def get_data(self):
        """Return tuple (List[Keys], List[Slots])"""
        # Entities
        checked_names = self.entity_combo.get_checked()
        keys = []
        for name in checked_names:
            k = self.entity_map.get(name)
            if k: keys.append(k)
            
        # Slots
        slots = self.slots_combo.get_checked()
        
        return keys, slots

class AssignmentListWidget(QWidget):
    """
    Widget matching workspace_list.py style.
    Host for AssignmentRowWidgets.
    """
    assignments_changed = pyqtSignal()
    sizeChanged = pyqtSignal()
    
    def __init__(self, entity_label="Entity", slot_label="Slots", parent=None):
        super().__init__(parent)
        self.entity_label = entity_label
        self.slot_label = slot_label
        
        self.entity_data = {} # Store for new rows
        self.slot_options = [] # Store for new rows
        self.slot_formatter = None
        self.slot_sorter = None
        
        self.rows = []
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        self.tree = QTreeWidget()
        self.tree.setColumnCount(1)
        # Header Label with padding for button
        self.tree.setHeaderLabels([f"{self.entity_label} Assignments"])
        self.tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid rgba(128, 128, 128, 0.3);
                background: rgba(0, 0, 0, 0.2);
                border-radius: 5px;
                outline: 0;
            }
            QTreeWidget::item {
                padding: 2px;
                border: none;
            }
            QTreeWidget::item:hover {
                background-color: transparent; 
            }
            QTreeWidget::item:selected {
                background-color: transparent;
            }
             QHeaderView::section {
                background-color: rgba(0, 0, 0, 0.3);
                color: #ddd;
                padding: 4px;
                border: none;
                border-bottom: 1px solid rgba(128, 128, 128, 0.3);
                font-weight: bold;
            }
        """)
        self.tree.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tree.setSelectionMode(QTreeWidget.SelectionMode.NoSelection)
        self.tree.setRootIsDecorated(False)
        self.tree.setIndentation(0)
        
        layout.addWidget(self.tree)
        
        # Add Button (Overlay on Header key)
        self.add_btn = QPushButton("+", self.tree.header())
        self.add_btn.setFixedSize(16, 16)
        self.add_btn.setToolTip("Add Assignment Row")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 3px;
                color: white;
                font-weight: bold;
                padding-bottom: 2px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        self.add_btn.clicked.connect(self.add_row)
        
        self.tree.header().installEventFilter(self)
        self.tree.installEventFilter(self)

    def eventFilter(self, source, event):
        if source == self.tree.header() or source == self.tree:
            if event.type() == QEvent.Type.Resize or event.type() == QEvent.Type.Move:
                self.update_add_btn_position()
                self.adjust_height() # Auto-resize height
        return super().eventFilter(source, event)
    
    def showEvent(self, event):
        super().showEvent(event)
        self.update_add_btn_position()
        self.adjust_height()

    def update_add_btn_position(self):
        header = self.tree.header()
        w = header.width()
        h = header.height()
        
        # Align right
        btn_w, btn_h = 16, 16
        padding_right = 8
        pos_x = w - btn_w - padding_right
        pos_y = (h - btn_h) // 2
        
        self.add_btn.setGeometry(pos_x, pos_y, btn_w, btn_h)

    def adjust_height(self):
        header_height = self.tree.header().height()
        row_count = self.tree.topLevelItemCount()
        row_height = 36 
        total = header_height + (row_count * row_height) + 6
        
        self.tree.setFixedHeight(total)
        self.setFixedHeight(total)
        self.sizeChanged.emit()

    def set_entities(self, entities: dict):
        self.entity_data = entities
        self.tree.setHeaderLabels([f"{self.entity_label} Assignments"])
        
    def set_slot_options(self, slots: list, formatter=None, sorter=None):
        self.slot_options = slots
        self.slot_formatter = formatter
        self.slot_sorter = sorter

    def add_row(self, default_entity=None, default_slots=None):
        item = QTreeWidgetItem(self.tree)

        row_widget = AssignmentRowWidget(
            self.entity_data, 
            self.slot_options, 
            default_entity, 
            default_slots,
            self.slot_formatter,
            self.slot_sorter
        )
        
        row_widget.entity_combo.model().dataChanged.connect(self.on_changed)
        row_widget.slots_combo.model().dataChanged.connect(self.on_changed)
        
        row_widget.remove_btn.clicked.connect(lambda: self.remove_row(item))
        
        self.tree.setItemWidget(item, 0, row_widget)
        self.adjust_height()
        
        if default_entity is None:
            pass 
             
    def remove_row(self, item):
        index = self.tree.indexOfTopLevelItem(item)
        if index >= 0:
            self.tree.takeTopLevelItem(index)
            self.adjust_height()
            self.on_changed()

    def on_changed(self, *args):
        self.assignments_changed.emit()

    def clear(self):
        self.tree.clear()
        self.adjust_height()
        self.on_changed()

    def set_assignments(self, data: list):
        """
        Populate rows.
        data: [{"id": key, "slots": [s1, s2]}]
        
        New design supports multi-key per row, but input data usually is normalized (one key per item).
        We can group them if slots are identical? 
        The "Simple Mode" behavior from EditPanel suggests grouping.
        
        Let's try to compact the data: Group by Slots.
        """
        self.tree.clear()
        
        grouped = {}
        for item in data:
            key = item["id"]
            slots = tuple(sorted(item["slots"]))
            if slots not in grouped:
                grouped[slots] = []
            grouped[slots].append(key)
            
        # Create rows
        for slots_tuple, keys in grouped.items():
            self.add_row(default_entity=keys, default_slots=list(slots_tuple))
            
        self.adjust_height()
            
    def get_assignments(self) -> list:
        """
        Flatten rows back to normalized list.
        [{"id": key, "slots": [s1, s2]}]
        """
        result = []
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            widget = self.tree.itemWidget(item, 0)
            if isinstance(widget, AssignmentRowWidget):
                keys, slots = widget.get_data()
                for k in keys:
                    result.append({
                        "id": k, 
                        "slots": sorted(slots)
                    })
        return result
