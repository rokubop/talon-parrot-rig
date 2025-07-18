from talon import Module, Context, actions, app
from .parrot_actions import parrot_actions
from .constants import *
from . import parrot_mode_ui  # Import UI module to register actions
from .events import event_manager

mod = Module()
mod.mode("parrot_v7", "parrot mode v7")

ctx_parrot_mode = Context()
ctx_parrot_mode.matches = """
mode: user.parrot_v7
"""

# Common noises for all modes
parrot_config_common = {
    "ee": ("stop", parrot_actions.stopper),
    "pop": ("click exit", parrot_actions.click_exit),
    "cluck": ("exit", parrot_actions.parrot_mode_disable),

    # Movement activation with mode change
    "ah": ("move left", lambda: parrot_actions.move_and_activate("left")),
    "oh": ("move right", lambda: parrot_actions.move_and_activate("right")),
    "t": ("move up", lambda: parrot_actions.move_and_activate("up")),
    "guh": ("move down", lambda: parrot_actions.move_and_activate("down")),

    # Mode switches
    "eh": ("head mode", parrot_actions.tracking_activate_head),
    "er": ("full mode", parrot_actions.tracking_activate_full),

    # Utility functions
    "tut mm": ("left click drag", lambda: parrot_actions.click(hold=True)),
    "tut oh": ("right click", lambda: parrot_actions.click(button=1)),
    "tut t": ("toggle shift", lambda: parrot_actions.toggle_modifier("shift")),
    "tut guh": ("toggle control", lambda: parrot_actions.toggle_modifier("ctrl")),
    "tut ah": ("toggle alt", lambda: parrot_actions.toggle_modifier("alt")),

    # Mode switches with tut
    "tut cluck": ("window mode", parrot_actions.set_window_mode),
    "tut pop": ("keyboard mode", parrot_actions.set_keyboard_mode),
    "tut er": ("number mode", parrot_actions.set_number_mode),

    # UI functions
    "tut palate": ("utility selector", parrot_actions.show_utility_selector),
    "tut tut": ("noise reference", parrot_actions.show_noise_reference),
    "tut hiss": ("settings", parrot_actions.show_settings),
    "tut shush": ("settings", parrot_actions.show_settings),

    # Utility action
    "palate": ("utility", parrot_actions.utility),
}

# Default mode config
parrot_config_default = {
    **parrot_config_common,
    "mm": ("click", parrot_actions.click),
    "hiss": ("scroll down", lambda: parrot_actions.scroll("down")),
    "hiss_stop": ("", parrot_actions.scroll_stop_soft),
    "shush": ("scroll up", lambda: parrot_actions.scroll("up")),
    "shush_stop": ("", parrot_actions.scroll_stop_soft),
}

# Move mode config
parrot_config_move = {
    **parrot_config_common,
    "mm": ("click", parrot_actions.click_with_mode_behavior),
    "shush":        ("boost large", parrot_actions.boost_large),
    "shush_stop":   ("", lambda: None),
    "hiss":         ("boost small", parrot_actions.boost_small),
    "hiss_stop":    ("", lambda: None),
}

# Head mode config
parrot_config_head = {
    **parrot_config_common,
    "mm": ("click", parrot_actions.click_with_mode_behavior),
    "hiss": ("scroll down", lambda: parrot_actions.scroll("down")),
    "hiss_stop": ("", parrot_actions.scroll_stop_soft),
    "shush": ("scroll up", lambda: parrot_actions.scroll("up")),
    "shush_stop": ("", parrot_actions.scroll_stop_soft),
}

# Full mode config
parrot_config_full = {
    **parrot_config_common,
    "mm": ("click temp stop", parrot_actions.click_with_mode_behavior),
    "hiss": ("scroll down", lambda: parrot_actions.scroll("down")),
    "hiss_stop": ("", parrot_actions.scroll_stop_soft_temp),
    "shush": ("scroll up", lambda: parrot_actions.scroll("up")),
    "shush_stop": ("", parrot_actions.scroll_stop_soft_temp),
}

