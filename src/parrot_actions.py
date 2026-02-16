from talon import actions, ctrl, cron
from .tracking import tracking
from .movement import movement
from ..ui.ui_manager import ui_manager
from .keys import keys
from .events import event_manager
from .repeater import repeat, reverse
from ..user_settings import (
    CLICK_BEHAVIOR,
    FULL_MODE_SETTINGS,
    SCROLLING_SETTINGS,
)
from .constants import *
from .utils import utils

class ParrotActions:
    def __init__(self):
        self.revive_tracking_job = None
        self._is_left_click_held = False
        self._parrot_mode_enabled = False
        self._stop_time_job = None

    def mouse_move_or_slow_dir(self, direction: str):
        cardinal = actions.user.mouse_rig_state_direction_cardinal()
        if movement.is_moving() and cardinal == direction:
            movement.slower()
        else:
            self.move(direction)

    def move(self, direction: str):
        tracking.freeze()
        actions.user.mouse_rig_scroll_stop()
        movement.move(direction)
        if event_manager.get_mode() not in ("glide", "boost"):
            event_manager.set_mode("move")

    def mouse_move_dir(self, direction: str):
        self.move(direction)

    def mouse_toggle_glide(self):
        movement.preserve_direction()
        if event_manager.get_mode() == "glide":
            event_manager.set_mode("move")
        else:
            event_manager.set_mode("glide")

    def mouse_boost(self):
        event_manager.set_mode("boost")
        movement.boost(
            lambda: event_manager.return_to_previous_mode() \
                if event_manager.get_mode() == "boost" else None)

    def mouse_boost_small(self):
        movement.boost_small()

    def tracking_activate(self):
        movement.stop()
        tracking.activate()
        event_manager.set_mode("full")

    def click_exit(self):
        self.mouse_click()
        self.parrot_mode_disable()

    def exit(self):
        self.parrot_mode_disable(stop_tracking=not tracking.is_tracking)

    def repeat(self):
        repeat()

    def reverse_repeat(self):
        reverse()

    def click_release(self, button=0):
        ctrl.mouse_click(button=button, up=True)
        ui_manager.hide_border()
        self._is_left_click_held = False

    def mouse_click(self, button=0, hold=False):
        current_mode = event_manager.get_mode()

        should_stop = hold != True and (
            (current_mode in CLICK_BEHAVIOR and CLICK_BEHAVIOR[current_mode] == "stop") or
            (current_mode == "full")
        )

        if self._is_left_click_held:
            self.click_release(button)
        elif hold:
            ctrl.mouse_click(button=button, down=True)
            ui_manager.show_border()
            self._is_left_click_held = True
        else:
            ctrl.mouse_click(button=button, hold=16000)
            ui_manager.hide_border()

        if should_stop:
            if current_mode == "full":
                self.stop_temporarily()
            else:
                self.stopper()

    def click_with_mode_behavior(self):
        self.mouse_click()

    def scroll(self, direction: str):
        actions.user.mouse_rig_scroll_go(direction, SCROLLING_SETTINGS["speed"])

    def scroll_stop(self):
        actions.user.mouse_rig_scroll_stop()

    def scroll_stop_temp(self):
        actions.user.mouse_rig_scroll_stop()
        self.stop_temporarily()

    def utility(self):
        action = event_manager.get_setting("utility_action", "hold_click")

        if action == "click":
            self.mouse_click()
        elif action == "hold_click":
            self.mouse_click(hold=True)
        elif action == "right_click":
            self.mouse_click(button=1)
        elif action == "hold_right_click":
            self.mouse_click(button=1, hold=True)
        elif action == "middle_click":
            self.mouse_click(button=2)
        elif action == "middle_hold":
            self.mouse_click(button=2, hold=True)
        elif action == "repeat_last":
            actions.core.repeat_command()
        elif action == "repeat_phrase":
            actions.user.parrot_rig_repeater()

    def parrot_mode_enable(self):
        self._parrot_mode_enabled = True
        actions.mode.disable("command")
        actions.mode.enable("user.parrot_rig")
        event_manager.set_mode("default")
        ui_manager.show()
        print("Parrot mode enabled")

    def parrot_mode_disable(
            self,
            stop_tracking=True,
            stop_moving=True,
            stop_scrolling=True,
            disable_mods=True
        ):
        self._parrot_mode_enabled = False
        ui_manager.hide_cheatsheet()
        ui_manager.hide()

        self.stopper(
            stop_tracking=stop_tracking,
            stop_moving=stop_moving,
            stop_scrolling=stop_scrolling,
            reset_mode=True)

        if disable_mods:
            self.disable_modifiers()

        if self._is_left_click_held:
            self.click_release()

        actions.mode.disable("user.parrot_rig")
        actions.mode.enable("command")
        print("Parrot mode disabled")

    def parrot_rig_get_state(self):
        return {
            "enabled": self._parrot_mode_enabled,
            "tracking": tracking.is_tracking,
            "moving": movement.is_moving(),
            "scrolling": actions.user.mouse_rig_state_is_scrolling(),
            "mode": event_manager.get_mode(),
            "modifiers": event_manager.get_modifiers(),
            "click_held": self._is_left_click_held,
        }

    def parrot_mode_get_mode(self):
        return event_manager.get_mode()

    def parrot_mode_toggle(self):
        if self._parrot_mode_enabled:
            self.parrot_mode_disable()
        else:
            self.parrot_mode_enable()

    def reload_files(self):
        utils.reload_files()

    def return_to_previous_mode(self):
        event_manager.return_to_previous_mode()

    def toggle_modifier(self, modifier: str):
        keys.toggle_modifier(modifier)

    def disable_modifiers(self):
        keys.clear_modifiers()
        event_manager.clear_modifiers()

    def stopper(self, stop_tracking=True, stop_moving=True, stop_scrolling=True, reset_mode=True):
        self.stop_revive_tracking()
        if stop_moving:
            movement.stop()
        if stop_scrolling:
            actions.user.mouse_rig_scroll_stop()
        if stop_tracking:
            tracking.freeze()
        if reset_mode:
            event_manager.set_mode("default")

    def stop_temporarily(self):
        movement.stop()
        tracking.freeze()

        # Cancel any existing stop job
        if self._stop_time_job:
            cron.cancel(self._stop_time_job)
        else:
            actions.user.mouse_rig_scroll_stop()

        # Schedule reactivation
        stop_time = FULL_MODE_SETTINGS["stop_time"]
        self._stop_time_job = cron.after(f"{stop_time}ms", self._reactivate_full_mode)

    def _reactivate_full_mode(self):
        self._stop_time_job = None
        if event_manager.get_mode() == "full":
            tracking.activate()

    def stop_revive_tracking(self):
        if self.revive_tracking_job:
            cron.cancel(self.revive_tracking_job)
            self.revive_tracking_job = None

    def await_revive_tracking(self):
        self.stop_revive_tracking()
        self.revive_tracking_job = cron.after("300ms", tracking.activate)

    def show_utility_selector(self):
        ui_manager.show_utility_selector()

    def show_cheatsheet(self):
        ui_manager.show_cheatsheet()

    def show_settings(self):
        print("Settings UI - not implemented yet")

    def scroll_with_stop(self, direction: str):
        self.stopper()
        self.scroll(direction)

    def scroll_with_temp_stop(self, direction: str):
        self.stop_temporarily()
        self.scroll(direction)

    def scroll_with_mode_reset(self, direction: str):
        tracking.freeze()
        event_manager.set_mode("default")
        self.scroll(direction)

    def is_active(self):
        return tracking.is_tracking or movement.is_moving() or actions.user.mouse_rig_state_is_scrolling()

parrot_actions = ParrotActions()
