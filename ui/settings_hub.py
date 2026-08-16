from talon import actions
from ..src.anchor import anchors
from ..src.menu import menu_register
from ..src.profiles import (
    PROFILE_SLOTS, profile_active, profile_is_locked, profile_names,
)
from ..src.settings_menu import (
    setting_maps, setting_label, setting_title, setting_number_text, is_numeric,
)
from ..parrot_rig_settings import (
    UI_BORDER_COLOR, UI_BACKGROUND_COLOR, UI_TEXT_COLOR, UI_SELECTED_COLOR,
)

_pending_custom = None


def set_custom_pending(name: str):
    global _pending_custom
    _pending_custom = name


def custom_pending():
    return _pending_custom


def _noises():
    from ..parrot_rig_actions import SELECT_NOISES
    return SELECT_NOISES


def _titles():
    from ..parrot_rig_actions import MENU_TITLES
    return MENU_TITLES


def menu_value(name: str) -> str:
    if name == "anchor_move":
        count = len(anchors())
        return f"{setting_label(name)} ({count})" if count else setting_label(name)
    if is_numeric(name):
        return f"{setting_label(name)}  {setting_number_text(name)}"
    if name in setting_maps:
        return setting_label(name)
    if name == "profiles":
        return profile_active()
    if name == "speeds":
        return ""
    from ..parrot_rig_actions import utility_maps
    util_map = utility_maps.get(name)
    if not util_map:
        return ""
    try:
        current = actions.user.input_map_single_mode_get(name)
    except (ValueError, KeyError):
        current = next(iter(util_map))
    return util_map.get(current, ("",))[0]


def _th(text_el, label, min_width):
    th = actions.user.ui_elements(["th"])
    return th(padding=8, border_width=1, border_color=UI_BORDER_COLOR,
              background_color=UI_BACKGROUND_COLOR, min_width=min_width)[
        text_el(label, color=UI_TEXT_COLOR, font_weight="bold", font_size=12)
    ]


def _noise_cell(td, text_el, noise):
    return td(padding=8, border_width=1, border_color=UI_BORDER_COLOR)[
        text_el(noise, color=UI_TEXT_COLOR, font_family="monospace")
    ]


def _back_row(tr, td, text_el, label):
    return tr()[
        td(padding=8, border_width=1, border_color=UI_BORDER_COLOR, background_color="#8B0000")[
            text_el("tut", color=UI_TEXT_COLOR, font_family="monospace", font_weight="bold")
        ],
        td(padding=8, border_width=1, border_color=UI_BORDER_COLOR, background_color="#8B0000")[
            text_el(label, color=UI_TEXT_COLOR, font_weight="bold")
        ],
        td(padding=8, border_width=1, border_color=UI_BORDER_COLOR, background_color="#8B0000")[
            text_el("", color=UI_TEXT_COLOR)
        ],
    ]


def _make_menu_list(window_id: str, title: str, menus_fn, back_label: str):
    """A menu whose rows open other menus."""
    def menu_list_ui(props):
        screen, window = actions.user.ui_elements(["screen", "window"])
        table, tr, td = actions.user.ui_elements(["table", "tr", "td"])
        text = actions.user.ui_elements(["text"])
        noises, titles = _noises(), _titles()

        rows = []
        for i, name in enumerate(menus_fn()):
            noise = noises[i] if i < len(noises) else ""
            rows.append(tr()[
                _noise_cell(td, text, noise),
                td(padding=8, border_width=1, border_color=UI_BORDER_COLOR)[
                    text(titles.get(name, name), color=UI_TEXT_COLOR, font_weight="bold")
                ],
                td(padding=8, border_width=1, border_color=UI_BORDER_COLOR)[
                    text(menu_value(name), color=UI_TEXT_COLOR)
                ],
            ])

        return screen(justify_content="center", align_items="center")[
            window(id=window_id, title=title, padding=0)[
                table(width="100%")[
                    tr()[
                        _th(text, "Noise", 80),
                        _th(text, "Setting", 120),
                        _th(text, "Value", 140),
                    ],
                    *rows,
                    _back_row(tr, td, text, back_label),
                ]
            ]
        ]

    menu_list_ui.__qualname__ = f"{window_id}_ui"
    menu_list_ui.__name__ = menu_list_ui.__qualname__
    return menu_list_ui


def _hub_menus():
    from ..parrot_rig_actions import HUB_MENUS
    return HUB_MENUS


def _speed_menus():
    from ..parrot_rig_actions import SPEED_MENUS
    return SPEED_MENUS


hub_ui = _make_menu_list("settings_hub", "Settings (tut palate)", _hub_menus, "Close")
speeds_ui = _make_menu_list("speeds_menu", "Speeds", _speed_menus, "Back")


