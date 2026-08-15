"""Runtime settings picked from a selector menu, unlike parrot_rig_settings.py
which is static config. Maps are {value: (label,)} to match utility maps so the
selector UI works on both. First entry is the default.
"""

setting_maps = {
    "click_freeze": {
        "freeze":    ("Freeze on Click",),
        "no_freeze": ("Keep Moving",),
    },
    "er_mode": {
        "scroll":      ("Scroll Mode",),
        "middle_drag": ("Middle Drag",),
    },
    "move_mode": {
        "orthogonal":   ("Orthogonal",),
        "always_glide": ("Always Glide",),
    },
    "turn_speed": {
        "normal":    ("Normal",),
        "snappy":    ("Snappy",),
        "slow":      ("Slow",),
        "very_slow": ("Very Slow",),
    },
    "anchor_move": {
        "smooth":  ("Over Time",),
        "instant": ("Instant",),
    },
}

SETTING_TITLES = {
    "click_freeze": "Click",
    "er_mode": "Er",
    "move_mode": "Move",
    "turn_speed": "Turn",
    "anchor_move": "Anchor",
}

TURN_SCALES = {
    "normal": 1.0,
    "snappy": 0.5,
    "slow": 2.5,
    "very_slow": 5.0,
}


def turn_scale() -> float:
    """Timing multiplier for smooth (glide) turns."""
    return TURN_SCALES[setting_get("turn_speed")]

_values = {name: next(iter(options)) for name, options in setting_maps.items()}


def setting_get(name: str) -> str:
    """Current value of a setting."""
    return _values.get(name, next(iter(setting_maps[name])))


def setting_set(name: str, value: str):
    """Set a setting to one of its map values."""
    _values[name] = value


def setting_label(name: str, value: str = None) -> str:
    """Display label for a setting value (defaults to the current one)."""
    return setting_maps[name][value or setting_get(name)][0]


def setting_title(name: str) -> str:
    return SETTING_TITLES.get(name, name)
