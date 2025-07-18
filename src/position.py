from talon import actions
from .utils import get_screen

class Position:
    mouse_pos_history = []
    mouse_pos_history_size = 2
    mouse_pos_history_pointer = 0

    def mouse_pos_save(self):
        current_pos = (actions.mouse_x(), actions.mouse_y())
        if len(self.mouse_pos_history) >= self.mouse_pos_history_size:
            self.mouse_pos_history.pop(0)
        self.mouse_pos_history.append(current_pos)
        self.mouse_pos_history_pointer = len(self.mouse_pos_history) - 1

    def mouse_pos_cycle(self):
        if len(self.mouse_pos_history) == 0:
            return
        self.mouse_pos_history_pointer = (self.mouse_pos_history_pointer + 1) % len(self.mouse_pos_history)
        x, y = self.mouse_pos_history[self.mouse_pos_history_pointer]
        actions.mouse_move(x, y)

        self.mouse_pos_history.pop(self.mouse_pos_history_pointer)
        self.mouse_pos_history.append((x, y))
        self.mouse_pos_history_pointer = len(self.mouse_pos_history) - 1

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