def profiles_ui(props):
    screen, window = actions.user.ui_elements(["screen", "window"])
    table, tr, td = actions.user.ui_elements(["table", "tr", "td"])
    text = actions.user.ui_elements(["text"])
    noises = _noises()

    saved = profile_names()
    current = profile_active()

    rows = []
    for i, name in enumerate(saved[:PROFILE_SLOTS]):
        is_active = name == current
        rows.append(tr()[
            _noise_cell(td, text, noises[i] if i < len(noises) else ""),
            td(padding=8, border_width=1, border_color=UI_BORDER_COLOR,
               background_color=UI_SELECTED_COLOR if is_active else None)[
                text(f"{name} (locked)" if profile_is_locked(name) else name,
                     color=UI_TEXT_COLOR,
                     font_weight="bold" if is_active else "normal")
            ],
        ])

    next_free = len(saved)
    if next_free < min(PROFILE_SLOTS, len(noises)):
        rows.append(tr()[
            _noise_cell(td, text, noises[next_free]),
            td(padding=8, border_width=1, border_color=UI_BORDER_COLOR)[
                text("save here (new)", color=UI_TEXT_COLOR)
            ],
        ])

    if not profile_is_locked(current):
        rows.append(tr()[
            _noise_cell(td, text, "palate"),
            td(padding=8, border_width=1, border_color=UI_BORDER_COLOR)[
                text(f"overwrite {current}", color=UI_TEXT_COLOR)
            ],
        ])

    return screen(justify_content="center", align_items="center")[
        window(id="profiles_menu", title="Profiles", padding=0)[
            table(width="100%")[
                tr()[
                    _th(text, "Noise", 80),
                    _th(text, "Profile", 180),
                ],
                *rows,
                tr()[
                    td(padding=8, border_width=1, border_color=UI_BORDER_COLOR, background_color="#8B0000")[
                        text("tut", color=UI_TEXT_COLOR, font_family="monospace", font_weight="bold")
                    ],
                    td(padding=8, border_width=1, border_color=UI_BORDER_COLOR, background_color="#8B0000")[
                        text("Back", color=UI_TEXT_COLOR, font_weight="bold")
                    ],
                ],
            ]
        ]
    ]


def profile_name_ui(props):
    screen, window = actions.user.ui_elements(["screen", "window"])
    div, text = actions.user.ui_elements(["div", "text"])
    form, input_text, button = actions.user.ui_elements(["form", "input_text", "button"])

    def on_submit(event):
        actions.user.parrot_rig_profile_name_submit(event.data.get("profile_name", ""))

    return screen(justify_content="center", align_items="center")[
        window(id="profile_name", title="Save profile", padding=0)[
            form(on_submit=on_submit)[
                div(padding=16, gap=12, min_width=280)[
                    text("Name this profile, enter to save", color=UI_TEXT_COLOR),
                    input_text(id="profile_name", autofocus=True),
                    div(flex_direction="row", gap=8, justify_content="flex_end")[
                        button("Save", type="submit"),
                        button("Cancel", on_click=lambda e: actions.user.parrot_rig_menu_back()),
                    ],
                ]
            ]
        ]
    ]


def setting_custom_ui(props):
    screen, window = actions.user.ui_elements(["screen", "window"])
    div, text = actions.user.ui_elements(["div", "text"])
    form, input_text, button = actions.user.ui_elements(["form", "input_text", "button"])

    name = custom_pending()
    title = setting_title(name) if name else "Custom"
    current = setting_number_text(name) if name else ""

    def on_submit(event):
        actions.user.parrot_rig_setting_custom_submit(event.data.get("setting_custom", ""))

    return screen(justify_content="center", align_items="center")[
        window(id="setting_custom", title=f"{title} custom", padding=0)[
            form(on_submit=on_submit)[
                div(padding=16, gap=12, min_width=280)[
                    text(f"Currently {current}. Enter a number.", color=UI_TEXT_COLOR),
                    input_text(id="setting_custom", autofocus=True),
                    div(flex_direction="row", gap=8, justify_content="flex_end")[
                        button("Set", type="submit"),
                        button("Cancel", on_click=lambda e: actions.user.parrot_rig_menu_back()),
                    ],
                ]
            ]
        ]
    ]


def show_setting_custom():
    actions.user.ui_elements_show(setting_custom_ui, show_hints=False)


def hide_setting_custom():
    actions.user.ui_elements_hide(setting_custom_ui)


def show_profile_name():
    actions.user.ui_elements_show(profile_name_ui, show_hints=False)


def hide_profile_name():
    actions.user.ui_elements_hide(profile_name_ui)


def show_hub():
    actions.user.ui_elements_show(hub_ui, show_hints=False)


def hide_hub():
    actions.user.ui_elements_hide(hub_ui)


def show_profiles():
    actions.user.ui_elements_show(profiles_ui, show_hints=False)


def hide_profiles():
    actions.user.ui_elements_hide(profiles_ui)


def show_speeds():
    actions.user.ui_elements_show(speeds_ui, show_hints=False)


def hide_speeds():
    actions.user.ui_elements_hide(speeds_ui)


menu_register("hub", show_hub, hide_hub)
menu_register("speeds", show_speeds, hide_speeds)
menu_register("profiles", show_profiles, hide_profiles)
menu_register("profile_name", show_profile_name, hide_profile_name)
menu_register("setting_custom", show_setting_custom, hide_setting_custom)
