from talon import actions
from ..parrot_rig_actions import utility_maps
from ..parrot_rig_settings import (
    UI_BORDER_COLOR, UI_BACKGROUND_COLOR, UI_TEXT_COLOR, UI_SELECTED_COLOR,
)

def _make_selector(name: str, util_map: dict):
    def selector_ui(props):
        screen, window = actions.user.ui_elements(["screen", "window"])
        table, tr, td, th = actions.user.ui_elements(["table", "tr", "td", "th"])
        text, state = actions.user.ui_elements(["text", "state"])

        title = props.get("title", name)
        legend = actions.user.input_map_channel_get_legend("parrot_rig", mode=f"{name}_select")
        try:
            current_mode = actions.user.input_map_single_mode_get(name)
        except (ValueError, KeyError):
            current_mode = next(iter(util_map))
        keys = list(util_map.keys())

        noise_list = list(legend.keys())

        header_row = tr()[
            th(padding=8, border_width=1, border_color=UI_BORDER_COLOR, background_color=UI_BACKGROUND_COLOR, min_width=80)[
                text("Noise", color=UI_TEXT_COLOR, font_weight="bold", font_size=12)
            ],
            th(padding=8, border_width=1, border_color=UI_BORDER_COLOR, background_color=UI_BACKGROUND_COLOR, min_width=120)[
                text(title, color=UI_TEXT_COLOR, font_weight="bold", font_size=12)
            ],
        ]

        cancel_noises = [k for k, v in legend.items() if v == "back"]
        selector_noises = [k for k, v in legend.items() if v != "back"]

        rows = []
        for i, key in enumerate(keys):
            label = util_map[key][0]
            noise = selector_noises[i] if i < len(selector_noises) else ""
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

        cancel_label = ", ".join(cancel_noises) if cancel_noises else ""
        cancel_row = tr()[
            td(padding=8, border_width=1, border_color=UI_BORDER_COLOR, background_color="#8B0000")[
                text(cancel_label, color=UI_TEXT_COLOR, font_family="monospace", font_weight="bold")
            ],
            td(padding=8, border_width=1, border_color=UI_BORDER_COLOR, background_color="#8B0000")[
                text("Cancel", color=UI_TEXT_COLOR, font_weight="bold")
            ],
        ]

        return screen(justify_content="center", align_items="center")[
            window(
                id=f"{name}_selector",
                title=title,
                padding=0,
            )[
                table(width="100%")[
                    header_row,
                    *rows,
                    cancel_row,
                ]
            ]
        ]
    return selector_ui

_selectors = {name: _make_selector(name, util_map) for name, util_map in utility_maps.items()}

def _on_unmount():
    from ..src.events import event_manager
    event_manager.return_to_previous_mode()

def show_utility_selector(name: str, title: str = ""):
    actions.user.ui_elements_show(_selectors[name], props={"title": title or name}, show_hints=False, on_unmount=_on_unmount)

def hide_utility_selector(name: str):
    actions.user.ui_elements_hide(_selectors[name])

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
