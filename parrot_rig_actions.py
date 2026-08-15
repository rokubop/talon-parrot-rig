from talon import Module, actions, ctrl
from .src.parrot_actions import parrot_actions
from .src.events import event_manager
from .parrot_rig_settings import CLICK_HOLD_MS
from .src.select import utility_input_maps
from .src.settings_menu import (
    setting_maps, setting_set, setting_label, setting_title, SETTING_TITLES,
)
from .src.menu import menu_open, menu_back, menu_close
from .src.profiles import (
    PROFILE_SLOTS, profile_active, profile_delete, profile_load,
    profile_names, profile_save,
)

mod = Module()
mod.mode("parrot_rig", "parrot rig")

CHANNEL = "parrot_rig"

# Noises that pick slot 1, 2, 3... in any selector menu
SELECT_NOISES = ["ah", "oh", "t", "guh", "eh", "mm", "pop", "ee", "cluck", "hiss", "shush"]

HUB_MENUS = ["click_freeze", "er_mode", "move_mode", "turn_speed", "anchor_move", "utility_1", "profiles"]

MENU_TITLES = {
    **SETTING_TITLES,
    "utility_1": "Palate",
    "profiles": "Profiles",
}

input_map_common = {
    "ee":     ("stop", actions.user.parrot_rig_stop),
    "mm":     ("click", actions.user.parrot_rig_click),
    "pop":    ("anchor / snap / click exit", actions.user.parrot_rig_pop),
    "ah":     ("move left", lambda: actions.user.parrot_rig_move("left")),
    "oh":     ("move right", lambda: actions.user.parrot_rig_move("right")),
    "t":      ("move up", lambda: actions.user.parrot_rig_move("up")),
    "guh":    ("move down", lambda: actions.user.parrot_rig_move("down")),
    "eh":     ("track", actions.user.parrot_rig_tracking_activate),
    "er":     ("scroll mode or middle drag", actions.user.parrot_rig_er),
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
    "tut er":     ("er settings", lambda: actions.user.parrot_rig_menu_open("er_mode")),
    "tut eh":     ("move settings", lambda: actions.user.parrot_rig_menu_open("move_mode")),
    "tut oh":     ("right click", lambda: actions.user.parrot_rig_click(1)),
    "tut palate": ("settings", lambda: actions.user.parrot_rig_settings_menu()),
}

input_map_default = {
    **input_map_common,
    "hiss":              ("scroll down", lambda: actions.user.parrot_rig_scroll("down")),
    "hiss_stop:db_170":  ("", actions.user.parrot_rig_scroll_stop),
    "shush":             ("scroll up", lambda: actions.user.parrot_rig_scroll("up")),
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
    "shush":      ("boost long", actions.user.parrot_rig_boost_long),
    "shush_stop": ("", lambda: None),
    "hiss":            ("burst or brake", actions.user.parrot_rig_burst_or_brake),
    "hiss_stop:db_50": ("", actions.user.parrot_rig_burst_or_brake_stop),
}

input_map_tracking = {
    **input_map_common,
    "mm":                ("click (pause track)", actions.user.parrot_rig_click),
    "hiss":              ("scroll down (pause track)", lambda: actions.user.parrot_rig_scroll("down")),
    "hiss_stop:db_170":  ("", actions.user.parrot_rig_scroll_stop_temp),
    "shush":             ("scroll up (pause track)", lambda: actions.user.parrot_rig_scroll("up")),
    "shush_stop:db_170": ("", actions.user.parrot_rig_scroll_stop_temp),
}

input_map_scroll_stop = {
    **input_map_common,
    "ah":     ("scroll go left", lambda: actions.user.parrot_rig_scroll_move("left")),
    "oh":     ("scroll go right", lambda: actions.user.parrot_rig_scroll_move("right")),
    "t":      ("scroll go up", lambda: actions.user.parrot_rig_scroll_move("up")),
    "guh":    ("scroll go down", lambda: actions.user.parrot_rig_scroll_move("down")),
    "eh":     ("scroll track", actions.user.parrot_rig_scroll_tracking_activate),
    "shush":      ("scroll resume", actions.user.parrot_rig_scroll_resume),
    "shush_stop": ("", lambda: None),
    "hiss":       ("scroll resume", actions.user.parrot_rig_scroll_resume),
    "hiss_stop":  ("", lambda: None),
    "er":     ("toggle scroll mode", actions.user.parrot_rig_stop),
}

