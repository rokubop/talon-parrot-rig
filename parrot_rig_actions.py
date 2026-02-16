from talon import Module, Context, actions, ctrl
from .src.parrot_actions import parrot_actions

mod = Module()
mod.mode("parrot_rig", "parrot rig")

ctx_parrot_rig = Context()
ctx_parrot_rig.matches = """
mode: user.parrot_rig
"""

input_map_common = {
    "ee":     ("stop", parrot_actions.stopper),
    "pop":    ("click exit", parrot_actions.click_exit),
    "ah":     ("move left", lambda: parrot_actions.mouse_move_dir("left")),
    "oh":     ("move right", lambda: parrot_actions.mouse_move_dir("right")),
    "t":      ("move up", lambda: parrot_actions.mouse_move_dir("up")),
    "guh":    ("move down", lambda: parrot_actions.mouse_move_dir("down")),
    "eh":     ("track", parrot_actions.tracking_activate),
    "er":     ("", lambda: None),  # available
    "palate": ("hold or utility", parrot_actions.utility),
    "cluck":  ("exit", parrot_actions.exit),
    "tut tut":    ("exit", parrot_actions.exit),
    "tut ee":     ("disable modifiers", parrot_actions.disable_modifiers),
    "tut ah":     ("toggle alt", lambda: parrot_actions.toggle_modifier("alt")),
    "tut shush":  ("toggle shift", lambda: parrot_actions.toggle_modifier("shift")),
    "tut guh":    ("toggle control", lambda: parrot_actions.toggle_modifier("ctrl")),
    "tut mm":     ("middle click hold", lambda: parrot_actions.mouse_click(button=2)),
    "tut oh":     ("right click", lambda: parrot_actions.mouse_click(button=1)),
    "tut palate": ("utility selector", parrot_actions.show_utility_selector),
}

input_map_default = {
    **input_map_common,
    "mm":                ("click", parrot_actions.mouse_click),
    "hiss":              ("scroll down", lambda: parrot_actions.scroll("down")),
    "hiss_stop:db_170":  ("", parrot_actions.scroll_stop),
    "shush":             ("scroll up", lambda: parrot_actions.scroll("up")),
    "shush_stop:db_170": ("", parrot_actions.scroll_stop),
}

input_map_move = {
    **input_map_common,
    "ah":         ("move left", lambda: parrot_actions.mouse_move_or_slow_dir("left")),
    "oh":         ("move right", lambda: parrot_actions.mouse_move_or_slow_dir("right")),
    "t":          ("move up", lambda: parrot_actions.mouse_move_or_slow_dir("up")),
    "guh":        ("move down", lambda: parrot_actions.mouse_move_or_slow_dir("down")),
    "eh":         ("toggle glide", parrot_actions.mouse_toggle_glide),
    "mm":         ("click", parrot_actions.click_with_mode_behavior),
    "shush":      ("boost", parrot_actions.mouse_boost),
    "shush_stop": ("", lambda: None),
    "hiss":       ("boost small", parrot_actions.mouse_boost_small),
    "hiss_stop":  ("", lambda: None),
}

input_map_tracking = {
    **input_map_common,
    "mm":                ("click temp stop", parrot_actions.click_with_mode_behavior),
    "hiss":              ("scroll down", lambda: parrot_actions.scroll("down")),
    "hiss_stop:db_170":  ("", parrot_actions.scroll_stop_temp),
    "shush":             ("scroll up", lambda: parrot_actions.scroll("up")),
    "shush_stop:db_170": ("", parrot_actions.scroll_stop_temp),
}

input_map = {
    "default": input_map_default,
    "move": input_map_move,
    "tracking": input_map_tracking,
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

    def parrot_rig_click():
        """Parrot rig click"""
        ctrl.mouse_click(button=0, hold=16000)

    def parrot_rig_repeater():
        """Parrot rig repeater"""
        parrot_actions.repeat()

    def parrot_rig_reverser():
        """Parrot rig reverser"""
        parrot_actions.reverse_repeat()

    def parrot_rig_get_state():
        """Get parrot rig state"""
        return parrot_actions.parrot_rig_get_state()

    def parrot_rig_tracking_activate():
        """Activate tracking"""
        parrot_actions.tracking_activate()

    def parrot_rig_reload():
        """Reload parrot rig"""
        parrot_actions.reload_files()

    def parrot_rig_get_mode():
        """Get current mode for parrot mode"""
        return parrot_actions.parrot_mode_get_mode()

    def parrot_rig_show_help():
        """Show parrot rig help/cheatsheet"""
        parrot_actions.show_cheatsheet()
