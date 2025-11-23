from talon import actions
from ..user_settings import UTILITY_ACTIONS
from ..src.events import event_manager

def create_action_button(action_key: str, action_name: str):
    state, button, text = actions.user.ui_elements(["state", "button", "text"])
    current_action, set_current_action = state.use("utility_action", "hold_click")
    is_selected = current_action == action_key
    bg_color = "#3E84DA" if is_selected else "#4A4A4A"

    return button(
        padding=8,
        border_width=1,
        border_radius=4,
        background_color=bg_color,
        on_click=lambda: [
            event_manager.set_setting("utility_action", action_key),
            set_current_action(action_key)
        ]
    )[
        text(action_name, color="#FFFFFF", font_weight="bold" if is_selected else "normal")
    ]

def utility_selector():
    screen, window, div = actions.user.ui_elements(["screen", "window", "div"])

    return screen(justify_content="center", align_items="center")[
        window(
            id="utility_selector",
            title="Utility Selector",
            padding=16,
        )[
            div(flex_direction="column", gap=10)[
                div(flex_direction="column", gap=5)[
                    *[create_action_button(key, name) for key, name in UTILITY_ACTIONS.items()]
                ]
            ]
        ]
    ]

def show_utility_selector():
    actions.user.ui_elements_toggle(utility_selector, show_hints="numbers")
