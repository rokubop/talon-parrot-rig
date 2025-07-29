from talon import actions, ctrl, cron
from .src.scrolling import scrolling
from .src.tracking import tracking
from .src.movement import movement
from .visual_interface import visual_interface
from .src.position import position
from .src.keys import keys
from .src.phrase import phrase
from .events import event_manager
from .noise_reference import noise_reference
from .config import (
    CLICK_BEHAVIOR, UTILITY_ACTIONS,
    FULL_MODE_SETTINGS, SETTINGS_OPTIONS
)
from .constants import *
import time

class ParrotActions:
    def __init__(self):
        self.revive_tracking_job = None
        self._is_left_click_held = False
        self._parrot_mode_enabled = False
        self._stop_time_job = None

    # Movement actions
    def move_or_slow(self, direction: str):
        """Move in direction or slow down if already moving that way"""
        if movement.is_moving() and actions.user.mouse_move_info().last_cardinal_dir == direction:
            movement.slower()
        else:
            self.move(direction)

    def move(self, direction: str):
        """Start moving in a direction"""
        tracking.freeze()
        scrolling.scroll_stop_hard()
        movement.move(direction)
        event_manager.set_mode("move")

    def move_and_activate(self, direction: str):
        """Activate move mode and move in direction"""
        self.move(direction)

    def boost_large(self):
        """Boost the cursor movement speed briefly a large amount"""
        movement.boost_large()

    def boost_small(self):
        """Boost the cursor movement speed briefly a small amount"""
        movement.boost_small()

    # Tracking actions
    def tracking_activate_head(self):
        """Activate head tracking mode"""
        movement.stop()
        tracking.activate(full_tracking=False)
        event_manager.set_mode("head")

    def tracking_activate_full(self):
        """Activate full tracking mode"""
        movement.stop()
        tracking.activate(full_tracking=True)
        event_manager.set_mode("full")

    def tracking_toggle(self):
        """Toggle full tracking on/off"""
        tracking.toggle_full_tracking()

    # Click actions
    def click_exit(self):
        """Click and exit parrot mode"""

        self.click()
        self.parrot_mode_disable()

    def click_await_one_phrase(self):
        """Click and await one phrase"""
        self.click()
        self.await_one_phrase()

    def await_one_phrase(self):
        """Disable parrot mode and await next phrase"""
        self.parrot_mode_disable()
        phrase.await_next_phrase(self.parrot_mode_enable)

    def click_release(self, button=0):
        """Release mouse click"""
        ctrl.mouse_click(button=button, up=True)
        visual_interface.hide_border()
        self._is_left_click_held = False

    def click(self, button=0, hold=False):
        """Click or hold mouse button"""
        position.mouse_pos_save()
        current_mode = event_manager.get_mode()

        should_stop = hold != True and (
            (current_mode in CLICK_BEHAVIOR and CLICK_BEHAVIOR[current_mode] == "stop") or
            (current_mode == "full")
        )

        if self._is_left_click_held:
            self.click_release(button)
        elif hold:
            ctrl.mouse_click(button=button, down=True)
            visual_interface.show_border()
            self._is_left_click_held = True
        else:
            ctrl.mouse_click(button=button, hold=16000)
            visual_interface.hide_border()

        if should_stop:
            if current_mode == "full":
                self.stop_temporarily()
            else:
                self.stopper()

    def click_with_mode_behavior(self):
        """Click with current mode behavior"""
        self.click()

    # Scrolling actions
    def scroll(self, direction: str):
        """Start scrolling in direction"""
        scrolling.scroll_start(direction)

    def scroll_stop_soft(self):
        """Stop scrolling softly"""
        scrolling.scroll_stop_soft()

    def scroll_stop_soft_temp(self):
        """Stop scrolling softly and temporarily"""
        scrolling.scroll_stop_soft()
        self.stop_temporarily()

    # Utility actions
    def utility(self):
        """Execute utility action based on current setting"""
        action = event_manager.get_setting("utility_action", "hold_click")

        if action == "click":
            self.click()
        elif action == "hold_click":
            self.click(hold=True)
        elif action == "right_click":
            self.click(button=1)
        elif action == "hold_right_click":
            self.click(button=1, hold=True)
        elif action == "middle_click":
            self.click(button=2)
        elif action == "middle_hold":
            self.click(button=2, hold=True)
        elif action == "repeat_last":
            actions.core.repeat_command()
        elif action == "repeat_phrase":
            actions.user.parrot_v7_repeater()

    # Mode management
    def parrot_mode_enable(self):
        """Enable parrot mode"""
        self._parrot_mode_enabled = True
        actions.mode.enable("user.parrot_v7")
        # event_manager.set_parrot_enabled(True)
        event_manager.set_mode("default")
        visual_interface.show()

    def parrot_mode_disable(self):
        """Disable parrot mode"""
        self._parrot_mode_enabled = False
        if actions.user.ui_elements_is_active("noise_reference"):
            actions.user.ui_elements_hide("noise_reference")
        visual_interface.hide()
        # event_manager.set_parrot_enabled(False)
        self.stopper()
        actions.mode.disable("user.parrot_v7")

    def parrot_mode_toggle(self):
        """Toggle parrot mode"""
        if self._parrot_mode_enabled:
            self.parrot_mode_disable()
        else:
            self.parrot_mode_enable()

    def return_to_previous_mode(self):
        """Return to previous mode"""
        event_manager.return_to_previous_mode()

    # Modifier actions
    def toggle_modifier(self, modifier: str):
        """Toggle modifier key"""
        is_active = keys.toggle_modifier(modifier)
        if is_active:
            event_manager.add_modifier(modifier)
        else:
            event_manager.remove_modifier(modifier)

    def disable_modifiers(self):
        """Disable all modifiers"""
        keys.clear_modifiers()
        event_manager.clear_modifiers()

    # Stop actions
    def stopper(self):
        """Stop all movement and tracking"""
        self.stop_revive_tracking()
        movement.stop()
        scrolling.scroll_stop_hard()
        tracking.freeze()
        event_manager.set_mode("default")

    def stop_temporarily(self):
        """Stop temporarily (for full mode)"""
        movement.stop()
        tracking.freeze()

        # Cancel any existing stop job
        if self._stop_time_job:
            cron.cancel(self._stop_time_job)
        else:
            scrolling.scroll_stop_hard()

        # Schedule reactivation
        stop_time = FULL_MODE_SETTINGS["stop_time"]
        self._stop_time_job = cron.after(f"{stop_time}ms", self._reactivate_full_mode)

    def _reactivate_full_mode(self):
        """Reactivate full mode after temporary stop"""
        self._stop_time_job = None
        if event_manager.get_mode() == "full":
            tracking.activate(full_tracking=True)

    def stop_revive_tracking(self):
        """Stop revive tracking job"""
        if self.revive_tracking_job:
            cron.cancel(self.revive_tracking_job)
            self.revive_tracking_job = None

    def await_revive_tracking(self):
        """Wait and then revive tracking"""
        self.stop_revive_tracking()
        self.revive_tracking_job = cron.after("300ms", tracking.activate)

    # Window management actions
    def window_snap_left(self):
        """Snap window to left"""
        actions.key("win-left")

    def window_snap_right(self):
        """Snap window to right"""
        actions.key("win-right")

    def window_snap_full(self):
        """Snap window to full screen"""
        actions.key("win-up")

    def window_close(self):
        """Close window"""
        actions.key("alt-f4")

    def window_swap(self):
        """Swap windows (alt-tab)"""
        actions.key("alt-tab")

    def screen_left(self):
        """Move window to left screen"""
        actions.key("win-shift-left")

    def screen_right(self):
        """Move window to right screen"""
        actions.key("win-shift-right")

    def app_switch(self, number: int):
        """Switch to application number"""
        actions.key(f"win-{number}")

    # Mode switching actions
    def set_window_mode(self):
        """Set window mode"""
        event_manager.set_mode("window")

    def set_keyboard_mode(self):
        """Set keyboard mode"""
        event_manager.set_mode("keyboard")

    def set_number_mode(self):
        """Set number mode"""
        event_manager.set_mode("number")

    def create_action_button(self, action_key: str, action_name: str):
        state, button, text = actions.user.ui_elements(["state", "button", "text"])
        current_action, set_current_action = state.use("utility_action", "hold_click")
        is_selected = current_action == action_key
        bg_color = "#3E84DA" if is_selected else "#4A4A4A"

        return button(
            padding=8,
            border_width=1,
            border_radius=4,
            # border_color="#666666",
            background_color=bg_color,
            on_click=lambda: [
                event_manager.set_setting("utility_action", action_key),
                set_current_action(action_key)
            ]
        )[
            text(action_name, color="#FFFFFF", font_weight="bold" if is_selected else "normal")
        ]

    def utility_selector(self):
        screen, window, div, text = actions.user.ui_elements(["screen", "window", "div", "text"])

        return screen(justify_content="center", align_items="center")[
            window(
                id="utility_selector",
                title="Utility Selector",
                padding=16,
            )[
                div(flex_direction="column", gap=10)[
                    div(flex_direction="column", gap=5)[
                        *[self.create_action_button(key, name) for key, name in UTILITY_ACTIONS.items()]
                    ]
                ]
            ]
        ]

    def show_utility_selector(self):
        actions.user.ui_elements_toggle(self.utility_selector)

    def show_noise_reference(self):
        """Show noise reference UI"""
        actions.user.ui_elements_toggle(noise_reference)

    def show_settings(self):
        """Show settings UI - placeholder for now"""
        print("Settings UI - not implemented yet")

    def scroll_with_stop(self, direction: str):
        """Scroll after stopping (for head mode)"""
        self.stopper()
        self.scroll(direction)

    def scroll_with_temp_stop(self, direction: str):
        """Scroll after temporary stop (for full mode)"""
        self.stop_temporarily()
        self.scroll(direction)

    def scroll_with_mode_reset(self, direction: str):
        """Scroll and reset to default mode (for head mode)"""
        tracking.freeze()
        event_manager.set_mode("default")
        self.scroll(direction)

    # Utility functions
    def is_active(self):
        """Check if any parrot action is active"""
        return tracking.is_tracking or movement.is_moving() or scrolling.is_scrolling()

# Global instance
parrot_actions = ParrotActions()
