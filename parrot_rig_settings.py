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
BURST_AMOUNT = 4.5
BRAKE_REVERT_MS = 0
# A burst is usually a hop to something nearby, so the cursor eases down after
# one to make the click easier. Another hiss inside the window clears it and
# bursts at full speed, so chaining still covers distance.
BURST_SETTLE_SCALE = 0.5
BURST_SETTLE_OVER_MS = 400
BURST_SETTLE_HOLD_MS = 700
BURST_SETTLE_REVERT_MS = 500
GLIDE_RELEASE_RATE = 5

# Scroll
SCROLL_SPEED = 0.4

# The app picker hotkey, named because two things reach for it: tut eh opens
# it, and utility 1 is set to it out of the box. This is what BentoPick binds.
APP_PICKER_KEY = "alt-`"

# Window mode. Whatever your window manager uses.
WINDOW_KEYS = {
    "picker":   APP_PICKER_KEY,
    "tab_next": "ctrl-tab",
    "tab_prev": "ctrl-shift-tab",
    "tab_close": "ctrl-w",
    "close":    "alt-f4",
}

# Sent while super is held, so a run of these keeps working. Letting super go
# between them is what makes Windows offer to fill the other half of the screen,
# and win+arrow stops working until you dismiss it.
WINDOW_SUPER_KEYS = {
    "left":         "left",
    "right":        "right",
    "up":           "up",
    "down":         "down",
    "screen_left":  "shift-left",
    "screen_right": "shift-right",
}

# How long alt is held either side of the tab, so the switcher registers
WINDOW_ALT_TAB_HOLD_MS = 60

# Gap between letting super go and the escape that dismisses snap assist
WINDOW_SNAP_ASSIST_MS = 80

# Canvas scale. Every wheel tick is a zoom step in most apps, so this runs
# slower than plain scroll. Boost and burst keep the same ratio to it that the
# canvas move ones keep to canvas speed.
CANVAS_SCALE_SPEED = 0.015

# Canvas move
CANVAS_MOVE_SPEED = 0.03
CANVAS_SLOW_MODE_MULTIPLIER = 0.5
CANVAS_BOOST_LONG_AMOUNT = 0.3
CANVAS_BOOST_LONG_OVER_MS = 1000
CANVAS_BOOST_LONG_RELEASE_MS = 1000
CANVAS_BURST_AMOUNT = 0.6
CANVAS_BRAKE_REVERT_MS = 400
CANVAS_RAMP_AMOUNT = 0.3
CANVAS_RAMP_REVERT_MS = 400
CANVAS_GLIDE_RELEASE_RATE = 0.1

# Anchor
ANCHOR_MOVE_MS = 200
ANCHOR_MOVE_EASING = "ease_in_out"
ANCHOR_MARKER_COLOR = "FFFFFF"
# How close counts as standing on an anchor, for removing it and for skipping
# it as a return target
ANCHOR_HIT_RADIUS = 24
ANCHOR_LINE_COLOR = "FFFFFF66"
# How far inside the screen edge a screen target lands, enough to be on the
# close button rather than the corner pixel
SCREEN_EDGE_INSET = 24

# Stand-in anchors used when the Return setting is Screen Anchors and you have
# not dropped any of your own. Never drawn. (snap target, anchor kind), and the
# targets come from TARGETS in src/snap.py.
SCREEN_ANCHORS = [
    ("top_right", "point"),      # close button
    ("center", "point"),
    ("bottom", "horizontal"),    # taskbar, keeping your x
    ("left", "vertical"),        # side bar, keeping your y
]
# How long after dropping an anchor the follow-up noise still opens the kind
# picker instead of doing its normal job
ANCHOR_CHASE_MS = 300

# Timing
TRACKING_STOP_MS = 800
REVERSE_TIMEOUT = "2s"

# Click behavior
CLICK_BEHAVIOR = {
    "move": "stop",
    "boost": "stop",
    "glide": "stop",
    "canvas_move": "canvas_stop",
    "canvas_glide": "canvas_stop",
    "canvas_boost": "canvas_stop",
    "canvas_scale_move": "canvas_scale",
}

# Cursor UI
CURSOR_UI_ENABLED = True

