from talon import actions, cron
from ..parrot_rig_settings import REVERSE_TIMEOUT

two_way_opposites = [
    ("north", "south"),
    ("upper", "downer"),
    ("up", "down"),
    ("left", "right"),
    ("push", "tug"),
    ("drain", "step"),
    ("undo", "redo"),
    ("last", "next"),
    ("forward", "back"),
    ("out", "in"),
    ("close", "reopen"),
]

opposites = {}

for key, value in two_way_opposites:
    opposites[key] = value
    opposites[value] = key

# Snapshot captured on first repeat. Locked until timeout.
# Palate always repeats _snapshot_phrase, tut always repeats its reverse.
_snapshot_phrase = ""
_snapshot_reversed = ""
_snapshot_timer = None


def _clear_snapshot():
    global _snapshot_phrase, _snapshot_reversed, _snapshot_timer
    _snapshot_phrase = ""
    _snapshot_reversed = ""
    _snapshot_timer = None


def _reset_snapshot_timer():
    global _snapshot_timer
    if _snapshot_timer:
        cron.cancel(_snapshot_timer)
    _snapshot_timer = cron.after(REVERSE_TIMEOUT, _clear_snapshot)


def _set_snapshot():
    """Capture the current phrase from history for later reversal. Only sets once until cleared."""
    global _snapshot_phrase, _snapshot_reversed

    if _snapshot_phrase:
        _reset_snapshot_timer()
        return

    try:
        phrase = actions.user.history_get(0)
    except (IndexError, KeyError):
        return

    if phrase:
        _snapshot_phrase = phrase
        _snapshot_reversed = _get_reversed(phrase) or ""
        _reset_snapshot_timer()


def _get_reversed(phrase: str):
    """Swap opposite words in phrase, or return None if no opposites found."""
    if not phrase:
        return None

    for word in opposites:
        if word in phrase:
            return phrase.replace(word, opposites[word])

    return None


def repeat_command():
    """Repeat the last command using the locked snapshot"""
    _set_snapshot()
    if _snapshot_phrase:
        _reset_snapshot_timer()
        actions.mimic(_snapshot_phrase)
    else:
        try:
            actions.core.repeat_command()
        except IndexError:
            pass


def repeat_phrase():
    """Repeat the last phrase using the locked snapshot"""
    _set_snapshot()
    if _snapshot_phrase:
        _reset_snapshot_timer()
        actions.mimic(_snapshot_phrase)
    else:
        try:
            actions.core.repeat_phrase()
        except IndexError:
            pass


def reverse_command():
    """Reverse the repeated command by swapping opposite words, then mimic"""
    if not _snapshot_reversed:
        return
    _reset_snapshot_timer()
    actions.mimic(_snapshot_reversed)


def reverse_phrase():
    """Reverse the repeated phrase by swapping opposite words, then mimic"""
    if not _snapshot_reversed:
        return
    _reset_snapshot_timer()
    actions.mimic(_snapshot_reversed)
