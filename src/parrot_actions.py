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
    BOOST_LONG_AMOUNT,
    BOOST_LONG_OVER_MS,
    BOOST_LONG_RELEASE_MS,
    BOOST_BURST_AMOUNT,
    BOOST_BURST_REVERT_MS,
    GLIDE_RELEASE_RATE,
    SCROLL_SPEED,
    SCROLL_MOVE_SPEED,
    SCROLL_SLOW_MODE_MULTIPLIER,
    SCROLL_BOOST_LONG_AMOUNT,
    SCROLL_BOOST_LONG_OVER_MS,
    SCROLL_BOOST_LONG_RELEASE_MS,
    SCROLL_BOOST_BURST_AMOUNT,
    SCROLL_BOOST_BURST_REVERT_MS,
    SCROLL_RAMP_AMOUNT,
    SCROLL_RAMP_REVERT_MS,
    SCROLL_GLIDE_RELEASE_RATE,
    TRACKING_STOP_MS,
    CLICK_BEHAVIOR,
)
from .utils import reload_files

class ParrotActions:
    def __init__(self):
        self._is_left_click_held = False
        self._parrot_mode_enabled = False
        self._stop_time_job = None
        self._move_speed_level = 0
        self._scroll_speed_level = 0
        self._scroll_direction = "down"

    def _get_move_speed(self):
        return MOVE_SPEED * (SLOW_MODE_MULTIPLIER ** self._move_speed_level)

    def _get_scroll_move_speed(self):
        return SCROLL_MOVE_SPEED * (SCROLL_SLOW_MODE_MULTIPLIER ** self._scroll_speed_level)

    def _emit_speed_level(self):
        mode = event_manager.get_mode()
        if mode in ("scroll_stop", "scroll_move", "scroll_glide", "scroll_boost", "scroll_tracking"):
            level = self._scroll_speed_level
        else:
            level = self._move_speed_level
        event_manager.emit("speed_level_changed", {"level": level})

    def mouse_move_or_slow_dir(self, direction: str):
        cardinal = actions.user.mouse_rig_state_direction_cardinal()
        if actions.user.mouse_rig_state_is_moving() and cardinal == direction:
            self._move_speed_level += 1
            actions.user.mouse_rig_speed_mul(SLOW_MODE_MULTIPLIER)
            self._emit_speed_level()
        else:
            self.move(direction)

    def move(self, direction: str):
        tracking.freeze()
        actions.user.mouse_rig_scroll_stop()
        mode = event_manager.get_mode()
        speed = self._get_move_speed()
        current_speed = actions.user.mouse_rig_state_speed()
        if mode in ("glide", "boost") or current_speed > speed:
            actions.user.mouse_rig_go_natural(direction, speed)
        else:
            actions.user.mouse_rig_go(direction, speed)
        if mode not in ("glide", "boost"):
            event_manager.set_mode("move")
            self._emit_speed_level()

    def mouse_move_dir(self, direction: str):
        self.move(direction)

    def mouse_toggle_glide(self):
        rig = actions.user.mouse_rig()
        rig.bake()
        if event_manager.get_mode() == "glide":
            speed = self._get_move_speed()
            rig.speed.to(speed).over(rate=GLIDE_RELEASE_RATE, easing="ease_out2")
            event_manager.set_mode("move")
        else:
            event_manager.set_mode("glide")

    def _move_speed_scale(self):
        return SLOW_MODE_MULTIPLIER ** self._move_speed_level

    def _scroll_speed_scale(self):
        return SCROLL_SLOW_MODE_MULTIPLIER ** self._scroll_speed_level

    def mouse_boost_long(self):
        event_manager.set_mode("boost")
        amount = BOOST_LONG_AMOUNT * self._move_speed_scale()
        actions.user.mouse_rig_boost(amount, over_ms=BOOST_LONG_OVER_MS, release_ms=BOOST_LONG_RELEASE_MS).then(
            lambda: event_manager.return_to_previous_mode()
                if event_manager.get_mode() == "boost" else None)

    def mouse_boost_burst(self):
        rig = actions.user.mouse_rig()
        rig.layer("hiss_boost").speed.offset.add(BOOST_BURST_AMOUNT)

    def mouse_boost_burst_stop(self):
        rig = actions.user.mouse_rig()
        rig.layer("hiss_boost").revert(BOOST_BURST_REVERT_MS, "ease_out2")

    def tracking_activate(self):
        actions.user.mouse_rig_stop()
        tracking.activate()
        event_manager.set_mode("tracking")

    def scroll_tracking_activate(self):
        actions.user.mouse_rig_scroll_stop()
        actions.user.mouse_rig_stop()
        tracking.activate()
        event_manager.set_mode("scroll_tracking")

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

    def reset_speed_level(self):
        mode = event_manager.get_mode()
        if mode in ("scroll_stop", "scroll_move", "scroll_glide", "scroll_boost", "scroll_tracking"):
            if self._scroll_speed_level == 0:
                return
            level = self._scroll_speed_level
            self._scroll_speed_level = 0
            if actions.user.mouse_rig_state_is_scrolling():
                restore = 1.0 / (SCROLL_SLOW_MODE_MULTIPLIER ** level)
                actions.user.mouse_rig_scroll_speed_mul(restore)
        else:
            if self._move_speed_level == 0:
                return
            level = self._move_speed_level
            self._move_speed_level = 0
            if actions.user.mouse_rig_state_is_moving():
                restore = 1.0 / (SLOW_MODE_MULTIPLIER ** level)
                actions.user.mouse_rig_speed_mul(restore)
        self._emit_speed_level()

    def click_release(self, button=0):
        ctrl.mouse_click(button=button, up=True)
        ui_manager.hide_border()
        self._is_left_click_held = False

    def mouse_click(self, button=0, hold=False):
        current_mode = event_manager.get_mode()

        should_stop = hold != True and (
            (current_mode in CLICK_BEHAVIOR and CLICK_BEHAVIOR[current_mode] == "stop") or
            (current_mode in ("tracking", "scroll_tracking"))
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
            if current_mode in ("tracking", "scroll_tracking"):
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
        from ..parrot_rig_actions import channel_init
        self._parrot_mode_enabled = True
        channel_init()
        actions.mode.disable("command")
        actions.mode.enable("user.parrot_rig")
        event_manager.set_mode("default")
        ui_manager.show()
        self._emit_speed_level()
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
        if event_manager.get_mode() in ("tracking", "scroll_tracking"):
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
        if mode == "tracking":
            event_manager.set_mode("scroll_tracking")
        elif mode == "scroll_tracking":
            event_manager.set_mode("tracking")
        elif mode in ("scroll_stop", "scroll_move", "scroll_glide", "scroll_boost"):
            actions.user.mouse_rig_scroll_stop()
            event_manager.set_mode("default")
        else:
            actions.user.mouse_rig_move_stop()
            event_manager.set_mode("scroll_stop")
        self._emit_speed_level()

    def scroll_move_dir(self, direction: str):
        tracking.freeze()
        actions.user.mouse_rig_move_stop()
        mode = event_manager.get_mode()
        speed = self._get_scroll_move_speed()
        rig = actions.user.mouse_rig()
        current_scroll_speed = rig.state.scroll_speed
        if mode in ("scroll_glide", "scroll_boost") or current_scroll_speed > speed:
            actions.user.mouse_rig_scroll_go_natural(direction, speed, scale=3.0)
        else:
            actions.user.mouse_rig_scroll_go(direction, speed)
        self._scroll_direction = direction
        event_manager.emit("scroll_direction_changed", {"direction": direction})
        if mode not in ("scroll_glide", "scroll_boost"):
            event_manager.set_mode("scroll_move")
            self._emit_speed_level()

    def scroll_move_or_slow_dir(self, direction: str):
        rig = actions.user.mouse_rig()
        cardinal = rig.state.scroll.direction_cardinal.current
        if actions.user.mouse_rig_state_is_scrolling() and cardinal == direction:
            self._scroll_speed_level += 1
            actions.user.mouse_rig_scroll_speed_mul(SCROLL_SLOW_MODE_MULTIPLIER)
            self._emit_speed_level()
        else:
            self.scroll_move_dir(direction)

    def scroll_toggle_glide(self):
        rig = actions.user.mouse_rig()
        rig.scroll.bake()
        if event_manager.get_mode() == "scroll_glide":
            speed = self._get_scroll_move_speed()
            rig.scroll.speed.to(speed).over(rate=SCROLL_GLIDE_RELEASE_RATE, easing="ease_out2")
            event_manager.set_mode("scroll_move")
        else:
            event_manager.set_mode("scroll_glide")

    def scroll_boost_long(self):
        event_manager.set_mode("scroll_boost")
        amount = SCROLL_BOOST_LONG_AMOUNT * self._scroll_speed_scale()
        actions.user.mouse_rig_scroll_boost(
            amount,
            over_ms=SCROLL_BOOST_LONG_OVER_MS,
            release_ms=SCROLL_BOOST_LONG_RELEASE_MS
        ).then(
            lambda: event_manager.return_to_previous_mode()
                if event_manager.get_mode() == "scroll_boost" else None
        )

    def scroll_boost_burst(self):
        rig = actions.user.mouse_rig()
        rig.layer("hiss_scroll_boost").scroll.speed.offset.add(SCROLL_BOOST_BURST_AMOUNT)

    def scroll_boost_burst_stop(self):
        rig = actions.user.mouse_rig()
        rig.layer("hiss_scroll_boost").revert(SCROLL_BOOST_BURST_REVERT_MS, "ease_out2")

    def scroll_stop_stay(self):
        actions.user.mouse_rig_scroll_stop()
        tracking.freeze()
        event_manager.set_mode("scroll_stop")

    def scroll_ramp_dir(self, direction: str):
        self.scroll_move_dir(direction)
        rig = actions.user.mouse_rig()
        amount = SCROLL_RAMP_AMOUNT * self._scroll_speed_scale()
        rig.scroll.speed.offset.add(amount).revert(
            SCROLL_RAMP_REVERT_MS, "ease_out2"
        )

    def scroll_resume(self):
        self.scroll_move_dir(self._scroll_direction)

parrot_actions = ParrotActions()
