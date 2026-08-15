"""Menu navigation stack. Opening drills in, tut backs out one level.

Each menu owns a "{name}_select" input map mode and a show/hide pair.
"""

from .events import event_manager

_stack = []
_return_mode = "default"
_registry = {}


def menu_register(name: str, show, hide):
    _registry[name] = (show, hide)


def _show(name):
    event_manager.set_mode(f"{name}_select")
    _registry[name][0]()


def _hide(name):
    _registry[name][1]()


def menu_open(name: str):
    global _return_mode
    if name not in _registry or name in _stack:
        return
    previous = _stack[-1] if _stack else None
    if previous:
        _hide(previous)
    else:
        _return_mode = event_manager.get_mode()
    try:
        _show(name)
    except Exception:
        if previous:
            _show(previous)
        else:
            event_manager.set_mode(_return_mode)
        raise
    _stack.append(name)


def menu_back():
    if not _stack:
        return
    _hide(_stack.pop())
    if _stack:
        _show(_stack[-1])
    else:
        event_manager.set_mode(_return_mode)


def menu_close():
    while _stack:
        _hide(_stack.pop())
    event_manager.set_mode(_return_mode)


def menu_reset():
    """Drop the stack without touching modes, for parrot mode teardown."""
    while _stack:
        _hide(_stack.pop())


def menu_current():
    return _stack[-1] if _stack else None
