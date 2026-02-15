from talon import actions, cron
from ..user_settings import MOVEMENT_SETTINGS

class Movement():
    def __init__(self):
        self.speed = MOVEMENT_SETTINGS["speed"]
        self.boost_amount = MOVEMENT_SETTINGS["boost"]
        self.boost_small_amount = MOVEMENT_SETTINGS["boost_small"]
        self._boost_revert_job = None

    def move(self, direction):
        mode = actions.user.parrot_rig_get_mode()
        if mode in ("glide", "boost"):
            actions.user.mouse_rig_go_natural(direction, self.speed)
        else:
            actions.user.mouse_rig_go(direction, self.speed)

    def preserve_direction(self):
        rig = actions.user.mouse_rig()
        rig.bake()

    def boost(self, on_complete=None):
        """Long speed pulse (shush) — ramp up 1s, revert 1s"""
        self._cancel_boost_revert()
        actions.user.mouse_rig_boost(
            self.boost_amount, over_ms=1000, release_ms=1000, max_stacks=0)
        if on_complete:
            self._boost_revert_job = cron.after("2000ms", on_complete)

    def boost_small(self):
        """Rapid speed pulse (hiss) — instant, fast decay with ease_out2"""
        rig = actions.user.mouse_rig()
        rig.speed.offset.add(self.boost_small_amount).revert(400, "ease_out2")

    def slower(self):
        actions.user.mouse_rig_speed_mul(0.5)

    def stop(self):
        self._cancel_boost_revert()
        actions.user.mouse_rig_stop()

    def is_moving(self):
        return actions.user.mouse_rig_state_is_moving()

    def _cancel_boost_revert(self):
        if self._boost_revert_job:
            cron.cancel(self._boost_revert_job)
            self._boost_revert_job = None

movement = Movement()
