from talon import Module, Context, actions, ctrl
from .src.parrot_actions import parrot_actions
from .src.events import event_manager
from .parrot_rig_settings import CLICK_HOLD_MS
from .parrot_rig_utilities import utility_map, utility2_map
from .src.select import utility_input_maps

mod = Module()
mod.mode("parrot_rig", "parrot rig")

ctx_parrot_rig = Context()
ctx_parrot_rig.matches = """
mode: user.parrot_rig
"""

input_map_common = {
    "ee":     ("stop", actions.user.parrot_rig_stop),
    "pop":    ("click exit", actions.user.parrot_rig_click_exit),
    "ah":     ("move left", lambda: actions.user.parrot_rig_move("left")),
    "oh":     ("move right", lambda: actions.user.parrot_rig_move("right")),
    "t":      ("move up", lambda: actions.user.parrot_rig_move("up")),
    "guh":    ("move down", lambda: actions.user.parrot_rig_move("down")),
    "eh":     ("track", actions.user.parrot_rig_tracking_activate),
    "er":     ("utility2", actions.user.parrot_rig_utility2),
    "palate": ("utility", actions.user.parrot_rig_utility),
    "cluck":  ("exit", actions.user.parrot_rig_exit),
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
    "mm":                ("click", actions.user.parrot_rig_click),
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
    "shush":      ("boost", actions.user.parrot_rig_boost),
    "shush_stop": ("", lambda: None),
    "hiss":       ("boost small", actions.user.parrot_rig_boost_small),
    "hiss_stop":  ("", lambda: None),
}

input_map_tracking = {
    **input_map_common,
    "mm":                ("click temp stop", actions.user.parrot_rig_click_mode),
    "hiss":              ("scroll down", lambda: actions.user.parrot_rig_scroll("down")),
    "hiss_stop:db_170":  ("", actions.user.parrot_rig_scroll_stop_temp),
    "shush":             ("scroll up", lambda: actions.user.parrot_rig_scroll("up")),
    "shush_stop:db_170": ("", actions.user.parrot_rig_scroll_stop_temp),
}

input_map = {
    "default": input_map_default,
    "move": input_map_move,
    "tracking": input_map_tracking,
    **utility_input_maps({
        "selectors": ["ah", "oh", "t", "guh", "eh", "mm", "pop", "ee", "cluck", "hiss", "shush"],
        "cancel": ["tut"],
    }),
}

@ctx_parrot_rig.action_class("user")
class Actions:
    def input_map():
        return input_map

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

    def parrot_rig_boost():
        """Boost mouse speed in current direction"""
        parrot_actions.mouse_boost()

    def parrot_rig_boost_small():
        """Small temporary speed boost"""
        parrot_actions.mouse_boost_small()

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

    def parrot_rig_repeat_command():
        """Repeat last command (with opposites reversal support)"""
        parrot_actions.repeat()

    def parrot_rig_reverse_command():
        """Reverse last command (uses opposites mapping)"""
        parrot_actions.reverse_repeat()

    def parrot_rig_repeat_phrase():
        """Repeat last phrase"""
        try:
            actions.core.repeat_phrase()
        except IndexError:
            pass

    def parrot_rig_reverse_phrase():
        """Reverse repeat last phrase"""
        pass

    def parrot_rig_get_state():
        """Get parrot rig state"""
        return parrot_actions.parrot_rig_get_state()

    def parrot_rig_tracking_activate():
        """Activate head tracking mode"""
        parrot_actions.tracking_activate()

    def parrot_rig_reload():
        """Reload parrot rig files"""
        parrot_actions.reload_files()

    def parrot_rig_get_mode():
        """Get current mode (default/move/boost/glide/tracking)"""
        return parrot_actions.parrot_mode_get_mode()

    def parrot_rig_show_help():
        """Show parrot rig cheatsheet"""
        parrot_actions.show_cheatsheet()
