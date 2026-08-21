from talon import Module, actions, ctrl
from .src.parrot_actions import parrot_actions
from .src.events import event_manager
from .parrot_rig_settings import CLICK_HOLD_MS
from .src.select import utility_input_maps
from .src.settings_menu import (
    setting_maps, setting_set, setting_label, setting_title, SETTING_TITLES,
    setting_set_custom, setting_number_text, is_numeric,
)
from .src.menu import menu_open, menu_back, menu_close
from .src.profiles import (
    PROFILE_SLOTS, profile_active, profile_delete, profile_load,
    profile_names, profile_save,
)

mod = Module()
mod.mode("parrot_rig", "parrot rig")


def setting_summary(name: str) -> str:
    """Label, plus the number behind it when there is one."""
    if is_numeric(name):
        return f"{setting_label(name)} {setting_number_text(name)}"
    return setting_label(name)

CHANNEL = "parrot_rig"

# Noises that pick slot 1, 2, 3... in any selector menu. The exit noise is
# absent on purpose, so it never doubles as a selector.
EXIT_NOISE = "cluck"
SELECT_NOISES = ["ah", "oh", "t", "guh", "eh", "mm", "pop", "ee", "hiss", "shush"]

HUB_MENUS = [
    "click_freeze", "speeds", "move_mode", "alt_mode",
    "anchor_move", "return_fallback", "utility_1", "profiles",
]

SPEED_MENUS = ["move_speed", "turn_speed", "scroll_speed", "canvas_move_speed",
               "canvas_scale_speed", "boost_power"]

# A line anchor pins one coordinate and leaves the other alone, so return lands
# on the closest point of the line rather than one spot.
ANCHOR_KINDS = [
    ("point", "Point"),
    ("vertical", "Vertical Line"),
    ("horizontal", "Horizontal Line"),
]

MENU_TITLES = {
    **SETTING_TITLES,
    "utility_1": "Palate",
    "profiles": "Profiles",
    "speeds": "Speeds",
}

# Wiring the input map and the UI call directly. The public surface is the
# action class at the bottom; everything here used to be an action for no
# reason other than being reachable from a dict.

def _settings_menu():
    menu_open("hub")


def _anchor_chase_open() -> bool:
    """Open the anchor kind picker if an anchor was just dropped. True if it did"""
    from .src.anchor import anchor_hold
    if not anchor_hold():
        return False
    menu_open("anchor_kind")
    return True


def _anchor_kind(kind: str):
    from .src.anchor import anchor_set_kind
    from .ui.utility_selector import show_utility_notification
    anchor_set_kind(kind)
    show_utility_notification("Anchor", dict(ANCHOR_KINDS).get(kind, kind).lower())
    menu_back()


def _anchor_clear_all():
    from .src.anchor import anchor_clear_all
    from .ui.utility_selector import show_utility_notification
    anchor_clear_all()
    show_utility_notification("Anchor", "cleared all")


def _setting_custom_prompt(name: str):
    from .ui.settings_hub import set_custom_pending
    set_custom_pending(name)
    menu_open("setting_custom")


def _setting_custom_submit(text: str):
    """Store a typed number for the pending setting"""
    from .ui.settings_hub import custom_pending
    from .ui.utility_selector import show_utility_notification
    name = custom_pending()
    if not name:
        return
    try:
        number = float((text or "").strip())
    except ValueError:
        show_utility_notification(setting_title(name), "not a number")
        return
    setting_set_custom(name, number)
    menu_back()
    show_utility_notification(setting_title(name), setting_summary(name))


def _profile_slot(slot: int):
    """Load the profile in a slot, or name a new one if it is the next free slot"""
    from .ui.utility_selector import show_utility_notification
    names = profile_names()
    if slot == len(names):
        _profile_name_prompt()
        return
    if slot > len(names):
        return
    profile_load(names[slot])
    show_utility_notification("Profile", names[slot])
    menu_back()


def _profile_save_current():
    """Save to the active profile, or prompt for a name if it is locked"""
    from .ui.utility_selector import show_utility_notification
    name = profile_active()
    if not profile_save(name):
        _profile_name_prompt()
        return
    show_utility_notification("Profile", f"saved {name}")


def _profile_name_prompt():
    menu_open("profile_name")


def _profile_name_submit(name: str):
    """Save under the typed name and return to the profiles menu"""
    from .ui.utility_selector import show_utility_notification
    name = (name or "").strip()
    if not name:
        return
    if not profile_save(name):
        show_utility_notification("Profile", f"{name} is locked")
        return
    menu_back()
    show_utility_notification("Profile", f"saved {name}")


