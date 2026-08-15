from talon import actions
from ..src.anchor import anchors
from ..src.menu import menu_register
from ..src.profiles import (
    PROFILE_SLOTS, profile_active, profile_is_locked, profile_names,
)
from ..src.settings_menu import setting_maps, setting_label
from ..parrot_rig_settings import (
    UI_BORDER_COLOR, UI_BACKGROUND_COLOR, UI_TEXT_COLOR, UI_SELECTED_COLOR,
)

def _menus():
    from ..parrot_rig_actions import SELECT_NOISES, HUB_MENUS, MENU_TITLES
    return SELECT_NOISES, HUB_MENUS, MENU_TITLES


def menu_value(name: str) -> str:
    if name == "anchor_move":
        count = len(anchors())
        return f"{setting_label(name)} ({count})" if count else setting_label(name)
    if name in setting_maps:
        return setting_label(name)
    if name == "profiles":
        return profile_active()
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


def hub_ui(props):
    screen, window = actions.user.ui_elements(["screen", "window"])
    table, tr, td = actions.user.ui_elements(["table", "tr", "td"])
    text = actions.user.ui_elements(["text"])
    noises, menus, titles = _menus()

    rows = []
    for i, name in enumerate(menus):
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
        window(id="settings_hub", title="Settings (tut palate)", padding=0)[
            table(width="100%")[
                tr()[
                    _th(text, "Noise", 80),
                    _th(text, "Setting", 120),
                    _th(text, "Value", 140),
                ],
                *rows,
                _back_row(tr, td, text, "Close"),
            ]
        ]
    ]


def profiles_ui(props):
    screen, window = actions.user.ui_elements(["screen", "window"])
    table, tr, td = actions.user.ui_elements(["table", "tr", "td"])
    text = actions.user.ui_elements(["text"])
    noises, _, _ = _menus()

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


menu_register("hub", show_hub, hide_hub)
menu_register("profiles", show_profiles, hide_profiles)
menu_register("profile_name", show_profile_name, hide_profile_name)
