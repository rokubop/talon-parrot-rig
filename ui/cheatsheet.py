"""
Cheatsheet UI for parrot mode v7
Shows the noise-to-action mapping in a table format
"""

from talon import actions
from .colors import get_mode_color
from ..parrot_rig_actions import input_map as parrot_input_map

def only_current_mode_table():
    """Create a table showing only the current mode"""
    table, tr, td, th = actions.user.ui_elements(["table", "tr", "td", "th"])
    text, state = actions.user.ui_elements(["text", "state"])

    current_mode = state.get("mode", "default")
    mode_config = parrot_input_map.get(current_mode, {})

    # Create header row
    header_row = tr()[
        th(padding=8, border_width=1, border_color="#666666")[
            text("Noise", color="#FFFFFF", font_weight="bold", font_size=12)
        ],
        th(padding=8, border_width=1, border_color="#666666")[
            text(f"Mode: {current_mode.upper()}", color="#FFFFFF", font_weight="bold", font_size=12)
        ]
    ]

    return table()[
        header_row,
        *[tr()[
            td(padding=8, border_width=1, border_color="#666666")[
                text(noise, color="#FFFFFF", font_family="monospace")
            ],
            td(padding=8, border_width=1, border_color="#666666")[
                text(mode_config.get(noise, ("",))[0], color="#FFFFFF")
            ]
        ] for noise in mode_config.keys()]
    ]

def cheatsheet_ui():
    """Create cheatsheet UI"""
    screen, window, div, text = actions.user.ui_elements(["screen", "window", "div", "text"])
    table, tr, td, th = actions.user.ui_elements(["table", "tr", "td", "th"])
    state, button, svg, circle = actions.user.ui_elements(["state", "button", "svg", "circle"])

    all_modes_config = parrot_input_map
    current_mode, set_current_mode = state.use("mode", "default")

    # Get all unique noises across all modes
    all_noises = set()
    for mode_config in all_modes_config.values():
        all_noises.update(mode_config.keys())
    all_noises = sorted(list(all_noises))

    # Create header row with mode names (clickable) and colored circles
    def create_mode_header(mode_name: str):
        mode_color = get_mode_color(mode_name)

        return th(padding=0, border_width=1, border_color="#666666", background_color="#4A4A4A")[
            div(
                flex_direction="row",
                align_items="center",
                gap=6,
                padding_left=6,
            )[
                svg()[
                    circle(cx=12, cy=12, r=7, fill=f"{mode_color}")
                ],
                text(mode_name.upper(), color="#FFFFFF", font_weight="bold", font_size=12)
            ]
        ]

    header_row = tr()[
        th(padding=0, border_width=1, border_color="#666666", background_color="#4A4A4A")[
            div(flex_direction="row", align_items="center", gap=6, padding_left=6)[
                text("NOISE", color="#FFFFFF", font_weight="bold", font_size=12),
                svg()[
                    circle(cx=12, cy=12, r=7, fill=f"#4A4A4A")
                ],
            ]
        ],
        *[create_mode_header(mode_name) for mode_name in all_modes_config.keys()]
    ]

    # Create rows for each noise
    def create_noise_row(noise: str):
        return tr()[
            td(padding=8, border_width=1, border_color="#666666")[
                text(noise, color="#FFFFFF", font_family="monospace")
            ],
            *[td(padding=8, border_width=1, border_color="#666666")[
                text(mode_config.get(noise, ("",))[0], color="#FFFFFF")
            ] for mode_name, mode_config in all_modes_config.items()]
        ]

    noise_rows = [create_noise_row(noise) for noise in all_noises]

    return screen(justify_content="center", align_items="center")[
        window(
            id="cheatsheet",
            title="Cheatsheet",
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
