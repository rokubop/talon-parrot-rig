from talon import actions, ctrl, cron
from .tracking import tracking
from ..ui.ui_manager import ui_manager
from .keys import keys
from .events import event_manager
from .repeater import repeat_command, repeat_phrase, reverse_command, reverse_phrase
from ..parrot_rig_settings import (
    MOVE_SPEED,
    SLOW_MODE_MULTIPLIER,
    CLICK_HOLD_MS,
    BOOST_AMOUNT,
    BOOST_OVER_MS,
    BOOST_RELEASE_MS,
    BOOST_SMALL_AMOUNT,
    BOOST_SMALL_REVERT_MS,
    SCROLL_SPEED,
    SCROLL_MOVE_SPEED,
    SCROLL_SLOW_MODE_MULTIPLIER,
    SCROLL_BOOST_AMOUNT,
    SCROLL_BOOST_OVER_MS,
    SCROLL_BOOST_RELEASE_MS,
    SCROLL_BOOST_SMALL_AMOUNT,
    SCROLL_BOOST_SMALL_REVERT_MS,
    TRACKING_STOP_MS,
    CLICK_BEHAVIOR,
)
from .utils import reload_files

class ParrotActions:
    def __init__(self):
        self._is_left_click_held = False
        self._parrot_mode_enabled = False
        self._stop_time_job = None

    def mouse_move_or_slow_dir(self, direction: str):
        cardinal = actions.user.mouse_rig_state_direction_cardinal()
        if actions.user.mouse_rig_state_is_moving() and cardinal == direction:
            actions.user.mouse_rig_speed_mul(SLOW_MODE_MULTIPLIER)
        else:
            self.move(direction)

    def move(self, direction: str):
        tracking.freeze()
        actions.user.mouse_rig_scroll_stop()
        mode = event_manager.get_mode()
        if mode in ("glide", "boost"):
            actions.user.mouse_rig_go_natural(direction, MOVE_SPEED)
        else:
            actions.user.mouse_rig_go(direction, MOVE_SPEED)
        if mode not in ("glide", "boost"):
            event_manager.set_mode("move")

    def mouse_move_dir(self, direction: str):
        self.move(direction)

    def mouse_toggle_glide(self):
        rig = actions.user.mouse_rig()
        rig.bake()
        if event_manager.get_mode() == "glide":
            event_manager.set_mode("move")
        else:
            event_manager.set_mode("glide")

    def mouse_boost(self):
        event_manager.set_mode("boost")
        actions.user.mouse_rig_boost(BOOST_AMOUNT, over_ms=BOOST_OVER_MS, release_ms=BOOST_RELEASE_MS).then(
            lambda: event_manager.return_to_previous_mode()
                if event_manager.get_mode() == "boost" else None)

    def mouse_boost_small(self):
        rig = actions.user.mouse_rig()
        rig.speed.offset.add(BOOST_SMALL_AMOUNT).revert(BOOST_SMALL_REVERT_MS, "ease_out2")

    def tracking_activate(self):
        actions.user.mouse_rig_stop()
        tracking.activate()
        event_manager.set_mode("tracking")

    def click_exit(self):
        self.mouse_click()
        self.parrot_mode_disable()

    def exit(self):
        self.parrot_mode_disable(stop_tracking=not tracking.is_tracking)

    def repeat_command(self):
        repeat_command()

    def repeat_phrase(self):
        repeat_phrase()

    def reverse_command(self):
        reverse_command()

    def reverse_phrase(self):
        reverse_phrase()

    def click_release(self, button=0):
        ctrl.mouse_click(button=button, up=True)
        ui_manager.hide_border()
        self._is_left_click_held = False

    def mouse_click(self, button=0, hold=False):
        current_mode = event_manager.get_mode()

        should_stop = hold != True and (
            (current_mode in CLICK_BEHAVIOR and CLICK_BEHAVIOR[current_mode] == "stop") or
            (current_mode == "tracking")
        )

        if self._is_left_click_held:
            self.click_release(button)
        elif hold:
            ctrl.mouse_click(button=button, down=True)
            ui_manager.show_border()
            self._is_left_click_held = True
        else:
            ctrl.mouse_click(button=button, hold=CLICK_HOLD_MS)
            ui_manager.hide_border()

        if should_stop:
            if current_mode == "tracking":
                self.stop_temporarily()
            else:
                self.stopper()

    def click_with_mode_behavior(self):
        self.mouse_click()

    def scroll(self, direction: str):
        actions.user.mouse_rig_scroll_go(direction, SCROLL_SPEED)

    def scroll_stop(self):
        actions.user.mouse_rig_scroll_stop()

    def scroll_stop_temp(self):
        actions.user.mouse_rig_scroll_stop()
        self.stop_temporarily()

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
            "moving": actions.user.mouse_rig_state_is_moving(),
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
        reload_files()

    def return_to_previous_mode(self):
        event_manager.return_to_previous_mode()

    def toggle_modifier(self, modifier: str):
        keys.toggle_modifier(modifier)

    def disable_modifiers(self):
        keys.clear_modifiers()
        event_manager.clear_modifiers()

    def stopper(self, stop_tracking=True, stop_moving=True, stop_scrolling=True, reset_mode=True):
        if stop_moving:
            actions.user.mouse_rig_stop()
        if stop_scrolling:
            actions.user.mouse_rig_scroll_stop()
        if stop_tracking:
            tracking.freeze()
        if reset_mode:
            event_manager.set_mode("default")

    def stop_temporarily(self):
        actions.user.mouse_rig_stop()
        tracking.freeze()

        # Cancel any existing stop job
        if self._stop_time_job:
            cron.cancel(self._stop_time_job)
        else:
            actions.user.mouse_rig_scroll_stop()

        # Schedule reactivation
        self._stop_time_job = cron.after(f"{TRACKING_STOP_MS}ms", self._reactivate_full_mode)

    def _reactivate_full_mode(self):
        self._stop_time_job = None
        if event_manager.get_mode() == "tracking":
            tracking.activate()

    def show_utility_selector(self, title: str = "Utility"):
        ui_manager.show_utility_selector(title)

    def show_utility2_selector(self, title: str = "Utility 2"):
        ui_manager.show_utility2_selector(title)

    def hide_utility_selector(self):
        ui_manager.hide_utility_selector()

    def hide_utility2_selector(self):
        ui_manager.hide_utility2_selector()

    def show_cheatsheet(self):
        ui_manager.show_cheatsheet()

    def toggle_scroll_move(self):
        mode = event_manager.get_mode()
        if mode in ("scroll_move", "scroll_glide", "scroll_boost"):
            actions.user.mouse_rig_scroll_stop()
            event_manager.set_mode("default")
        else:
            event_manager.set_mode("scroll_move")

    def scroll_move_dir(self, direction: str):
        tracking.freeze()
        actions.user.mouse_rig_stop()
        mode = event_manager.get_mode()
        if mode in ("scroll_glide", "scroll_boost"):
            actions.user.mouse_rig_scroll_go_natural(direction, SCROLL_MOVE_SPEED, False)
        else:
            actions.user.mouse_rig_scroll_go_natural(direction, SCROLL_MOVE_SPEED, False)

    def scroll_move_or_slow_dir(self, direction: str):
        rig = actions.user.mouse_rig()
        cardinal = rig.state.scroll.direction_cardinal.current
        if actions.user.mouse_rig_state_is_scrolling() and cardinal == direction:
            actions.user.mouse_rig_scroll_speed_mul(SCROLL_SLOW_MODE_MULTIPLIER)
        else:
            self.scroll_move_dir(direction)

    def scroll_toggle_glide(self):
        rig = actions.user.mouse_rig()
        rig.bake()
        if event_manager.get_mode() == "scroll_glide":
            event_manager.set_mode("scroll_move")
        else:
            event_manager.set_mode("scroll_glide")

    def scroll_boost(self):
        event_manager.set_mode("scroll_boost")
        actions.user.mouse_rig_scroll_boost(
            SCROLL_BOOST_AMOUNT,
            over_ms=SCROLL_BOOST_OVER_MS,
            release_ms=SCROLL_BOOST_RELEASE_MS
        ).then(
            lambda: event_manager.return_to_previous_mode()
                if event_manager.get_mode() == "scroll_boost" else None
        )

    def scroll_boost_small(self):
        rig = actions.user.mouse_rig()
        rig.scroll.speed.offset.add(SCROLL_BOOST_SMALL_AMOUNT).revert(
            SCROLL_BOOST_SMALL_REVERT_MS, "ease_out2"
        )

    def scroll_stop_stay(self):
        actions.user.mouse_rig_scroll_stop()

parrot_actions = ParrotActions()
