"""Saved cursor positions. While any are set, return always travels to one of
them, never clicking or snapping. The same noise drops an anchor or removes the
one you are standing on.

An anchor is a point, or a line through that point. Return goes to the closest
point on a line, so a line pins one coordinate and leaves the other alone.
"""

import time
from talon import actions, ctrl
from .settings_menu import setting_get
from ..ui.anchor_marker import anchor_markers_show
from ..parrot_rig_settings import (
    ANCHOR_MOVE_MS, ANCHOR_MOVE_EASING, ANCHOR_HIT_RADIUS, ANCHOR_CHASE_MS,
    SCREEN_ANCHORS,
)

POINT = "point"
VERTICAL = "vertical"
HORIZONTAL = "horizontal"

_anchors = []
_last_set = None
_last_set_at = 0.0
_held = None


def anchors() -> list:
    return list(_anchors)


def _target(anchor, x: float, y: float):
    """Where return lands: the point itself, or the closest point on the line."""
    if anchor["kind"] == VERTICAL:
        return anchor["x"], y
    if anchor["kind"] == HORIZONTAL:
        return x, anchor["y"]
    return anchor["x"], anchor["y"]


def _distance(anchor, x: float, y: float) -> float:
    tx, ty = _target(anchor, x, y)
    return ((tx - x) ** 2 + (ty - y) ** 2) ** 0.5


def anchor_index_at(x: float, y: float):
    """Index of the anchor dropped where you are standing, or None. Keyed to the
    drop point even for lines, so a line does not swallow every toggle along it."""
    for i, anchor in enumerate(_anchors):
        if (anchor["x"] - x) ** 2 + (anchor["y"] - y) ** 2 <= ANCHOR_HIT_RADIUS ** 2:
            return i
    return None


def anchor_toggle() -> str:
    """Drop an anchor at the cursor, or remove the one under it. "set" or "cleared"."""
    global _last_set, _last_set_at
    x, y = ctrl.mouse_pos()
    index = anchor_index_at(x, y)
    if index is None:
        _anchors.append({"x": x, "y": y, "kind": POINT})
        _last_set = len(_anchors) - 1
        _last_set_at = time.monotonic()
        result = "set"
    else:
        _anchors.pop(index)
        _last_set = None
        result = "cleared"
    anchor_markers_show(_anchors)
    return result


def anchor_pending() -> bool:
    """True while the follow-up window on the anchor just dropped is open."""
    if _last_set is None or _last_set >= len(_anchors):
        return False
    return (time.monotonic() - _last_set_at) * 1000 <= ANCHOR_CHASE_MS


def anchor_hold() -> bool:
    """Pin that anchor for the kind picker, which outlives the window."""
    global _held
    _held = _last_set if anchor_pending() else None
    return _held is not None


def anchor_set_kind(kind: str):
    """Apply a kind to the pinned anchor."""
    global _held
    if _held is None or _held >= len(_anchors):
        return
    _anchors[_held]["kind"] = kind
    _held = None
    anchor_markers_show(_anchors)


def anchor_clear_all():
    global _last_set, _held
    _anchors.clear()
    _last_set = None
    _held = None
    anchor_markers_show(_anchors)


def _go(anchors) -> bool:
    """Move to the nearest of these, or the next one round if already on one.

    While any are set this always takes the return noise, so it never falls
    through. Standing on the only one lands on it again, which pulls you flush
    onto a line."""
    if not anchors:
        return False
    x, y = ctrl.mouse_pos()
    here = next(
        (i for i, a in enumerate(anchors) if _distance(a, x, y) <= ANCHOR_HIT_RADIUS),
        None,
    )
    if here is None:
        anchor = min(anchors, key=lambda a: _distance(a, x, y))
    else:
        anchor = anchors[(here + 1) % len(anchors)]
    tx, ty = _target(anchor, x, y)
    if setting_get("anchor_move") == "instant":
        actions.user.mouse_rig_move_to(tx, ty)
    else:
        actions.user.mouse_rig_move_to(tx, ty, ANCHOR_MOVE_MS, ANCHOR_MOVE_EASING)
    return True


def anchor_go() -> bool:
    return _go(_anchors)


def _screen_anchors() -> list:
    """Stand-ins built from the screen you are on. Never stored, never drawn."""
    from .snap import TARGETS
    built = []
    for name, kind in SCREEN_ANCHORS:
        target = TARGETS.get(name)
        if not target:
            continue
        x, y = target()
        built.append({"x": x, "y": y, "kind": kind})
    return built


def anchor_go_screen() -> bool:
    """The Screen Anchors return fallback. Only reached empty handed."""
    if _anchors or setting_get("return_fallback") != "screen_anchors":
        return False
    return _go(_screen_anchors())
