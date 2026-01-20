from talon import Module, Context, actions, ctrl
from .src.parrot_actions import parrot_actions
from .src.constants import *

MARK_NAMES = ["ah", "oh", "t", "sh", "ss", "mm", "guh", "pop", "palate"]

mod = Module()
mod.mode("parrot_rig", "parrot rig")

ctx_parrot_rig = Context()
ctx_parrot_rig.matches = """
mode: user.parrot_rig
"""

input_map_common = {
    "ee":     ("stop", parrot_actions.stopper),
    "pop":    ("click exit", parrot_actions.click_exit),
    "cluck":  ("exit", parrot_actions.exit),
    "ah":     ("move left", lambda: parrot_actions.mouse_move_dir("left")),
    "oh":     ("move right", lambda: parrot_actions.mouse_move_dir("right")),
    "t":      ("move up", lambda: parrot_actions.mouse_move_dir("up")),
    "guh":    ("move down", lambda: parrot_actions.mouse_move_dir("down")),
    "eh":     ("track full", parrot_actions.tracking_activate_full),
    "er":     ("mark target next", lambda: parrot_actions.mouse_pos_mark_next(MARK_NAMES)),
    "er ee":  ("clear all marks", parrot_actions.mouse_pos_clear_all_marks),
    "er ah":  ("mark or goto ah", lambda: parrot_actions.mouse_pos_mark_or_teleport("ah")),
    "er oh":  ("mark or goto oh", lambda: parrot_actions.mouse_pos_mark_or_teleport("oh")),
    "er t":   ("mark or goto t", lambda: parrot_actions.mouse_pos_mark_or_teleport("t")),
    "er sh":  ("mark or goto sh", lambda: parrot_actions.mouse_pos_mark_or_teleport("sh")),
    "er ss":  ("mark or goto ss", lambda: parrot_actions.mouse_pos_mark_or_teleport("ss")),
    "er mm":  ("mark or goto mm", lambda: parrot_actions.mouse_pos_mark_or_teleport("mm")),
    "er guh": ("mark or goto guh", lambda: parrot_actions.mouse_pos_mark_or_teleport("guh")),
    "er pop": ("mark or goto pop", lambda: parrot_actions.mouse_pos_mark_or_teleport("pop")),
    "er palate": ("mark or goto palate", lambda: parrot_actions.mouse_pos_mark_or_teleport("palate")),
    "palate": ("hold or utility", parrot_actions.utility),
    # "tut":        (" ", lambda: None),
    "tut mm":     ("left click drag", lambda: parrot_actions.mouse_click(hold=True)),
    "tut oh":     ("right click", lambda: parrot_actions.mouse_click(button=1)),
    "tut t":      ("toggle shift", lambda: parrot_actions.toggle_modifier("shift")),
    "tut guh":    ("toggle control", lambda: parrot_actions.toggle_modifier("ctrl")),
    "tut ah":     ("toggle alt", lambda: parrot_actions.toggle_modifier("alt")),
    "tut palate": ("utility selector", parrot_actions.show_utility_selector),
    "tut eh":     ("go last pos", parrot_actions.mouse_stopped_pos_cycle),
    "tut pop":    ("go last pos click exit", parrot_actions.mouse_stopped_pos_cycle_click_exit),
    "tut ee":     ("disable modifiers", parrot_actions.disable_modifiers),
    "tut tut":    ("show cheatsheet", parrot_actions.show_cheatsheet),
    "tut hiss":   ("settings", parrot_actions.show_settings),
    "tut shush":  ("settings", parrot_actions.show_settings),
}

input_map_default = {
    **input_map_common,
    "mm":         ("click", parrot_actions.mouse_click),
    "hiss":       ("scroll down", lambda: parrot_actions.scroll("down")),
    "hiss_stop":  ("", parrot_actions.scroll_stop_soft),
    "shush":      ("scroll up", lambda: parrot_actions.scroll("up")),
    "shush_stop": ("", parrot_actions.scroll_stop_soft),
}

input_map_move = {
    **input_map_common,
    "ah":         ("move left", lambda: parrot_actions.mouse_move_or_slow_dir("left")),
    "oh":         ("move right", lambda: parrot_actions.mouse_move_or_slow_dir("right")),
    "t":          ("move up", lambda: parrot_actions.mouse_move_or_slow_dir("up")),
    "guh":        ("move down", lambda: parrot_actions.mouse_move_or_slow_dir("down")),
    "eh":         ("toggle glide", parrot_actions.mouse_toggle_glide),
    "mm":         ("click", parrot_actions.click_with_mode_behavior),
    "shush":      ("boost large", parrot_actions.mouse_boost_large),
    "shush_stop": ("", lambda: None),
    "hiss":       ("boost small", parrot_actions.mouse_boost_small),
    "hiss_stop":  ("", lambda: None),
}

input_map_head = {
    **input_map_common,
    "mm":         ("click", parrot_actions.click_with_mode_behavior),
    "hiss":       ("scroll down", lambda: parrot_actions.scroll_with_mode_reset("down")),
    "hiss_stop":  ("", parrot_actions.scroll_stop_soft),
    "shush":      ("scroll up", lambda: parrot_actions.scroll_with_mode_reset("up")),
    "shush_stop": ("", parrot_actions.scroll_stop_soft),
}

input_map_full = {
    **input_map_common,
    "mm":         ("click temp stop", parrot_actions.click_with_mode_behavior),
    "tut":        ("windows zoom out", lambda: actions.key("win-keypad_minus")),
    "tut tut":    ("reset zoom", lambda: actions.key("win-escape")),
    "hiss":       ("scroll down", lambda: parrot_actions.scroll("down")),
    "hiss_stop":  ("", parrot_actions.scroll_stop_soft_temp),
    "shush":      ("scroll up", lambda: parrot_actions.scroll("up")),
    "shush_stop": ("", parrot_actions.scroll_stop_soft_temp),
}

input_map = {
    "default": input_map_default,
    "move": input_map_move,
    "head": input_map_head,
    "full": input_map_full,
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
        # or parrot_actions.mouse_click() for stopping behaviors

    def parrot_rig_repeater():
        """Parrot rig repeater"""
        parrot_actions.repeat()

    def parrot_rig_reverser():
        """Parrot rig reverser"""
        parrot_actions.reverse_repeat()

    # def parrot_rig_utility_1():
    #     """Parrot rig utility 1"""
    #     parrot_actions.utility_1()

    # def parrot_rig_utility_chooser_1():
    #     """Parrot rig utility chooser 1"""
    #     parrot_actions.utility_chooser_1()

    # def parrot_rig_utility_2():
    #     """Parrot rig utility 2"""
    #     parrot_actions.utility_2()

    # def parrot_rig_utility_chooser_2():
    #     """Parrot rig utility chooser 2"""
    #     parrot_actions.utility_chooser_2()

    def parrot_rig_get_state():
        """Get parrot rig state"""
        return parrot_actions.parrot_rig_get_state()

    def parrot_rig_tracking_activate_full():
        """Activate full tracking mode"""
        parrot_actions.tracking_activate_full()

    def parrot_rig_reload():
        """Reload parrot rig"""
        parrot_actions.reload_files()

    def parrot_rig_get_mode():
        """Get current mode for parrot mode"""
        return parrot_actions.parrot_mode_get_mode()

    def parrot_rig_show_help():
        """Show parrot rig help/cheatsheet"""
        parrot_actions.show_cheatsheet()
