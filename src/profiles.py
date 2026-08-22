"""Named snapshots of every menu value, persisted in talon storage.

Slot 1 is always "default": the factory values, never stored, never writable.
Loading it resets everything. Nothing else persists between sessions until a
profile is saved.
"""

from talon import actions, storage
from .utility import utility_apply, utility_binding
from .settings_menu import (
    setting_maps, setting_get, setting_set, setting_customs, setting_apply_customs,
)

PROFILES_KEY = "parrot_rig_profiles"
PROFILE_SLOTS = 8
DEFAULT_PROFILE = "default"

_active = DEFAULT_PROFILE


def profile_is_locked(name: str) -> bool:
    return name == DEFAULT_PROFILE


def factory_defaults() -> dict:
    return {
        "settings": {name: next(iter(options)) for name, options in setting_maps.items()},
        "utility_1": None,
        "customs": {},
    }


def profile_snapshot() -> dict:
    return {
        "settings": {name: setting_get(name) for name in setting_maps},
        "utility_1": utility_binding(),
        "customs": setting_customs(),
    }


def profile_apply(data: dict):
    setting_apply_customs(data.get("customs"))
    for name, value in (data.get("settings") or {}).items():
        if name in setting_maps and value in setting_maps[name]:
            setting_set(name, value)
    utility_apply(data.get("utility_1") or _legacy_utility(data))


def _legacy_utility(data: dict):
    """Older profiles stored this under other names: a preset key inside
    utilities, then a binding under the noise it sat on, then shortcut. Read
    them all so those profiles still load."""
    for key in ("shortcut", "palate"):
        if data.get(key):
            return data[key]
    preset = (data.get("utilities") or {}).get("utility_1")
    return {"kind": "preset", "key": preset} if preset else None


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
