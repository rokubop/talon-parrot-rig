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

# One column per input map, wearing the shape and every colour the cursor uses
# for it.
COLUMNS = [
    ("default",      "default",      "circle",   ["default"]),
    ("move",         "move",         "circle",   ["move", "boost", "glide"]),
    ("tracking",     "tracking",     "circle",   ["tracking"]),
    ("canvas",       "canvas_stop",  "triangle", ["canvas_stop", "canvas_tracking"]),
    ("canvas move",  "canvas_move",  "triangle", ["canvas_move", "canvas_boost", "canvas_glide"]),
    ("canvas scale", "canvas_scale", "diamond",  ["canvas_scale", "canvas_scale_move"]),
    ("window",       "window",       "square",   ["window_stop", "window", "window_move"]),
]


# Labels that switch modes rather than act, so the cell can wear the mode's mark
MODE_LABELS = {
    "canvas scroll":  ("triangle", "canvas_stop"),
    "canvas scale":   ("diamond",  "canvas_scale"),
    "canvas drag":    ("circle",   "move"),
    "window pick":    ("square",   "window"),
    "window control": ("square",   "window_stop"),
}


def cheatsheet_ui():
    """Create cheatsheet UI"""
    screen, window, div, text = actions.user.ui_elements(["screen", "window", "div", "text"])
    table, tr, td, th = actions.user.ui_elements(["table", "tr", "td", "th"])
    state, button, svg, circle, path = actions.user.ui_elements(["state", "button", "svg", "circle", "path"])

    current_mode, set_current_mode = state.use("mode", "default")

    columns = [(title, parrot_input_map.get(mode, {}), shape, states)
               for title, mode, shape, states in COLUMNS]

    all_noises = sorted({n for _, config, _, _ in columns for n in config})

    def _icon(mode, shape, cx):
        color = MODE_COLORS.get(mode, "#FF0000")
        if shape == "triangle":
            return path(d=f"M {cx} 19 L {cx - 8} 5 L {cx + 8} 5 Z", fill=color)
        if shape == "diamond":
            return path(d=f"M {cx} 4 L {cx + 8} 12 L {cx} 20 L {cx - 8} 12 Z", fill=color)
        if shape == "square":
            return path(d=f"M {cx - 6} 6 H {cx + 6} V 18 H {cx - 6} Z", fill=color)
        return circle(cx=cx, cy=12, r=7, fill=color)

    def create_mode_header(title, shape, states):
        icons = [_icon(m, shape, 12 + i * 18) for i, m in enumerate(states)]
        svg_width = 24 + (len(icons) - 1) * 18

        return th(padding=0, border_width=1, border_color=UI_BORDER_COLOR, background_color=UI_BACKGROUND_COLOR)[
            div(
                flex_direction="row",
                align_items="center",
                gap=6,
                padding_left=6,
            )[
                svg(width=svg_width)[*icons],
                text(title.upper(), color=UI_TEXT_COLOR, font_weight="bold", font_size=12)
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
        *[create_mode_header(title, shape, states) for title, _, shape, states in columns]
    ]

    DIM_COLOR = "#666666"

    def create_noise_row(noise: str):
        labels = [config.get(noise, ("",))[0] for _, config, _, _ in columns]

        def cell_for_mode(idx):
            label = labels[idx]
            is_same_as_prev = idx > 0 and label == labels[idx - 1]
            color = DIM_COLOR if is_same_as_prev else UI_TEXT_COLOR
            mark = None if is_same_as_prev else MODE_LABELS.get(label)
            body = text(label, color=color)
            if mark:
                shape, mode = mark
                body = div(flex_direction="row", align_items="center", gap=6)[
                    svg(width=24)[_icon(mode, shape, 12)],
                    text(label, color=color),
                ]
            return td(padding=8, border_width=1, border_color=UI_BORDER_COLOR)[
                body
            ]

        return tr()[
            td(padding=8, border_width=1, border_color=UI_BORDER_COLOR)[
                text(noise, color=UI_TEXT_COLOR, font_family="monospace")
            ],
            *[cell_for_mode(i) for i in range(len(columns))]
        ]

    visible_noises = [
        noise for noise in all_noises
        if any(config.get(noise, ("",))[0] for _, config, _, _ in columns)
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
