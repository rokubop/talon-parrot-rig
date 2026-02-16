MODE_COLORS = {
    "default": "#FF0000",
    "move": "#FFFF00",
    "boost": "#2AE33C",
    "glide": "#2AE3B8",
    "full": "#A7D3FF",
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