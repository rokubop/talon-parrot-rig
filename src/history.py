"""The two histories the utility 1 picker offers, kept apart on purpose.

Voice is Talon's own command history, read through the community
`user.history_get`. Parrot rig is our own: every labelled input the channel
announces, minus the ones already sitting on a bare noise.

Voice history only ever fills outside parrot rig, since parrot mode disables
command mode. That is the point of it: say a command, enter the rig, bind it.
"""

from talon import actions
from ..parrot_rig_settings import UTILITY_RECENT_COUNT, UTILITY_HISTORY_SKIP

# Newest first, so the picker reads top down without reversing
_parrot = []


def parrot_history_record(mode: str, key: str, label: str):
    """Remember an action worth binding. Repeats move to the top, they do not
    stack up, or a run of the same noise would be the whole list."""
    if not label or _is_skipped(label):
        return
    entry = {"mode": mode, "key": key, "label": label}
    _drop(key, label)
    _parrot.insert(0, entry)
    del _parrot[UTILITY_RECENT_COUNT:]


def _drop(key: str, label: str):
    for i, existing in enumerate(_parrot):
        if existing["key"] == key and existing["label"] == label:
            del _parrot[i]
            return


def _is_skipped(label: str) -> bool:
    lowered = label.lower()
    return any(word in lowered for word in UTILITY_HISTORY_SKIP)


def parrot_history(limit: int = None) -> list:
    return _parrot[:limit or UTILITY_RECENT_COUNT]


def parrot_history_clear():
    _parrot.clear()


def voice_history(limit: int = None) -> list:
    """Recent phrases, newest first, without consecutive repeats.

    Absent `user.history_get` is not an error here. The picker just shows an
    empty voice column, and every other kind still works."""
    limit = limit or UTILITY_RECENT_COUNT
    phrases = []
    index = 0
    # History holds repeats, and reads past the end raise. Over-scan so a run
    # of one phrase does not eat the whole column.
    while len(phrases) < limit and index < limit * 5:
        try:
            phrase = actions.user.history_get(index)
        except Exception:
            break
        index += 1
        phrase = (phrase or "").strip()
        if phrase and phrase not in phrases:
            phrases.append(phrase)
    return phrases
