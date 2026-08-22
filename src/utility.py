"""What the utility 1 noise does. One binding, three kinds of thing it can be.

preset - an entry in utility_presets, the eight mouse actions it always had
phrase - something you said, replayed with mimic
parrot - an input map entry, called the way the noise that fired it would

Held here rather than in input_map_single because only presets are keys in a
map. A phrase and a parrot action carry their own payload, and the picker
needs all three to look like one list of choices.
"""

from talon import actions

PRESET = "preset"
PHRASE = "phrase"
PARROT = "parrot"

_binding = None


def _presets() -> dict:
    from ..parrot_rig_actions import utility_presets
    return utility_presets["utility_1"]


def _default() -> dict:
    return {"kind": PRESET, "key": next(iter(_presets()))}


def utility_binding() -> dict:
    global _binding
    if _binding is None:
        _binding = _default()
    return dict(_binding)


def utility_reset():
    global _binding
    _binding = None


def utility_set_preset(key: str):
    global _binding
    if key in _presets():
        _binding = {"kind": PRESET, "key": key}


def utility_set_phrase(phrase: str):
    global _binding
    phrase = (phrase or "").strip()
    if phrase:
        _binding = {"kind": PHRASE, "phrase": phrase}


def utility_set_parrot(mode: str, key: str, label: str):
    global _binding
    _binding = {"kind": PARROT, "mode": mode, "key": key, "label": label}


def utility_apply(data: dict):
    """Restore a binding from a profile, ignoring one that no longer resolves."""
    global _binding
    kind = (data or {}).get("kind")
    if kind == PRESET and data.get("key") in _presets():
        _binding = {"kind": PRESET, "key": data["key"]}
    elif kind == PHRASE and data.get("phrase"):
        _binding = {"kind": PHRASE, "phrase": data["phrase"]}
    elif kind == PARROT and _parrot_entry(data.get("mode"), data.get("key")):
        _binding = {"kind": PARROT, "mode": data["mode"], "key": data["key"],
                    "label": data.get("label", data["key"])}
    else:
        _binding = _default()


def utility_is(kind: str, ident=None) -> bool:
    """Whether the picker should show a tile as the current binding."""
    binding = utility_binding()
    if binding["kind"] != kind:
        return False
    if ident is None:
        return True
    if kind == PRESET:
        return binding["key"] == ident
    if kind == PHRASE:
        return binding["phrase"] == ident
    return (binding["mode"], binding["key"]) == ident


def utility_label() -> str:
    """One line naming the binding, for the picker header and the settings hub."""
    binding = utility_binding()
    if binding["kind"] == PRESET:
        entry = _presets().get(binding["key"])
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


def utility_run():
    """Fire whatever utility 1 is bound to."""
    binding = utility_binding()
    if binding["kind"] == PRESET:
        entry = _presets().get(binding["key"])
        if entry:
            entry[1]()
        return
    if binding["kind"] == PHRASE:
        actions.mimic(binding["phrase"])
        return
    entry = _parrot_entry(binding.get("mode"), binding.get("key"))
    if entry:
        entry[1]()
