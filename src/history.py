"""The two histories the utility 1 picker offers, kept apart on purpose.

Voice is Talon's own, through `actions.core.recent_commands()`. Parrot rig is
ours: every labelled input the channel announces, minus the ones already
sitting on a bare noise.
"""

from talon import actions
from ..parrot_rig_settings import UTILITY_RECENT_COUNT, UTILITY_HISTORY_SKIP

# parrot_rig_input.talon swallows speech with `^<phrase>$: skip()` so talking
# cannot fire noises. Talon still records those recognitions, and what they
# hold is the recogniser guessing at a mouth noise, never anything said on
# purpose. Commands that matched only this rule are dropped.
SWALLOWED_RULE = "<phrase>"

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
    """Commands you ran, newest first, no repeats.

    Commands rather than phrases, because a phrase the rig swallowed or a
    stretch of dictation is not something anyone wants on a noise."""
    limit = limit or UTILITY_RECENT_COUNT
    phrases = []
    for commands in reversed(actions.core.recent_commands()):
        if not commands or all(_rule(c) == SWALLOWED_RULE for c, _ in commands):
            continue
        spoken = " ".join(str(capture) for _, capture in commands).strip()
        if spoken and spoken not in phrases:
            phrases.append(spoken)
        if len(phrases) >= limit:
            break
    return phrases


def _rule(command) -> str:
    rule = getattr(command, "rule", None)
    return getattr(rule, "rule", "") if rule is not None else ""
