from talon import actions


def _make_mode(name, util_map, ui_selectors, ui_cancel, select, close, ui_exit):
    """Noises pick slots in order, except where an entry names its own.

    A third element pins that option to a noise wherever it sits in the map,
    and the rest fill the noises left over, still in order."""
    keys = list(util_map.keys())
    pinned = {}
    for i, key in enumerate(keys):
        entry = util_map[key]
        if len(entry) > 2 and entry[2]:
            pinned[entry[2]] = i

    mode = {}
    for noise, i in pinned.items():
        mode[noise] = (util_map[keys[i]][0], lambda i=i, n=name: select(n, i))

    free = [n for n in ui_selectors if n not in pinned]
    rest = [i for i in range(len(keys)) if i not in set(pinned.values())]
    for noise, i in zip(free, rest):
        mode[noise] = (util_map[keys[i]][0], lambda i=i, n=name: select(n, i))

    # Last, so back always wins a noise a pin tried to take
    for noise in ui_cancel:
        mode[noise] = ("back", lambda n=name: close(n))

    # Except exit, which outranks back because it means the same thing in every
    # mode, menus included
    for noise in ui_exit or []:
        mode[noise] = ("exit", lambda: actions.user.parrot_rig_exit())

    return mode


def utility_input_maps(maps: dict, ui_selectors: list, ui_cancel: list,
                       select=None, close=None, ui_exit=None):
    """Create selector input map modes.

    maps: {"mode_name": util_map, ...}, entries (label, action) or
        (label, action, noise) to pin that option to a noise
    ui_selectors: noises mapped to the unpinned slots, in order
    ui_cancel: noises that close the selector
    ui_exit: noises that leave parrot rig outright, winning over everything
    select: (name, slot) -> None, defaults to picking a utility action
    close: (name) -> None, required

    Returns a dict with "{mode_name}_select" keys to spread into the main input_map.
    """
    if select is None:
        select = lambda n, i: actions.user.parrot_rig_utility_select(n, i)

    result = {}
    for name, util_map in maps.items():
        result[f"{name}_select"] = _make_mode(
            name, util_map, ui_selectors, ui_cancel, select, close, ui_exit
        )
    return result
