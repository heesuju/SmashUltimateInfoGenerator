"""
Contains definitions for color hexcodes
"""
from enum import Enum

WHITE = "white"
DEFAULT = "#F0F0F0"
LIGHT_GREEN = "#90EE90"
ROYAL_BLUE = "#599ED8"

class ButtonColor(Enum):
    """Colors for button tinting"""
    YELLOW = "#FFD700"      # Gold/Yellow
    GRAY = "#9E9E9E"        # Dimmed gray
    CYAN = "#00BCD4"        # Cyan
    GREEN = "#4CAF50"       # Green
    RED = "#F44336"         # Red