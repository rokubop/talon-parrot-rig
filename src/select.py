from talon import actions


def _make_mode(name, util_map, ui_selectors, ui_cancel, select, close):
    keys = list(util_map.keys())
    mode = {}

    for i, noise in enumerate(ui_selectors):
        if i < len(keys):
            label = util_map[keys[i]][0]
            mode[noise] = (label, lambda i=i, n=name: select(n, i))

    for noise in ui_cancel:
        mode[noise] = ("back", lambda n=name: close(n))

    return mode


def utility_input_maps(maps: dict, ui_selectors: list, ui_cancel: list,
                       select=None, close=None):
    """Create selector input map modes.

    maps: {"mode_name": util_map, ...}
    ui_selectors: noises mapped to slots in order
    ui_cancel: noises that close the selector
    select: (name, slot) -> None, defaults to picking a utility action
    close: (name) -> None, defaults to closing a utility selector

    Returns a dict with "{mode_name}_select" keys to spread into the main input_map.
    """
    if select is None:
        select = lambda n, i: actions.user.parrot_rig_utility_select(n, i)
    if close is None:
        close = lambda n: actions.user.parrot_rig_utility_select_close(n)

    result = {}
    for name, util_map in maps.items():
        result[f"{name}_select"] = _make_mode(
            name, util_map, ui_selectors, ui_cancel, select, close
        )
    return result
