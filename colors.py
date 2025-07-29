"""
Color definitions for parrot mode v7
Centralized color management for consistency across UI components
"""

# Mode colors - used for visual cursor and UI indicators
MODE_COLORS = {
    "default": "FF0000",     # Red
    "move": "FFFF00",        # Yellow
    "head": "83E99B",        # Light Green
    "full": "BD10E0",        # Purple
    "window": "E35050",      # Red-ish
    "keyboard": "A7D3FF",    # Light Blue
    "number": "F89C1C",      # Orange
}

# Modifier colors - used for visual cursor modifier indicators
MODIFIER_COLORS = {
    "shift": "0490c9",       # Blue
    "ctrl": "84E773",        # Green
    "alt": "FF6DD9",         # Pink
}

def get_mode_color(mode: str) -> str:
    """Get the color for a specific mode"""
    return MODE_COLORS.get(mode, "FF0000")  # Default to red

def get_modifier_color(modifier: str) -> str:
    """Get the color for a specific modifier"""
    return MODIFIER_COLORS.get(modifier, "FFFFFF")  # Default to white
