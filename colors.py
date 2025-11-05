MODE_COLORS = {
    "default": "#FF0000",
    "move": "#FFFF00",
    "head": "#83E99B",
    "full": "#BD10E0",
    "window": "#E35050",
    "keyboard": "#A7D3FF",
    "number": "#F89C1C",
}


MODIFIER_COLORS = {
    "shift": "#0490c9",
    "ctrl": "#84E773",
    "alt": "#FF6DD9",
}

def get_mode_color(mode: str) -> str:
    return MODE_COLORS.get(mode, "#FF0000")

def get_modifier_color(modifier: str) -> str:
    return MODIFIER_COLORS.get(modifier, "#FFFFFF")