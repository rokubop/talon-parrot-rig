# Note:
# Say "parrot rig reload" after changing these

# Mouse
MOVE_SPEED = 3
SLOW_MODE_MULTIPLIER = 0.5
CLICK_HOLD_MS = 16000

# Boost
BOOST_LONG_AMOUNT = 10
BOOST_LONG_OVER_MS = 1000
BOOST_LONG_RELEASE_MS = 1000
BOOST_LONG_MAX = 15
BURST_AMOUNT = 9
BRAKE_REVERT_MS = 400
GLIDE_RELEASE_RATE = 5

# Scroll
SCROLL_SPEED = 0.4

# Scroll mode
SCROLL_MOVE_SPEED = 0.03
SCROLL_SLOW_MODE_MULTIPLIER = 0.5
SCROLL_BOOST_LONG_AMOUNT = 0.3
SCROLL_BOOST_LONG_OVER_MS = 1000
SCROLL_BOOST_LONG_RELEASE_MS = 1000
SCROLL_BURST_AMOUNT = 0.3
SCROLL_BRAKE_REVERT_MS = 400
SCROLL_RAMP_AMOUNT = 0.3
SCROLL_RAMP_REVERT_MS = 400
SCROLL_GLIDE_RELEASE_RATE = 0.1

# Timing
TRACKING_STOP_MS = 800
REVERSE_TIMEOUT = "2s"

# Click behavior
CLICK_BEHAVIOR = {
    "move": "stop",
    "boost": "stop",
    "glide": "stop",
    "scroll_move": "scroll_stop",
    "scroll_glide": "scroll_stop",
    "scroll_boost": "scroll_stop",
}

# Cursor UI
CURSOR_UI_ENABLED = True

# Mode colors
MODE_COLORS = {
    "default": "#FF0000",
    "move": "#FFFF00",
    "boost": "#2AE33C",
    "glide": "#578EF5",
    "tracking": "#A7D3FF",
    "scroll_tracking": "#A7D3FF",
    "scroll_stop": "#FF4444",
    "scroll_move": "#FFFF44",
    "scroll_boost": "#44E84E",
    "scroll_glide": "#6B9EF7",
}

# Modifier colors
MODIFIER_COLORS = {
    "shift": "#0490c9",
    "ctrl": "#84E773",
    "alt": "#FF6DD9",
}

# UI colors
UI_BORDER_COLOR = "#666666"
UI_BACKGROUND_COLOR = "#4A4A4A"
UI_TEXT_COLOR = "#FFFFFF"
UI_SELECTED_COLOR = "#3E84DA"
