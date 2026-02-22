from talon import Module, actions, ctrl
from .src.parrot_actions import parrot_actions
from .src.events import event_manager
from .parrot_rig_settings import CLICK_HOLD_MS
from .parrot_rig_utilities import utility_map, utility2_map
from .src.select import utility_input_maps

mod = Module()
mod.mode("parrot_rig", "parrot rig")

CHANNEL = "parrot_rig"

input_map_common = {
    "ee":     ("stop", actions.user.parrot_rig_stop),
    "mm":     ("click", actions.user.parrot_rig_click),
    "pop":    ("click exit", actions.user.parrot_rig_click_exit),
    "ah":     ("move left", lambda: actions.user.parrot_rig_move("left")),
    "oh":     ("move right", lambda: actions.user.parrot_rig_move("right")),
    "t":      ("move up", lambda: actions.user.parrot_rig_move("up")),
    "guh":    ("move down", lambda: actions.user.parrot_rig_move("down")),
    "eh":     ("track", actions.user.parrot_rig_tracking_activate),
    "er":     ("scroll mode", actions.user.parrot_rig_toggle_scroll_move),
    "palate": ("utility", actions.user.parrot_rig_utility),
    "cluck":  ("exit", actions.user.parrot_rig_exit),
    "tut":        ("reset speed", actions.user.parrot_rig_reset_speed_level),
    "tut tut":    ("exit", actions.user.parrot_rig_exit),
    "tut ee":     ("disable modifiers", actions.user.parrot_rig_disable_modifiers),
    "tut ah":     ("toggle alt", lambda: actions.user.parrot_rig_toggle_modifier("alt")),
    "tut shush":  ("toggle shift", lambda: actions.user.parrot_rig_toggle_modifier("shift")),
    "tut guh":    ("toggle control", lambda: actions.user.parrot_rig_toggle_modifier("ctrl")),
    "tut mm":     ("middle click hold", lambda: actions.user.parrot_rig_click(2)),
    "tut oh":     ("right click", lambda: actions.user.parrot_rig_click(1)),
    "tut palate": ("utility selector", lambda: actions.user.parrot_rig_show_utility_selector("palate")),
    "tut er":     ("utility2 selector", lambda: actions.user.parrot_rig_show_utility2_selector("er")),
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
    "ah":         ("move left", lambda: actions.user.parrot_rig_move_or_slow("left")),
    "oh":         ("move right", lambda: actions.user.parrot_rig_move_or_slow("right")),
    "t":          ("move up", lambda: actions.user.parrot_rig_move_or_slow("up")),
    "guh":        ("move down", lambda: actions.user.parrot_rig_move_or_slow("down")),
    "eh":         ("toggle glide", actions.user.parrot_rig_toggle_glide),
    "mm":         ("click", actions.user.parrot_rig_click_mode),
    "shush":      ("boost long", actions.user.parrot_rig_boost_long),
    "shush_stop": ("", lambda: None),
    "hiss":            ("boost burst", actions.user.parrot_rig_boost_burst),
    "hiss_stop:db_30": ("", actions.user.parrot_rig_boost_burst_stop),
}

input_map_tracking = {
    **input_map_common,
    "mm":                ("click temp stop", actions.user.parrot_rig_click_mode),
    "hiss":              ("scroll down", lambda: actions.user.parrot_rig_scroll("down")),
    "hiss_stop:db_170":  ("", actions.user.parrot_rig_scroll_stop_temp),
    "shush":             ("scroll up", lambda: actions.user.parrot_rig_scroll("up")),
    "shush_stop:db_170": ("", actions.user.parrot_rig_scroll_stop_temp),
}

input_map_scroll_stop = {
    **input_map_common,
    "ah":     ("scroll left", lambda: actions.user.parrot_rig_scroll_move("left")),
    "oh":     ("scroll right", lambda: actions.user.parrot_rig_scroll_move("right")),
    "t":      ("scroll up", lambda: actions.user.parrot_rig_scroll_move("up")),
    "guh":    ("scroll down", lambda: actions.user.parrot_rig_scroll_move("down")),
    "eh":     ("scroll track", actions.user.parrot_rig_scroll_tracking_activate),
    "shush":      ("scroll resume", actions.user.parrot_rig_scroll_resume),
    "shush_stop": ("", lambda: None),
    "hiss":       ("scroll resume", actions.user.parrot_rig_scroll_resume),
    "hiss_stop":  ("", lambda: None),
    "er":     ("exit scroll", actions.user.parrot_rig_stop),
}

