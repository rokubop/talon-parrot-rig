"""Menu navigation stack. Opening drills in, tut backs out one level.

No menu takes a mode or a noise. They open over the rig and it keeps running
underneath, so you aim at one the way you aim at anything. tut is the only
noise they take, handled in parrot_actions.cancel.
"""

_stack = []
_registry = {}


def menu_register(name: str, show, hide):
    _registry[name] = (show, hide)


def menu_open(name: str):
    if name not in _registry or name in _stack:
        return
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
