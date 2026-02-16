from talon import actions
from ..parrot_rig_utilities import utility_map, utility2_map

def _make_mode(name, activation_noise, util_map, noises, exit_noises):
    keys = list(util_map.keys())
    mode = {}

    for i, noise in enumerate(noises):
        if i < len(keys):
            label = util_map[keys[i]][0]
            mode[noise] = (label, lambda i=i, n=name, an=activation_noise: actions.user.parrot_rig_utility_select(n, i, an))

    for noise in exit_noises:
        mode[noise] = ("back", lambda: actions.user.parrot_rig_utility_select_close(name))

    return mode

def utility_input_maps(config: dict):
    """Create utility_select and utility2_select input map modes.

    config: {
        "selectors": ["ah", "oh", ...],  # noises mapped to slots in order
        "cancel": ["ee", "cluck"],        # noises that close the selector
        "utility_noise": "palate",        # noise that activates utility
        "utility2_noise": "er",           # noise that activates utility2
    }

    Returns a dict with "utility_select" and "utility2_select" keys
    to spread into the main input_map.
    """
    noises = config.get("selectors", [])
    exit_noises = config.get("cancel", [])
    utility_noise = config.get("utility_noise", "palate")
    utility2_noise = config.get("utility2_noise", "er")

    return {
        "utility_select": _make_mode("utility", utility_noise, utility_map, noises, exit_noises),
        "utility2_select": _make_mode("utility2", utility2_noise, utility2_map, noises, exit_noises),
    }
