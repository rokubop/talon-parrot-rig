"""Menu navigation stack. Opening drills in, tut backs out one level.

No menu takes a noise. tut is the only one they borrow, handled in
parrot_actions.cancel.

Opening one takes a mode. A menu is aimed at, so the rig goes to tracking.
"""

_stack = []
_registry = {}


def menu_register(name: str, show, hide):
    _registry[name] = (show, hide)


def _track():
    """Tracking is what puts the cursor on a tile. Nothing to aim with when
    parrot mode is off, so this skips."""
    from .parrot_actions import parrot_actions
    if parrot_actions.parrot_mode_is_enabled():
        parrot_actions.tracking_activate()


def menu_open(name: str):
    if name not in _registry or name in _stack:
        return
    _track()
    previous = _stack[-1] if _stack else None
    if previous:
        _registry[previous][1]()
    try:
        _registry[name][0]()
    except Exception:
        if previous:
            _registry[previous][0]()
        raise
    _stack.append(name)


def menu_back():
    if not _stack:
        return
    _registry[_stack.pop()][1]()
    if _stack:
        _registry[_stack[-1]][0]()


def menu_close():
    while _stack:
        _registry[_stack.pop()][1]()


def menu_reset():
    """Drop the stack, for parrot mode teardown."""
    menu_close()


def menu_current():
    return _stack[-1] if _stack else None
