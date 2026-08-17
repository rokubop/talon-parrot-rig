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

# Noises that pick slot 1, 2, 3... in any selector menu
SELECT_NOISES = ["ah", "oh", "t", "guh", "eh", "mm", "pop", "ee", "cluck", "hiss", "shush"]

HUB_MENUS = [
    "click_freeze", "speeds", "move_mode", "canvas_mode", "canvas_scale",
    "anchor_move", "return_fallback", "utility_1", "profiles",
]

SPEED_MENUS = ["move_speed", "turn_speed", "scroll_speed", "canvas_move_speed", "boost_power"]

CANVAS_SCALE_MENUS = ["canvas_scale_y_mod", "canvas_scale_y_wheel", "canvas_scale_x_mod", "canvas_scale_x_wheel"]

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
    "canvas_scale": "Canvas Scale",
}

def _anchor_chase(action):
    """Right after dropping an anchor, this noise picks its kind instead."""
    return lambda: None if actions.user.parrot_rig_anchor_chase() else action()


input_map_common = {
    "ee":     ("stop", actions.user.parrot_rig_stop),
    "mm":     ("click", actions.user.parrot_rig_click),
    "pop":    ("anchor / snap / click exit", actions.user.parrot_rig_return),
    "ah":     ("move left", lambda: actions.user.parrot_rig_move("left")),
    "oh":     ("move right", lambda: actions.user.parrot_rig_move("right")),
    "t":      ("move up", lambda: actions.user.parrot_rig_move("up")),
    "guh":    ("move down", lambda: actions.user.parrot_rig_move("down")),
    "eh":     ("track", actions.user.parrot_rig_tracking_activate),
    "er":     ("canvas mode", actions.user.parrot_rig_canvas_toggle),
    "palate": ("utility_1", lambda: actions.user.parrot_rig_utility("utility_1")),
    "cluck":  ("exit", actions.user.parrot_rig_exit),
    "tut":        ("reset slow", actions.user.parrot_rig_reset_speed_level),
    "tut tut":    ("exit", actions.user.parrot_rig_exit),
    "tut ee":     ("disable modifiers", actions.user.parrot_rig_disable_modifiers),
    "tut ah":     ("toggle alt", lambda: actions.user.parrot_rig_toggle_modifier("alt")),
    "tut t":      ("toggle shift", lambda: actions.user.parrot_rig_toggle_modifier("shift")),
    "tut guh":    ("toggle control", lambda: actions.user.parrot_rig_toggle_modifier("ctrl")),
    "tut pop":    ("anchor set / clear", actions.user.parrot_rig_anchor_toggle),
    "tut hiss":   ("scroll bottom", lambda: actions.user.parrot_rig_scroll_extreme("down")),
    "tut shush":  ("scroll top", lambda: actions.user.parrot_rig_scroll_extreme("up")),
    "tut mm":     ("click settings", lambda: actions.user.parrot_rig_menu_open("click_freeze")),
    "tut er":     ("canvas settings", lambda: actions.user.parrot_rig_menu_open("canvas_mode")),
    "tut eh":     ("move settings", lambda: actions.user.parrot_rig_menu_open("move_mode")),
    "tut oh":     ("right click", lambda: actions.user.parrot_rig_click(1)),
    "tut palate": ("settings", lambda: actions.user.parrot_rig_settings_menu()),
    "tut cluck":  ("canvas scale", actions.user.parrot_rig_canvas_scale_toggle),
}

input_map_default = {
    **input_map_common,
    "hiss":              ("scroll down", lambda: actions.user.parrot_rig_scroll("down")),
    "hiss_stop:db_170":  ("", actions.user.parrot_rig_scroll_stop),
    "shush":             ("scroll up", _anchor_chase(lambda: actions.user.parrot_rig_scroll("up"))),
    "shush_stop:db_170": ("", actions.user.parrot_rig_scroll_stop),
}

input_map_move = {
    **input_map_common,
    "ah":         ("move left or slow", lambda: actions.user.parrot_rig_move_or_slow("left")),
    "oh":         ("move right or slow", lambda: actions.user.parrot_rig_move_or_slow("right")),
    "t":          ("move up or slow", lambda: actions.user.parrot_rig_move_or_slow("up")),
    "guh":        ("move down or slow", lambda: actions.user.parrot_rig_move_or_slow("down")),
    "eh":         ("toggle glide / lock turn", actions.user.parrot_rig_toggle_glide),
    "mm":         ("click", actions.user.parrot_rig_click),
    "shush":      ("boost long", _anchor_chase(actions.user.parrot_rig_boost_long)),
    "shush_stop": ("", lambda: None),
    "hiss":            ("burst or brake", actions.user.parrot_rig_burst_or_brake),
    "hiss_stop:db_50": ("", actions.user.parrot_rig_burst_or_brake_stop),
}

