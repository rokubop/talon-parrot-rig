"""Runtime settings picked from a selector menu, unlike parrot_rig_settings.py
which is static config. Maps are {value: (label,)} to match utility maps so the
selector UI works on both. First entry is the default.

Numeric settings resolve to a number: the real value where NUMERIC_SETTINGS
names a base to scale, otherwise the multiplier itself. Their "custom" option
holds a typed number instead.
"""

from ..parrot_rig_settings import MOVE_SPEED, SCROLL_SPEED, SCROLL_MOVE_SPEED

SPEED_OPTIONS = (
    ("normal",    ("Normal",)),
    ("fast",      ("Fast",)),
    ("faster",    ("Faster",)),
    ("slow",      ("Slow",)),
    ("very_slow", ("Very Slow",)),
    ("custom",    ("Custom",)),
)

setting_maps = {
    "click_freeze": {
        "freeze":    ("Freeze on Click",),
        "no_freeze": ("Keep Moving",),
    },
    "alt_move_mode": {
        "scroll":      ("Scroll Mode",),
        "middle_drag": ("Middle Drag",),
        "mod_scroll":  ("Modifier Scroll",),
    },
    # Modifier scroll. Each parrot axis picks a modifier and which wheel it
    # sends. Apps mostly read the vertical wheel and tell the gestures apart by
    # the modifier, so both axes default to it and only the modifier differs.
    "mod_scroll_y_mod": {
        "ctrl":  ("Ctrl",),
        "shift": ("Shift",),
        "alt":   ("Alt",),
        "none":  ("None",),
    },
    "mod_scroll_y_wheel": {
        "vertical":   ("Wheel Up/Down",),
        "horizontal": ("Wheel Side",),
    },
    "mod_scroll_x_mod": {
        "shift": ("Shift",),
        "ctrl":  ("Ctrl",),
        "alt":   ("Alt",),
        "none":  ("None",),
    },
    "mod_scroll_x_wheel": {
        "vertical":   ("Wheel Up/Down",),
        "horizontal": ("Wheel Side",),
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
        "custom":    ("Custom",),
    },
    "move_speed": dict(SPEED_OPTIONS),
    "scroll_speed": dict(SPEED_OPTIONS),
    "scroll_move_speed": dict(SPEED_OPTIONS),
    "boost_power": {
        "normal": ("Normal",),
        "strong": ("Strong",),
        "gentle": ("Gentle",),
        "custom": ("Custom",),
    },
    # A second tuple entry names an action to run instead of setting the value
    "anchor_move": {
        "smooth":  ("Over Time",),
        "instant": ("Instant",),
        "clear":   ("Clear All", "parrot_rig_anchor_clear_all"),
    },
}

SETTING_TITLES = {
    "click_freeze": "Click",
    "alt_move_mode": "Alt Move",
    "mod_scroll_y_mod": "Y Modifier",
    "mod_scroll_y_wheel": "Y Wheel",
    "mod_scroll_x_mod": "X Modifier",
    "mod_scroll_x_wheel": "X Wheel",
    "move_mode": "Move",
    "turn_speed": "Turn",
    "anchor_move": "Anchor",
    "move_speed": "Move Speed",
    "scroll_speed": "Scroll Speed",
    "scroll_move_speed": "Scroll Move",
    "boost_power": "Boost",
}

TURN_SCALES = {
    "normal": 1.0,
    "snappy": 0.5,
    "slow": 2.5,
    "very_slow": 5.0,
}

SPEED_SCALES = {
    "normal": 1.0,
    "fast": 1.5,
    "faster": 2.0,
    "slow": 0.7,
    "very_slow": 0.5,
}

BOOST_SCALES = {
    "normal": 1.0,
    "strong": 1.5,
    "gentle": 0.7,
}

# base: what the scale multiplies, or None when the multiplier is the number
NUMERIC_SETTINGS = {
    "move_speed":        {"base": MOVE_SPEED,        "scales": SPEED_SCALES},
    "scroll_speed":      {"base": SCROLL_SPEED,      "scales": SPEED_SCALES},
    "scroll_move_speed": {"base": SCROLL_MOVE_SPEED, "scales": SPEED_SCALES},
    "turn_speed":        {"base": None,              "scales": TURN_SCALES},
    "boost_power":       {"base": None,              "scales": BOOST_SCALES},
}

_values = {name: next(iter(options)) for name, options in setting_maps.items()}
_customs = {}


def setting_get(name: str) -> str:
    return _values.get(name, next(iter(setting_maps[name])))


def setting_set(name: str, value: str):
    _values[name] = value


def setting_label(name: str, value: str = None) -> str:
    """Display label for a setting value (defaults to the current one)."""
    return setting_maps[name][value or setting_get(name)][0]


def mod_scroll_axis(axis: str) -> tuple:
    """(modifier, wheel) for the "y" or "x" axis. Modifier may be "none"."""
    return setting_get(f"mod_scroll_{axis}_mod"), setting_get(f"mod_scroll_{axis}_wheel")


def setting_title(name: str) -> str:
    return SETTING_TITLES.get(name, name)


def is_numeric(name: str) -> bool:
    return name in NUMERIC_SETTINGS


def setting_number(name: str, value: str = None) -> float:
    """The number a setting resolves to."""
    spec = NUMERIC_SETTINGS[name]
    value = value or setting_get(name)
    if value == "custom":
        return _customs.get(name, setting_number(name, next(iter(spec["scales"]))))
    scale = spec["scales"][value]
    return spec["base"] * scale if spec["base"] is not None else scale


def setting_number_text(name: str, value: str = None) -> str:
    """Number as shown in menus. Multipliers get an x, real values do not."""
    number = setting_number(name, value)
    text = f"{number:.3f}".rstrip("0").rstrip(".")
    return text if NUMERIC_SETTINGS[name]["base"] is not None else f"x{text}"


def setting_set_custom(name: str, number: float):
    _customs[name] = number
    _values[name] = "custom"


def setting_customs() -> dict:
    return dict(_customs)


def setting_apply_customs(customs: dict):
    _customs.clear()
    _customs.update({k: v for k, v in (customs or {}).items() if k in NUMERIC_SETTINGS})


def turn_scale() -> float:
    """Timing multiplier for smooth (glide) turns."""
    return setting_number("turn_speed")


def boost_scale() -> float:
    return setting_number("boost_power")
