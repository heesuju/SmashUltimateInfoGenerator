
# Table cell styles
ROW_CONTENT_HEIGHT = 24


# Basic cell border for the QFrame container
GRID_CELL_STYLE = """
    QFrame {
        background-color: transparent;
        border-right: 1px solid rgba(128, 128, 128, 0.3);
        border-bottom: 1px solid rgba(128, 128, 128, 0.3);
        border-top: none;
        border-left: none;
        border-radius: 0;
    }
"""

# First column (Label) style - slightly different background
GRID_LABEL_CELL_STYLE = """
    QFrame {
        background-color: rgba(128, 128, 128, 0.1);
        border-right: 1px solid rgba(128, 128, 128, 0.3);
        border-bottom: 1px solid rgba(128, 128, 128, 0.3);
        border-top: none;
        border-left: none;
        border-radius: 0;
    }
"""

# Header label style (top row)
TABLE_HEADER_STYLE = """
    QLabel {
        background-color: rgba(128, 128, 128, 0.2);
        border: 1px solid rgba(128, 128, 128, 0.3);
        padding: 6px 8px;
        font-weight: bold;
        border-radius: 0;
    }
"""

# Style for the Highlighted cell (New Value Changed)
GRID_CELL_HIGHLIGHT_STYLE = """
    QFrame {
        background-color: rgba(33, 150, 243, 0.15);
        border-right: 1px solid rgba(128, 128, 128, 0.3);
        border-bottom: 1px solid rgba(128, 128, 128, 0.3);
        border-top: none;
        border-left: none;
        border-radius: 0;
    }
"""

# Inner Label style (Text inside the cell)
CELL_LABEL_STYLE = """
    QLabel {
        border: none;
        background: transparent;
        padding: 4px;
        color: #ddd;
    }
"""

CELL_LABEL_MUTED_STYLE = """
    QLabel {
        border: none;
        background: transparent;
        padding: 4px;
        color: #888;
    }
"""

# Input styles (LineEdit/TextEdit inside the cell)
# They should look seamless or have a very subtle border
CELL_INPUT_STYLE = """
    QLineEdit {
        border: none;
        background: transparent;
        padding: 0px 4px;
        border-radius: 0;
        min-height: 24px;
        max-height: 24px;
    }
    QLineEdit:focus {
        background-color: rgba(255, 255, 255, 0.05);
    }
"""

CELL_TEXTEDIT_STYLE = """
    QTextEdit {
        border: none;
        background: transparent;
        padding: 4px;
        border-radius: 0;
    }
    QTextEdit:focus {
        background-color: rgba(255, 255, 255, 0.05);
    }
"""

CELL_COMBO_STYLE = """
    QComboBox {
        border: none;
        padding: 0px 4px;
        background-color: transparent;
        min-height: 24px;
        max-height: 24px;
    }
    QComboBox:hover {
        background-color: rgba(255, 255, 255, 0.05);
    }
    QComboBox::drop-down {
        border: none;
    }
"""

THUMBNAIL_SIZE = 60
