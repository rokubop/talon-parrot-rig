from talon import actions
from .picker import footer, now_line, panel, section, tile
from ..src.anchor import anchors
from ..src.menu import menu_back, menu_register
from ..src.profiles import (
    PROFILE_SLOTS, profile_active, profile_is_locked, profile_names,
)
from ..src.settings_menu import (
    setting_maps, setting_label, setting_title, setting_number_text, is_numeric,
)
from ..parrot_rig_settings import (
    PICKER_HEADER_COLOR, PICKER_PADDING, PICKER_PANEL_COLOR, PICKER_RADIUS,
    PICKER_TITLE_BAR_COLOR,
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


def _legend(mode: str) -> dict:
    """Noise per label, straight from the input map, so a remapped noise shows
    up here without this file knowing any noise names."""
    try:
        legend = actions.user.input_map_channel_get_legend("parrot_rig", mode=mode)
    except Exception:
        return {}
    return {label: noise for noise, label in legend.items()}


def _back_noise(mode: str) -> str:
    try:
        legend = actions.user.input_map_channel_get_legend("parrot_rig", mode=mode)
    except Exception:
        return ""
    return ", ".join(noise for noise, label in legend.items() if label == "back")


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
    if name == "utility_1":
        from ..src.utility import utility_label
        return utility_label()
    return ""


def _make_menu_list(window_id: str, menu: str, title: str, menus_fn, back_label: str):
    """A menu whose tiles open other menus."""
    def menu_list_ui(props):
        from ..parrot_rig_actions import menu_opener
        noises, titles = _noises(), _titles()

        tiles = [
            tile(
                titles.get(name, name),
                noise=noises[i] if i < len(noises) else "",
                value=menu_value(name),
                on_click=lambda _e, n=name: menu_opener(n)(),
            )
            for i, name in enumerate(menus_fn())
        ]

        return panel(window_id, title, [
            section(None, tiles),
            footer([tile(back_label, noise=_back_noise(f"{menu}_select"),
                         exit=True, on_click=lambda _e: menu_back())]),
        ])

    menu_list_ui.__qualname__ = f"{window_id}_ui"
    menu_list_ui.__name__ = menu_list_ui.__qualname__
    return menu_list_ui


def _hub_menus():
    from ..parrot_rig_actions import HUB_MENUS
    return HUB_MENUS


def _speed_menus():
    from ..parrot_rig_actions import SPEED_MENUS
    return SPEED_MENUS


hub_ui = _make_menu_list("settings_hub", "hub", "Settings", _hub_menus, "Close")
speeds_ui = _make_menu_list("speeds_menu", "speeds", "Speeds", _speed_menus, "Back")


def profiles_ui(props):
    from ..parrot_rig_actions import _profile_slot, _profile_save_current
    noises = _noises()
    saved = profile_names()
    current = profile_active()

    tiles = [
        tile(
            name,
            noise=noises[i] if i < len(noises) else "",
            value="locked" if profile_is_locked(name) else None,
            selected=name == current,
            on_click=lambda _e, i=i: _profile_slot(i),
        )
        for i, name in enumerate(saved[:PROFILE_SLOTS])
    ]

    next_free = len(saved)
    if next_free < min(PROFILE_SLOTS, len(noises)):
        tiles.append(tile("Save here", noise=noises[next_free], value="new",
                          on_click=lambda _e, i=next_free: _profile_slot(i)))

    overwrite = []
    if not profile_is_locked(current):
        overwrite = [tile(f"Overwrite {current}",
                          noise=_legend("profiles_select").get("overwrite active", ""),
                          on_click=lambda _e: _profile_save_current())]

    return panel("profiles_menu", "Profiles", [
        now_line(current, "Active"),
        section(None, tiles),
        footer(overwrite + [tile("Back", noise=_back_noise("profiles_select"),
                                 exit=True, on_click=lambda _e: menu_back())]),
    ])


def anchor_kind_ui(props):
    from ..parrot_rig_actions import ANCHOR_KINDS, _anchor_kind
    noises = _noises()

    tiles = [
        tile(label, noise=noises[i] if i < len(noises) else "",
             on_click=lambda _e, k=kind: _anchor_kind(k))
        for i, (kind, label) in enumerate(ANCHOR_KINDS)
    ]

    return panel("anchor_kind", "Anchor", [
        section(None, tiles),
        footer([tile("Keep point", noise=_back_noise("anchor_kind_select"),
                     exit=True, on_click=lambda _e: menu_back())]),
    ])


def _form_panel(window_id, title, prompt, input_id, on_submit):
    """The two menus that take typing rather than a pick. Same backdrop, but a
    field instead of tiles, because a name and a number are not a known set."""
    screen, window = actions.user.ui_elements(["screen", "window"])
    div, text = actions.user.ui_elements(["div", "text"])
    form, input_text, button = actions.user.ui_elements(["form", "input_text", "button"])

    return screen(justify_content="center", align_items="center")[
        window(id=window_id, title=title, padding=0,
               background_color=PICKER_PANEL_COLOR,
               title_bar_style={"background_color": PICKER_TITLE_BAR_COLOR},
               border_radius=PICKER_RADIUS, border_width=0)[
            form(on_submit=on_submit)[
                div(padding=PICKER_PADDING, gap=12, min_width=320)[
                    text(prompt, color=PICKER_HEADER_COLOR, font_size=13),
                    input_text(id=input_id, autofocus=True),
                    div(flex_direction="row", gap=8, justify_content="flex_end")[
                        button("Save", type="submit"),
                        button("Cancel", on_click=lambda e: menu_back()),
                    ],
                ]
            ]
        ]
    ]


def profile_name_ui(props):
    def on_submit(event):
        from ..parrot_rig_actions import _profile_name_submit
        _profile_name_submit(event.data.get("profile_name", ""))

    return _form_panel("profile_name", "Save profile",
                       "Name this profile, enter to save",
                       "profile_name", on_submit)


def setting_custom_ui(props):
    name = custom_pending()
    title = setting_title(name) if name else "Custom"
    current = setting_number_text(name) if name else ""

    def on_submit(event):
        from ..parrot_rig_actions import _setting_custom_submit
        _setting_custom_submit(event.data.get("setting_custom", ""))

    return _form_panel("setting_custom", f"{title} custom",
                       f"Currently {current}. Enter a number.",
                       "setting_custom", on_submit)


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


def show_anchor_kind():
    actions.user.ui_elements_show(anchor_kind_ui, show_hints=False)


def hide_anchor_kind():
    actions.user.ui_elements_hide(anchor_kind_ui)


menu_register("hub", show_hub, hide_hub)
menu_register("speeds", show_speeds, hide_speeds)
menu_register("anchor_kind", show_anchor_kind, hide_anchor_kind)
menu_register("profiles", show_profiles, hide_profiles)
menu_register("profile_name", show_profile_name, hide_profile_name)
menu_register("setting_custom", show_setting_custom, hide_setting_custom)