input_map_tracking = {
    **input_map_common,
    "mm":                ("click (pause track)", actions.user.parrot_rig_click),
    "hiss":              ("scroll down (pause track)", lambda: actions.user.parrot_rig_scroll("down")),
    "hiss_stop:db_170":  ("", actions.user.parrot_rig_scroll_stop_temp),
    "shush":             ("scroll up (pause track)", _anchor_chase(lambda: actions.user.parrot_rig_scroll("up"))),
    "shush_stop:db_170": ("", actions.user.parrot_rig_scroll_stop_temp),
}

input_map_canvas_stop = {
    **input_map_common,
    "ah":     ("canvas left", lambda: actions.user.parrot_rig_canvas_move("left")),
    "oh":     ("canvas right", lambda: actions.user.parrot_rig_canvas_move("right")),
    "t":      ("canvas up", lambda: actions.user.parrot_rig_canvas_move("up")),
    "guh":    ("canvas down", lambda: actions.user.parrot_rig_canvas_move("down")),
    "eh":     ("canvas track", actions.user.parrot_rig_canvas_tracking_activate),
    "shush":      ("canvas scale, or resume", _anchor_chase(actions.user.parrot_rig_canvas_resume_or_scale)),
    "shush_stop": ("", lambda: None),
    "hiss":       ("canvas resume", actions.user.parrot_rig_canvas_resume),
    "hiss_stop":  ("", lambda: None),
    "er":     ("exit canvas mode", actions.user.parrot_rig_stop),
}

input_map_canvas_move = {
    **input_map_common,
    "ah":         ("canvas left or slow", lambda: actions.user.parrot_rig_canvas_move_or_slow("left")),
    "oh":         ("canvas right or slow", lambda: actions.user.parrot_rig_canvas_move_or_slow("right")),
    "t":          ("canvas up or slow", lambda: actions.user.parrot_rig_canvas_move_or_slow("up")),
    "guh":        ("canvas down or slow", lambda: actions.user.parrot_rig_canvas_move_or_slow("down")),
    "eh":         ("toggle canvas glide", actions.user.parrot_rig_canvas_toggle_glide),
    "ee":         ("canvas stop", actions.user.parrot_rig_canvas_stop),
    "mm":         ("click", actions.user.parrot_rig_click),
    "shush":      ("canvas boost long", _anchor_chase(actions.user.parrot_rig_canvas_boost_long)),
    "shush_stop": ("", lambda: None),
    "hiss":            ("canvas burst or brake", actions.user.parrot_rig_canvas_burst_or_brake),
    "hiss_stop:db_50": ("", actions.user.parrot_rig_canvas_burst_or_brake_stop),
}

input_map_canvas_scale = {
    **input_map_common,
    "ah":     ("scale x left", lambda: actions.user.parrot_rig_canvas_scale("left")),
    "oh":     ("scale x right", lambda: actions.user.parrot_rig_canvas_scale("right")),
    "t":      ("scale y up", lambda: actions.user.parrot_rig_canvas_scale("up")),
    "guh":    ("scale y down", lambda: actions.user.parrot_rig_canvas_scale("down")),
    "ee":     ("stop, stay in canvas scale", actions.user.parrot_rig_canvas_scale_stop),
    "er":     ("exit canvas scale", actions.user.parrot_rig_canvas_scale_toggle),
    "hiss":              ("plain scroll down", lambda: actions.user.parrot_rig_canvas_scale_plain("down")),
    "hiss_stop:db_170":  ("", actions.user.parrot_rig_scroll_stop),
    "shush":             ("plain scroll up", _anchor_chase(lambda: actions.user.parrot_rig_canvas_scale_plain("up"))),
    "shush_stop:db_170": ("", actions.user.parrot_rig_scroll_stop),
}

input_map_canvas_tracking = {
    **input_map_canvas_stop,
    "ee":         ("canvas stop", actions.user.parrot_rig_canvas_stop),
    "mm":         ("click (pause track)", actions.user.parrot_rig_click),
    "er":         ("exit canvas mode", actions.user.parrot_rig_canvas_move_toggle),
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
                lambda n=name: actions.user.parrot_rig_menu_open(n),
            )
    mode["tut"] = (back_label, actions.user.parrot_rig_menu_back)
    return mode