# Settings rows that run something instead of setting a value, keyed by the
# name stored in setting_maps.
SETTING_ACTIONS = {
    "anchor_clear_all": _anchor_clear_all,
}


def _anchor_chase(action):
    """Right after dropping an anchor, this noise picks its kind instead."""
    return lambda: None if _anchor_chase_open() else action()


# Last input that fired. Input map announces every one, so repeating is
# looking that key back up and calling what it holds.
_last_input = None


def _on_input(event):
    global _last_input
    if event.type != "input" or event.label in ("", "repeat last"):
        return
    _last_input = (event.mode, event.input)


def _repeat_last():
    if not _last_input:
        return
    mode, key = _last_input
    entries = input_map.get(mode) or {}
    # Keys carry their throttle and debounce suffixes, the event does not
    entry = next((v for k, v in entries.items() if k.split(":")[0] == key), None)
    if entry:
        entry[1]()


input_map_common = {
    "ee":     ("stop / reset", parrot_actions.stop_or_reset),
    "mm":     ("click", actions.user.parrot_rig_click),
    "pop":    ("return", parrot_actions.return_action),
    "ah":     ("move left", lambda: actions.user.parrot_rig_move("left")),
    "oh":     ("move right", lambda: actions.user.parrot_rig_move("right")),
    "t":      ("move up", lambda: actions.user.parrot_rig_move("up")),
    "guh":    ("move down", lambda: actions.user.parrot_rig_move("down")),
    "eh":     ("track", parrot_actions.tracking_activate),
    "er":     ("mode swap", parrot_actions.alt_mode_toggle),
    "palate": ("utility_1", lambda: actions.user.parrot_rig_utility("utility_1")),
    EXIT_NOISE: ("exit", actions.user.parrot_rig_exit),
    "tut":        ("cancel / exit", parrot_actions.cancel),
    "tut tut":    ("exit", actions.user.parrot_rig_exit),
    "tut eh":     ("window pick", lambda: parrot_actions.alt_mode_open("window_pick")),
    "tut ee":     ("window control", lambda: parrot_actions.alt_mode_open("window_control")),
    "tut ah":     ("toggle alt", lambda: parrot_actions.toggle_modifier("alt")),
    "tut t":      ("toggle shift", lambda: parrot_actions.toggle_modifier("shift")),
    "tut guh":    ("toggle ctrl", lambda: parrot_actions.toggle_modifier("ctrl")),
    "tut pop":    ("anchor set / clear", parrot_actions.toggle_anchor),
    "tut shush":  ("canvas scroll", lambda: parrot_actions.alt_mode_open("canvas_scroll")),
    "tut hiss":   ("canvas scale", lambda: parrot_actions.alt_mode_open("canvas_scale")),
    "tut mm":     ("canvas drag", lambda: parrot_actions.alt_mode_open("canvas_drag")),
    "tut oh":     ("right click", lambda: actions.user.parrot_rig_click(1)),
    "tut palate": ("settings", _settings_menu),
}

input_map_default = {
    **input_map_common,
    "hiss":              ("scroll down", lambda: parrot_actions.scroll("down")),
    "hiss_stop:db_170":  ("", parrot_actions.scroll_stop),
    "shush":             ("scroll up", _anchor_chase(lambda: parrot_actions.scroll("up"))),
    "shush_stop:db_170": ("", parrot_actions.scroll_stop),
}

input_map_move = {
    **input_map_common,
    "ah":         ("move left / slow", lambda: parrot_actions.mouse_move_or_slow_dir("left")),
    "oh":         ("move right / slow", lambda: parrot_actions.mouse_move_or_slow_dir("right")),
    "t":          ("move up / slow", lambda: parrot_actions.mouse_move_or_slow_dir("up")),
    "guh":        ("move down / slow", lambda: parrot_actions.mouse_move_or_slow_dir("down")),
    "eh":         ("glide / lock turn", parrot_actions.mouse_toggle_glide),
    "mm":         ("click", actions.user.parrot_rig_click),
    "shush":      ("boost", _anchor_chase(parrot_actions.mouse_boost_long)),
    "shush_stop": ("", lambda: None),
    "hiss":            ("burst / brake", parrot_actions.mouse_burst_or_brake),
    "hiss_stop:db_50": ("", parrot_actions.mouse_burst_or_brake_stop),
}

