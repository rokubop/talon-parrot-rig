from talon import actions
from ..parrot_rig_settings import MODE_COLORS, MODIFIER_COLORS
from ..parrot_rig_settings import CURSOR_UI_ENABLED

SCROLL_MODES = {"scroll_stop", "scroll_move", "scroll_boost", "scroll_glide", "scroll_tracking"}

TRIANGLE_PATHS = {
    "down":  "M 12 19 L 4 5 L 20 5 Z",
    "up":    "M 12 5 L 4 19 L 20 19 Z",
    "left":  "M 5 12 L 19 4 L 19 20 Z",
    "right": "M 19 12 L 5 4 L 5 20 Z",
}

TRIANGLE_BORDER_OUTER = {
    "down":  "M 12 24 L 0 2 L 24 2 Z",
    "up":    "M 12 0 L 0 22 L 24 22 Z",
    "left":  "M 0 12 L 22 0 L 22 24 Z",
    "right": "M 24 12 L 2 0 L 2 24 Z",
}

TRIANGLE_BORDER_MID = {
    "down":  "M 12 23 L 1 3 L 23 3 Z",
    "up":    "M 12 1 L 1 21 L 23 21 Z",
    "left":  "M 1 12 L 21 1 L 21 23 Z",
    "right": "M 23 12 L 3 1 L 3 23 Z",
}

TRIANGLE_BORDER_INNER = {
    "down":  "M 12 21 L 3 4 L 21 4 Z",
    "up":    "M 12 3 L 3 20 L 21 20 Z",
    "left":  "M 3 12 L 20 3 L 20 21 Z",
    "right": "M 21 12 L 4 3 L 4 21 Z",
}

default_cursor_color = "FF0000"
default_border_color = "FFFFFF"

def cursor_ui():
    screen, cursor, svg, circle, state = actions.user.ui_elements(
        ["screen", "cursor", "svg", "circle", "state"]
    )
    div, text, path = actions.user.ui_elements(["div", "text", "path"])

    cursor_color = state.get("cursor_color")
    border_color = state.get("border_color")
    show_border = state.get("show_border")
    modifiers = state.get("modifiers")
    speed_level = state.get("speed_level")

    modifier_elements = []
    if modifiers:
        offset_x = 31
        for modifier in ["shift", "ctrl", "alt"]:
            if modifier in modifiers:
                modifier_color = MODIFIER_COLORS.get(modifier, "FFFFFF")
                modifier_elements.append(
                    svg(position="absolute", left=offset_x, top=30)[
                        circle(r=5, cx=5, cy=5, fill=modifier_color)
                    ]
                )
                offset_x += 11

    speed_label = None
    if speed_level and speed_level > 0:
        speed_label = div(
            position="absolute",
            left=30,
            top=12,
            width=20,
            height=20,
            justify_content="center",
            align_items="center",
        )[
            text(
                str(speed_level),
                color="white",
                font_size=12,
                font_weight="bold",
                stroke_color="000000",
                stroke_width=3,
            )
        ]

    mode = state.get("mode")
    is_scroll = mode in SCROLL_MODES

    if is_scroll:
        scroll_dir = state.get("scroll_direction") or "down"
        cursor_shape = svg(position="absolute", left=10, top=10)[
            path(d=TRIANGLE_PATHS[scroll_dir], fill=cursor_color)
        ]
        border_shape = svg(position="absolute", left=10, top=10)[
            path(d=TRIANGLE_BORDER_OUTER[scroll_dir], fill="black"),
            path(d=TRIANGLE_BORDER_MID[scroll_dir], fill=border_color),
            path(d=TRIANGLE_BORDER_INNER[scroll_dir], fill="black"),
        ] if show_border else None
    else:
        # Circle for move modes
        cursor_shape = svg(position="absolute", left=10, top=10)[
            circle(r=7, cx=12, cy=12, fill=cursor_color)
        ]
        border_shape = svg(position="absolute", left=10, top=10)[
            circle(r=11, cx=12, cy=12, fill="black"),
            circle(r=10, cx=12, cy=12, fill=border_color),
            circle(r=8, cx=12, cy=12, fill="black")
        ] if show_border else None

    return screen()[
        cursor()[
            border_shape,
            cursor_shape,
            # Speed level number
            speed_label,
            # Modifiers
            *modifier_elements
        ]
    ]

