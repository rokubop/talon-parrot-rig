"""Return is a click-exit until a snap condition applies. First match wins.

Snapping teleports through the rig, not ctrl.mouse_move, so the rig's internal
position stays in sync and movement carries on from the new spot.
"""

from talon import actions, ui


def main_screen_center():
    return ui.main_screen().rect.center


TARGETS = {
    "center": main_screen_center,
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
    actions.user.mouse_rig_move_to(pos.x, pos.y)
    if rule.get("after"):
        rule["after"]()


def rule_names():
    return [r["name"] for r in _rules]
