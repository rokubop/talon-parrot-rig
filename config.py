# Configuration file for parrot_mode_v7
# This file contains all configurable constants and settings

# Mode colors - easy to configure
MODE_COLORS = {
    "default": "#43ABF5",    # Blue
    "move": "#176918",       # Orange
    "head": "#83E99B",       # Green
    "full": "#BD10E0",       # Purple
    "window": "#E35050",     # Teal
    "keyboard": "#A7D3FF",   # Light Green
    "number": "#F89C1C",     # Yellow
}

# Mode display codes
MODE_CODES = {
    "default": "DEF",
    "move": "MOV",
    "head": "HEAD",
    "full": "FULL",
    "window": "WIN",
    "keyboard": "KEYB",
    "number": "NUMB",
}

# Movement settings
MOVEMENT_SETTINGS = {
    "speed": 60,  # Base movement speed
    "boost_small": 100,  # Small boost multiplier
    "boost_large": 200,  # Large boost multiplier
}

# Scrolling settings
SCROLLING_SETTINGS = {
    "speed": 0.8,  # Base scroll speed
}

# Full mode settings
FULL_MODE_SETTINGS = {
    "stop_time": 1000,  # Time to stop temporarily in full mode (milliseconds)
}

# Click behavior settings per mode
CLICK_BEHAVIOR = {
    "move": "stop",     # "stop" or "continue"
    "head": "stop",     # "stop" or "continue"
}

# Utility (palate) action setting
UTILITY_ACTION = "hold_click"  # Default utility action

# Available utility actions
UTILITY_ACTIONS = {
    "click": "Click",
    "hold_click": "Hold Click",
    "right_click": "Right Click",
    "hold_right_click": "Hold Right Click",
    "middle_click": "Middle Click",
    "middle_hold": "Middle Hold",
    "repeat_last": "Repeat Last",
    "repeat_phrase": "Repeat Phrase",
}

# Settings UI options (5 discrete values each)
SETTINGS_OPTIONS = {
    "speed": [30, 60, 90, 120, 150],
    "boost_small": [50, 100, 150, 200, 250],
    "boost_large": [100, 200, 300, 400, 500],
    "stop_time": [500, 1000, 1500, 2000, 2500],
}

# Modifier colors (matching existing implementation)
MODIFIER_COLORS = {
    "shift": "#0490c9",
    "ctrl": "#84E773",
    "alt": "#FF6DD9",
}
