from talon import actions
from ..parrot_rig_settings import MODE_COLORS, MODIFIER_COLORS
from ..parrot_rig_settings import CURSOR_UI_ENABLED

default_cursor_color = "FF0000"
default_border_color = "FFFFFF"

def cursor_ui():
    screen, cursor, svg, circle, state = actions.user.ui_elements(
        ["screen", "cursor", "svg", "circle", "state"]
    )

    cursor_color = state.get("cursor_color")
    border_color = state.get("border_color")
    show_border = state.get("show_border")
    modifiers = state.get("modifiers")

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

    return screen()[
        cursor()[
            # Border (if enabled)
            svg(position="absolute", left=10, top=10)[
                circle(r=11, cx=12, cy=12, fill="black"),
                circle(r=10, cx=12, cy=12, fill=border_color),
                circle(r=8, cx=12, cy=12, fill="black")
            ] if show_border else None,
            # Main cursor
            svg(position="absolute", left=10, top=10)[
                circle(r=7, cx=12, cy=12, fill=cursor_color)
            ],
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

    def _get_state(self):
        return {
            "cursor_color": self._color,
            "border_color": self._border_color,
            "show_border": self._border_show,
            "modifiers": self._modifiers,
            "mode": self._mode
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
