from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, 
    QGridLayout, QLineEdit, QTextEdit, QComboBox, QFileDialog, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize, QEvent
from PyQt6.QtGui import QFont

from src.managers.data_manager import DataManager
from src.ui.components.multi_combobox import CheckableComboBox
from src.ui.components.single_combobox import SingleComboBox
from src.ui.components.thumbnail_label import ThumbnailLabel
from src.core.formatting import format_slots, format_display_name, format_folder_name, format_character_names_for_display, format_character_names_for_folder, clean_version
from src.ui.components.batch_task_styles import *



def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text with ellipsis if too long"""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def truncate_to_lines(text: str, max_lines: int = 3) -> str:
    """Truncate text to max number of lines, adding ellipsis if truncated"""
    if not text:
        return ""
    lines = text.split('\n')
    if len(lines) <= max_lines:
        return text
    return '\n'.join(lines[:max_lines]) + "..."


class GridCell(QFrame):
    """
    A unified cell container for the grid.
    Handles borders, background highlighting, and layout of internal widget.
    """
    def __init__(self, style_sheet=GRID_CELL_STYLE, parent=None):
        super().__init__(parent)
        self.setStyleSheet(style_sheet)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        self.cell_layout = QVBoxLayout(self)
        self.cell_layout.setContentsMargins(0, 0, 0, 0)
        self.cell_layout.setSpacing(0)
        self.cell_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    def set_content(self, widget: QWidget):
        # Clear existing content if any
        while self.cell_layout.count():
            item = self.cell_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.cell_layout.addWidget(widget)

    def set_highlight(self, highlighted: bool):
        if highlighted:
            self.setStyleSheet(GRID_CELL_HIGHLIGHT_STYLE)
        else:
            self.setStyleSheet(GRID_CELL_STYLE)



class AutoResizingTextEdit(QTextEdit):
    """
    A QTextEdit that automatically resizes vertically to fit its content.
    Acts like a multi-line QLineEdit with word wrap.
    """
    textChanged = pyqtSignal(str)
    
    def __init__(self, text="", parent=None, read_only=False):
        super().__init__(parent)
        self.setAcceptRichText(False)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTabChangesFocus(True)
        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum) # Expand vertically
        
        # Zero margins for the widget, use document margin for text padding
        self.setContentsMargins(0, 0, 0, 0)
        self.document().setDocumentMargin(4)
        
        self.setReadOnly(read_only)
        if not read_only:
            self.setStyleSheet(CELL_INPUT_STYLE)
        
        # Connect internal signal
        super().textChanged.connect(self._emit_text_changed)
        super().textChanged.connect(self._adjust_height)

        # Set text last to trigger initial adjust
        self.setPlainText(text)
        self._adjust_height()

    def setFont(self, font):
        """Override setFont to trigger height adjustment"""
        super().setFont(font)
        self._adjust_height()

    def _emit_text_changed(self):
        self.textChanged.emit(self.toPlainText())

    def _adjust_height(self):
        doc_height = self.document().size().height()
        # Add a small buffer for safety
        h = int(doc_height + 2) 
        # Ensure minimum height for single line
        h = max(h, 24)
        
        self.setMinimumHeight(h)
        self.setMaximumHeight(h) # Force fixed height for table stability
        self.updateGeometry()

    def sizeHint(self):
        return QSize(super().sizeHint().width(), self.minimumHeight())
        
    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._adjust_height()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            event.ignore() 
            return
        super().keyPressEvent(event)
        
    def setText(self, text):
        self.setPlainText(text)
        self._adjust_height()
        
    def text(self):
        return self.toPlainText()


class WrappingLabel(QLabel):
    def __init__(self, text="", parent=None, style=CELL_LABEL_STYLE):
        super().__init__(text, parent)
        self.setWordWrap(True)
        self.setStyleSheet(style)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)


class BatchTaskRow:
    """Base class for a row in the BatchTaskItem table"""
    def __init__(self, label: str, data_font: QFont):
        self.label_text = label
        self.data_font = data_font
        self.input_widget = None
        self.new_cell = None  # Reference to the editable cell for highlighting

    def _create_label_widget(self) -> QWidget:
        # Wrap in GridCell for styling consistency
        cell = GridCell(GRID_LABEL_CELL_STYLE)
        label = WrappingLabel(self.label_text, style=CELL_LABEL_STYLE)
        label.setFont(self.data_font)
        cell.set_content(label)
        return cell

    def _create_original_value_widget(self, text: str, tooltip: str = None, is_muted: bool = False) -> QWidget:
        cell = GridCell(GRID_CELL_STYLE)
        
        display_text = text if text else "—"
        
        text_edit = AutoResizingTextEdit(display_text, read_only=True)
        text_edit.setFont(self.data_font)
        
        color = "#888" if (is_muted or not text) else "#ddd"
        
        text_edit.setStyleSheet(f"""
            QTextEdit {{
                border: none;
                background: transparent;
                padding: 0px; 
                color: {color};
            }}
        """)
        
        if tooltip:
            text_edit.setToolTip(tooltip)
            
        cell.set_content(text_edit)
        return cell

    def _create_new_value_cell(self) -> GridCell:
        self.new_cell = GridCell(GRID_CELL_STYLE)
        return self.new_cell
        
    def create_widgets(self) -> tuple[QWidget, QWidget, QWidget]:
        """Returns (LabelWidget, OriginalValueWidget, NewValueWidget)"""
        raise NotImplementedError
        
    def set_highlight(self, highlighted: bool):
        """Highlight the editable cell"""
        if self.new_cell:
            self.new_cell.set_highlight(highlighted)


class TextRow(BatchTaskRow):
    def __init__(self, label: str, data_font: QFont, 
                 orig_value: str, new_value: str, attr_name: str, on_change: callable, orig_tooltip: str = None):
        super().__init__(label, data_font)
        self.orig_value = orig_value
        self.new_value = new_value
        self.attr_name = attr_name
        self.on_change = on_change
        self.orig_tooltip = orig_tooltip

    def create_widgets(self):
        label_widget = self._create_label_widget()
        orig_widget = self._create_original_value_widget(self.orig_value, self.orig_tooltip)
        
        cell = self._create_new_value_cell()
        
        self.input_widget = AutoResizingTextEdit(self.new_value if self.new_value else "")
        self.input_widget.setFont(self.data_font)
        self.input_widget.textChanged.connect(lambda text: self.on_change(self.attr_name, text))
        
        cell.set_content(self.input_widget)
        
        return label_widget, orig_widget, cell


class DescriptionRow(BatchTaskRow):
    def __init__(self, data_font: QFont, 
                 orig_desc: str, new_desc: str, on_change: callable):
        super().__init__("Description", data_font)
        self.orig_desc = orig_desc
        self.new_desc = new_desc
        self.on_change = on_change
        
    def create_widgets(self):
        label_widget = self._create_label_widget()
        orig_widget = self._create_original_value_widget(self.orig_desc)
        
        cell = self._create_new_value_cell()
        
        self.input_widget = AutoResizingTextEdit(self.new_desc if self.new_desc else "")
        self.input_widget.setFont(self.data_font)
        self.input_widget.setPlaceholderText("Enter description...")
        self.input_widget.setStyleSheet(CELL_TEXTEDIT_STYLE)
        self.input_widget.textChanged.connect(lambda: self.on_change("description", self.input_widget.toPlainText()))
        
        cell.set_content(self.input_widget)
        
        return label_widget, orig_widget, cell


class ComboRow(BatchTaskRow):
    def __init__(self, label: str, data_font: QFont,
                 orig_value: str, current_value: str, options: list, attr_name: str, 
                 on_change: callable, on_index_changed: callable = None):
        super().__init__(label, data_font)
        self.orig_value = orig_value
        self.current_value = current_value
        self.options = options
        self.attr_name = attr_name
        self.on_change = on_change
        self.on_index_changed = on_index_changed

    def create_widgets(self):
        label_widget = self._create_label_widget()
        orig_widget = self._create_original_value_widget(self.orig_value)
        
        cell = self._create_new_value_cell()
        
        self.input_widget = SingleComboBox()
        self.input_widget.addItems(self.options)
        
        if self.current_value in self.options:
            self.input_widget.setCurrentIndex(self.options.index(self.current_value))
            
        self.input_widget.currentTextChanged.connect(lambda text: self.on_change(self.attr_name, text))
        if self.on_index_changed:
            self.input_widget.currentIndexChanged.connect(self.on_index_changed)
            
        self.input_widget.setStyleSheet(CELL_COMBO_STYLE)
        self.input_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        cell.set_content(self.input_widget)
        
        return label_widget, orig_widget, cell


class MultiComboRow(BatchTaskRow):
    def __init__(self, label: str, data_font: QFont,
                 orig_text: str, current_items: list, all_items: list, attr_name: str,
                 on_model_change: callable, formatter: callable = None):
        super().__init__(label, data_font)
        self.orig_text = orig_text
        self.current_items = current_items
        self.all_items = all_items
        self.attr_name = attr_name
        self.on_model_change = on_model_change 
        self.formatter = formatter

    def create_widgets(self):
        label_widget = self._create_label_widget()
        orig_widget = self._create_original_value_widget(self.orig_text)
        
        cell = self._create_new_value_cell()
        
        self.input_widget = CheckableComboBox(self.all_items, [], False, f"Select {self.label_text}", formatter=self.formatter)
        
        # Manually set check states
        current_set = set(str(x) for x in self.current_items)
        
        for i in range(self.input_widget.model().rowCount()):
            item = self.input_widget.model().item(i)
            if item:
                text = item.text()
                check = False
                if self.attr_name == "slots":
                    try:
                        slot_num = int(text[1:])
                        if slot_num in self.current_items:
                            check = True
                    except:
                        pass
                else:
                    if text in current_set:
                        check = True
                        
                if check:
                    item.setCheckState(Qt.CheckState.Checked)

        self.input_widget.update_display()
        self.input_widget.model().dataChanged.connect(lambda *args: self.on_model_change())
        self.input_widget.setStyleSheet(CELL_COMBO_STYLE)
        self.input_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        cell.set_content(self.input_widget)
        
        return label_widget, orig_widget, cell


class NonScrollableComboBox(QComboBox):
    def wheelEvent(self, e):
        e.ignore()


class ThumbnailRow(BatchTaskRow):
    def __init__(self, data_font: QFont,
                 parent_widget, on_browse: callable, on_source_change: callable):
        super().__init__("Thumbnail", data_font)
        self.parent_widget = parent_widget 
        self.on_browse = on_browse
        self.on_source_change = on_source_change
        self.orig_thumbnail_widget = None
        self.new_thumbnail_widget = None
        self.thumb_combo = None

    def create_widgets(self):
        label_widget = self._create_label_widget()
        
        # Original thumbnail cell
        orig_cell = GridCell(GRID_CELL_STYLE)
        orig_container = QWidget()
        orig_layout = QHBoxLayout(orig_container)
        orig_layout.setContentsMargins(4, 4, 4, 4)
        
        self.orig_thumbnail_widget = ThumbnailLabel()
        self.orig_thumbnail_widget.setFixedSize(THUMBNAIL_SIZE, THUMBNAIL_SIZE)
        orig_layout.addWidget(self.orig_thumbnail_widget)
        orig_layout.addStretch()
        orig_cell.set_content(orig_container)
        
        # New thumbnail cell
        cell = self._create_new_value_cell()
        new_container = QWidget()
        new_layout = QVBoxLayout(new_container)
        new_layout.setContentsMargins(4, 4, 4, 4)
        
        # Controls
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        
        self.thumb_combo = NonScrollableComboBox()
        self.thumb_combo.addItems(["Current"])
        self.thumb_combo.setCurrentIndex(0)
        self.thumb_combo.currentIndexChanged.connect(self.on_source_change)
        self.thumb_combo.setStyleSheet(CELL_COMBO_STYLE)
        controls_layout.addWidget(self.thumb_combo, 1)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.setFixedHeight(24)
        browse_btn.clicked.connect(self.on_browse)
        browse_btn.setStyleSheet("border: 1px solid rgba(128, 128, 128, 0.3);")
        controls_layout.addWidget(browse_btn)
        
        new_layout.addLayout(controls_layout)
        
        # Preview
        self.new_thumbnail_widget = ThumbnailLabel()
        self.new_thumbnail_widget.setFixedSize(THUMBNAIL_SIZE, THUMBNAIL_SIZE)
        self.new_thumbnail_widget.setScaledContents(False)
        
        thumb_wrapper = QHBoxLayout()
        thumb_wrapper.addStretch()
        thumb_wrapper.addWidget(self.new_thumbnail_widget)
        thumb_wrapper.addStretch()
        new_layout.addLayout(thumb_wrapper)
        
        cell.set_content(new_container)
        
        return label_widget, orig_cell, cell
