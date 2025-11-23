from talon import actions, ctrl
from ..user_settings import MOVEMENT_SETTINGS, SETTINGS_OPTIONS

class Movement():
    def __init__(self):
        self.speed = MOVEMENT_SETTINGS["speed"]
        self.boost_small_amount = MOVEMENT_SETTINGS["boost_small"]
        self.boost_large_amount = MOVEMENT_SETTINGS["boost_large"]

    def move(self, direction):
        direction_map = {
            "left": (-1, 0),
            "right": (1, 0),
            "up": (0, -1),
            "down": (0, 1)
        }
        if direction in direction_map:
            dx, dy = direction_map[direction]
            self._move_in_direction(dx, dy)

    def _move_in_direction(self, dx, dy):
        rig = actions.user.mouse_rig()
        boost_large = rig.state.layer("boost_large")

        if boost_large:
            # Early turns (0-0.5s): slower, less responsive (higher turn_time)
            # Late turns (0.5s+): faster, more responsive (lower turn_time)
            # Interpolate from 2000ms (early) to 500ms (late) based on time_alive
            time_alive = boost_large.time_alive()
            control_factor = min(time_alive / 2.0, 0.75)  # Clamp to [0, 0.75] over 2 seconds
            turn_time = int(2000 - (1500 * control_factor))  # 2000ms -> 875ms at max
            rig.direction.to(dx, dy).over(turn_time, "ease_out_2")

            # print('time alive', boost_large.time_alive())
            # turn_time = min(rig.state.s#peed ** 3 + 500, 2000)#b
            # print(f"Turning with time: {turn_time}ms")
            # rig.direction(dx, dy).over(turn_time, "ease_out_2")
            # boost_large.revert(2000)
            # boost_large.speed.mul(0.5).revert(turn_time)-#
        else:
            rig.direction(dx, dy)

        if not rig.state.base.speed:
            rig.speed(self.speed)

    def move_left(self):
        self._move_in_direction(-1, 0)

    def move_right(self):
        self._move_in_direction(1, 0)

    def move_up(self):
        self._move_in_direction(0, -1)

    def move_down(self):
        self._move_in_direction(0, 1)

    def preserve_direction(self):
        rig = actions.user.mouse_rig()
        rig.direction.bake()

    def boost_large(self, on_complete):
        rig = actions.user.mouse_rig()

        if rig.state.layer("boost_small"):
            rig.layer("boost_large", order=2).speed.to(self.boost_large_amount * 2) \
                .revert(1500, "ease_in_out").then(on_complete)
            return

        if rig.state.layer("boost_large"):
            amount = self.boost_large_amount + rig.state.layer("boost_large").speed * 0.8
        else:
            amount = self.boost_large_amount

        rig.layer("boost_large", order=2).speed.add(amount) \
            .over(1000).revert(1000).then(on_complete)

    def boost_small(self):
        rig = actions.user.mouse_rig()
        rig.layer("boost_small", order=1).speed.add(self.boost_small_amount) \
            .hold(100).revert(100)

    def slower(self):
        rig = actions.user.mouse_rig()
        rig.speed.div(2)
        # actions.user.mouse_move_continuous_speed_decrease()

    def stop(self):
        rig = actions.user.mouse_rig()
        rig.stop()
        # actions.user.mouse_move_continuous_stop()

    def is_moving(self):
        rig = actions.user.mouse_rig()

        return rig.state.speed > 0
        # return state
        # info = actions.user.mouse_move_info()
        # return info["is_moving"]

movement = Movement()

def mouse_move_smooth_to_gaze():
    x = actions.mouse_x()
    y = actions.mouse_y()
    actions.tracking.jump()
    gaze_x = actions.mouse_x()
    gaze_y = actions.mouse_y()
    actions.mouse_move(x, y)
    actions.user.mouse_move_smooth_from_to(x, y, gaze_x, gaze_y)

def mouse_move_smooth_from_gaze():
    x = actions.mouse_x()
    y = actions.mouse_y()
    actions.tracking.jump()
    gaze_x = actions.mouse_x()
    gaze_y = actions.mouse_y()
    actions.user.mouse_move_smooth_from_to(gaze_x, gaze_y, x, y)
