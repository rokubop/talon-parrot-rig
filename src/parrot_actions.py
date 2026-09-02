import time
from talon import actions, ctrl, cron
from .tracking import tracking
from ..ui.ui_manager import ui_manager
from .keys import keys
from .events import event_manager
from .repeater import repeat_command, repeat_phrase, reverse_command, reverse_phrase
from ..parrot_rig_settings import (
    SLOW_MODE_MULTIPLIER,
    CLICK_HOLD_MS,
    BOOST_LONG_AMOUNT,
    BOOST_LONG_OVER_MS,
    BOOST_LONG_RELEASE_MS,
    BOOST_LONG_MAX,
    BURST_AMOUNT,
    BRAKE_REVERT_MS,
    BURST_SETTLE_SCALE,
    BURST_SETTLE_OVER_MS,
    BURST_SETTLE_HOLD_MS,
    BURST_SETTLE_REVERT_MS,
    GLIDE_RELEASE_RATE,
    APP_PICKER_KEY,
    WINDOW_KEYS,
    WINDOW_SUPER_KEYS,
    WINDOW_SNAP_ASSIST_MS,
    WINDOW_ALT_TAB_HOLD_MS,
    CANVAS_SLOW_MODE_MULTIPLIER,
    CANVAS_BOOST_LONG_AMOUNT,
    CANVAS_BOOST_LONG_OVER_MS,
    CANVAS_BOOST_LONG_RELEASE_MS,
    CANVAS_BURST_AMOUNT,
    CANVAS_BRAKE_REVERT_MS,
    CANVAS_RAMP_AMOUNT,
    CANVAS_RAMP_REVERT_MS,
    CANVAS_GLIDE_RELEASE_RATE,
    TRACKING_STOP_MS,
    CLICK_BEHAVIOR,
    CANVAS_SCALE_MODES,
)
from .utils import reload_files
from .settings_menu import (
    setting_get, setting_set, setting_label, setting_title,
    setting_number, setting_step, turn_scale, boost_scale,
)
from .menu import menu_back, menu_current, menu_reset
from .anchor import anchor_go, anchor_go_screen, anchor_toggle, anchors
from .snap import active_rule, do_snap, snap_rule

DRAG_BUTTONS = {"middle": 2, "left": 0, "right": 1}

# Canvas drag is absent: a held button or key, not a mode of its own.
ALT_MODE_MODES = {
    "canvas_scroll":  ("canvas_stop", "canvas_move", "canvas_glide",
                       "canvas_boost", "canvas_tracking"),
    "canvas_scale":   ("canvas_scale", "canvas_scale_move"),
    "window_pick":    ("window",),
    "window_control": ("window_stop", "window_move"),
}

