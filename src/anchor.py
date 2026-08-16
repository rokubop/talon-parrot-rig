"""Saved cursor positions. While any are set, return travels to the nearest one
instead of clicking or snapping. The same noise drops an anchor or removes the
one you are standing on.
"""

from talon import actions, ctrl
from .settings_menu import setting_get
from ..ui.anchor_marker import anchor_markers_show
from ..parrot_rig_settings import (
    ANCHOR_MOVE_MS, ANCHOR_MOVE_EASING, ANCHOR_HIT_RADIUS,
)

_anchors = []


def anchors() -> list:
    return list(_anchors)


def anchor_index_at(x: float, y: float):
    """Index of the anchor you are standing on, or None."""
    for i, (ax, ay) in enumerate(_anchors):
        if (ax - x) ** 2 + (ay - y) ** 2 <= ANCHOR_HIT_RADIUS ** 2:
            return i
    return None


def anchor_toggle() -> str:
    """Drop an anchor at the cursor, or remove the one under it. "set" or "cleared"."""
    x, y = ctrl.mouse_pos()
    index = anchor_index_at(x, y)
    if index is None:
        _anchors.append((x, y))
        result = "set"
    else:
        _anchors.pop(index)
        result = "cleared"
    anchor_markers_show(_anchors)
    return result


def anchor_clear_all():
    _anchors.clear()
    anchor_markers_show(_anchors)


def anchor_go() -> bool:
    """Move to the nearest anchor, or the next one round if already on one."""
    if not _anchors:
        return False
    x, y = ctrl.mouse_pos()
    here = anchor_index_at(x, y)
    if here is None:
        tx, ty = min(_anchors, key=lambda a: (a[0] - x) ** 2 + (a[1] - y) ** 2)
    elif len(_anchors) == 1:
        return False
    else:
        tx, ty = _anchors[(here + 1) % len(_anchors)]
    if setting_get("anchor_move") == "instant":
        actions.user.mouse_rig_move_to(tx, ty)
    else:
        actions.user.mouse_rig_move_to(tx, ty, ANCHOR_MOVE_MS, ANCHOR_MOVE_EASING)
    return True
