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
GLIDE_RELEASE_RATE = 5

# Scroll
SCROLL_SPEED = 0.4

# Jump keys for tut hiss / tut shush. Plain home/end if you want page top
# and bottom rather than document ends.
SCROLL_EXTREME_KEYS = {
    "up": "ctrl-home",
    "down": "ctrl-end",
}

# Canvas scale. Every wheel tick is a zoom step in most apps, so this runs
# slower than plain scroll.
CANVAS_SCALE_SPEED = 0.015

# How long after entering canvas mode the follow-up noise still means "canvas
# scale" instead of its normal action. Matches the input map combo window,
# since it stands in for a combo that a mode switch would otherwise eat.
CANVAS_SCALE_CHASE_MS = 300

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

# Mode colors
MODE_COLORS = {
    "default": "#FF0000",
    "move": "#FFFF00",
    "boost": "#2AE33C",
    "glide": "#578EF5",
    "tracking": "#A7D3FF",
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
