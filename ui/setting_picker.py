from talon import actions
from .picker import footer, now_line, panel, section, tile
from ..src.menu import menu_back, menu_register
from ..src.settings_menu import (
    setting_maps, setting_get, setting_number_text, is_numeric,
)
from ..parrot_rig_settings import (
    PICKER_HEADER_COLOR, PICKER_PANEL_COLOR, PICKER_RADIUS, PICKER_TEXT_COLOR,
)


def _menu_title(name: str) -> str:
    from ..parrot_rig_actions import MENU_TITLES
    return MENU_TITLES.get(name, name)


def _make_selector(name: str, options: dict, get_current):
    def selector_ui(props):
        legend = actions.user.input_map_channel_get_legend(
            "parrot_rig", mode=f"{name}_select")
        current = get_current()
        numeric = is_numeric(name)

        cancel_noises = [k for k, v in legend.items() if v == "back"]
        # By label, not position: a pinned option sits wherever it was pinned,
        # so the legend no longer runs in the same order as the map
        noise_by_label = {v: k for k, v in legend.items() if v != "back"}

        tiles = [
            tile(
                options[key][0],
                noise=noise_by_label.get(options[key][0], ""),
                value=setting_number_text(name, key) if numeric else None,
                selected=key == current,
                on_click=lambda _e, i=i: actions.user.parrot_rig_setting_select(name, i),
            )
            for i, key in enumerate(options)
        ]

        return panel(f"{name}_selector", props.get("title", name), [
            now_line(options[current][0] if current in options else ""),
            section(None, tiles),
            footer([tile("Back", noise=", ".join(cancel_noises), exit=True,
                         on_click=lambda _e: menu_back())]),
        ])
    selector_ui.__qualname__ = f"{name}_selector_ui"
    selector_ui.__name__ = selector_ui.__qualname__
    return selector_ui


# Utility 1 is absent on purpose: it has its own picker, aimed at rather than
# spoken to, so it never becomes one of these noise-per-tile menus.
_selectors = {
    name: _make_selector(name, options, lambda n=name: setting_get(n))
    for name, options in setting_maps.items()
}


def show_setting_picker(name: str, title: str = ""):
    actions.user.ui_elements_show(
        _selectors[name], props={"title": title or name}, show_hints=False)


def hide_setting_picker(name: str):
    actions.user.ui_elements_hide(_selectors[name])


for _name in _selectors:
    menu_register(
        _name,
        lambda n=_name: show_setting_picker(n, _menu_title(n)),
        lambda n=_name: hide_setting_picker(n),
    )


def _notification(props):
    screen, div = actions.user.ui_elements(["screen", "div"])
    text = actions.user.ui_elements(["text"])
    noise = props.get("noise", "")
    label = props.get("label", "")

    return screen(align_items="center", justify_content="flex_end")[
        div(flex_direction="row", gap=8, align_items="center", padding=14,
            margin_bottom=100, background_color=PICKER_PANEL_COLOR,
            border_radius=PICKER_RADIUS)[
            text(noise, color=PICKER_HEADER_COLOR, font_size=18),
            text(label, color=PICKER_TEXT_COLOR, font_size=18,
                 font_weight="bold"),
        ]
    ]


def show_notification(noise: str, label: str):
    actions.user.ui_elements_show(
        _notification,
        props={"noise": noise, "label": label},
        duration="1500ms",
    )
