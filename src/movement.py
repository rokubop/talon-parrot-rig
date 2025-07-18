from talon import actions, ctrl
from ..config import MOVEMENT_SETTINGS, SETTINGS_OPTIONS

class Movement():
    def __init__(self):
        self.speed = MOVEMENT_SETTINGS["speed"]
        self.boost_small_amount = MOVEMENT_SETTINGS["boost_small"]
        self.boost_large_amount = MOVEMENT_SETTINGS["boost_large"]

    def update_speed(self, speed_index: int):
        """Update movement speed from settings options"""
        if 0 <= speed_index < len(SETTINGS_OPTIONS["speed"]):
            self.speed = SETTINGS_OPTIONS["speed"][speed_index]
            MOVEMENT_SETTINGS["speed"] = self.speed

    def update_boost_small(self, boost_index: int):
        """Update small boost from settings options"""
        if 0 <= boost_index < len(SETTINGS_OPTIONS["boost_small"]):
            self.boost_small_amount = SETTINGS_OPTIONS["boost_small"][boost_index]
            MOVEMENT_SETTINGS["boost_small"] = self.boost_small_amount

    def update_boost_large(self, boost_index: int):
        """Update large boost from settings options"""
        if 0 <= boost_index < len(SETTINGS_OPTIONS["boost_large"]):
            self.boost_large_amount = SETTINGS_OPTIONS["boost_large"][boost_index]
            MOVEMENT_SETTINGS["boost_large"] = self.boost_large_amount

    def move(self, direction):
        if direction == "left":
            self.move_left()
        elif direction == "right":
            self.move_right()
        elif direction == "up":
            self.move_up()
        elif direction == "down":
            self.move_down()

    def move_left(self):
        actions.user.mouse_move_continuous(-1, 0)

    def move_right(self):
        actions.user.mouse_move_continuous(1, 0)

    def move_up(self):
        actions.user.mouse_move_continuous(0, -1)

    def move_down(self):
        actions.user.mouse_move_continuous(0, 1)

    def boost_large(self):
        amount = self.boost_large_amount
        info = actions.user.mouse_move_info()
        unit_vector = info["last_unit_vector"]

        def continue_slowly():
            actions.user.mouse_move_continuous(unit_vector.x, unit_vector.y)

        actions.user.mouse_move_smooth_delta(
            unit_vector.x * amount,
            unit_vector.y * amount,
            callback_stop=continue_slowly
        )

    def boost_small(self):
        amount = self.boost_small_amount
        info = actions.user.mouse_move_info()
        unit_vector = info["last_unit_vector"]

        def continue_slowly():
            actions.user.mouse_move_continuous(unit_vector.x, unit_vector.y)

        actions.user.mouse_move_smooth_delta(
            unit_vector.x * amount,
            unit_vector.y * amount,
            callback_stop=continue_slowly
        )

    def slower(self):
        actions.user.mouse_move_continuous_speed_decrease()

    def stop(self):
        actions.user.mouse_move_continuous_stop()

    def is_moving(self):
        info = actions.user.mouse_move_info()
        return info["is_moving"]

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
