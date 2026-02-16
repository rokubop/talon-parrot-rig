from talon import actions
from ..parrot_rig_utilities import utility_map, utility2_map
from ..parrot_rig_settings import (
    UI_BORDER_COLOR, UI_BACKGROUND_COLOR, UI_TEXT_COLOR, UI_SELECTED_COLOR,
)

def _make_selector(name: str, util_map: dict):
    def selector_ui(props):
        screen, window = actions.user.ui_elements(["screen", "window"])
        table, tr, td, th = actions.user.ui_elements(["table", "tr", "td", "th"])
        text, state = actions.user.ui_elements(["text", "state"])

        title = props.get("title", name)
        legend = actions.user.input_map_get_legend(mode=f"{name}_select")
        try:
            current_mode = actions.user.input_map_single_mode_get(name)
        except (ValueError, KeyError):
            current_mode = next(iter(util_map))
        keys = list(util_map.keys())

        noise_list = list(legend.keys())

        header_row = tr()[
            th(padding=8, border_width=1, border_color=UI_BORDER_COLOR, background_color=UI_BACKGROUND_COLOR)[
                text("Noise", color=UI_TEXT_COLOR, font_weight="bold", font_size=12)
            ],
            th(padding=8, border_width=1, border_color=UI_BORDER_COLOR, background_color=UI_BACKGROUND_COLOR)[
                text(title, color=UI_TEXT_COLOR, font_weight="bold", font_size=12)
            ],
        ]

        rows = []
        for i, key in enumerate(keys):
            label = util_map[key][0]
            noise = noise_list[i] if i < len(noise_list) else ""
            is_selected = key == current_mode
            bg = UI_SELECTED_COLOR if is_selected else None

            rows.append(tr()[
                td(padding=8, border_width=1, border_color=UI_BORDER_COLOR)[
                    text(noise, color=UI_TEXT_COLOR, font_family="monospace")
                ],
                td(padding=8, border_width=1, border_color=UI_BORDER_COLOR, background_color=bg)[
                    text(label, color=UI_TEXT_COLOR, font_weight="bold" if is_selected else "normal")
                ],
            ])

        return screen(justify_content="center", align_items="center")[
            window(
                id=f"{name}_selector",
                title=title,
                padding=0,
            )[
                table(width="100%")[
                    header_row,
                    *rows,
                ]
            ]
        ]
    return selector_ui

utility_selector = _make_selector("utility", utility_map)
utility2_selector = _make_selector("utility2", utility2_map)

def show_utility_selector(title: str = "Utility"):
    actions.user.ui_elements_show(utility_selector, props={"title": title}, show_hints=False)

def show_utility2_selector(title: str = "Utility 2"):
    actions.user.ui_elements_show(utility2_selector, props={"title": title}, show_hints=False)

def hide_utility_selector():
    actions.user.ui_elements_hide(utility_selector)

def hide_utility2_selector():
    actions.user.ui_elements_hide(utility2_selector)

def _utility_notification(props):
    screen, div = actions.user.ui_elements(["screen", "div"])
    text = actions.user.ui_elements(["text"])
    noise = props.get("noise", "")
    label = props.get("label", "")

    return screen(align_items="center", justify_content="flex_end")[
        div(padding=12, margin_bottom=100, background_color=UI_SELECTED_COLOR, border_radius=8)[
            text(f"{noise}: {label}", color=UI_TEXT_COLOR, font_size=20, font_weight="bold")
        ]
    ]

def show_utility_notification(noise: str, label: str):
    actions.user.ui_elements_show(
        _utility_notification,
        props={"noise": noise, "label": label},
        duration="1500ms",
    )