# Mode families. Colors below, and the cursor draws one shape per family:
# circle for cursor move, triangle for canvas, diamond for canvas scale,
# square for window.
CANVAS_MODES = ("canvas_stop", "canvas_move", "canvas_boost", "canvas_glide", "canvas_tracking")
CANVAS_SCALE_MODES = ("canvas_scale", "canvas_scale_move")
WINDOW_MODES = ("window", "window_stop", "window_move")

MODE_COLORS = {
    "default": "#FF0000",
    "move": "#FFFF00",
    "boost": "#2AE33C",
    "glide": "#578EF5",
    "tracking": "#A7D3FF",
    "window": "#A7D3FF",
    "window_move": "#FFFF00",
    "window_stop": "#FF0000",
    "canvas_tracking": "#A7D3FF",
    "canvas_stop": "#FF4444",
    "canvas_move": "#FFFF44",
    "canvas_boost": "#44E84E",
    "canvas_glide": "#6B9EF7",
    "canvas_scale": "#FF4444",
    "canvas_scale_move": "#FFFF44",
}

# Modifier letters, shown next to the cursor in this order
MODIFIER_LETTERS = {
    "shift": "S",
    "ctrl": "C",
    "alt": "A",
}

# UI colors
UI_BORDER_COLOR = "#666666"
UI_BACKGROUND_COLOR = "#4A4A4A"
UI_TEXT_COLOR = "#FFFFFF"
UI_SELECTED_COLOR = "#3E84DA"
# Picker menus. Big targets for an eye tracker, and every tile takes a click as
# well as the noise beside it. Styled after the BentoPick panel: one backdrop,
# sections named by a header instead of boxed off, tiles that carry every state
# in their fill.
PICKER_TILE_WIDTH = 160
PICKER_TILE_HEIGHT = 118
PICKER_COLUMNS = 5
PICKER_GAP = 12
PICKER_PADDING = 20
PICKER_RADIUS = 8
# Clearly bigger than the gap between tiles. Nothing is boxed, so this space is
# what tells one section from the next.
PICKER_SECTION_GAP = 22
PICKER_HEADER_GAP = 10
PICKER_TILE_GAP = 6
PICKER_FONT = "Segoe UI"

# Nothing in a picker goes under this. These are read at a glance, from a
# distance, by someone aiming rather than reading.
PICKER_TEXT_SIZE = 16
PICKER_TITLE_SIZE = 20

PICKER_PANEL_COLOR = "1A1A1EF0"
# The window derives its title bar from the panel and drops the alpha doing it,
# so the matching translucent tone is set rather than computed
PICKER_TITLE_BAR_COLOR = "242428F0"
PICKER_TILE_COLOR = "2A2A32"
# Neighbouring sections alternate between the two tile fills. That is what
# separates them, in place of a border around each.
PICKER_TILE_ALT_COLOR = "22222A"
PICKER_TILE_HOVER_COLOR = "3C3C48"
PICKER_TILE_SELECTED_COLOR = "4C5A78"
# Back and close, warmed just enough to read as leaving without shouting
PICKER_TILE_EXIT_COLOR = "3A2A30"
PICKER_TEXT_COLOR = "E8E8EC"
PICKER_HEADER_COLOR = "9A9AA8"
PICKER_NOISE_COLOR = "8A8A98"

# Utility pickers (tut palate)
# One binding each, and they do not know about each other. utility_1 is the
# noise inside parrot mode, utility_global is palate with the rig off.
# Named here rather than beside their presets so the picker can build itself
# without importing the module that holds them.
UTILITY_SLOTS = ("utility_1", "utility_global")
# How many entries each Recent row offers. Voice and parrot rig histories are
# separate lists, this is the depth of each.
UTILITY_RECENT_COUNT = 5
# Longest phrase shown on a tile, so one rambling command cannot stretch the
# whole row
UTILITY_PHRASE_MAX = 38
# Parrot rig actions kept out of the Recent column, matched as substrings of
# the action label. These are the ones already sitting on a bare noise or
# already offered as a preset, so binding them here would gain nothing.
UTILITY_HISTORY_SKIP = (
    "move", "track", "glide", "boost", "burst", "brake",
    "scroll up", "scroll down", "resume", "stop", "reset", "speed",
    "exit", "cancel", "return", "mode swap", "repeat", "click",
    "escape", "back", "utility",
)