def _profiles_input_map():
    mode = {}
    for i in range(min(PROFILE_SLOTS, len(SELECT_NOISES))):
        mode[SELECT_NOISES[i]] = (
            f"profile {i + 1}",
            lambda i=i: actions.user.parrot_rig_profile_slot(i),
        )
    mode["palate"] = ("overwrite active", actions.user.parrot_rig_profile_save_current)
    mode["tut"] = ("back", actions.user.parrot_rig_menu_back)
    return mode


def _anchor_kind_input_map():
    mode = {}
    for i, (kind, label) in enumerate(ANCHOR_KINDS):
        if i < len(SELECT_NOISES):
            mode[SELECT_NOISES[i]] = (
                label,
                lambda k=kind: actions.user.parrot_rig_anchor_kind(k),
            )
    mode["tut"] = ("keep point", actions.user.parrot_rig_menu_back)
    return mode


def _typing_input_map():
    # Talking while typing must not fire noises. Only a double tut escapes,
    # and the bare tut is just the combo prefix.
    return {
        "tut": ("", lambda: None),
        "tut tut": ("cancel", actions.user.parrot_rig_menu_back),
    }


input_map = {
    "default": input_map_default,
    "move": input_map_move,
    "tracking": input_map_tracking,
    "canvas_stop": input_map_canvas_stop,
    "canvas_move": input_map_canvas_move,
    "canvas_tracking": input_map_canvas_tracking,
    "canvas_scale": input_map_canvas_scale,
    "hub_select": _menu_list_input_map(HUB_MENUS, "close"),
    "speeds_select": _menu_list_input_map(SPEED_MENUS),
    "canvas_scale_select": _menu_list_input_map(CANVAS_SCALE_MENUS),
    "anchor_kind_select": _anchor_kind_input_map(),
    "profiles_select": _profiles_input_map(),
    "profile_name_select": _typing_input_map(),
    "setting_custom_select": _typing_input_map(),
    **utility_input_maps(
        maps=utility_maps,
        ui_selectors=SELECT_NOISES,
        ui_cancel=["tut"],
        close=lambda n: actions.user.parrot_rig_menu_back(),
    ),
    **utility_input_maps(
        maps=setting_maps,
        ui_selectors=SELECT_NOISES,
        ui_cancel=["tut"],
        select=lambda n, i: actions.user.parrot_rig_setting_select(n, i),
        close=lambda n: actions.user.parrot_rig_menu_back(),
    ),
}

def channel_init():
    """Register the parrot_rig channel if not already registered."""
    if CHANNEL not in actions.user.input_map_channel_list():
        actions.user.input_map_channel_register(CHANNEL, input_map)

