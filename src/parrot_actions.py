from talon import actions, ctrl, cron
from .scrolling import scrolling
from .tracking import tracking
from .movement import movement
from ..ui.ui_manager import ui_manager
from .position import position
from .keys import keys
from .phrase import phrase
from .events import event_manager
from .utils import utils, get_screen
from ..user_settings import (
    CLICK_BEHAVIOR,
    FULL_MODE_SETTINGS
)
from .constants import *

class ParrotActions:
    def __init__(self):
        self.revive_tracking_job = None
        self._is_left_click_held = False
        self._parrot_mode_enabled = False
        self._stop_time_job = None

    def mouse_move_or_slow_dir(self, direction: str):
        rig = actions.user.mouse_rig()
        print(rig.state.base)
        cardinal = rig.state.base.direction.to_cardinal()
        if movement.is_moving() and cardinal == direction:
            if any("boost" in layer for layer in rig.state.layers):
                rig.bake()
            movement.slower()
        else:
            self.move(direction)

    def move(self, direction: str):
        tracking.freeze()
        scrolling.scroll_stop_hard()
        # Only save position if transitioning into move mode (not already moving)
        if event_manager.get_mode() != "move":
            position.mouse_stopped_pos_save()
        movement.move(direction)
        rig = actions.user.mouse_rig()
        if event_manager.get_mode() == "glide":
            return
        event_manager.set_mode("boost" if "boost_large" in rig.state.layers else "move")

    def mouse_move_dir(self, direction: str):
        self.move(direction)

    def mouse_toggle_glide(self):
        movement.preserve_direction()
        if event_manager.get_mode() == "glide":
            event_manager.set_mode("move")
        else:
            event_manager.set_mode("glide")

    def mouse_boost_large(self):
        event_manager.set_mode("boost")
        movement.boost_large(
            lambda: event_manager.return_to_previous_mode() \
                if event_manager.get_mode() == "boost" else None)

    def mouse_boost_small(self):
        movement.boost_small()

    def tracking_activate_head(self):
        movement.stop()
        # Only save position if transitioning into tracking mode (not already tracking)
        if event_manager.get_mode() not in ["head", "full"]:
            position.mouse_stopped_pos_save()
        tracking.activate(full_tracking=False)
        event_manager.set_mode("head")

    def tracking_activate_full(self):
        movement.stop()
        # Only save position if transitioning into tracking mode (not already tracking)
        if event_manager.get_mode() not in ["head", "full"]:
            position.mouse_stopped_pos_save()
        tracking.activate(full_tracking=True)
        event_manager.set_mode("full")

    def tracking_toggle(self):
        tracking.toggle_full_tracking()

    def click_exit(self):
        self.mouse_click()
        self.parrot_mode_disable()

    def exit(self):
        self.parrot_mode_disable(stop_tracking=not tracking.is_tracking)

    def click_await_one_phrase(self):
        self.mouse_click()
        self.await_one_phrase()

    def await_one_phrase(self):
        self.parrot_mode_disable()
        phrase.await_next_phrase(self.parrot_mode_enable)

    def click_release(self, button=0):
        ctrl.mouse_click(button=button, up=True)
        ui_manager.hide_border()
        self._is_left_click_held = False

    def mouse_click(self, button=0, hold=False):
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
        scrolling.scroll_start(direction)

    def scroll_stop_soft(self):
        scrolling.scroll_stop_soft()

    def scroll_stop_soft_temp(self):
        scrolling.scroll_stop_soft()
        self.stop_temporarily()

    def mouse_pos_mark_or_teleport(self, noise: str):
        print("noise", noise)
        position.mouse_pos_mark_or_teleport(noise)

    def mouse_pos_tele_nearest(self):
        position.mouse_pos_tele_nearest()

    def mouse_pos_go_last(self):
        position.mouse_pos_swap_last()

    def mouse_stopped_pos_go_last(self):
        position.mouse_stopped_pos_go_last()

    def mouse_stopped_pos_cycle(self):
        position.mouse_stopped_pos_cycle()

    def mouse_stopped_pos_cycle_click_exit(self):
        position.mouse_stopped_pos_cycle()
        self.click_exit()

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
            actions.user.parrot_v7_repeater()

    def parrot_mode_enable(self):
        self._parrot_mode_enabled = True
        actions.mode.disable("command")
        actions.mode.enable("user.parrot_v7")
        # event_manager.set_parrot_enabled(True)
        event_manager.set_mode("default")
        ui_manager.show()
        position.mouse_stopped_pos_save()
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

        actions.mode.disable("user.parrot_v7")
        actions.mode.enable("command")
        print("Parrot mode disabled")

    def parrot_mode_get_state(self):
        return {
            "enabled": self._parrot_mode_enabled,
            "tracking": tracking.is_tracking,
            "moving": movement.is_moving(),
            "scrolling": scrolling.is_scrolling(),
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
            scrolling.scroll_stop_hard()
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
            scrolling.scroll_stop_hard()

        # Schedule reactivation
        stop_time = FULL_MODE_SETTINGS["stop_time"]
        self._stop_time_job = cron.after(f"{stop_time}ms", self._reactivate_full_mode)

    def _reactivate_full_mode(self):
        self._stop_time_job = None
        if event_manager.get_mode() == "full":
            tracking.activate(full_tracking=True)

    def stop_revive_tracking(self):
        if self.revive_tracking_job:
            cron.cancel(self.revive_tracking_job)
            self.revive_tracking_job = None

    def await_revive_tracking(self):
        self.stop_revive_tracking()
        self.revive_tracking_job = cron.after("300ms", tracking.activate)

    def window_snap_left(self):
        actions.key("win-left")

    def window_snap_right(self):
        actions.key("win-right")

    def window_snap_full(self):
        actions.key("win-up")

    def window_close(self):
        actions.key("alt-f4")

    def window_swap(self):
        actions.key("alt-tab")

    def screen_left(self):
        actions.key("win-shift-left")

    def screen_right(self):
        actions.key("win-shift-right")

    def app_switch(self, number: int):
        actions.key(f"win-{number}")

    def set_window_mode(self):
        event_manager.set_mode("window")

    def set_keyboard_mode(self):
        event_manager.set_mode("keyboard")

    def set_number_mode(self):
        event_manager.set_mode("number")

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

    def zoom_in(self):
        utils.zoom_in()

    def is_active(self):
        return tracking.is_tracking or movement.is_moving() or scrolling.is_scrolling()

parrot_actions = ParrotActions()