input_map_tracking = {
    **input_map_common,
    "mm":                ("click (pause)", actions.user.parrot_rig_click),
    "hiss":              ("scroll down (pause)", lambda: parrot_actions.scroll("down")),
    "hiss_stop:db_170":  ("", parrot_actions.scroll_stop_temp),
    "shush":             ("scroll up (pause)", _anchor_chase(lambda: parrot_actions.scroll("up"))),
    "shush_stop:db_170": ("", parrot_actions.scroll_stop_temp),
}

input_map_canvas_stop = {
    **input_map_common,
    "ah":     ("canvas left", lambda: parrot_actions.canvas_move_dir("left")),
    "oh":     ("canvas right", lambda: parrot_actions.canvas_move_dir("right")),
    "t":      ("canvas up", lambda: parrot_actions.canvas_move_dir("up")),
    "guh":    ("canvas down", lambda: parrot_actions.canvas_move_dir("down")),
    "eh":     ("canvas track", parrot_actions.canvas_tracking_activate),
    "shush":      ("canvas resume", _anchor_chase(parrot_actions.canvas_resume)),
    "shush_stop": ("", lambda: None),
    "hiss":       ("canvas resume", parrot_actions.canvas_resume),
    "hiss_stop":  ("", lambda: None),
}

input_map_canvas_move = {
    **input_map_common,
    "ah":         ("canvas left / slow", lambda: parrot_actions.canvas_move_or_slow_dir("left")),
    "oh":         ("canvas right / slow", lambda: parrot_actions.canvas_move_or_slow_dir("right")),
    "t":          ("canvas up / slow", lambda: parrot_actions.canvas_move_or_slow_dir("up")),
    "guh":        ("canvas down / slow", lambda: parrot_actions.canvas_move_or_slow_dir("down")),
    "eh":         ("canvas glide", parrot_actions.canvas_toggle_glide),
    "ee":         ("canvas stop / reset",
                   lambda: parrot_actions.stop_or_reset(parrot_actions.canvas_stop)),
    "mm":         ("click", actions.user.parrot_rig_click),
    "shush":      ("canvas boost", _anchor_chase(parrot_actions.canvas_boost_long)),
    "shush_stop": ("", lambda: None),
    "hiss":            ("canvas burst / brake", parrot_actions.canvas_burst_or_brake),
    "hiss_stop:db_50": ("", parrot_actions.canvas_burst_or_brake_stop),
}

# Tracking stays live here, because the app picker is an overlay you aim at.
input_map_window = {
    **input_map_common,
    "ah":     ("window left", lambda: parrot_actions.window_move("left")),
    "oh":     ("window right", lambda: parrot_actions.window_move("right")),
    "t":      ("window up", lambda: parrot_actions.window_move("up")),
    "guh":    ("window down", lambda: parrot_actions.window_move("down")),
    "eh":     ("app picker", parrot_actions.window_picker),
    "pop":    ("alt tab", parrot_actions.window_alt_tab),
    "ee":     ("escape", parrot_actions.window_escape),
    "palate": ("repeat last", lambda: _repeat_last()),
    "shush:th_90": ("next tab", lambda: parrot_actions.window_key("tab_next")),
    "hiss:th_90":  ("previous tab", lambda: parrot_actions.window_key("tab_prev")),
    "tut pop":   ("close window", lambda: parrot_actions.window_key("close")),
    "tut t":     ("close tab", lambda: parrot_actions.window_key("tab_close")),
    "tut ah":    ("screen left", lambda: parrot_actions.window_move("screen_left")),
    "tut oh":    ("screen right", lambda: parrot_actions.window_move("screen_right")),
}

# Three pairs, one modifier each, both ways on the vertical wheel. No axis to
# choose, because that is the only wheel apps read for these gestures. Tracking
# keeps its own noise here, since it aims the zoom.
input_map_canvas_scale = {
    **input_map_common,
    "oh":     ("alt up", lambda: parrot_actions.canvas_scale_dir("alt", "up")),
    "ah":     ("alt down", lambda: parrot_actions.canvas_scale_dir("alt", "down")),
    "t":      ("ctrl up", lambda: parrot_actions.canvas_scale_dir("ctrl", "up")),
    "guh":    ("ctrl down", lambda: parrot_actions.canvas_scale_dir("ctrl", "down")),
    "pop":    ("shift up", lambda: parrot_actions.canvas_scale_dir("shift", "up")),
    "mm":     ("shift down", lambda: parrot_actions.canvas_scale_dir("shift", "down")),
    "palate": ("scale step", parrot_actions.canvas_scale_step),
    "ee":     ("stop",
               lambda: parrot_actions.stop_or_reset(parrot_actions.canvas_scale_stop)),
    "shush":             ("boost / scale up", _anchor_chase(parrot_actions.canvas_scale_boost)),
    "shush_stop":        ("", lambda: None),
    "hiss":              ("burst / scale down", parrot_actions.canvas_scale_burst_or_brake),
    "hiss_stop:db_50":   ("", parrot_actions.canvas_scale_burst_or_brake_stop),
}

