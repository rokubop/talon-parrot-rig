"""Shared look for every picker menu.

Taken from the BentoPick panel: one backdrop, sections named by a header
rather than boxed off, tiles carrying every state in their fill. Neighbouring
sections alternate between two tile fills, and that is what separates them.

A tile holds three things at most, all optional but the label: the noise that
picks it, the label, and what it is currently set to. Every tile also takes a
click, so a menu works the same whether you say it or look at it.
"""

from talon import actions
from ..parrot_rig_settings import (
    PICKER_COLUMNS, PICKER_FONT, PICKER_GAP, PICKER_HEADER_COLOR,
    PICKER_HEADER_GAP, PICKER_NOISE_COLOR, PICKER_PADDING, PICKER_PANEL_COLOR,
    PICKER_RADIUS, PICKER_SECTION_GAP, PICKER_TEXT_COLOR,
    PICKER_TILE_ALT_COLOR, PICKER_TILE_COLOR, PICKER_TILE_EXIT_COLOR,
    PICKER_TILE_HEIGHT, PICKER_TILE_HOVER_COLOR, PICKER_TILE_SELECTED_COLOR,
    PICKER_TILE_WIDTH, PICKER_TITLE_BAR_COLOR,
)


def row_width(columns: int) -> int:
    return PICKER_TILE_WIDTH * columns + PICKER_GAP * max(0, columns - 1)


def _elements():
    return actions.user.ui_elements(["div", "text"])


def tile(label, noise=None, value=None, selected=False, on_click=None,
         band=0, exit=False):
    """One choice. Fill says the state, nothing is outlined."""
    div, text = _elements()
    if exit:
        background = PICKER_TILE_EXIT_COLOR
    elif selected:
        background = PICKER_TILE_SELECTED_COLOR
    else:
        background = PICKER_TILE_ALT_COLOR if band % 2 else PICKER_TILE_COLOR

    return div(
        width=PICKER_TILE_WIDTH,
        min_height=PICKER_TILE_HEIGHT,
        padding=10,
        gap=4,
        justify_content="center",
        align_items="center",
        border_radius=PICKER_RADIUS,
        background_color=background,
        highlight_style={"background_color": PICKER_TILE_HOVER_COLOR},
        on_click=on_click,
    )[
        text(noise, color=PICKER_NOISE_COLOR, font_size=11,
             font_family="monospace", text_align="center") if noise else None,
        text(label, color=PICKER_TEXT_COLOR, font_size=13, font_weight="bold",
             text_align="center"),
        text(value, color=PICKER_HEADER_COLOR, font_size=11,
             text_align="center") if value else None,
    ]


def section(title, tiles, columns: int = PICKER_COLUMNS, fixed: bool = False,
            empty: str = None):
    """A header and the tiles under it. No box: the fill does that job.

    fixed pins the row to the full column width, for a panel whose sections
    have to line up with each other."""
    div, text = _elements()
    width = row_width(min(columns, max(1, len(tiles))))
    return div(gap=PICKER_HEADER_GAP)[
        text(title, color=PICKER_HEADER_COLOR, font_size=14,
             font_weight="bold") if title else None,
        div(flex_direction="row", flex_wrap="wrap", gap=PICKER_GAP,
            max_width=row_width(columns) if fixed else width,
            min_width=row_width(columns) if fixed else None)[
            *(tiles or [_empty(empty or "Nothing here yet")])
        ],
    ]


def _empty(message):
    div, text = _elements()
    return div(min_height=PICKER_TILE_HEIGHT, justify_content="center")[
        text(message, color=PICKER_HEADER_COLOR, font_size=13)
    ]


def now_line(label, prefix="Now"):
    """What the menu is currently set to, above its choices."""
    div, text = _elements()
    return div(flex_direction="row", align_items="center", gap=8,
               padding_bottom=2)[
        text(prefix, color=PICKER_HEADER_COLOR, font_size=13),
        text(label, color=PICKER_TEXT_COLOR, font_size=16, font_weight="bold"),
    ]


def panel(window_id, title, children):
    """The backdrop every picker sits on."""
    screen, window = actions.user.ui_elements(["screen", "window"])
    div, _ = _elements()
    return screen(justify_content="center", align_items="center")[
        window(id=window_id, title=title, padding=0,
               background_color=PICKER_PANEL_COLOR,
               title_bar_style={"background_color": PICKER_TITLE_BAR_COLOR},
               border_radius=PICKER_RADIUS, border_width=0)[
            div(padding=PICKER_PADDING, gap=PICKER_SECTION_GAP,
                font_family=PICKER_FONT)[
                *children
            ]
        ]
    ]


def footer(tiles, note=None):
    """Back, close, exit. Sits under everything, with room for a word."""
    div, text = _elements()
    return div(flex_direction="row", gap=PICKER_GAP, align_items="center")[
        *tiles,
        text(note, color=PICKER_HEADER_COLOR, font_size=12) if note else None,
    ]
