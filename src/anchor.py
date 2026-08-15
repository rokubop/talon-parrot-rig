"""A saved cursor position. While one is set, pop relocates there instead of
clicking or snapping. Set and cleared with the same noise.
"""

from talon import actions, ctrl
from .settings_menu import setting_get
from ..ui.anchor_marker import anchor_marker_hide, anchor_marker_show
from ..parrot_rig_settings import ANCHOR_MOVE_MS, ANCHOR_MOVE_EASING

_pos = None


def anchor_get():
    return _pos


def anchor_set(pos=None):
    global _pos
    _pos = tuple(pos) if pos else ctrl.mouse_pos()
    anchor_marker_show(*_pos)


def anchor_clear():
    global _pos
    _pos = None
    anchor_marker_hide()


def anchor_toggle() -> bool:
    """Set at the cursor, or clear an existing one. True if an anchor is now set."""
    if _pos:
        anchor_clear()
        return False
    anchor_set()
    return True


def anchor_go() -> bool:
    """Move to the anchor. False if there is nothing to move to."""
    if not _pos:
        return False
    x, y = _pos
    if setting_get("anchor_move") == "instant":
        actions.user.mouse_rig_move_to(x, y)
    else:
        actions.user.mouse_rig_move_to(x, y, ANCHOR_MOVE_MS, ANCHOR_MOVE_EASING)
    return True