def channel_reset():
    """Unregister and re-register the channel with fresh data."""
    actions.user.input_map_channel_unregister(CHANNEL)
    actions.user.input_map_channel_register(CHANNEL, input_map)

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

    def parrot_rig_move_or_slow(direction: str):
        """Move mouse or slow down if already moving in that direction"""
        parrot_actions.mouse_move_or_slow_dir(direction)

    def parrot_rig_stop():
        """Stop all mouse movement, scrolling, and tracking"""
        parrot_actions.stopper()

    def parrot_rig_boost_long():
        """Boost mouse speed in current direction"""
        parrot_actions.mouse_boost_long()

    def parrot_rig_burst_or_brake():
        """Speed burst or brake (release glide/boost)"""
        parrot_actions.mouse_burst_or_brake()

    def parrot_rig_burst_or_brake_stop():
        """Stop burst (fade out)"""
        parrot_actions.mouse_burst_or_brake_stop()

    def parrot_rig_click_exit():
        """Click and exit parrot mode"""
        parrot_actions.click_exit()

    def parrot_rig_exit():
        """Exit parrot mode (tracking-aware)"""
        parrot_actions.exit()

    def parrot_rig_scroll(direction: str):
        """Scroll in direction (up/down)"""
        parrot_actions.scroll(direction)

    def parrot_rig_scroll_stop():
        """Stop scrolling"""
        parrot_actions.scroll_stop()

    def parrot_rig_scroll_extreme(direction: str):
        """Jump to the top or bottom instead of scrolling there"""
        parrot_actions.scroll_extreme(direction)

    def parrot_rig_scroll_stop_temp():
        """Stop scrolling and temporarily pause tracking"""
        parrot_actions.scroll_stop_temp()

    def parrot_rig_toggle_glide():
        """Toggle glide mode"""
        parrot_actions.mouse_toggle_glide()

    def parrot_rig_toggle_modifier(modifier: str):
        """Toggle a modifier key (shift/ctrl/alt)"""
        parrot_actions.toggle_modifier(modifier)

    def parrot_rig_disable_modifiers():
        """Release all held modifier keys"""
        parrot_actions.disable_modifiers()

    def parrot_rig_reset_speed_level():
        """Reset speed level back to normal"""
        parrot_actions.reset_speed_level()

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

    def parrot_rig_tracking_activate():
        """Activate head tracking mode"""
        parrot_actions.tracking_activate()

    def parrot_rig_canvas_tracking_activate():
        """Activate canvas tracking mode (triangle + tracking)"""
        parrot_actions.canvas_tracking_activate()

    def parrot_rig_reload():
        """Reload parrot rig files"""
        parrot_actions.reload_files()

    def parrot_rig_get_mode():
        """Get current mode (default/move/boost/glide/tracking)"""
        return parrot_actions.parrot_mode_get_mode()

    def parrot_rig_canvas_move_toggle():
        """Toggle scroll move mode"""
        parrot_actions.canvas_move_toggle()

    def parrot_rig_canvas_move(direction: str):
        """Scroll in direction using scroll move mode"""
        parrot_actions.canvas_move_dir(direction)

    def parrot_rig_canvas_move_or_slow(direction: str):
        """Scroll or slow down if already scrolling in that direction"""
        parrot_actions.canvas_move_or_slow_dir(direction)

    def parrot_rig_canvas_toggle_glide():
        """Toggle canvas glide mode"""
        parrot_actions.canvas_toggle_glide()

    def parrot_rig_canvas_boost_long():
        """Boost scroll speed in current direction"""
        parrot_actions.canvas_boost_long()

    def parrot_rig_canvas_burst_or_brake():
        """Canvas burst or brake (release canvas glide/boost)"""
        parrot_actions.canvas_burst_or_brake()

    def parrot_rig_canvas_burst_or_brake_stop():
        """Stop canvas burst (fade out)"""
        parrot_actions.canvas_burst_or_brake_stop()

    def parrot_rig_canvas_stop():
        """Stop the canvas but stay in canvas mode"""
        parrot_actions.canvas_stop()

    def parrot_rig_canvas_ramp(direction: str):
        """Start scrolling with ramp-up bounce-back effect"""
        parrot_actions.canvas_ramp_dir(direction)

    def parrot_rig_canvas_resume():
        """Resume scrolling in the last scroll direction"""
        parrot_actions.canvas_resume()

    def parrot_rig_show_help():
        """Show parrot rig cheatsheet"""
        parrot_actions.show_cheatsheet()

    # Utility actions

    def parrot_rig_utility(name: str):
        """Execute the currently selected utility action"""
        actions.user.input_map_single(name, utility_maps[name])

    def parrot_rig_show_utility_selector(name: str, noise: str = ""):
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

    # Settings menus

    def parrot_rig_canvas_toggle():
        """Toggle the alternate movement mode named by the canvas_mode setting"""
        parrot_actions.canvas_toggle()

    def parrot_rig_middle_drag_toggle():
        """Hold middle mouse down and keep moving; toggle again to release"""
        parrot_actions.toggle_middle_drag()

    def parrot_rig_canvas_resume_or_scale():
        """Canvas scale when it lands right after canvas mode, else canvas resume"""
        parrot_actions.canvas_resume_or_scale()

    def parrot_rig_canvas_scale_toggle():
        """Enter or leave canvas scale, whatever the canvas_mode setting is"""
        parrot_actions.canvas_scale_toggle()

    def parrot_rig_canvas_scale(direction: str):
        """Scroll with the axis modifier held, so the app zooms or pans"""
        parrot_actions.canvas_scale_dir(direction)

    def parrot_rig_canvas_scale_stop():
        """Stop canvas scale and release the held modifier, staying in the mode"""
        parrot_actions.canvas_scale_stop()

    def parrot_rig_canvas_scale_plain(direction: str):
        """Ordinary scroll from inside canvas scale, no modifier held"""
        parrot_actions.canvas_scale_plain(direction)

    def parrot_rig_return():
        """Return to an anchor if any are set, else the snap target, else click and exit"""
        parrot_actions.return_action()

    def parrot_rig_snap():
        """Snap the cursor now (center by default), without stopping movement"""
        parrot_actions.snap_now()

    def parrot_rig_anchor_toggle():
        """Drop an anchor at the cursor, or remove the one under it"""
        parrot_actions.toggle_anchor()

    def parrot_rig_anchor_chase() -> bool:
        """Open the anchor kind picker if an anchor was just dropped. True if it did"""
        from .src.anchor import anchor_hold
        if not anchor_hold():
            return False
        menu_open("anchor_kind")
        return True

    def parrot_rig_anchor_kind(kind: str):
        """Make the anchor just dropped a point, or a line through it"""
        from .src.anchor import anchor_set_kind
        from .ui.utility_selector import show_utility_notification
        anchor_set_kind(kind)
        show_utility_notification("Anchor", dict(ANCHOR_KINDS).get(kind, kind).lower())
        menu_back()

    def parrot_rig_anchor_go() -> bool:
        """Move to the nearest anchor, or the next one round if already on one"""
        from .src.anchor import anchor_go
        return anchor_go()

    def parrot_rig_anchor_clear_all():
        """Remove every anchor"""
        from .src.anchor import anchor_clear_all
        from .ui.utility_selector import show_utility_notification
        anchor_clear_all()
        show_utility_notification("Anchor", "cleared all")

    def parrot_rig_setting_get(name: str) -> str:
        """Get the current value of a settings-menu setting"""
        from .src.settings_menu import setting_get
        return setting_get(name)

    def parrot_rig_show_setting_selector(name: str, noise: str = ""):
        """Show a settings selector UI and enter select mode"""
        menu_open(name)

    def parrot_rig_setting_select(name: str, slot: int):
        """Select a setting value by slot index, or run its action if it has one"""
        from .ui.utility_selector import show_utility_notification
        entries = list(setting_maps[name].items())
        if slot < len(entries):
            key, entry = entries[slot]
            if key == "custom":
                actions.user.parrot_rig_setting_custom_prompt(name)
                return
            if len(entry) > 1:
                menu_back()
                getattr(actions.user, entry[1])()
                return
            setting_set(name, key)
            show_utility_notification(setting_title(name), setting_summary(name))
        menu_back()

    def parrot_rig_setting_custom_prompt(name: str):
        """Open the number input for a numeric setting"""
        from .ui.settings_hub import set_custom_pending
        set_custom_pending(name)
        menu_open("setting_custom")

    def parrot_rig_setting_custom_submit(text: str):
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

    # Menu navigation

    def parrot_rig_settings_menu():
        """Open the settings hub"""
        menu_open("hub")

    def parrot_rig_menu_open(name: str):
        """Open a menu by name, drilling in from whatever is open"""
        menu_open(name)

    def parrot_rig_menu_back():
        """Back one menu level, closing out at the top"""
        menu_back()

    def parrot_rig_menu_close():
        """Close every open menu"""
        menu_close()

    # Profiles

    def parrot_rig_profile_slot(slot: int):
        """Load the profile in a slot, or name a new one if it is the next free slot"""
        from .ui.utility_selector import show_utility_notification
        names = profile_names()
        if slot == len(names):
            actions.user.parrot_rig_profile_name_prompt()
            return
        if slot > len(names):
            return
        profile_load(names[slot])
        show_utility_notification("Profile", names[slot])
        menu_back()

    def parrot_rig_profile_save_current():
        """Save to the active profile, or prompt for a name if it is locked"""
        from .ui.utility_selector import show_utility_notification
        name = profile_active()
        if not profile_save(name):
            actions.user.parrot_rig_profile_name_prompt()
            return
        show_utility_notification("Profile", f"saved {name}")

    def parrot_rig_profile_name_prompt():
        """Open the name input for saving a new profile"""
        menu_open("profile_name")

    def parrot_rig_profile_name_submit(name: str):
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

    def parrot_rig_profile_save(name: str):
        """Save current settings as a named profile"""
        if not profile_save(name):
            print(f"parrot rig: {name} is locked")
            return
        print(f"parrot rig: saved profile {name}")

    def parrot_rig_profile_load(name: str):
        """Load a named profile"""
        if not profile_load(name):
            print(f"parrot rig: no profile {name}")

    def parrot_rig_profile_delete(name: str):
        """Delete a named profile"""
        if not profile_delete(name):
            print(f"parrot rig: no profile {name}, or it is locked")

    def parrot_rig_profile_list() -> list:
        """List saved profile names"""
        names = profile_names()
        print(f"parrot rig profiles: {names or 'none'}")
        return names
