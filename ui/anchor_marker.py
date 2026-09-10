"""Hollow rings drawn where the anchors sit. Same size as the cursor dot's
border, no fill, so you can see what is underneath them. Line anchors also draw
their line across the screen, with the ring still marking where it was dropped.

One UI per screen holding anchors, since a tree's canvas is bounded by its
screen root.
"""

from talon import actions, ui
from ..parrot_rig_settings import ANCHOR_MARKER_COLOR, ANCHOR_LINE_COLOR

_previous_shown = globals().get("_shown")

_shown = []


def _screen_at(x: float, y: float):
    for index, screen in enumerate(ui.screens()):
        rect = screen.rect
        if rect.x <= x < rect.x + rect.width and rect.y <= y < rect.y + rect.height:
            return index, rect
    return 0, ui.main_screen().rect


def _by_screen(anchors):
    """{screen index: (rect, [anchor in that screen's own coordinates])}"""
    grouped = {}
    for anchor in anchors:
        index, rect = _screen_at(anchor["x"], anchor["y"])
        local = dict(anchor, x=anchor["x"] - rect.x, y=anchor["y"] - rect.y)
        grouped.setdefault(index, (rect, []))[1].append(local)
    return grouped


def _make_markers(index: int, rect, anchors: list):
    def markers_ui():
        screen, svg, circle = actions.user.ui_elements(["screen", "svg", "circle"])
        div = actions.user.ui_elements(["div"])

        def line(anchor):
            if anchor["kind"] == "vertical":
                return div(position="absolute", left=anchor["x"] - 1, top=0,
                           width=2, height=rect.height,
                           background_color=ANCHOR_LINE_COLOR)
            if anchor["kind"] == "horizontal":
                return div(position="absolute", left=0, top=anchor["y"] - 1,
                           width=rect.width, height=2,
                           background_color=ANCHOR_LINE_COLOR)
            return None

        def ring(anchor):
            return svg(position="absolute", left=anchor["x"] - 12, top=anchor["y"] - 12)[
                circle(cx=12, cy=12, r=10.5, fill=False, stroke="000000", stroke_width=1),
                circle(cx=12, cy=12, r=9, fill=False, stroke=ANCHOR_MARKER_COLOR, stroke_width=2),
                circle(cx=12, cy=12, r=7.5, fill=False, stroke="000000", stroke_width=1),
            ]

        return screen(index)[
            *[line(anchor) for anchor in anchors],
            *[ring(anchor) for anchor in anchors],
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


def anchor_markers_show(anchors):
    anchor_markers_hide()
    for index, (rect, local) in _by_screen(anchors).items():
        markers_ui = _make_markers(index, rect, local)
        actions.user.ui_elements_show(markers_ui, show_hints=False)
        _shown.append(markers_ui)


if _previous_shown:
    for _stale in _previous_shown:
        try:
            actions.user.ui_elements_hide(_stale)
        except Exception:
            pass
