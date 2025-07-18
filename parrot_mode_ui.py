from talon import actions, Module
from .config import MODE_COLORS, MODE_CODES, MODIFIER_COLORS, UTILITY_ACTIONS, SETTINGS_OPTIONS, FULL_MODE_SETTINGS
from .events import event_manager
from .src.movement import movement

mod = Module()

def status_mod(mod_name: str):
    """Create a modifier status indicator"""
    text = actions.user.ui_elements(["text"])
    color = MODIFIER_COLORS.get(mod_name, "#666666")
    return text(mod_name[0].upper(), background_color=color, border_radius=4, padding=8)

def mode_circle(color: str, code: str):
    """Create a mode circle indicator"""
    div, text = actions.user.ui_elements(["div", "text"])

    return div(
        align_items="center",
        justify_content="center",
        width=40,
        height=40,
        border_radius=20,
        background_color=color,
        border_width=2,
        border_color="#FFFFFF",
    )[
        text(code, color="#FFFFFF", font_weight="bold", font_size=10)
    ]

def parrot_hud():
    screen, div = actions.user.ui_elements(["screen", "div"])
    state = actions.user.ui_elements(["state"])

    mode = state.get("mode", "default")
    color = MODE_COLORS.get(mode, "#FFFFFF")
    code = MODE_CODES.get(mode, "?")
    modifiers = state.get("modifiers", [])

    modifier_elements = [status_mod(mod) for mod in modifiers if mod in MODIFIER_COLORS]

    return screen()[
        div(
            position="absolute",
            bottom=100,
            right=100,
            flex_direction="row",
            align_items="center",
            gap=8,
            opacity=0.9,
            background_color="#414141",
            border_radius=12,
            border_width=1,
            border_color="#666666",
            padding=12,
        )[
            mode_circle(color, code),
            div(
                flex_direction="row",
                align_items="center",
                gap=4,
                min_width=100,
                padding=4,
                border_radius=4,
                background_color="#3F3F3F",
            )[
                *modifier_elements,
            ] if modifier_elements else None,
        ]
    ]

# Utility selector UI
def utility_selector():
    """Create utility selector UI"""
    screen, div, button, text = actions.user.ui_elements(["screen", "div", "button", "text"])

    def create_utility_button(key: str, label: str):
        def on_click():
            set_utility_action(key)
            actions.user.ui_elements_hide(utility_selector)

        return button(
            padding=12,
            margin=4,
            background_color="#4A90E2",
            color="#FFFFFF",
            border_radius=6,
            border_width=0,
            on_click=on_click,
        )[
            text(label)
        ]

    return screen(justify_content="center", align_items="center")[
        div(
            # position="absolute",
            # top="50%",
            # left="50%",
            # transform="translate(-50%, -50%)",
            background_color="#2D2D2D",
            border_radius=8,
            border_width=2,
            border_color="#666666",
            padding=20,
            min_width=300,
        )[
            text("Select Utility Action", font_size=16, font_weight="bold", color="#FFFFFF", margin_bottom=16),
            div(gap=8)[
                *[create_utility_button(key, label) for key, label in UTILITY_ACTIONS.items()]
            ]
        ]
    ]

# Settings UI
def settings_ui():
    """Create settings UI"""
    screen, div, button, text = actions.user.ui_elements(["screen", "div", "button", "text"])

    def create_setting_row(setting_name: str, label: str, options: list):
        def create_option_button(index: int, value):
            def on_click():
                update_setting(setting_name, index)
                actions.user.ui_elements_hide_all()

            return button(
                padding=8,
                margin=2,
                background_color="#4A90E2",
                color="#FFFFFF",
                border_radius=4,
                border_width=0,
                on_click=on_click,
            )[
                text(str(value))
            ]

        return div(
            flex_direction="column",
            margin_bottom=16,
        )[
            text(label, font_size=14, font_weight="bold", color="#FFFFFF", margin_bottom=8),
            div(
                flex_direction="row",
                gap=4,
            )[
                *[create_option_button(i, val) for i, val in enumerate(options)]
            ]
        ]

    return screen(justify_content="center", align_items="center")[
        div(
            # position="absolute",
            # top="50%",
            # left="50%",
            # transform="translate(-50%, -50%)",
            background_color="#2D2D2D",
            border_radius=8,
            border_width=2,
            border_color="#666666",
            padding=20,
            min_width=400,
        )[
            text("Parrot Mode Settings", font_size=16, font_weight="bold", color="#FFFFFF", margin_bottom=20),
            create_setting_row("speed", "Movement Speed", SETTINGS_OPTIONS["speed"]),
            create_setting_row("boost_small", "Small Boost", SETTINGS_OPTIONS["boost_small"]),
            create_setting_row("boost_large", "Large Boost", SETTINGS_OPTIONS["boost_large"]),
            create_setting_row("stop_time", "Stop Time (seconds)", SETTINGS_OPTIONS["stop_time"]),
        ]
    ]

