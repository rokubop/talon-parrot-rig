"""
Cheatsheet UI for parrot mode v7
Shows the noise-to-action mapping in a table format
"""

from talon import actions, settings
from ..src.menu import menu_back, menu_current, menu_open, menu_register
from ..parrot_rig_settings import MODE_COLORS
from ..parrot_rig_settings import UI_BORDER_COLOR, UI_BACKGROUND_COLOR, UI_TEXT_COLOR
from ..parrot_rig_actions import input_map as parrot_input_map

# Secondary line in a cell, quieter than the label above it
INIT_COLOR = "#8A8A98"


def _split_key(key: str):
    """'hiss:init_150' -> ('hiss', 150). Throttle and debounce suffixes drop
    out, since they do not change what the noise does."""
    base, *suffixes = key.split(":")
    for part in suffixes:
        if part == "init":
            return base, settings.get("user.input_map_init_window", 300)
        if part.startswith("init_") and part[5:].isdigit():
            return base, int(part[5:])
    return base, None


def mode_labels(config: dict):
    """One map into {noise: label} and {noise: (window_ms, label)}, so a noise
    that means one thing on arrival and another after shows up once, not twice."""
    normal, init = {}, {}
    for key, entry in config.items():
        base, window = _split_key(key)
        if window is not None:
            init[base] = (window, entry[0])
        elif key == base or base not in normal:
            normal[base] = entry[0]
    return normal, init


def only_current_mode_table():
    """Create a table showing only the current mode"""
    table, tr, td, th = actions.user.ui_elements(["table", "tr", "td", "th"])
    text, state, div = actions.user.ui_elements(["text", "state", "div"])

    current_mode = state.get("mode", "default")
    normal, init = mode_labels(parrot_input_map.get(current_mode, {}))

    # Create header row
    header_row = tr()[
        th(padding=8, border_width=1, border_color=UI_BORDER_COLOR)[
            text("Noise", color=UI_TEXT_COLOR, font_weight="bold", font_size=16)
        ],
        th(padding=8, border_width=1, border_color=UI_BORDER_COLOR)[
            text(f"Mode: {current_mode.upper()}", color=UI_TEXT_COLOR, font_weight="bold", font_size=16)
        ]
    ]

    return table()[
        header_row,
        *[tr()[
            td(padding=8, border_width=1, border_color=UI_BORDER_COLOR)[
                text(noise, color=UI_TEXT_COLOR, font_family="monospace")
            ],
            td(padding=8, border_width=1, border_color=UI_BORDER_COLOR)[
                div(flex_direction="column", gap=2)[
                    text(normal.get(noise, ""), color=UI_TEXT_COLOR),
                    *([text(f"{init[noise][0]}ms  {init[noise][1]}", color=INIT_COLOR, font_size=13)]
                      if noise in init else []),
                ]
            ]
        ] for noise in sorted(set(normal) | set(init))]
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

    columns = [(title, *mode_labels(parrot_input_map.get(mode, {})), shape, states)
               for title, mode, shape, states in COLUMNS]

    all_noises = sorted({n for _, normal, init, _, _ in columns
                         for n in list(normal) + list(init)})

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
                text(title.upper(), color=UI_TEXT_COLOR, font_weight="bold", font_size=16)
            ]
        ]

    header_row = tr()[
        th(padding=0, border_width=1, border_color=UI_BORDER_COLOR, background_color=UI_BACKGROUND_COLOR)[
            div(flex_direction="row", align_items="center", gap=6, padding_left=6)[
                text("NOISE", color=UI_TEXT_COLOR, font_weight="bold", font_size=16),
                svg()[
                    circle(cx=12, cy=12, r=7, fill=UI_BACKGROUND_COLOR)
                ],
            ]
        ],
        *[create_mode_header(title, shape, states) for title, _, _, shape, states in columns]
    ]

    DIM_COLOR = "#666666"

    def marked_label(label, color, mark):
        """A label, wearing the mark of the mode it takes you to when it has one."""
        if not mark:
            return text(label, color=color)
        shape, mode = mark
        return div(flex_direction="row", align_items="center", gap=6)[
            svg(width=24)[_icon(mode, shape, 12)],
            text(label, color=color),
        ]

    def create_noise_row(noise: str):
        labels = [normal.get(noise, "") for _, normal, _, _, _ in columns]
        inits = [init.get(noise) for _, _, init, _, _ in columns]

        def cell_for_mode(idx):
            label = labels[idx]
            is_same_as_prev = idx > 0 and label == labels[idx - 1]
            color = DIM_COLOR if is_same_as_prev else UI_TEXT_COLOR
            mark = None if is_same_as_prev else MODE_LABELS.get(label)
            body = marked_label(label, color, mark)
            entry = inits[idx]
            if entry:
                window, init_label = entry
                body = div(flex_direction="column", gap=2)[
                    body,
                    div(flex_direction="row", align_items="center", gap=6)[
                        text(f"{window}ms", color=INIT_COLOR, font_size=13),
                        marked_label(init_label, INIT_COLOR, MODE_LABELS.get(init_label)),
                    ],
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
        if any(normal.get(noise) or init.get(noise) for _, normal, init, _, _ in columns)
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

def cheatsheet_show():
    actions.user.ui_elements_show(cheatsheet_ui, show_hints=False)


def cheatsheet_hide():
    actions.user.ui_elements_hide(cheatsheet_ui)


def show_cheatsheet():
    """The voice command and the hub tile open the same thing. Going through
    the stack is what makes tut back out of it, like every other menu."""
    if menu_current() == "cheatsheet":
        menu_back()
    else:
        menu_open("cheatsheet")


menu_register("cheatsheet", cheatsheet_show, cheatsheet_hide)