# Window mode config
parrot_config_window = {
    "ah": ("snap left", lambda: actions.user.snap_window_to_position("left")),
    "oh": ("snap right", lambda: actions.user.snap_window_to_position("right")),
    "eh": ("snap full", lambda: actions.user.snap_window_to_position("full")),
    "guh": ("window minimize", actions.user.window_minimize),
    "hiss": ("screen right", parrot_actions.screen_right),
    "shush": ("screen left", parrot_actions.screen_left),
    "pop": ("window cycle next", actions.app.window_next),
    "palate": ("window cycle previous", actions.app.window_previous),
    "er": ("window close", parrot_actions.window_close),
    "tut": ("window swap", parrot_actions.window_swap),
    "cluck": ("return to previous", parrot_actions.return_to_previous_mode),

    # Application switches
    "tut ee": ("app switch 1", lambda: parrot_actions.app_switch(1)),
    "tut er": ("app switch 2", lambda: parrot_actions.app_switch(2)),
    "tut ah": ("app switch 3", lambda: parrot_actions.app_switch(3)),
    "tut hiss": ("app switch 4", lambda: parrot_actions.app_switch(4)),
    "tut shush": ("app switch 5", lambda: parrot_actions.app_switch(5)),
    "tut mm": ("app switch 6", lambda: parrot_actions.app_switch(6)),
    "tut guh": ("app switch 7", lambda: parrot_actions.app_switch(7)),
    "tut t": ("app switch 8", lambda: parrot_actions.app_switch(8)),
    "tut eh": ("app switch 9", lambda: parrot_actions.app_switch(9)),
    "tut oh": ("app switch 0", lambda: parrot_actions.app_switch(0)),
}

# Keyboard mode config
parrot_config_keyboard = {
    "ah": ("left arrow", lambda: actions.key("left")),
    "oh": ("right arrow", lambda: actions.key("right")),
    "t": ("up arrow", lambda: actions.key("up")),
    "guh": ("down arrow", lambda: actions.key("down")),
    "palate": ("tab", lambda: actions.key("tab")),
    "hiss": ("backspace", lambda: actions.key("backspace")),
    "shush": ("delete", lambda: actions.key("delete")),
    "tut": ("escape", lambda: actions.key("escape")),
    "pop": ("enter", lambda: actions.key("enter")),
    "cluck": ("return to previous", parrot_actions.return_to_previous_mode),
}

# Number mode config
parrot_config_number = {
    "oh": ("0", lambda: actions.key("0")),
    "ee": ("1", lambda: actions.key("1")),
    "er": ("2", lambda: actions.key("2")),
    "ah": ("3", lambda: actions.key("3")),
    "hiss": ("4", lambda: actions.key("4")),
    "shush": ("5", lambda: actions.key("5")),
    "mm": ("6", lambda: actions.key("6")),
    "guh": ("7", lambda: actions.key("7")),
    "t": ("8", lambda: actions.key("8")),
    "eh": ("9", lambda: actions.key("9")),
    "palate": ("tab", lambda: actions.key("tab")),
    "tut": ("escape", lambda: actions.key("escape")),
    "pop": ("enter", lambda: actions.key("enter")),
    "cluck": ("return to previous", parrot_actions.return_to_previous_mode),
}

# Complete parrot configuration
parrot_config = {
    "default": parrot_config_default,
    "move": parrot_config_move,
    "head": parrot_config_head,
    "full": parrot_config_full,
    "window": parrot_config_window,
    "keyboard": parrot_config_keyboard,
    "number": parrot_config_number,
}

@ctx_parrot_mode.action_class("user")
class Actions:
    def parrot_config():
        return parrot_config

@mod.action_class
class Actions:
    def parrot_mode_v7_enable():
        """Enable parrot mode v7"""
        parrot_actions.parrot_mode_enable()

    def parrot_mode_v7_disable():
        """Disable parrot mode v7"""
        parrot_actions.parrot_mode_disable()

    def parrot_mode_v7_toggle():
        """Toggle parrot mode v7"""
        parrot_actions.parrot_mode_toggle()