# Noise reference UI
def noise_reference():
    """Create noise reference UI"""
    screen, div, text, table, tr, td, th = actions.user.ui_elements(["screen", "div", "text", "table", "tr", "td", "th"])
    state = actions.user.ui_elements(["state"])

    all_modes_config = actions.user.parrot_config()
    current_mode = state.get("mode", "default")

    # Get all unique noises across all modes
    all_noises = set()
    for mode_config in all_modes_config.values():
        all_noises.update(mode_config.keys())
    all_noises = sorted(list(all_noises))

    # Create header row with mode names
    header_row = tr()[
        th(padding=8, border_width=1, border_color="#666666", background_color="#4A4A4A")[
            text("Noise", color="#FFFFFF", font_weight="bold", font_size=12)
        ],
        *[th(padding=8, border_width=1, border_color="#666666",
              background_color="#4A90E2" if mode_name == current_mode else "#4A4A4A")[
            text(mode_name.upper(), color="#FFFFFF", font_weight="bold", font_size=12)
        ] for mode_name in all_modes_config.keys()]
    ]

    # Create rows for each noise
    def create_noise_row(noise: str):
        return tr()[
            td(padding=8, border_width=1, border_color="#666666")[
                text(noise, color="#FFFFFF", font_family="monospace")
            ],
            *[td(padding=8, border_width=1, border_color="#666666",
                 background_color="#1A3A5C" if mode_name == current_mode else None)[
                text(mode_config.get(noise, [""])[0], color="#FFFFFF")
            ] for mode_name, mode_config in all_modes_config.items()]
        ]

    noise_rows = [create_noise_row(noise) for noise in all_noises]

    return screen(justify_content="center", align_items="center")[
        div(
            background_color="#2D2D2D",
            border_radius=8,
            border_width=2,
            border_color="#666666",
            padding=20,
        )[
            text(f"Noise Reference - Current Mode: {current_mode.upper()}",
                 font_size=16, font_weight="bold", color="#FFFFFF", margin_bottom=20),
            table(width="100%")[
                header_row,
                *noise_rows
            ]
        ]
    ]

# Direct functions instead of actions class
def show_hud():
    """Show the parrot HUD with the current mode, color, code, and modifiers"""
    actions.user.ui_elements_show(
        parrot_hud,
        on_mount=lambda: event_manager.register_hud_callbacks(show_hud, hide_hud),
        on_unmount=lambda: event_manager.unregister_hud_callbacks()
    )

def hide_hud():
    """Hide the parrot HUD"""
    actions.user.ui_elements_hide_all()

def set_utility_action(action: str):
    """Set the utility action"""
    event_manager.set_setting("utility_action", action)

def update_setting(setting_name: str, value_index: int):
    """Update a setting value"""
    if setting_name == "speed":
        movement.update_speed(value_index)
    elif setting_name == "boost_small":
        movement.update_boost_small(value_index)
    elif setting_name == "boost_large":
        movement.update_boost_large(value_index)
    elif setting_name == "stop_time":
        if 0 <= value_index < len(SETTINGS_OPTIONS["stop_time"]):
            FULL_MODE_SETTINGS["stop_time"] = SETTINGS_OPTIONS["stop_time"][value_index]