input_map_scroll_move = {
    **input_map_common,
    "ah":         ("scroll left", lambda: actions.user.parrot_rig_scroll_move_or_slow("left")),
    "oh":         ("scroll right", lambda: actions.user.parrot_rig_scroll_move_or_slow("right")),
    "t":          ("scroll up", lambda: actions.user.parrot_rig_scroll_move_or_slow("up")),
    "guh":        ("scroll down", lambda: actions.user.parrot_rig_scroll_move_or_slow("down")),
    "eh":         ("toggle scroll glide", actions.user.parrot_rig_scroll_toggle_glide),
    "ee":         ("scroll stop", actions.user.parrot_rig_scroll_stop_stay),
    "mm":         ("click", actions.user.parrot_rig_click_mode),
    "shush":      ("scroll boost long", actions.user.parrot_rig_scroll_boost_long),
    "shush_stop": ("", lambda: None),
    "hiss":            ("scroll boost burst", actions.user.parrot_rig_scroll_boost_burst),
    "hiss_stop:db_30": ("", actions.user.parrot_rig_scroll_boost_burst_stop),
}

input_map_scroll_tracking = {
    **input_map_scroll_stop,
    "ee":         ("scroll stop", actions.user.parrot_rig_scroll_stop_stay),
    "mm":         ("click temp stop", actions.user.parrot_rig_click_mode),
    "er":         ("track mode", actions.user.parrot_rig_toggle_scroll_move),
}

input_map = {
    "default": input_map_default,
    "move": input_map_move,
    "tracking": input_map_tracking,
    "scroll_stop": input_map_scroll_stop,
    "scroll_move": input_map_scroll_move,
    "scroll_tracking": input_map_scroll_tracking,
    **utility_input_maps({
        "selectors": ["ah", "oh", "t", "guh", "eh", "mm", "pop", "ee", "cluck", "hiss", "shush"],
        "cancel": ["tut"],
    }),
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

    def parrot_rig_boost_burst():
        """Small temporary speed boost"""
        parrot_actions.mouse_boost_burst()

    def parrot_rig_boost_burst_stop():
        """Stop small speed boost (fade out)"""
        parrot_actions.mouse_boost_burst_stop()

    def parrot_rig_click_exit():
        """Click and exit parrot mode"""
        parrot_actions.click_exit()

    def parrot_rig_exit():
        """Exit parrot mode (tracking-aware)"""
        parrot_actions.exit()

    def parrot_rig_click_mode():
        """Click with mode-aware stop behavior"""
        parrot_actions.click_with_mode_behavior()

    def parrot_rig_scroll(direction: str):
        """Scroll in direction (up/down)"""
        parrot_actions.scroll(direction)

    def parrot_rig_scroll_stop():
        """Stop scrolling"""
        parrot_actions.scroll_stop()

    def parrot_rig_scroll_stop_temp():
        """Stop scrolling and temporarily pause tracking"""
        parrot_actions.scroll_stop_temp()

    def parrot_rig_toggle_glide():
        """Toggle glide mode"""
        parrot_actions.mouse_toggle_glide()

    def parrot_rig_utility():
        """Execute the currently selected utility action"""
        actions.user.input_map_single("utility", utility_map)

    def parrot_rig_utility2():
        """Execute the currently selected utility2 action"""
        actions.user.input_map_single("utility2", utility2_map)

    def parrot_rig_toggle_modifier(modifier: str):
        """Toggle a modifier key (shift/ctrl/alt)"""
        parrot_actions.toggle_modifier(modifier)

    def parrot_rig_disable_modifiers():
        """Release all held modifier keys"""
        parrot_actions.disable_modifiers()

    def parrot_rig_show_utility_selector(noise: str = "palate"):
        """Show utility selector UI and enter select mode"""
        event_manager.set_mode("utility_select")
        parrot_actions.show_utility_selector(f"Utility ({noise})")

    def parrot_rig_show_utility2_selector(noise: str = "er"):
        """Show utility2 selector UI and enter select mode"""
        event_manager.set_mode("utility2_select")
        parrot_actions.show_utility2_selector(f"Utility 2 ({noise})")

    def parrot_rig_utility_select(name: str, slot: int, noise: str = ""):
        """Select a utility option by slot index"""
        from .ui.utility_selector import show_utility_notification
        util_map = utility_map if name == "utility" else utility2_map
        keys = list(util_map.keys())
        if slot < len(keys):
            actions.user.input_map_single_mode_set(name, keys[slot], util_map)
            label = util_map[keys[slot]][0]
            show_utility_notification(noise or name, label)
        actions.user.parrot_rig_utility_select_close(name)

    def parrot_rig_utility_select_close(name: str):
        """Close utility selector and revert mode"""
        if name == "utility":
            parrot_actions.hide_utility_selector()
        else:
            parrot_actions.hide_utility2_selector()
        event_manager.return_to_previous_mode()

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

    def parrot_rig_scroll_boost_burst():
        """Small temporary scroll speed boost"""
        parrot_actions.scroll_boost_burst()

    def parrot_rig_scroll_boost_burst_stop():
        """Stop small scroll speed boost (fade out)"""
        parrot_actions.scroll_boost_burst_stop()

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
