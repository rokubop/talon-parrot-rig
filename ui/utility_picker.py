"""Picker for what a utility noise does. One per slot.

The one picker with no noises at all. Every other menu is spoken and clicked;
this one is only clicked, because it opens without taking a mode or a noise
away. The rig keeps working underneath, so you move the cursor onto a tile the
way you move it anywhere else. Only tut is borrowed, to close.

Three sections, because they are three separate lists: the presets, what Talon
heard, what the rig did.
"""

from talon import actions
from .picker import footer, now_line, panel, section, tile
from ..src.menu import menu_back, menu_register
from ..src.history import parrot_history, voice_history
from ..src.utility import (
    PARROT, PHRASE, PRESET, utility_is, utility_label,
    utility_set_parrot, utility_set_phrase, utility_set_preset,
)
from ..parrot_rig_settings import (
    UTILITY_PHRASE_MAX, UTILITY_RECENT_COUNT, UTILITY_SLOTS,
)


def _presets(slot):
    from ..parrot_rig_actions import utility_presets
    return utility_presets[slot]


def _title(slot):
    from ..parrot_rig_actions import MENU_TITLES
    return MENU_TITLES.get(slot, slot)


def _assign(slot, setter):
    """Every tile does the same two things, so the handlers only differ in
    which setter they carry."""
    def on_click(_event):
        setter()
        menu_back()
        _notify(slot)
    return on_click


def _notify(slot):
    from .setting_picker import show_notification
    show_notification(_title(slot), utility_label(slot))


def _shorten(text: str) -> str:
    text = text.strip()
    if len(text) <= UTILITY_PHRASE_MAX:
        return text
    return text[:UTILITY_PHRASE_MAX - 1].rstrip() + "…"


def _preset_tiles(slot, band):
    return [
        tile(entry[0], selected=utility_is(slot, PRESET, key), band=band,
             on_click=_assign(slot, lambda k=key: utility_set_preset(slot, k)))
        for key, entry in _presets(slot).items()
    ]


def _voice_tiles(slot, band):
    return [
        tile(f'"{_shorten(phrase)}"', selected=utility_is(slot, PHRASE, phrase), band=band,
             on_click=_assign(slot, lambda p=phrase: utility_set_phrase(slot, p)))
        for phrase in voice_history(UTILITY_RECENT_COUNT)
    ]


def _parrot_tiles(slot, band):
    return [
        tile(entry["label"], value=entry["key"], band=band,
             selected=utility_is(slot, PARROT, (entry["mode"], entry["key"])),
             on_click=_assign(slot, lambda e=entry: utility_set_parrot(
                 slot, e["mode"], e["key"], e["label"])))
        for entry in parrot_history(UTILITY_RECENT_COUNT)
    ]


def _make_picker(slot):
    def utility_picker_ui(props):
        return panel(f"{slot}_picker", _title(slot), [
            now_line(utility_label(slot)),
            section("Presets", _preset_tiles(slot, 0), fixed=True),
            section("Last voice commands", _voice_tiles(slot, 1), fixed=True,
                    empty="Nothing said yet this session"),
            section("Last parrot rig actions", _parrot_tiles(slot, 0), fixed=True,
                    empty="Nothing done yet this session"),
            footer(
                [tile("Close", noise="tut", exit=True,
                      on_click=lambda _e: menu_back())],
                "Your noises keep working while this is open",
            ),
        ])

    utility_picker_ui.__qualname__ = f"{slot}_picker_ui"
    utility_picker_ui.__name__ = utility_picker_ui.__qualname__
    return utility_picker_ui


_pickers = {slot: _make_picker(slot) for slot in UTILITY_SLOTS}


def utility_picker_show(slot):
    actions.user.ui_elements_show(_pickers[slot], show_hints=False)


def utility_picker_hide(slot):
    actions.user.ui_elements_hide(_pickers[slot])


for _slot in _pickers:
    menu_register(
        _slot,
        lambda s=_slot: utility_picker_show(s),
        lambda s=_slot: utility_picker_hide(s),
    )