class ParrotActions:
    def __init__(self):
        self._is_left_click_held = False
        self._held_button = 0
        self._is_drag = False
        self._drag_hold = "middle"
        self._parrot_mode_enabled = False
        self._stop_time_job = None
        self._move_speed_level = 0
        self._canvas_speed_level = 0
        self._scroll_direction = "down"
        self._burst_or_brake_did_break = False
        self._canvas_burst_or_brake_did_break = False
        self._canvas_scale_key = None
        self._canvas_scale_last = "ctrl"
        self._canvas_scale_dir = "up"
        self._window_super_held = False
        self._burst_gliding = False
        self._burst_glide_job = None
        self._last_alt_mode = None

    def _get_move_speed(self):
        return setting_number("move_speed") * (SLOW_MODE_MULTIPLIER ** self._move_speed_level)

    def _get_canvas_move_speed(self):
        return setting_number("canvas_move_speed") * (CANVAS_SLOW_MODE_MULTIPLIER ** self._canvas_speed_level)

    def _emit_speed_level(self):
        mode = event_manager.get_mode()
        if mode == "canvas_scale":
            level = 0
        elif mode in ("canvas_stop", "canvas_move", "canvas_glide", "canvas_boost", "canvas_tracking"):
            level = self._canvas_speed_level
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
        always_glide = setting_get("move_mode") == "always_glide"
        if always_glide or self._burst_gliding or mode in ("glide", "boost") or current_speed > speed:
            actions.user.mouse_rig_move_continuous_smooth(direction, speed, scale=turn_scale())
        else:
            actions.user.mouse_rig_move_continuous(direction, speed)
        if mode not in ("glide", "boost"):
            event_manager.set_mode("glide" if always_glide else "move")
            self._emit_speed_level()

    def mouse_move_dir(self, direction: str):
        self.move(direction)

    def _is_turning(self):
        """True while a smooth turn is still sweeping toward its target."""
        return actions.user.mouse_rig().state.direction.target is not None

    def mouse_toggle_glide(self):
        rig = actions.user.mouse_rig()
        if event_manager.get_mode() == "glide" and self._is_turning():
            rig.direction.bake()
            return
        rig.bake()
        if event_manager.get_mode() == "glide":
            speed = self._get_move_speed()
            rig.speed.to(speed).over(rate=GLIDE_RELEASE_RATE, easing="ease_out2")
            event_manager.set_mode("move")
        else:
            event_manager.set_mode("glide")

    def _move_speed_scale(self):
        return SLOW_MODE_MULTIPLIER ** self._move_speed_level

    def _canvas_speed_scale(self):
        return CANVAS_SLOW_MODE_MULTIPLIER ** self._canvas_speed_level

    def mouse_boost_long(self):
        event_manager.set_mode("boost")
        amount = BOOST_LONG_AMOUNT * boost_scale() * self._move_speed_scale()
        max_speed = BOOST_LONG_MAX * boost_scale()
        actions.user.mouse_rig_boost(amount, over_ms=BOOST_LONG_OVER_MS, release_ms=BOOST_LONG_RELEASE_MS, max_speed=max_speed).then(
            lambda: event_manager.return_to_previous_mode()
                if event_manager.get_mode() == "boost" else None)

    def _burst_glide(self, on: bool, ms: int = 0):
        """Turns stay smooth through a burst and its settle. A flag, not the
        glide mode, because burst_or_brake reads that mode as "brake" and a
        chained hiss would stop bursting."""
        if self._burst_glide_job:
            cron.cancel(self._burst_glide_job)
            self._burst_glide_job = None
        self._burst_gliding = on
        if on and ms:
            self._burst_glide_job = cron.after(f"{ms}ms", lambda: self._burst_glide(False))

    def _burst_settle(self):
        """Ease under normal speed for a moment, so the click after a burst is
        easier. Off the configured speed, not the live one, which still has the
        burst in it. Another hiss clears it and runs at full speed."""
        settle = -self._get_move_speed() * (1 - BURST_SETTLE_SCALE)
        actions.user.mouse_rig().layer("burst_settle").speed.offset.add(settle) \
            .over(BURST_SETTLE_OVER_MS) \
            .hold(BURST_SETTLE_HOLD_MS) \
            .revert(BURST_SETTLE_REVERT_MS)
        self._burst_glide(
            True,
            BURST_SETTLE_OVER_MS + BURST_SETTLE_HOLD_MS + BURST_SETTLE_REVERT_MS,
        )

    def mouse_burst_or_brake(self):
        actions.user.mouse_rig().layer("burst_settle").revert(0)
        if event_manager.get_mode() in ("boost", "glide"):
            rig = actions.user.mouse_rig()
            rig.bake()
            speed = self._get_move_speed()
            rig.speed.to(speed)
            event_manager.set_mode("move")
            self._burst_or_brake_did_break = True
            self._burst_settle()
            return
        self._burst_or_brake_did_break = False
        self._burst_glide(True)
        rig = actions.user.mouse_rig()
        rig.layer("hiss_boost").stack(1).speed.offset.add(BURST_AMOUNT * boost_scale())

    def mouse_burst_or_brake_stop(self):
        if self._burst_or_brake_did_break:
            self._burst_or_brake_did_break = False
            return
        rig = actions.user.mouse_rig()
        rig.layer("hiss_boost").revert(BRAKE_REVERT_MS, "ease_out2")
        self._burst_settle()

    def tracking_activate(self):
        """The way out to plain tracking from anywhere, so a super window mode
        was holding is let go here rather than at every caller."""
        self._window_super_release()
        actions.user.mouse_rig_stop()
        tracking.activate()
        event_manager.set_mode("tracking")

    def app_picker(self):
        """Tracking first: it is what lets go of a held super, and win+alt+`
        is not the hotkey."""
        self.tracking_activate()
        actions.key(APP_PICKER_KEY)

    def canvas_tracking_activate(self):
        actions.user.mouse_rig_scroll_stop()
        actions.user.mouse_rig_stop()
        tracking.activate()
        event_manager.set_mode("canvas_tracking")

    def click_exit(self):
        self.mouse_click()
        self.parrot_mode_disable()

    def return_action(self):
        """Your own anchors win and take this outright. Otherwise the snap
        target if a rule applies, then whatever the Return setting picks for
        being empty handed."""
        if anchor_go():
            return
        rule = active_rule()
        if rule:
            do_snap(rule)
            return
        if anchor_go_screen():
            return
        self.click_exit()

    def toggle_anchor(self):
        from ..ui.setting_picker import show_notification
        result = anchor_toggle()
        show_notification("Anchor", f"{result} ({len(anchors())})")

    def snap_now(self):
        """Snap regardless of condition, using the active rule if there is one."""
        do_snap(active_rule())

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

    def click_release(self, button=None):
        """Releases the button that went down, not the one asking."""
        ctrl.mouse_click(button=self._held_button if button is None else button, up=True)
        ui_manager.hide_border()
        self._is_left_click_held = False
        self._held_button = 0

    def mouse_click(self, button=0, hold=False):
        # Never send a click with the canvas scale modifier still down.
        self._canvas_scale_release()
        current_mode = event_manager.get_mode()

        should_stop = hold != True and (
            (current_mode in CLICK_BEHAVIOR
             and setting_get("click_freeze") == "freeze") or
            (current_mode in ("tracking", "canvas_tracking")
             and setting_get("track_freeze") == "freeze")
        )

        if self._is_left_click_held:
            self.click_release()
        elif hold:
            ctrl.mouse_click(button=button, down=True)
            ui_manager.show_border()
            self._is_left_click_held = True
            self._held_button = button
        else:
            ctrl.mouse_click(button=button, hold=CLICK_HOLD_MS)
            ui_manager.hide_border()

        if should_stop:
            if current_mode in ("tracking", "canvas_tracking"):
                self.stop_temporarily()
            elif CLICK_BEHAVIOR.get(current_mode) in ("canvas_stop", "canvas_scale"):
                actions.user.mouse_rig_scroll_stop()
                event_manager.set_mode(CLICK_BEHAVIOR[current_mode])
            else:
                self.stopper()

    def scroll(self, direction: str):
        actions.user.mouse_rig_scroll_continuous(direction, setting_number("scroll_speed"))

    def scroll_stop(self):
        actions.user.mouse_rig_scroll_stop()

    def window_enter(self):
        self._canvas_scale_release()
        actions.user.mouse_rig_stop()
        actions.user.mouse_rig_scroll_stop()
        self.window_picker()

    def window_enter_stopped(self):
        """Window mode with nothing else. No picker, and tracking is left
        running: changing what the noises do should not drop your aim."""
        self._canvas_scale_release()
        actions.user.mouse_rig_stop()
        actions.user.mouse_rig_scroll_stop()
        event_manager.set_mode("window_stop")

    def window_picker(self):
        """The picker is an overlay you aim at, so this tracks."""
        self._window_super_release()
        tracking.activate()
        event_manager.set_mode("window")
        actions.key(WINDOW_KEYS["picker"])

    def window_exit(self):
        self._window_super_release()
        self.stopper()

    def window_key(self, name: str):
        self._window_super_release()
        actions.key(WINDOW_KEYS[name])

    def window_move_enter(self, name: str):
        """tut+direction is the door into window mode as well as the nudge, so
        it stops what was running first. window_move alone only holds super."""
        if self.alt_mode_current() not in ("window_pick", "window_control"):
            self.alt_mode_open("window_control")
        self.window_move(name)

    def window_move(self, name: str):
        """Super stays down across a run of these, so the next one still lands."""
        if not self._window_super_held:
            actions.key("super:down")
            self._window_super_held = True
            event_manager.set_mode("window_move")
        actions.key(WINDOW_SUPER_KEYS[name])

    def _window_super_release(self) -> bool:
        if not self._window_super_held:
            return False
        actions.key("super:up")
        self._window_super_held = False
        if event_manager.get_mode() == "window_move":
            event_manager.set_mode("window")
        return True

    def window_escape(self):
        """Letting super go is what raises snap assist, so escape follows it."""
        if self._window_super_release():
            actions.sleep(f"{WINDOW_SNAP_ASSIST_MS}ms")
        actions.key("escape")
        actions.user.mouse_rig_stop()
        tracking.freeze()
        event_manager.set_mode("window_stop")

    def window_alt_tab(self):
        """Alt has to be down before and after the tab or the switcher never
        comes up, so this is held rather than sent as one chord."""
        actions.key("alt:down")
        actions.sleep(f"{WINDOW_ALT_TAB_HOLD_MS}ms")
        actions.key("tab")
        actions.sleep(f"{WINDOW_ALT_TAB_HOLD_MS}ms")
        actions.key("alt:up")

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
        menu_reset()
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

        self.drag_release()
        self._canvas_scale_release()
        self._window_super_release()

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
            "drag": self._is_drag,
            "drag_hold": self._drag_hold,
            "click_freeze": setting_get("click_freeze"),
            "track_freeze": setting_get("track_freeze"),
            "alt_mode": setting_get("alt_mode"),
            "last_alt_mode": self._last_alt_mode,
        }

    def parrot_mode_get_mode(self):
        return event_manager.get_mode()

    def parrot_mode_is_enabled(self) -> bool:
        return self._parrot_mode_enabled

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

    def is_idle(self) -> bool:
        return not (
            actions.user.mouse_rig_state_is_moving()
            or actions.user.mouse_rig_state_is_scrolling()
            or tracking.is_tracking
        )

    def full_reset(self):
        """Zeroing the counters is not enough while something is running: the
        slow steps are already multiplied into the rig, so undo them there too."""
        self.disable_modifiers()
        self._canvas_scale_release()
        if self._move_speed_level:
            level = self._move_speed_level
            self._move_speed_level = 0
            if actions.user.mouse_rig_state_is_moving():
                actions.user.mouse_rig_speed_mul(1.0 / (SLOW_MODE_MULTIPLIER ** level))
        if self._canvas_speed_level:
            level = self._canvas_speed_level
            self._canvas_speed_level = 0
            if actions.user.mouse_rig_state_is_scrolling():
                actions.user.mouse_rig_scroll_speed_mul(1.0 / (CANVAS_SLOW_MODE_MULTIPLIER ** level))
        self._emit_speed_level()

    def cancel(self):
        """Progressive cancel, one step at a time:
        held button -> modifiers and slow steps -> mode -> exit
        """
        if menu_current():
            menu_back()
            return
        if self._is_drag:
            self.alt_mode_close("canvas_drag")
            return
        if self._is_left_click_held:
            self.click_release()
            return
        if (event_manager.get_modifiers()
                or self._move_speed_level
                or self._canvas_speed_level):
            self.full_reset()
            return
        name = self.alt_mode_current()
        if name:
            self.alt_mode_close(name)
            return
        self.exit()

    def stop_or_reset(self, stop=None):
        """Stop what is running. Standing still already, this is the reset
        instead, which is what frees the bare tut."""
        if self.is_idle():
            self.full_reset()
            return
        (stop or self.stopper)()

    def stopper(self, stop_tracking=True, stop_moving=True, stop_scrolling=True, reset_mode=True):
        self._burst_glide(False)
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
        if event_manager.get_mode() in ("tracking", "canvas_tracking"):
            tracking.activate()

    def show_setting_picker(self, name: str, title: str = ""):
        ui_manager.show_setting_picker(name, title)

    def hide_setting_picker(self, name: str):
        ui_manager.hide_setting_picker(name)

    def show_cheatsheet(self):
        ui_manager.show_cheatsheet()

    def alt_mode_current(self):
        """The open mode, or None for cursor move."""
        if self._is_drag:
            return "canvas_drag"
        mode = event_manager.get_mode()
        return next((n for n, modes in ALT_MODE_MODES.items() if mode in modes), None)

    def alt_mode_open(self, name: str):
        """Leaves the current mode first, so a held super or middle button
        never stacks. Reopening the open one does nothing."""
        current = self.alt_mode_current()
        if current == name:
            return
        if current:
            self.alt_mode_close(current)
        self._last_alt_mode = name
        if name == "canvas_scale":
            self.canvas_scale_toggle()
        elif name == "canvas_drag":
            self.toggle_drag()
        elif name == "window_pick":
            self.window_enter()
        elif name == "window_control":
            self.window_enter_stopped()
        else:
            self.canvas_move_toggle()

    def alt_mode_close(self, name: str):
        if name == "canvas_scale":
            self.canvas_scale_toggle()
        elif name == "canvas_drag":
            self.toggle_drag()
        elif name in ("window_pick", "window_control"):
            self.window_exit()
        else:
            self.canvas_move_toggle()
        # Tracking is the exception: it is the mode this came back to.
        self.stopper(
            stop_tracking=event_manager.get_mode() != "tracking",
            reset_mode=False,
        )

    def canvas_toggle(self):
        """Canvas and back, always. The other modes are reached from the
        redirect window canvas opens with, not from here."""
        current = self.alt_mode_current()
        if current:
            self.alt_mode_close(current)
        else:
            self.alt_mode_open("canvas_scroll")

    def alt_mode_toggle(self):
        """Swap to the most recent mode, or back. The alt_mode setting picks
        the first one."""
        current = self.alt_mode_current()
        if current:
            self.alt_mode_close(current)
        else:
            self.alt_mode_open(self._last_alt_mode or setting_get("alt_mode"))

    def canvas_scale_toggle(self):
        if event_manager.get_mode() in CANVAS_SCALE_MODES:
            self.canvas_scale_stop()
            event_manager.set_mode("default")
        else:
            actions.user.mouse_rig_move_stop()
            actions.user.mouse_rig_scroll_stop()
            event_manager.set_mode("canvas_scale")
            self._emit_speed_level()

    def canvas_scale_dir(self, modifier: str, wheel: str):
        """Scroll with a modifier held, so the app scales the canvas. Each pair
        of noises owns one modifier and sends the vertical wheel both ways,
        which is the gesture apps actually listen for."""
        self._canvas_scale_hold(modifier)
        self._canvas_scale_last = modifier
        self._canvas_scale_dir = wheel
        actions.user.mouse_rig_scroll_continuous(
            wheel, setting_number("canvas_scale_speed"), force=True)
        self._scroll_direction = wheel
        event_manager.set_mode("canvas_scale_move")
        event_manager.emit("scale_modifier_changed", {"modifier": modifier})

    def canvas_scale_step(self):
        """One tick, on the modifier and direction the last scale used."""
        if event_manager.get_mode() == "canvas_scale_move":
            self.canvas_scale_stop()
        self._canvas_scale_hold(self._canvas_scale_last)
        actions.user.mouse_rig_scroll_delta(self._canvas_scale_dir)

    def canvas_scale_speed_step(self, delta: int):
        """Some apps zoom a whole level per tick, so the range has to reach very
        low. Takes effect mid-scale, not just on the next one."""
        from ..ui.setting_picker import show_notification
        label = setting_step("canvas_scale_speed", delta)
        show_notification(setting_title("canvas_scale_speed"), label)
        if event_manager.get_mode() == "canvas_scale_move":
            actions.user.mouse_rig_scroll_continuous(
                self._canvas_scale_dir, setting_number("canvas_scale_speed"), force=True)

    def canvas_scale_stop(self):
        actions.user.mouse_rig_scroll_stop()
        self._canvas_scale_release()
        if event_manager.get_mode() == "canvas_scale_move":
            event_manager.set_mode("canvas_scale")

    def _canvas_scale_hold(self, modifier: str):
        if self._canvas_scale_key == modifier:
            return
        self._canvas_scale_release()
        if modifier != "none":
            actions.key(f"{modifier}:down")
            self._canvas_scale_key = modifier

    def _canvas_scale_release(self):
        if not self._canvas_scale_key:
            return
        actions.key(f"{self._canvas_scale_key}:up")
        self._canvas_scale_key = None

    def drag_press(self):
        """Remembers what went down, so changing the setting mid-drag cannot
        strand a held button."""
        self._drag_hold = setting_get("drag_hold")
        if self._drag_hold == "space":
            actions.key("space:down")
        else:
            ctrl.mouse_click(button=DRAG_BUTTONS[self._drag_hold], down=True)

    def drag_lift(self):
        if self._drag_hold == "space":
            actions.key("space:up")
        else:
            ctrl.mouse_click(button=DRAG_BUTTONS[self._drag_hold], up=True)

    def toggle_drag(self):
        """Hold something down and keep moving; toggle to release."""
        if self._is_drag:
            self.drag_release()
            self.stopper()
        else:
            self.drag_press()
            self._is_drag = True
            ui_manager.show_border()
            # default mode maps hiss/shush to scroll, move mode gives boost/burst
            event_manager.set_mode("move")

    def drag_release(self):
        if not self._is_drag:
            return
        self.drag_lift()
        self._is_drag = False
        if not self._is_left_click_held:
            ui_manager.hide_border()

    def canvas_move_toggle(self):
        mode = event_manager.get_mode()
        if mode == "tracking":
            event_manager.set_mode("canvas_tracking")
        elif mode == "canvas_tracking":
            event_manager.set_mode("tracking")
        elif mode in ("canvas_stop", "canvas_move", "canvas_glide", "canvas_boost"):
            actions.user.mouse_rig_scroll_stop()
            event_manager.set_mode("default")
        else:
            actions.user.mouse_rig_move_stop()
            event_manager.set_mode("canvas_stop")
        self._emit_speed_level()

    def canvas_move_dir(self, direction: str):
        tracking.freeze()
        actions.user.mouse_rig_move_stop()
        mode = event_manager.get_mode()
        speed = self._get_canvas_move_speed()
        rig = actions.user.mouse_rig()
        current_scroll_speed = rig.state.scroll_speed
        if mode in ("canvas_glide", "canvas_boost") or current_scroll_speed > speed:
            actions.user.mouse_rig_scroll_continuous_smooth(direction, speed, scale=3.0)
        else:
            actions.user.mouse_rig_scroll_continuous(direction, speed)
        self._scroll_direction = direction
        event_manager.emit("scroll_direction_changed", {"direction": direction})
        if mode not in ("canvas_glide", "canvas_boost"):
            event_manager.set_mode("canvas_move")
            self._emit_speed_level()

    def canvas_move_or_slow_dir(self, direction: str):
        rig = actions.user.mouse_rig()
        cardinal = rig.state.scroll.direction_cardinal.current
        if actions.user.mouse_rig_state_is_scrolling() and cardinal == direction:
            self._canvas_speed_level += 1
            actions.user.mouse_rig_scroll_speed_mul(CANVAS_SLOW_MODE_MULTIPLIER)
            self._emit_speed_level()
        else:
            self.canvas_move_dir(direction)

    def canvas_toggle_glide(self):
        rig = actions.user.mouse_rig()
        rig.scroll.bake()
        if event_manager.get_mode() == "canvas_glide":
            speed = self._get_canvas_move_speed()
            rig.scroll.speed.to(speed).over(rate=CANVAS_GLIDE_RELEASE_RATE, easing="ease_out2")
            event_manager.set_mode("canvas_move")
        else:
            event_manager.set_mode("canvas_glide")

    def canvas_boost_long(self):
        event_manager.set_mode("canvas_boost")
        amount = CANVAS_BOOST_LONG_AMOUNT * boost_scale() * self._canvas_speed_scale()
        actions.user.mouse_rig_scroll_boost(
            amount,
            over_ms=CANVAS_BOOST_LONG_OVER_MS,
            release_ms=CANVAS_BOOST_LONG_RELEASE_MS
        ).then(
            lambda: event_manager.return_to_previous_mode()
                if event_manager.get_mode() == "canvas_boost" else None
        )

    def canvas_burst_or_brake(self):
        if event_manager.get_mode() in ("canvas_boost", "canvas_glide"):
            rig = actions.user.mouse_rig()
            rig.scroll.bake()
            speed = self._get_canvas_move_speed()
            rig.scroll.speed.to(speed).over(rate=CANVAS_GLIDE_RELEASE_RATE, easing="ease_out2")
            event_manager.set_mode("canvas_move")
            self._canvas_burst_or_brake_did_break = True
            return
        self._canvas_burst_or_brake_did_break = False
        rig = actions.user.mouse_rig()
        rig.layer("hiss_canvas_boost").stack(1).scroll.speed.offset.add(CANVAS_BURST_AMOUNT * boost_scale())

    def canvas_burst_or_brake_stop(self):
        if self._canvas_burst_or_brake_did_break:
            self._canvas_burst_or_brake_did_break = False
            return
        rig = actions.user.mouse_rig()
        rig.layer("hiss_canvas_boost").revert(CANVAS_BRAKE_REVERT_MS, "ease_out2")

    def canvas_stop(self):
        actions.user.mouse_rig_scroll_stop()
        tracking.freeze()
        event_manager.set_mode("canvas_stop")

    def canvas_ramp_dir(self, direction: str):
        self.canvas_move_dir(direction)
        rig = actions.user.mouse_rig()
        amount = CANVAS_RAMP_AMOUNT * self._canvas_speed_scale()
        rig.scroll.speed.offset.add(amount).revert(
            CANVAS_RAMP_REVERT_MS, "ease_out2"
        )

    def canvas_resume(self):
        self.canvas_move_dir(self._scroll_direction)

parrot_actions = ParrotActions()


def _release_canvas_scale_on_exit(data):
    """Any route out of canvas scale drops the held key, including exit,
    stop, tracking, and the settings menus."""
    if (data.get("previous_mode") in CANVAS_SCALE_MODES
            and data.get("current_mode") not in CANVAS_SCALE_MODES):
        parrot_actions._canvas_scale_release()

event_manager.subscribe("mode_changed", _release_canvas_scale_on_exit)


def _remember_alt_mode(data):
    """Any route into a mode counts, not just the swap."""
    name = parrot_actions.alt_mode_current()
    if name:
        parrot_actions._last_alt_mode = name

event_manager.subscribe("mode_changed", _remember_alt_mode)

# Release before the jump so the jump itself isn't dragged, then re-press.
snap_rule(
    "drag",
    when=lambda: parrot_actions._is_drag,
    target="center",
    before=lambda: parrot_actions.drag_lift(),
    after=lambda: parrot_actions.drag_press(),
)