input_map_canvas_tracking = {
    **input_map_canvas_stop,
    "ee":         ("canvas stop / reset",
                   lambda: parrot_actions.stop_or_reset(parrot_actions.canvas_stop)),
    "mm":         ("click (pause)", actions.user.parrot_rig_click),
}

utility_maps = {
    "utility_1": {
        "hold_click":       ("Hold Click",       lambda: actions.user.parrot_rig_click(0, True)),
        "click":            ("Click",            lambda: actions.user.parrot_rig_click(0)),
        "right_click":      ("Right Click",      lambda: actions.user.parrot_rig_click(1)),
        "hold_right_click": ("Hold Right Click", lambda: actions.user.parrot_rig_click(1, True)),
        "middle_click":     ("Middle Click",     lambda: actions.user.parrot_rig_click(2)),
        "middle_hold":      ("Middle Hold",      lambda: actions.user.parrot_rig_click(2, True)),
        "repeat_last":      ("Repeat Last",      lambda: actions.core.repeat_command()),
        "repeat_phrase":    ("Repeat Phrase",    lambda: actions.user.parrot_rig_repeat_phrase()),
    },
}

def _menu_list_input_map(names, back_label="back"):
    """Input map for a menu whose rows open other menus."""
    mode = {}
    for i, name in enumerate(names):
        if i < len(SELECT_NOISES):
            mode[SELECT_NOISES[i]] = (
                MENU_TITLES.get(name, name),
                lambda n=name: menu_open(n),
            )
    mode["tut"] = (back_label, menu_back)
    mode[EXIT_NOISE] = ("exit", actions.user.parrot_rig_exit)
    return mode


def _profiles_input_map():
    mode = {}
    for i in range(min(PROFILE_SLOTS, len(SELECT_NOISES))):
        mode[SELECT_NOISES[i]] = (
            f"profile {i + 1}",
            lambda i=i: _profile_slot(i),
        )
    mode["palate"] = ("overwrite active", _profile_save_current)
    mode["tut"] = ("back", menu_back)
    mode[EXIT_NOISE] = ("exit", actions.user.parrot_rig_exit)
    return mode


def _anchor_kind_input_map():
    mode = {}
    for i, (kind, label) in enumerate(ANCHOR_KINDS):
        if i < len(SELECT_NOISES):
            mode[SELECT_NOISES[i]] = (
                label,
                lambda k=kind: _anchor_kind(k),
            )
    mode["tut"] = ("keep point", menu_back)
    mode[EXIT_NOISE] = ("exit", actions.user.parrot_rig_exit)
    return mode


def _typing_input_map():
    # Talking while typing must not fire noises. Only a double tut escapes,
    # and the bare tut is just the combo prefix.
    return {
        "tut": ("", lambda: None),
        "tut tut": ("cancel", menu_back),
    }


input_map = {
    "default": input_map_default,
    "move": input_map_move,
    "tracking": input_map_tracking,
    "canvas_stop": input_map_canvas_stop,
    "canvas_move": input_map_canvas_move,
    "canvas_tracking": input_map_canvas_tracking,
    "canvas_scale": input_map_canvas_scale,
    "window": input_map_window,
    "window_stop": input_map_window,
    "window_move": input_map_window,
    "hub_select": _menu_list_input_map(HUB_MENUS, "close"),
    "speeds_select": _menu_list_input_map(SPEED_MENUS),
    "anchor_kind_select": _anchor_kind_input_map(),
    "profiles_select": _profiles_input_map(),
    "profile_name_select": _typing_input_map(),
    "setting_custom_select": _typing_input_map(),
    **utility_input_maps(
        maps=utility_maps,
        ui_selectors=SELECT_NOISES,
        ui_cancel=["tut"],
        ui_exit=[EXIT_NOISE],
        close=lambda n: menu_back(),
    ),
    **utility_input_maps(
        maps=setting_maps,
        ui_selectors=SELECT_NOISES,
        ui_cancel=["tut"],
        ui_exit=[EXIT_NOISE],
        select=lambda n, i: actions.user.parrot_rig_setting_select(n, i),
        close=lambda n: menu_back(),
    ),
}

