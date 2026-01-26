from src.constants.colors import AppColors

# Table cell styles
ROW_CONTENT_HEIGHT = 24


# Basic cell border for the QFrame container
GRID_CELL_STYLE = f"""
    QFrame {{
        background-color: {AppColors.BG_TRANSPARENT};
        border-right: 1px solid {AppColors.BORDER_DEFAULT};
        border-bottom: 1px solid {AppColors.BORDER_DEFAULT};
        border-top: none;
        border-left: none;
        border-radius: 0;
    }}
"""

# First column (Label) style - slightly different background
GRID_LABEL_CELL_STYLE = f"""
    QFrame {{
        background-color: {AppColors.BG_SELECTED};
        border-right: 1px solid {AppColors.BORDER_DEFAULT};
        border-bottom: 1px solid {AppColors.BORDER_DEFAULT};
        border-top: none;
        border-left: none;
        border-radius: 0;
    }}
"""

# Header label style (top row)
TABLE_HEADER_STYLE = f"""
    QLabel {{
        background-color: {AppColors.BG_HOVER};
        border: 1px solid {AppColors.BORDER_DEFAULT};
        padding: 6px 8px;
        font-weight: bold;
        border-radius: 0;
    }}
"""

# Style for the Highlighted cell (New Value Changed)
GRID_CELL_HIGHLIGHT_STYLE = f"""
    QFrame {{
        background-color: {AppColors.HIGHLIGHT_BLUE_BG};
        border-right: 1px solid {AppColors.BORDER_DEFAULT};
        border-bottom: 1px solid {AppColors.BORDER_DEFAULT};
        border-top: none;
        border-left: none;
        border-radius: 0;
    }}
"""

# Inner Label style (Text inside the cell)
CELL_LABEL_STYLE = f"""
    QLabel {{
        border: none;
        background: {AppColors.BG_TRANSPARENT};
        padding: 4px;
        color: {AppColors.TEXT_PRIMARY};
    }}
"""

CELL_LABEL_MUTED_STYLE = f"""
    QLabel {{
        border: none;
        background: {AppColors.BG_TRANSPARENT};
        padding: 4px;
        color: {AppColors.TEXT_SECONDARY};
    }}
"""

# Input styles (LineEdit/TextEdit inside the cell)
# They should look seamless or have a very subtle border
CELL_INPUT_STYLE = f"""
    QLineEdit {{
        border: none;
        background: {AppColors.BG_TRANSPARENT};
        padding: 0px 4px;
        border-radius: 0;
        min-height: 24px;
        max-height: 24px;
    }}
    QLineEdit:focus {{
        background-color: {AppColors.INPUT_HOVER_FOCUS};
    }}
"""

CELL_TEXTEDIT_STYLE = f"""
    QTextEdit {{
        border: none;
        background: {AppColors.BG_TRANSPARENT};
        padding: 4px;
        border-radius: 0;
    }}
    QTextEdit:focus {{
        background-color: {AppColors.INPUT_HOVER_FOCUS};
    }}
"""

CELL_COMBO_STYLE = f"""
    QComboBox {{
        border: none;
        padding: 0px 4px;
        background-color: {AppColors.BG_TRANSPARENT};
        min-height: 24px;
        max-height: 24px;
    }}
    QComboBox:hover {{
        background-color: {AppColors.INPUT_HOVER_FOCUS};
    }}
    QComboBox::drop-down {{
        border: none;
    }}
    QComboBox QAbstractItemView {{
        background-color: {AppColors.BG_DARK};
        border: 1px solid {AppColors.BORDER_DEFAULT};
        selection-background-color: {AppColors.HIGHLIGHT_BLUE_SELECTION};
        color: {AppColors.TEXT_PRIMARY};
    }}
"""

THUMBNAIL_SIZE = 60