input_map_scroll_move = {
    **input_map_common,
    "ah":         ("scroll go left or slow", lambda: actions.user.parrot_rig_scroll_move_or_slow("left")),
    "oh":         ("scroll go right or slow", lambda: actions.user.parrot_rig_scroll_move_or_slow("right")),
    "t":          ("scroll go up or slow", lambda: actions.user.parrot_rig_scroll_move_or_slow("up")),
    "guh":        ("scroll go down or slow", lambda: actions.user.parrot_rig_scroll_move_or_slow("down")),
    "eh":         ("toggle scroll glide", actions.user.parrot_rig_scroll_toggle_glide),
    "ee":         ("scroll stop", actions.user.parrot_rig_scroll_stop_stay),
    "mm":         ("click", actions.user.parrot_rig_click),
    "shush":      ("scroll boost long", actions.user.parrot_rig_scroll_boost_long),
    "shush_stop": ("", lambda: None),
    "hiss":            ("scroll burst or brake", actions.user.parrot_rig_scroll_burst_or_brake),
    "hiss_stop:db_50": ("", actions.user.parrot_rig_scroll_burst_or_brake_stop),
}

input_map_scroll_tracking = {
    **input_map_scroll_stop,
    "ee":         ("scroll stop", actions.user.parrot_rig_scroll_stop_stay),
    "mm":         ("click (pause track)", actions.user.parrot_rig_click),
    "er":         ("toggle scroll mode", actions.user.parrot_rig_toggle_scroll_move),
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

def _hub_input_map():
    mode = {}
    for i, name in enumerate(HUB_MENUS):
        if i < len(SELECT_NOISES):
            mode[SELECT_NOISES[i]] = (
                MENU_TITLES.get(name, name),
                lambda n=name: actions.user.parrot_rig_menu_open(n),
            )
    mode["tut"] = ("close", actions.user.parrot_rig_menu_back)
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


def _profile_name_input_map():
    # Deliberately inert. Talking while typing must not fire noises, so only a
    # double tut escapes. The bare tut is a no-op prefix for the combo.
    return {
        "tut": ("", lambda: None),
        "tut tut": ("cancel", actions.user.parrot_rig_menu_back),
    }


input_map = {
    "default": input_map_default,
    "move": input_map_move,
    "tracking": input_map_tracking,
    "scroll_stop": input_map_scroll_stop,
    "scroll_move": input_map_scroll_move,
    "scroll_tracking": input_map_scroll_tracking,
    "hub_select": _hub_input_map(),
    "profiles_select": _profiles_input_map(),
    "profile_name_select": _profile_name_input_map(),
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

    def parrot_rig_scroll_tracking_activate():
        """Activate scroll tracking mode (triangle + tracking)"""
        parrot_actions.scroll_tracking_activate()

    def parrot_rig_reload():
        """Reload parrot rig files"""
        parrot_actions.reload_files()

    def parrot_rig_get_mode():
        """Get current mode (default/move/boost/glide/tracking)"""
        return parrot_actions.parrot_mode_get_mode()

    def parrot_rig_toggle_scroll_move():
        """Toggle scroll move mode"""
        parrot_actions.toggle_scroll_move()

    def parrot_rig_scroll_move(direction: str):
        """Scroll in direction using scroll move mode"""
        parrot_actions.scroll_move_dir(direction)

    def parrot_rig_scroll_move_or_slow(direction: str):
        """Scroll or slow down if already scrolling in that direction"""
        parrot_actions.scroll_move_or_slow_dir(direction)

    def parrot_rig_scroll_toggle_glide():
        """Toggle scroll glide mode"""
        parrot_actions.scroll_toggle_glide()

    def parrot_rig_scroll_boost_long():
        """Boost scroll speed in current direction"""
        parrot_actions.scroll_boost_long()

    def parrot_rig_scroll_burst_or_brake():
        """Scroll burst or brake (release scroll glide/boost)"""
        parrot_actions.scroll_burst_or_brake()

    def parrot_rig_scroll_burst_or_brake_stop():
        """Stop scroll burst (fade out)"""
        parrot_actions.scroll_burst_or_brake_stop()

    def parrot_rig_scroll_stop_stay():
        """Stop scrolling but stay in scroll stop mode"""
        parrot_actions.scroll_stop_stay()

    def parrot_rig_scroll_ramp(direction: str):
        """Start scrolling with ramp-up bounce-back effect"""
        parrot_actions.scroll_ramp_dir(direction)

    def parrot_rig_scroll_resume():
        """Resume scrolling in the last scroll direction"""
        parrot_actions.scroll_resume()

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

    def parrot_rig_er():
        """Toggle scroll mode or middle drag, per the er_mode setting"""
        parrot_actions.er_toggle()

    def parrot_rig_pop():
        """Snap if a snap condition applies, otherwise click and exit"""
        parrot_actions.pop_action()

    def parrot_rig_snap():
        """Snap the cursor now (center by default), without stopping movement"""
        parrot_actions.snap_now()

    def parrot_rig_anchor_toggle():
        """Drop an anchor at the cursor, or remove the one under it"""
        parrot_actions.toggle_anchor()

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
            if len(entry) > 1:
                menu_back()
                getattr(actions.user, entry[1])()
                return
            setting_set(name, key)
            show_utility_notification(setting_title(name), setting_label(name))
        menu_back()

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