def _listen():
    """Reloading leaves the previous module's listener on the channel, and the
    _last_input it fills is the one this module can no longer see."""
    actions.user.input_map_channel_event_unregister(CHANNEL, _on_input)
    actions.user.input_map_channel_event_register(CHANNEL, _on_input)

def channel_init():
    """Register the parrot_rig channel if not already registered."""
    if CHANNEL not in actions.user.input_map_channel_list():
        actions.user.input_map_channel_register(CHANNEL, input_map)
    _listen()

def channel_reset():
    """Unregister and re-register the channel with fresh data."""
    actions.user.input_map_channel_unregister(CHANNEL)
    actions.user.input_map_channel_register(CHANNEL, input_map)
    _listen()

# The channel keeps the map it was registered with, so a reload has to
# re-register. Without this the previous module stays live, with its own state.
try:
    if CHANNEL in actions.user.input_map_channel_list():
        channel_reset()
except Exception:
    pass


@mod.action_class
class Actions:
    def parrot_rig_enable():
        """Enable parrot rig"""
        parrot_actions.parrot_mode_enable()

    def parrot_rig_disable():
        """Disable parrot rig"""
        parrot_actions.parrot_mode_disable()

    def parrot_rig_toggle():
        """Toggle parrot rig"""
        parrot_actions.parrot_mode_toggle()

    def parrot_rig_simple_click():
        """Simple click with hold duration (for use outside parrot mode)"""
        ctrl.mouse_click(button=0, hold=CLICK_HOLD_MS)

    def parrot_rig_click(button: int = 0, hold: bool = False):
        """Mode-aware click. button: 0=left, 1=right, 2=middle"""
        parrot_actions.mouse_click(button=button, hold=hold)

    def parrot_rig_move(direction: str):
        """Move mouse in direction (up/down/left/right)"""
        parrot_actions.mouse_move_dir(direction)

    def parrot_rig_stop():
        """Stop all mouse movement, scrolling, and tracking"""
        parrot_actions.stopper()

    def parrot_rig_exit():
        """Exit parrot mode (tracking-aware)"""
        parrot_actions.exit()

    def parrot_rig_repeat_command():
        """Repeat last command"""
        parrot_actions.repeat_command()

    def parrot_rig_reverse_command():
        """Reverse last command (swaps opposite words and mimics)"""
        parrot_actions.reverse_command()

    def parrot_rig_repeat_phrase():
        """Repeat last phrase"""
        parrot_actions.repeat_phrase()

    def parrot_rig_reverse_phrase():
        """Reverse last phrase (swaps opposite words and mimics)"""
        parrot_actions.reverse_phrase()

    def parrot_rig_get_state():
        """Get parrot rig state"""
        return parrot_actions.parrot_rig_get_state()

    def parrot_rig_reload():
        """Reload parrot rig files"""
        parrot_actions.reload_files()

    def parrot_rig_get_mode():
        """Get current mode (default/move/boost/glide/tracking/canvas_*)"""
        return parrot_actions.parrot_mode_get_mode()

    def parrot_rig_show_help():
        """Show parrot rig cheatsheet"""
        parrot_actions.show_cheatsheet()

    def parrot_rig_utility(name: str):
        """Execute the currently selected utility action"""
        actions.user.input_map_single(name, utility_maps[name])

    def parrot_rig_show_utility_selector(name: str):
        """Show utility selector UI and enter select mode"""
        menu_open(name)

    def parrot_rig_utility_select(name: str, slot: int):
        """Select a utility option by slot index"""
        from .ui.utility_selector import show_utility_notification
        util_map = utility_maps[name]
        keys = list(util_map.keys())
        if slot < len(keys):
            actions.user.input_map_single_mode_set(name, keys[slot], util_map)
            show_utility_notification(MENU_TITLES.get(name, name), util_map[keys[slot]][0])
        menu_back()

    def parrot_rig_setting_get(name: str) -> str:
        """Get the current value of a settings-menu setting"""
        from .src.settings_menu import setting_get
        return setting_get(name)

    def parrot_rig_show_setting_selector(name: str):
        """Show a settings selector UI and enter select mode"""
        menu_open(name)

    def parrot_rig_setting_select(name: str, slot: int):
        """Select a setting value by slot index, or run its action if it has one"""
        from .ui.utility_selector import show_utility_notification
        entries = list(setting_maps[name].items())
        if slot < len(entries):
            key, entry = entries[slot]
            if key == "custom":
                _setting_custom_prompt(name)
                return
            if len(entry) > 1:
                menu_back()
                SETTING_ACTIONS[entry[1]]()
                return
            setting_set(name, key)
            show_utility_notification(setting_title(name), setting_summary(name))
        menu_back()
