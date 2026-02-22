"""
Cheatsheet UI for parrot mode v7
Shows the noise-to-action mapping in a table format
"""

from talon import actions
from ..parrot_rig_settings import MODE_COLORS
from ..parrot_rig_settings import UI_BORDER_COLOR, UI_BACKGROUND_COLOR, UI_TEXT_COLOR
from ..parrot_rig_actions import input_map as parrot_input_map

def only_current_mode_table():
    """Create a table showing only the current mode"""
    table, tr, td, th = actions.user.ui_elements(["table", "tr", "td", "th"])
    text, state = actions.user.ui_elements(["text", "state"])

    current_mode = state.get("mode", "default")
    mode_config = parrot_input_map.get(current_mode, {})

    # Create header row
    header_row = tr()[
        th(padding=8, border_width=1, border_color=UI_BORDER_COLOR)[
            text("Noise", color=UI_TEXT_COLOR, font_weight="bold", font_size=12)
        ],
        th(padding=8, border_width=1, border_color=UI_BORDER_COLOR)[
            text(f"Mode: {current_mode.upper()}", color=UI_TEXT_COLOR, font_weight="bold", font_size=12)
        ]
    ]

    return table()[
        header_row,
        *[tr()[
            td(padding=8, border_width=1, border_color=UI_BORDER_COLOR)[
                text(noise, color=UI_TEXT_COLOR, font_family="monospace")
            ],
            td(padding=8, border_width=1, border_color=UI_BORDER_COLOR)[
                text(mode_config.get(noise, ("",))[0], color=UI_TEXT_COLOR)
            ]
        ] for noise in mode_config.keys()]
    ]

def cheatsheet_ui():
    """Create cheatsheet UI"""
    screen, window, div, text = actions.user.ui_elements(["screen", "window", "div", "text"])
    table, tr, td, th = actions.user.ui_elements(["table", "tr", "td", "th"])
    state, button, svg, circle, path = actions.user.ui_elements(["state", "button", "svg", "circle", "path"])

    all_modes_config = {k: v for k, v in parrot_input_map.items() if not k.endswith("_select")}
    current_mode, set_current_mode = state.use("mode", "default")

    # Get all unique noises across all modes
    all_noises = set()
    for mode_config in all_modes_config.values():
        all_noises.update(mode_config.keys())
    all_noises = sorted(list(all_noises))

    # Modes that share the same input map bindings (sub-states of move/scroll_move)
    RELATED_MODES = {
        "move": ["move", "boost", "glide"],
        "scroll_move": ["scroll_move", "scroll_boost", "scroll_glide"],
    }
    SCROLL_MODES = {"scroll_stop", "scroll_move", "scroll_boost", "scroll_glide", "scroll_tracking"}

    def _make_icon(mode, cx):
        """Create a circle or triangle icon depending on mode type."""
        color = MODE_COLORS.get(mode, "#FF0000")
        if mode in SCROLL_MODES:
            return path(d=f"M {cx} 19 L {cx - 8} 5 L {cx + 8} 5 Z", fill=color)
        return circle(cx=cx, cy=12, r=7, fill=color)

    # Create header row with mode names and colored icons
    def create_mode_header(mode_name: str):
        related = RELATED_MODES.get(mode_name)
        if related:
            icons = [_make_icon(m, 12 + i * 18) for i, m in enumerate(related)]
        else:
            icons = [_make_icon(mode_name, 12)]

        svg_width = 24 + (len(icons) - 1) * 18 if len(icons) > 1 else 24

        return th(padding=0, border_width=1, border_color=UI_BORDER_COLOR, background_color=UI_BACKGROUND_COLOR)[
            div(
                flex_direction="row",
                align_items="center",
                gap=6,
                padding_left=6,
            )[
                svg(width=svg_width)[*icons],
                text(mode_name.upper(), color=UI_TEXT_COLOR, font_weight="bold", font_size=12)
            ]
        ]

    header_row = tr()[
        th(padding=0, border_width=1, border_color=UI_BORDER_COLOR, background_color=UI_BACKGROUND_COLOR)[
            div(flex_direction="row", align_items="center", gap=6, padding_left=6)[
                text("NOISE", color=UI_TEXT_COLOR, font_weight="bold", font_size=12),
                svg()[
                    circle(cx=12, cy=12, r=7, fill=UI_BACKGROUND_COLOR)
                ],
            ]
        ],
        *[create_mode_header(mode_name) for mode_name in all_modes_config.keys()]
    ]

    # Create rows for each noise
    default_config = all_modes_config.get("default", {})
    DIM_COLOR = "#666666"

    mode_names = list(all_modes_config.keys())

    def create_noise_row(noise: str):
        labels = [config.get(noise, ("",))[0] for config in all_modes_config.values()]

        def cell_for_mode(idx):
            label = labels[idx]
            is_first = idx == 0
            is_same_as_prev = not is_first and label == labels[idx - 1]
            color = DIM_COLOR if is_same_as_prev else UI_TEXT_COLOR
            return td(padding=8, border_width=1, border_color=UI_BORDER_COLOR)[
                text(label, color=color)
            ]

        return tr()[
            td(padding=8, border_width=1, border_color=UI_BORDER_COLOR)[
                text(noise, color=UI_TEXT_COLOR, font_family="monospace")
            ],
            *[cell_for_mode(i) for i in range(len(mode_names))]
        ]

    # Filter out noises that have no labels in any mode
    visible_noises = [
        noise for noise in all_noises
        if any(mode_config.get(noise, ("",))[0] for mode_config in all_modes_config.values())
    ]
    noise_rows = [create_noise_row(noise) for noise in visible_noises]

    return screen(justify_content="center", align_items="center")[
        window(
            id="cheatsheet",
            title="Parrot Rig",
            minimized_body=only_current_mode_table,
        )[
            table(width="100%")[
                header_row,
                *noise_rows
            ]
        ]
    ]

def show_cheatsheet():
    actions.user.ui_elements_toggle(cheatsheet_ui)
