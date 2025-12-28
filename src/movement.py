from talon import actions, ctrl
from ..user_settings import MOVEMENT_SETTINGS

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
        mode = actions.user.parrot_mode_v7_get_mode()
        print("mode", mode)

        if boost_large:
            # Early turns slow( reloadb
            # Later turns fast
            print(boost_large)
            control_factor = min(boost_large.time_alive / 2.0, 0.75)
            turn_time = int(2000 - (1500 * control_factor))
            rig.direction.to(dx, dy).over(turn_time, "ease_out2")
        elif mode == "glide":
            rig.direction.to(dx, dy).over(rig.state.speed * 100, "ease_out2")
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
        rig.bake()

    def boost_large(self, on_complete):
        rig = actions.user.mouse_rig()

        if rig.state.layer("boost_small"):
            rig.layer("boost_large", order=2).speed.offset.to(self.boost_large_amount * 2) \
                .revert(1500, "ease_in_out").then(on_complete)
            return

        # print("state", rig.state)
        # print("state base", rig.state.base)
        # print("state layer", rig.state.layer("boost_large"))
        # print("state layer speed", rig.state.layer("boost_large").speed)
        if rig.state.layer("boost_large"):
            amount = self.boost_large_amount + rig.state.layer("boost_large").value
        else:
            amount = self.boost_large_amount

        rig.layer("boost_large", order=2).speed.offset.add(amount) \
            .over(1000).revert(1000).then(on_complete)

    def boost_small(self):
        rig = actions.user.mouse_rig()
        rig.layer("boost_small", order=1).speed.offset.add(self.boost_small_amount) \
            .revert(400, "ease_out2")

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
