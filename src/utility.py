"""What a utility noise does. One binding per slot, three kinds of thing it can be.

preset - an entry in utility_presets, the mouse actions the slot always had
phrase - something you said, replayed with mimic
parrot - an input map entry, called the way the noise that fired it would

Slots are independent. utility_1 is the noise inside parrot mode, utility_global
is palate with the rig off, and neither knows about the other.

Held here rather than in input_map_single because only presets are keys in a
map. A phrase and a parrot action carry their own payload, and the picker
needs all three to look like one list of choices.
"""

from talon import actions

PRESET = "preset"
PHRASE = "phrase"
PARROT = "parrot"

_bindings = {}


def utility_slots() -> list:
    from ..parrot_rig_settings import UTILITY_SLOTS
    return list(UTILITY_SLOTS)


def _presets(slot: str) -> dict:
    from ..parrot_rig_actions import utility_presets
    return utility_presets[slot]


def _default(slot: str) -> dict:
    return {"kind": PRESET, "key": next(iter(_presets(slot)))}


def utility_binding(slot: str) -> dict:
    if _bindings.get(slot) is None:
        _bindings[slot] = _default(slot)
    return dict(_bindings[slot])


def utility_reset(slot: str):
    _bindings[slot] = None


def utility_set_preset(slot: str, key: str):
    if key in _presets(slot):
        _bindings[slot] = {"kind": PRESET, "key": key}


def utility_set_phrase(slot: str, phrase: str):
    phrase = (phrase or "").strip()
    if phrase:
        _bindings[slot] = {"kind": PHRASE, "phrase": phrase}


def utility_set_parrot(slot: str, mode: str, key: str, label: str):
    _bindings[slot] = {"kind": PARROT, "mode": mode, "key": key, "label": label}


def utility_apply(slot: str, data: dict):
    """Restore a binding from a profile, ignoring one that no longer resolves."""
    kind = (data or {}).get("kind")
    if kind == PRESET and data.get("key") in _presets(slot):
        _bindings[slot] = {"kind": PRESET, "key": data["key"]}
    elif kind == PHRASE and data.get("phrase"):
        _bindings[slot] = {"kind": PHRASE, "phrase": data["phrase"]}
    elif kind == PARROT and _parrot_entry(data.get("mode"), data.get("key")):
        _bindings[slot] = {"kind": PARROT, "mode": data["mode"], "key": data["key"],
                           "label": data.get("label", data["key"])}
    else:
        _bindings[slot] = _default(slot)


def utility_is(slot: str, kind: str, ident=None) -> bool:
    """Whether the picker should show a tile as the current binding."""
    binding = utility_binding(slot)
    if binding["kind"] != kind:
        return False
    if ident is None:
        return True
    if kind == PRESET:
        return binding["key"] == ident
    if kind == PHRASE:
        return binding["phrase"] == ident
    return (binding["mode"], binding["key"]) == ident


def utility_label(slot: str) -> str:
    """One line naming the binding, for the picker header and the settings hub."""
    binding = utility_binding(slot)
    if binding["kind"] == PRESET:
        entry = _presets(slot).get(binding["key"])
        return entry[0] if entry else binding["key"]
    if binding["kind"] == PHRASE:
        return f'"{binding["phrase"]}"'
    return binding.get("label") or binding.get("key", "")


def _parrot_entry(mode: str, key: str):
    """The input map entry a parrot binding points at.

    Looked up in the mode it was recorded in, then the default map, because a
    combo lives in input_map_common and every mode inherits it. Keys carry
    their throttle and debounce suffixes, the recorded input does not."""
    from ..parrot_rig_actions import input_map
    for name in (mode, "default"):
        entries = input_map.get(name) or {}
        entry = next((v for k, v in entries.items() if k.split(":")[0] == key), None)
        if entry:
            return entry
    return None


def utility_run(slot: str):
    """Fire whatever this slot is bound to."""
    binding = utility_binding(slot)
    if binding["kind"] == PRESET:
        entry = _presets(slot).get(binding["key"])
        if entry:
            entry[1]()
        return
    if binding["kind"] == PHRASE:
        actions.mimic(binding["phrase"])
        return
    entry = _parrot_entry(binding.get("mode"), binding.get("key"))
    if entry:
        entry[1]()
