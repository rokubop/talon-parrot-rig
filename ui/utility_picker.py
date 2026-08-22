"""Picker for what the utility 1 noise does.

The one picker with no noises at all. Every other menu is spoken and clicked;
this one is only clicked, because it opens without taking a mode or a noise
away. The rig keeps working underneath, so you move the cursor onto a tile the
way you move it anywhere else. Only tut is borrowed, to close.

Three sections, because they are three separate lists: the presets, what Talon
heard, what the rig did.
"""

from talon import actions
from .picker import footer, now_line, panel, section, tile
from ..src.history import parrot_history, voice_history
from ..src.utility import (
    PARROT, PHRASE, PRESET, utility_is, utility_label,
    utility_set_parrot, utility_set_phrase, utility_set_preset,
)
from ..parrot_rig_settings import UTILITY_PHRASE_MAX, UTILITY_RECENT_COUNT


def _presets():
    from ..parrot_rig_actions import utility_presets
    return utility_presets["utility_1"]


def _assign(setter):
    """Every tile does the same two things, so the handlers only differ in
    which setter they carry."""
    def on_click(_event):
        setter()
        utility_picker_close()
        _notify()
    return on_click


def _notify():
    from .setting_picker import show_notification
    show_notification("Utility 1", utility_label())


def _shorten(text: str) -> str:
    text = text.strip()
    if len(text) <= UTILITY_PHRASE_MAX:
        return text
    return text[:UTILITY_PHRASE_MAX - 1].rstrip() + "…"


def _preset_tiles(band):
    return [
        tile(entry[0], selected=utility_is(PRESET, key), band=band,
             on_click=_assign(lambda k=key: utility_set_preset(k)))
        for key, entry in _presets().items()
    ]


def _voice_tiles(band):
    return [
        tile(f'"{_shorten(phrase)}"', selected=utility_is(PHRASE, phrase), band=band,
             on_click=_assign(lambda p=phrase: utility_set_phrase(p)))
        for phrase in voice_history(UTILITY_RECENT_COUNT)
    ]


def _parrot_tiles(band):
    return [
        tile(entry["label"], value=entry["key"], band=band,
             selected=utility_is(PARROT, (entry["mode"], entry["key"])),
             on_click=_assign(lambda e=entry: utility_set_parrot(
                 e["mode"], e["key"], e["label"])))
        for entry in parrot_history(UTILITY_RECENT_COUNT)
    ]


def utility_picker_ui(props):
    return panel("utility_picker", "Utility 1", [
        now_line(utility_label()),
        section("Presets", _preset_tiles(0), fixed=True),
        section("Last voice commands", _voice_tiles(1), fixed=True,
                empty="Nothing said yet this session"),
        section("Last parrot rig actions", _parrot_tiles(0), fixed=True,
                empty="Nothing done yet this session"),
        footer(
            [tile("Close", noise="tut", exit=True,
                  on_click=lambda _e: utility_picker_close())],
            "Your noises keep working while this is open",
        ),
    ])


def utility_picker_is_open() -> bool:
    return actions.user.ui_elements_is_active(utility_picker_ui)


def utility_picker_show():
    actions.user.ui_elements_show(utility_picker_ui, show_hints=False)


def utility_picker_close():
    if utility_picker_is_open():
        actions.user.ui_elements_hide(utility_picker_ui)


def utility_picker_toggle():
    if utility_picker_is_open():
        utility_picker_close()
    else:
        utility_picker_show()
