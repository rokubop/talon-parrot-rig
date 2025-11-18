from talon import actions, ctrl
from ..user_settings import MOVEMENT_SETTINGS, SETTINGS_OPTIONS

class Movement():
    def __init__(self):
        self.speed = MOVEMENT_SETTINGS["speed"]
        self.boost_small_amount = MOVEMENT_SETTINGS["boost_small"]
        self.boost_large_amount = MOVEMENT_SETTINGS["boost_large"]

    def update_speed(self, speed_index: int):
        if 0 <= speed_index < len(SETTINGS_OPTIONS["speed"]):
            self.speed = SETTINGS_OPTIONS["speed"][speed_index]
            MOVEMENT_SETTINGS["speed"] = self.speed

    def update_boost_small(self, boost_index: int):
        if 0 <= boost_index < len(SETTINGS_OPTIONS["boost_small"]):
            self.boost_small_amount = SETTINGS_OPTIONS["boost_small"][boost_index]
            MOVEMENT_SETTINGS["boost_small"] = self.boost_small_amount

    def update_boost_large(self, boost_index: int):
        if 0 <= boost_index < len(SETTINGS_OPTIONS["boost_large"]):
            self.boost_large_amount = SETTINGS_OPTIONS["boost_large"][boost_index]
            MOVEMENT_SETTINGS["boost_large"] = self.boost_large_amount

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
        boost = rig.state.tag("boost")

        if boost:
            turn_time = min(rig.state.speed * 50, 2000)
            rig.direction(dx, dy).over(turn_time, interpolation="lerp")
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

    def boost_large(self):
        amount = self.boost_large_amount

        # info = actions.user.mouse_move_info()
        # print("info:", vars(info))
        # unit_vector = info["last_unit_vector"]

        # def continue_slowly():
        #     actions.user.mouse_move_continuous(unit_vector.x, unit_vector.y)

        rig = actions.user.mouse_rig()
        rig.tag("boost").speed.add(amount).over(1000).revert(1000)
        # rig.boost(20).over(1000).ease("ease_out")

        # actions.user.mouse_move_smooth_delta(
        #     unit_vector.x * amount,
        #     unit_vector.y * amount,
        #     callback_stop=continue_slowly
        # )

    def boost_small(self):
        amount = self.boost_small_amount
        rig = actions.user.mouse_rig()
        rig.tag("boost").speed.add(amount).over(100).revert(500)

        # info = actions.user.mouse_move_info()
        # unit_vector = info["last_unit_vector"]

        # def continue_slowly():
        #     actions.user.mouse_move_continuous(unit_vector.x, unit_vector.y)

        # actions.user.mouse_move_smooth_delta(
        #     unit_vector.x * amount,
        #     unit_vector.y * amount,
        #     callback_stop=continue_slowly
        # )

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