class CursorUI:
    def __init__(self):
        self._color = default_cursor_color
        self._border_color = default_border_color
        self._border_show = False
        self._modifiers = set()
        self._mode = "default"
        self._speed_level = 0
        self._scroll_direction = "down"

    def _get_state(self):
        return {
            "cursor_color": self._color,
            "border_color": self._border_color,
            "show_border": self._border_show,
            "modifiers": self._modifiers,
            "mode": self._mode,
            "speed_level": self._speed_level,
            "scroll_direction": self._scroll_direction,
        }

    def show(self):
        if not CURSOR_UI_ENABLED:
            return
        actions.user.ui_elements_show(
            cursor_ui,
            initial_state=self._get_state(),
            min_version="0.10.0"
        )

    def hide(self):
        if not CURSOR_UI_ENABLED:
            return
        actions.user.ui_elements_hide(cursor_ui)
        self._color = default_cursor_color
        self._border_color = default_border_color
        self._border_show = False
        self._modifiers = set()
        self._mode = "default"
        self._speed_level = 0
        self._scroll_direction = "down"

    def color(self, color):
        if not CURSOR_UI_ENABLED:
            return
        self._color = color
        actions.user.ui_elements_set_state("cursor_color", color)

    def show_border(self):
        if not CURSOR_UI_ENABLED:
            return
        self._border_show = True
        actions.user.ui_elements_set_state("show_border", True)

    def hide_border(self):
        if not CURSOR_UI_ENABLED:
            return
        self._border_show = False
        actions.user.ui_elements_set_state("show_border", False)

    def add_modifier(self, modifier):
        if not CURSOR_UI_ENABLED:
            return
        self._modifiers.add(modifier)
        actions.user.ui_elements_set_state("modifiers", self._modifiers.copy())

    def remove_modifier(self, modifier):
        if not CURSOR_UI_ENABLED:
            return
        self._modifiers.discard(modifier)
        actions.user.ui_elements_set_state("modifiers", self._modifiers.copy())

    def clear_modifiers(self):
        if not CURSOR_UI_ENABLED:
            return
        self._modifiers.clear()
        actions.user.ui_elements_set_state("modifiers", set())

    def set_mode(self, mode: str):
        if not CURSOR_UI_ENABLED:
            return
        self._mode = mode
        actions.user.ui_elements_set_state("mode", mode)

    def set_speed_level(self, level: int):
        if not CURSOR_UI_ENABLED:
            return
        self._speed_level = level
        actions.user.ui_elements_set_state("speed_level", level)

    def set_scroll_direction(self, direction: str):
        if not CURSOR_UI_ENABLED:
            return
        self._scroll_direction = direction
        actions.user.ui_elements_set_state("scroll_direction", direction)

    def get_mode(self) -> str:
        return self._mode

    def get_mode_color(self, mode: str) -> str:
        return MODE_COLORS.get(mode, "#FF0000")

    def get_modifier_color(self, modifier: str) -> str:
        return MODIFIER_COLORS.get(modifier, "#FFFFFF")

    def cleanup(self):
        try:
            self.hide()
        except Exception as e:
            print(f"Error during cursor UI cleanup: {e}")
            import traceback
            traceback.print_exc()

try:
    if 'cursor_ui_instance' in globals() and hasattr(globals()['cursor_ui_instance'], 'cleanup'):
        globals()['cursor_ui_instance'].cleanup()
except Exception as e:
    print(f"Error cleaning up previous cursor_ui_instance: {e}")
    import traceback
    traceback.print_exc()

cursor_ui_instance = CursorUI()
