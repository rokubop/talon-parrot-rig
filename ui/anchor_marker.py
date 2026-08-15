"""Hollow ring drawn where the anchor sits. Same size as the cursor dot's
border, no fill, so you can see what is underneath it.
"""

from talon import actions, ui
from ..parrot_rig_settings import ANCHOR_MARKER_COLOR

_previous_ui = globals().get("anchor_marker_ui")

_state = {"screen": 0, "left": 0, "top": 0}


def _screen_at(x: float, y: float):
    for index, screen in enumerate(ui.screens()):
        rect = screen.rect
        if rect.x <= x < rect.x + rect.width and rect.y <= y < rect.y + rect.height:
            return index, rect
    return 0, ui.main_screen().rect


def anchor_marker_ui():
    screen, svg, circle = actions.user.ui_elements(["screen", "svg", "circle"])

    return screen(_state["screen"])[
        svg(position="absolute", left=_state["left"], top=_state["top"])[
            circle(cx=12, cy=12, r=10.5, fill=False, stroke="000000", stroke_width=1),
            circle(cx=12, cy=12, r=9, fill=False, stroke=ANCHOR_MARKER_COLOR, stroke_width=2),
            circle(cx=12, cy=12, r=7.5, fill=False, stroke="000000", stroke_width=1),
        ]
    ]


def anchor_marker_show(x: float, y: float):
    index, rect = _screen_at(x, y)
    _state["screen"] = index
    _state["left"] = x - rect.x - 12
    _state["top"] = y - rect.y - 12
    actions.user.ui_elements_hide(anchor_marker_ui)
    actions.user.ui_elements_show(anchor_marker_ui, show_hints=False)


def anchor_marker_hide():
    actions.user.ui_elements_hide(anchor_marker_ui)


if _previous_ui is not None:
    try:
        actions.user.ui_elements_hide(_previous_ui)
    except Exception:
        pass
