from talon import actions, Module
from .config import MODE_COLORS, MODE_CODES, MODIFIER_COLORS, UTILITY_ACTIONS
from .events import event_manager

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
            actions.user.parrot_v7_set_utility_action(key)
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

    from .config import SETTINGS_OPTIONS

    def create_setting_row(setting_name: str, label: str, options: list):
        def create_option_button(index: int, value):
            def on_click():
                actions.user.parrot_v7_update_setting(setting_name, index)
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
    screen, div, text, table, tr, td = actions.user.ui_elements(["screen", "div", "text", "table", "tr", "td"])

    current_mode = event_manager.get_mode()
    mode_config = actions.user.parrot_config().get(current_mode, {})

    def create_noise_row(noise: str, description: str):
        return tr()[
            td(padding=8, border_width=1, border_color="#666666")[
                text(noise, color="#FFFFFF", font_family="monospace")
            ],
            td(padding=8, border_width=1, border_color="#666666")[
                text(description, color="#FFFFFF")
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
            # max_width=600,
            # max_height=400,
            # overflow="auto",
        )[
            text(f"Noise Reference - {current_mode.upper()} Mode",
                 font_size=16, font_weight="bold", color="#FFFFFF", margin_bottom=20),
            table(
                width="100%",
                border_collapse="collapse",
            )[
                *[create_noise_row(noise, desc[0]) for noise, desc in mode_config.items()]
            ]
        ]
    ]

@mod.action_class
class Actions:
    def parrot_v7_show_hud():
        """Show the parrot HUD with the current mode, color, code, and modifiers"""
        actions.user.ui_elements_show(parrot_hud)

    def parrot_v7_hide_hud():
        """Hide the parrot HUD"""
        actions.user.ui_elements_hide_all()

    def parrot_v7_ui_utility_selector():
        """Show utility selector UI"""
        actions.user.ui_elements_show(utility_selector)

    def parrot_v7_ui_settings():
        """Show settings UI"""
        actions.user.ui_elements_show(settings_ui)

    def parrot_v7_ui_noise_reference():
        """Show noise reference UI"""
        actions.user.ui_elements_show(noise_reference)

    def parrot_v7_set_utility_action(action: str):
        """Set the utility action"""
        from . import config
        config.UTILITY_ACTION = action

    def parrot_v7_update_setting(setting_name: str, value_index: int):
        """Update a setting value"""
        from .src.movement import movement
        from .config import FULL_MODE_SETTINGS

        if setting_name == "speed":
            movement.update_speed(value_index)
        elif setting_name == "boost_small":
            movement.update_boost_small(value_index)
        elif setting_name == "boost_large":
            movement.update_boost_large(value_index)
        elif setting_name == "stop_time":
            from .config import SETTINGS_OPTIONS
            if 0 <= value_index < len(SETTINGS_OPTIONS["stop_time"]):
                FULL_MODE_SETTINGS["stop_time"] = SETTINGS_OPTIONS["stop_time"][value_index]
