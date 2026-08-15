"""Named snapshots of every menu value, persisted in talon storage.

Slot 1 is always "default": the factory values, never stored, never writable.
Loading it resets everything. Nothing else persists between sessions until a
profile is saved.
"""

from talon import actions, storage
from .settings_menu import setting_maps, setting_get, setting_set

PROFILES_KEY = "parrot_rig_profiles"
PROFILE_SLOTS = 8
DEFAULT_PROFILE = "default"

_active = DEFAULT_PROFILE


def _utility_maps():
    from ..parrot_rig_actions import utility_maps
    return utility_maps


def profile_is_locked(name: str) -> bool:
    return name == DEFAULT_PROFILE


def factory_defaults() -> dict:
    return {
        "settings": {name: next(iter(options)) for name, options in setting_maps.items()},
        "utilities": {name: next(iter(m)) for name, m in _utility_maps().items()},
    }


def profile_snapshot() -> dict:
    utilities = {}
    for name, util_map in _utility_maps().items():
        try:
            utilities[name] = actions.user.input_map_single_mode_get(name)
        except (ValueError, KeyError):
            utilities[name] = next(iter(util_map))
    return {
        "settings": {name: setting_get(name) for name in setting_maps},
        "utilities": utilities,
    }


def profile_apply(data: dict):
    for name, value in (data.get("settings") or {}).items():
        if name in setting_maps and value in setting_maps[name]:
            setting_set(name, value)
    for name, value in (data.get("utilities") or {}).items():
        util_map = _utility_maps().get(name)
        if util_map and value in util_map:
            actions.user.input_map_single_mode_set(name, value, util_map)


def all_profiles() -> dict:
    saved = dict(storage.get(PROFILES_KEY, {}) or {})
    saved.pop(DEFAULT_PROFILE, None)
    return saved


def profile_names() -> list:
    return [DEFAULT_PROFILE] + list(all_profiles())


def profile_active() -> str:
    return _active


def profile_save(name: str) -> bool:
    global _active
    if profile_is_locked(name):
        return False
    profiles = all_profiles()
    profiles[name] = profile_snapshot()
    storage.set(PROFILES_KEY, profiles)
    _active = name
    return True


def profile_load(name: str) -> bool:
    global _active
    if profile_is_locked(name):
        profile_apply(factory_defaults())
        _active = DEFAULT_PROFILE
        return True
    data = all_profiles().get(name)
    if data is None:
        return False
    profile_apply(data)
    _active = name
    return True


def profile_delete(name: str) -> bool:
    global _active
    if profile_is_locked(name):
        return False
    profiles = all_profiles()
    if name not in profiles:
        return False
    del profiles[name]
    storage.set(PROFILES_KEY, profiles)
    if _active == name:
        _active = DEFAULT_PROFILE
    return True
