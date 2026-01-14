from talon import actions, cron
from .utils import get_screen
from ..ui.ui_manager import ui_manager

saved_loc_map = {}
hide_mouse_cron_job = None

def mouse_pos_ui():
    screen, div, text = actions.user.ui_elements(["screen", "div", "text"])

    padding = 6
    offset = 10  # offset from the actual position

    return screen()[
      *[div(
          position="absolute",
          left=x - 10,
          top=y - 10,
          background_color="333333",
          border_width=1,
          border_color="555555",
          border_radius=2,
          padding=padding,
          opacity=0.8,
      )[
          text(name, font_size=12, color="FFFFFF")
      ] for name, (x, y) in saved_loc_map.items()]
    ]

class Position:
    mouse_pos_history = []
    mouse_pos_history_size = 2
    mouse_pos_history_pointer = 0
    mouse_stopped_pos_history = []
    mouse_stopped_pos_history_size = 10
    mouse_stopped_pos_history_pointer = 0

    def mouse_pos_show_marks(self):
        ui_manager.show_mouse_pos_marks(mouse_pos_ui)

    def mouse_pos_show_marks_briefly(self):
        global hide_mouse_cron_job
        ui_manager.show_mouse_pos_marks(mouse_pos_ui)
        if hide_mouse_cron_job:
            cron.cancel(hide_mouse_cron_job)
        hide_mouse_cron_job = cron.after("2s", self.mouse_pos_hide_marks)

    def mouse_pos_hide_marks(self):
        global hide_mouse_cron_job
        ui_manager.hide_mouse_pos_marks(mouse_pos_ui)
        hide_mouse_cron_job = None

    def mouse_pos_save(self, name: str = None):
        current_pos = (actions.mouse_x(), actions.mouse_y())
        if len(self.mouse_pos_history) >= self.mouse_pos_history_size:
            self.mouse_pos_history.pop(0)
        self.mouse_pos_history.append(current_pos)
        self.mouse_pos_history_pointer = len(self.mouse_pos_history) - 1
        if name:
            saved_loc_map[name] = current_pos
            self.mouse_pos_show_marks()

    def mouse_stopped_pos_save(self):
        current_pos = (actions.mouse_x(), actions.mouse_y())
        # Don't save if it's the same as the last stopped position
        if self.mouse_stopped_pos_history and self.mouse_stopped_pos_history[-1] == current_pos:
            return
        if len(self.mouse_stopped_pos_history) >= self.mouse_stopped_pos_history_size:
            self.mouse_stopped_pos_history.pop(0)
        self.mouse_stopped_pos_history.append(current_pos)
        # Reset pointer to the end when a new position is saved
        self.mouse_stopped_pos_history_pointer = len(self.mouse_stopped_pos_history) - 1

    def mouse_stopped_pos_go_last(self):
        if len(self.mouse_stopped_pos_history) == 0:
            return

        # Get current mouse position
        current_pos = (actions.mouse_x(), actions.mouse_y())

        # If we're at the last position and have a second position, go to second-to-last
        if len(self.mouse_stopped_pos_history) >= 2 and self.mouse_stopped_pos_history[-1] == current_pos:
            x, y = self.mouse_stopped_pos_history[-2]
            actions.mouse_move(x, y)
        else:
            # Otherwise go to the last position
            x, y = self.mouse_stopped_pos_history[-1]
            actions.mouse_move(x, y)

    def mouse_stopped_pos_cycle(self):
        if len(self.mouse_stopped_pos_history) == 0:
            return
        # Move backwards through history (decrement pointer)
        self.mouse_stopped_pos_history_pointer = (self.mouse_stopped_pos_history_pointer - 1) % len(self.mouse_stopped_pos_history)
        x, y = self.mouse_stopped_pos_history[self.mouse_stopped_pos_history_pointer]
        actions.mouse_move(x, y)

    def mouse_pos_mark_next(self, mark_names: list):
        """Mark current position with next available name from mark_names"""
        for name in mark_names:
            if name not in saved_loc_map:
                self.mouse_pos_save(name)
                return
        # If all names used, overwrite the first one
        self.mouse_pos_save(mark_names[0])

    def mouse_pos_mark_or_teleport(self, noise: str):
        if noise in saved_loc_map:
            self.mouse_pos_goto(noise)
        else:
            self.mouse_pos_save(noise)

    def mouse_pos_tele_nearest(self):
        actions.tracking.jump()
        pos = actions.mouse_x(), actions.mouse_y()
        nearest_name = None
        nearest_dist = None

        for name, (x, y) in saved_loc_map.items():
            dist = ((x - pos[0]) ** 2 + (y - pos[1]) ** 2) ** 0.5
            if nearest_dist is None or dist < nearest_dist:
                nearest_dist = dist
                nearest_name = name

        if nearest_name:
            self.mouse_pos_goto(nearest_name)

    def mouse_pos_goto(self, name: str):
        if name in saved_loc_map:
            x, y = saved_loc_map[name]
            actions.mouse_move(x, y)
        self.mouse_pos_show_marks()

    def mouse_pos_clear(self, name: str):
        if name in saved_loc_map:
            del saved_loc_map[name]

    def mouse_pos_clear_all(self):
        saved_loc_map.clear()
        ui_manager.hide_mouse_pos_marks(mouse_pos_ui)

    def mouse_pos_cycle(self):
        if len(self.mouse_pos_history) == 0:
            return
        self.mouse_pos_history_pointer = (self.mouse_pos_history_pointer + 1) % len(self.mouse_pos_history)
        x, y = self.mouse_pos_history[self.mouse_pos_history_pointer]
        actions.mouse_move(x, y)

        self.mouse_pos_history.pop(self.mouse_pos_history_pointer)
        self.mouse_pos_history.append((x, y))
        self.mouse_pos_history_pointer = len(self.mouse_pos_history) - 1

    def mouse_pos_swap_last(self):
        if len(self.mouse_pos_history) == 0:
            return

        # Get current mouse position
        current_pos = (actions.mouse_x(), actions.mouse_y())

        # If we're at the last position and have a second position, go to second-to-last
        if len(self.mouse_pos_history) >= 2 and self.mouse_pos_history[-1] == current_pos:
            x, y = self.mouse_pos_history[-2]
            actions.mouse_move(x, y)
        else:
            # Otherwise go to the last position
            x, y = self.mouse_pos_history[-1]
            actions.mouse_move(x, y)

    def left(self):
        screen = get_screen()
        actions.mouse_move(screen.x + 200, screen.y + screen.height / 2)

    def main(self):
        screen = get_screen()
        actions.mouse_move(screen.x + screen.width * .4, screen.y + screen.height / 2)

    def down(self):
        screen = get_screen()
        actions.mouse_move(screen.x + screen.width / 2, screen.y + screen.height - 150)

    def right(self):
        screen = get_screen()
        actions.mouse_move(screen.x + screen.width - 200, screen.y + screen.height / 2)

    def up(self):
        screen = get_screen()
        actions.mouse_move(screen.x + screen.width / 2, screen.y + 50)

position = Position()
