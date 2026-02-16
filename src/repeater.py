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

# Snapshot captured on repeat. Reverse only works while this is set.
# Cleared after REVERSE_TIMEOUT.
_snapshot_phrase = ""
_snapshot_timer = None


def _clear_snapshot():
    global _snapshot_phrase, _snapshot_timer
    _snapshot_phrase = ""
    _snapshot_timer = None


def _set_snapshot():
    """Capture the current phrase from history for later reversal."""
    global _snapshot_phrase, _snapshot_timer

    try:
        phrase = actions.user.history_get(0)
    except (IndexError, KeyError):
        return

    if phrase:
        _snapshot_phrase = phrase
        if _snapshot_timer:
            cron.cancel(_snapshot_timer)
        _snapshot_timer = cron.after(REVERSE_TIMEOUT, _clear_snapshot)


def _get_reversed(phrase: str):
    """Swap opposite words in phrase, or return None if no opposites found."""
    if not phrase:
        return None

    for word in opposites:
        if word in phrase:
            return phrase.replace(word, opposites[word])

    return None


def repeat_command():
    """Repeat the last command and snapshot for reversal"""
    _set_snapshot()
    try:
        actions.core.repeat_command()
    except IndexError:
        pass


def repeat_phrase():
    """Repeat the last phrase and snapshot for reversal"""
    _set_snapshot()
    try:
        actions.core.repeat_phrase()
    except IndexError:
        pass


def reverse_command():
    """Reverse the repeated command by swapping opposite words, then mimic"""
    if not _snapshot_phrase:
        return
    reversed_phrase = _get_reversed(_snapshot_phrase)
    if reversed_phrase:
        actions.mimic(reversed_phrase)


def reverse_phrase():
    """Reverse the repeated phrase by swapping opposite words, then mimic"""
    if not _snapshot_phrase:
        return
    reversed_phrase = _get_reversed(_snapshot_phrase)
    if reversed_phrase:
        actions.mimic(reversed_phrase)
