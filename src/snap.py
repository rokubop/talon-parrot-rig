"""With no anchors set, return is a click-exit until a snap condition applies.
First match wins. Any anchor set takes return before these are consulted.

Snapping teleports through the rig, not ctrl.mouse_move, so the rig's internal
position stays in sync and movement carries on from the new spot.
"""

from talon import actions, ctrl, ui
from ..parrot_rig_settings import SCREEN_EDGE_INSET


def _screen_rect():
    """The screen the cursor is on, so targets follow you across monitors."""
    x, y = ctrl.mouse_pos()
    for screen in ui.screens():
        rect = screen.rect
        if rect.x <= x < rect.x + rect.width and rect.y <= y < rect.y + rect.height:
            return rect
    return ui.main_screen().rect


def _center():
    rect = _screen_rect()
    return rect.x + rect.width / 2, rect.y + rect.height / 2


def _top_right():
    rect = _screen_rect()
    return rect.x + rect.width - SCREEN_EDGE_INSET, rect.y + SCREEN_EDGE_INSET


def _top_left():
    rect = _screen_rect()
    return rect.x + SCREEN_EDGE_INSET, rect.y + SCREEN_EDGE_INSET


def _bottom():
    """Keeps your x, the way a horizontal line anchor does."""
    rect = _screen_rect()
    return ctrl.mouse_pos()[0], rect.y + rect.height - SCREEN_EDGE_INSET


def _left():
    """Keeps your y, the way a vertical line anchor does."""
    return _screen_rect().x + SCREEN_EDGE_INSET, ctrl.mouse_pos()[1]


TARGETS = {
    "center": _center,
    "top_right": _top_right,
    "top_left": _top_left,
    "bottom": _bottom,
    "left": _left,
}

_rules = []


def snap_rule(name: str, when, target="center", before=None, after=None):
    """Register a snap condition. Re-registering by name replaces, so reloads stay idempotent."""
    _rules[:] = [r for r in _rules if r["name"] != name]
    _rules.append({
        "name": name, "when": when, "target": target,
        "before": before, "after": after,
    })


def active_rule():
    for rule in _rules:
        try:
            if rule["when"]():
                return rule
        except Exception:
            continue
    return None


def resolve_target(target):
    return TARGETS[target]() if isinstance(target, str) else target()


def do_snap(rule=None):
    rule = rule or {"target": "center", "before": None, "after": None}
    if rule.get("before"):
        rule["before"]()
    pos = resolve_target(rule.get("target", "center"))
    x, y = (pos.x, pos.y) if hasattr(pos, "x") else pos
    actions.user.mouse_rig_move_to(x, y)
    if rule.get("after"):
        rule["after"]()


def rule_names():
    return [r["name"] for r in _rules]
