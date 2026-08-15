"""Hollow rings drawn where the anchors sit. Same size as the cursor dot's
border, no fill, so you can see what is underneath them.

One UI per screen holding anchors, since a tree's canvas is bounded by its
screen root.
"""

from talon import actions, ui
from ..parrot_rig_settings import ANCHOR_MARKER_COLOR

_previous_shown = globals().get("_shown")

_shown = []


def _screen_at(x: float, y: float):
    for index, screen in enumerate(ui.screens()):
        rect = screen.rect
        if rect.x <= x < rect.x + rect.width and rect.y <= y < rect.y + rect.height:
            return index, rect
    return 0, ui.main_screen().rect


def _by_screen(positions):
    """{screen index: [(left, top), ...]} in that screen's own coordinates."""
    grouped = {}
    for x, y in positions:
        index, rect = _screen_at(x, y)
        grouped.setdefault(index, []).append((x - rect.x - 12, y - rect.y - 12))
    return grouped


def _make_markers(index: int, offsets: list):
    def markers_ui():
        screen, svg, circle = actions.user.ui_elements(["screen", "svg", "circle"])

        return screen(index)[
            *[
                svg(position="absolute", left=left, top=top)[
                    circle(cx=12, cy=12, r=10.5, fill=False, stroke="000000", stroke_width=1),
                    circle(cx=12, cy=12, r=9, fill=False, stroke=ANCHOR_MARKER_COLOR, stroke_width=2),
                    circle(cx=12, cy=12, r=7.5, fill=False, stroke="000000", stroke_width=1),
                ]
                for left, top in offsets
            ]
        ]

    # ui_elements keys trees by qualname, so each screen needs its own or they
    # collide onto one tree
    markers_ui.__qualname__ = f"anchor_markers_screen_{index}"
    markers_ui.__name__ = markers_ui.__qualname__
    return markers_ui


def anchor_markers_hide():
    for markers_ui in _shown:
        try:
            actions.user.ui_elements_hide(markers_ui)
        except Exception:
            pass
    _shown.clear()


def anchor_markers_show(positions):
    anchor_markers_hide()
    for index, offsets in _by_screen(positions).items():
        markers_ui = _make_markers(index, offsets)
        actions.user.ui_elements_show(markers_ui, show_hints=False)
        _shown.append(markers_ui)


if _previous_shown:
    for _stale in _previous_shown:
        try:
            actions.user.ui_elements_hide(_stale)
        except Exception:
            pass
