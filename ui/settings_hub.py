from talon import actions
from .picker import footer, now_line, panel, section, tile
from ..src.anchor import anchors
from ..src.events import event_manager
from ..src.menu import menu_back, menu_open, menu_register
from ..src.profiles import (
    PROFILE_SLOTS, profile_active, profile_is_locked, profile_names,
)
from ..src.settings_menu import (
    setting_maps, setting_label, setting_title, setting_number_text, is_numeric,
)
from ..parrot_rig_settings import (
    PICKER_HEADER_COLOR, PICKER_PADDING, PICKER_PANEL_COLOR, PICKER_RADIUS,
    PICKER_TEXT_SIZE, PICKER_TITLE_BAR_COLOR,
)

_pending_custom = None


def set_custom_pending(name: str):
    global _pending_custom
    _pending_custom = name


def custom_pending():
    return _pending_custom


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
    if name == "utility_1":
        from ..src.utility import utility_label
        return utility_label()
    return ""


def _back_tile(label="Back"):
    from ..parrot_rig_actions import CANCEL_NOISE
    return tile(label, noise=CANCEL_NOISE, exit=True,
                on_click=lambda _e: menu_back())


def _make_menu_list(window_id: str, title: str, menus_fn, back_label: str):
    """A menu whose tiles open other menus."""
    def menu_list_ui(props):
        titles = _titles()

        tiles = [
            tile(titles.get(name, name), value=menu_value(name),
                 on_click=lambda _e, n=name: menu_open(n))
            for name in menus_fn()
        ]

        return panel(window_id, title, [
            section(None, tiles),
            footer([_back_tile(back_label)]),
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


hub_ui = _make_menu_list("settings_hub", "Settings", _hub_menus, "Close")
speeds_ui = _make_menu_list("speeds_menu", "Speeds", _speed_menus, "Back")


def profiles_ui(props):
    from ..parrot_rig_actions import _profile_slot, _profile_save_current
    saved = profile_names()
    current = profile_active()

    tiles = [
        tile(
            name,
            value="locked" if profile_is_locked(name) else None,
            selected=name == current,
            on_click=lambda _e, i=i: _profile_slot(i),
        )
        for i, name in enumerate(saved[:PROFILE_SLOTS])
    ]

    next_free = len(saved)
    if next_free < PROFILE_SLOTS:
        tiles.append(tile("Save here", value="new",
                          on_click=lambda _e, i=next_free: _profile_slot(i)))

    overwrite = []
    if not profile_is_locked(current):
        overwrite = [tile(f"Overwrite {current}",
                          on_click=lambda _e: _profile_save_current())]

    return panel("profiles_menu", "Profiles", [
        now_line(current, "Active"),
        section(None, tiles),
        footer(overwrite + [_back_tile()]),
    ])


def anchor_kind_ui(props):
    from ..parrot_rig_actions import ANCHOR_KINDS, _anchor_kind

    tiles = [
        tile(label, on_click=lambda _e, k=kind: _anchor_kind(k))
        for kind, label in ANCHOR_KINDS
    ]

    return panel("anchor_kind", "Anchor", [
        section(None, tiles),
        footer([_back_tile("Keep point")]),
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
                div(padding=PICKER_PADDING, gap=14, min_width=360)[
                    text(prompt, color=PICKER_HEADER_COLOR,
                         font_size=PICKER_TEXT_SIZE),
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


# The only menus that still touch the input mode. A field wants the keyboard,
# and a noise fired mid sentence would move the mouse out from under it, so
# these two suppress every noise but a double tut while they are open.
_typing_return = None


def _typing_enter(mode: str):
    global _typing_return
    _typing_return = event_manager.get_mode()
    event_manager.set_mode(mode)


def _typing_leave():
    global _typing_return
    if _typing_return is not None:
        event_manager.set_mode(_typing_return)
        _typing_return = None


def show_setting_custom():
    _typing_enter("setting_custom_select")
    actions.user.ui_elements_show(setting_custom_ui, show_hints=False)


def hide_setting_custom():
    actions.user.ui_elements_hide(setting_custom_ui)
    _typing_leave()


def show_profile_name():
    _typing_enter("profile_name_select")
    actions.user.ui_elements_show(profile_name_ui, show_hints=False)


def hide_profile_name():
    actions.user.ui_elements_hide(profile_name_ui)
    _typing_leave()


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
