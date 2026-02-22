from talon import actions


def _make_mode(name, util_map, ui_selectors, ui_cancel):
    keys = list(util_map.keys())
    mode = {}

    for i, noise in enumerate(ui_selectors):
        if i < len(keys):
            label = util_map[keys[i]][0]
            mode[noise] = (label, lambda i=i, n=name: actions.user.parrot_rig_utility_select(n, i))

    for noise in ui_cancel:
        mode[noise] = ("back", lambda: actions.user.parrot_rig_utility_select_close(name))

    return mode


def utility_input_maps(maps: dict, ui_selectors: list, ui_cancel: list):
    """Create utility select input map modes.

    maps: {"mode_name": util_map, ...}
    ui_selectors: noises mapped to slots in order
    ui_cancel: noises that close the selector

    Returns a dict with "{mode_name}_select" keys to spread into the main input_map.
    """
    result = {}
    for name, util_map in maps.items():
        result[f"{name}_select"] = _make_mode(name, util_map, ui_selectors, ui_cancel)
    return result
