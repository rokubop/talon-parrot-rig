"""Picker for what the palate noise does.

Built to be aimed at, not spoken to. Nothing here is on a noise, every choice
is a tile big enough to hit with an eye tracker and click with your click
noise. Opening it changes no mode and takes no noise away: the rig keeps
working underneath, so you move the cursor onto a tile the way you move it
anywhere else. Only tut is borrowed, to close.

Laid out like the BentoPick panel. One backdrop, three sections named by a
header, no box around any of them. Neighbouring sections alternate their tile
fill, which is what tells them apart.
"""

from talon import actions
from ..src.history import parrot_history, voice_history
from ..src.palate import (
    PARROT, PHRASE, PRESET, palate_is, palate_label,
    palate_set_parrot, palate_set_phrase, palate_set_preset,
)
from ..parrot_rig_settings import (
    PALATE_COLUMNS, PALATE_FONT, PALATE_GAP, PALATE_HEADER_COLOR,
    PALATE_HEADER_GAP, PALATE_PADDING, PALATE_PANEL_COLOR, PALATE_PHRASE_MAX,
    PALATE_RADIUS, PALATE_RECENT_COUNT, PALATE_SECTION_GAP,
    PALATE_TEXT_COLOR, PALATE_TILE_ALT_COLOR, PALATE_TILE_COLOR,
    PALATE_TITLE_BAR_COLOR,
    PALATE_TILE_HEIGHT, PALATE_TILE_HOVER_COLOR, PALATE_TILE_SELECTED_COLOR,
    PALATE_TILE_WIDTH,
)

ROW_WIDTH = PALATE_TILE_WIDTH * PALATE_COLUMNS + PALATE_GAP * (PALATE_COLUMNS - 1)


def _presets():
    from ..parrot_rig_actions import utility_maps
    return utility_maps["utility_1"]


def _assign(setter):
    """Every tile does the same two things, so the handlers only differ in
    which setter they carry."""
    def on_click(_event):
        setter()
        palate_picker_close()
        _notify()
    return on_click


def _notify():
    from .utility_selector import show_utility_notification
    show_utility_notification("Palate", palate_label())


def _shorten(text: str) -> str:
    text = text.strip()
    if len(text) <= PALATE_PHRASE_MAX:
        return text
    return text[:PALATE_PHRASE_MAX - 1].rstrip() + "…"


def _tile(div, text, label, sub, selected, on_click, band=0):
    return div(
        width=PALATE_TILE_WIDTH,
        min_height=PALATE_TILE_HEIGHT,
        padding=10,
        gap=4,
        justify_content="center",
        align_items="center",
        border_radius=PALATE_RADIUS,
        background_color=PALATE_TILE_SELECTED_COLOR if selected else (
            PALATE_TILE_ALT_COLOR if band % 2 else PALATE_TILE_COLOR),
        highlight_style={"background_color": PALATE_TILE_HOVER_COLOR},
        on_click=on_click,
    )[
        text(label, color=PALATE_TEXT_COLOR, font_size=13, font_weight="bold",
             text_align="center"),
        text(sub, color=PALATE_HEADER_COLOR, font_size=11, text_align="center")
        if sub else None,
    ]


def _section(div, text, title, tiles, empty_message=None):
    return div(gap=PALATE_HEADER_GAP)[
        text(title, color=PALATE_HEADER_COLOR, font_size=14, font_weight="bold"),
        div(flex_direction="row", flex_wrap="wrap", gap=PALATE_GAP,
            max_width=ROW_WIDTH, min_width=ROW_WIDTH)[
            *(tiles or [_empty(div, text, empty_message)])
        ],
    ]


def _empty(div, text, message):
    return div(min_height=PALATE_TILE_HEIGHT, justify_content="center")[
        text(message, color=PALATE_HEADER_COLOR, font_size=13)
    ]


def _preset_tiles(div, text, band):
    return [
        _tile(div, text, entry[0], None, palate_is(PRESET, key),
              _assign(lambda k=key: palate_set_preset(k)), band)
        for key, entry in _presets().items()
    ]


def _voice_tiles(div, text, band):
    return [
        _tile(div, text, f'"{_shorten(phrase)}"', None, palate_is(PHRASE, phrase),
              _assign(lambda p=phrase: palate_set_phrase(p)), band)
        for phrase in voice_history(PALATE_RECENT_COUNT)
    ]


def _parrot_tiles(div, text, band):
    return [
        _tile(div, text, entry["label"], entry["key"],
              palate_is(PARROT, (entry["mode"], entry["key"])),
              _assign(lambda e=entry: palate_set_parrot(
                  e["mode"], e["key"], e["label"])), band)
        for entry in parrot_history(PALATE_RECENT_COUNT)
    ]


def palate_picker_ui(props):
    screen, window = actions.user.ui_elements(["screen", "window"])
    div, text = actions.user.ui_elements(["div", "text"])

    return screen(justify_content="center", align_items="center")[
        window(id="palate_picker", title="Palate", padding=0,
               background_color=PALATE_PANEL_COLOR,
               title_bar_style={"background_color": PALATE_TITLE_BAR_COLOR},
               border_radius=PALATE_RADIUS, border_width=0)[
            div(padding=PALATE_PADDING, gap=PALATE_SECTION_GAP,
                font_family=PALATE_FONT)[
                div(flex_direction="row", align_items="center", gap=8,
                    padding_bottom=2)[
                    text("Now", color=PALATE_HEADER_COLOR, font_size=13),
                    text(palate_label(), color=PALATE_TEXT_COLOR, font_size=16,
                         font_weight="bold"),
                ],
                _section(div, text, "Presets", _preset_tiles(div, text, 0)),
                _section(div, text, "Last voice commands",
                         _voice_tiles(div, text, 1),
                         "Nothing said yet this session"),
                _section(div, text, "Last parrot rig actions",
                         _parrot_tiles(div, text, 0),
                         "Nothing done yet this session"),
                div(flex_direction="row", gap=PALATE_GAP, align_items="center")[
                    _tile(div, text, "Close", "tut", False,
                          lambda _e: palate_picker_close(), 1),
                    text("Your noises keep working while this is open",
                         color=PALATE_HEADER_COLOR, font_size=12),
                ],
            ]
        ]
    ]


def palate_picker_is_open() -> bool:
    return actions.user.ui_elements_is_active(palate_picker_ui)


def palate_picker_show():
    actions.user.ui_elements_show(palate_picker_ui, show_hints=False)


def palate_picker_close():
    if palate_picker_is_open():
        actions.user.ui_elements_hide(palate_picker_ui)


def palate_picker_toggle():
    if palate_picker_is_open():
        palate_picker_close()
    else:
        palate_picker_show()
