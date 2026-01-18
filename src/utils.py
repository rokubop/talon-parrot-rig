from talon import ui, ctrl, actions
import os
import math

def get_screen():
    current_screen = None
    (x, y) = ctrl.mouse_pos()
    for screen in ui.screens():
        if screen.contains(x, y):
            current_screen = screen

    return current_screen

class Utils:
    def update_time_of_file(self, filepath, filename):
        try:
            # Touch the file by updating its modification time
            import time
            os.utime(filepath, None)  # Updates to current time
        except Exception as e:
            print(f"Error updating {filename}: {e}")

    def reload_files(self):
        actions.user.parrot_mode_interactive_disable()

        src_dir = os.path.dirname(__file__)
        main_dir = os.path.dirname(os.path.join("..", __file__))

        touched_count = 0

        for filename in os.listdir(src_dir):
            if filename.endswith('.py'):
                filepath = os.path.join(src_dir, filename)
                self.update_time_of_file(filepath, filename)
                touched_count += 1

        for filename in os.listdir(main_dir):
            if filename.endswith('.py'):
                filepath = os.path.join(main_dir, filename)
                self.update_time_of_file(filepath, filename)
                touched_count += 1

        print(f"✓ Parrot mode reset and {touched_count} files touched for reload")

    def zoom_in(self):
        """Zoom in while moving mouse to edge of screen along line from center"""
        # Capture current mouse position
        # original_pos = ctrl.mouse_pos()
        # original_x, original_y = original_pos

        # # Get screen bounds
        # screen = get_screen()
        # if not screen:
        #     # Fallback if screen detection fails
        #     print("No screen detected for zoom_in")
        #     actions.key("win-keypad_plus")
        #     return

        # center_x = screen.x + screen.width // 2
        # center_y = screen.y + screen.height // 2

        # # Calculate direction vector from center to mouse (outward)
        # dx = original_x - center_x
        # dy = original_y - center_y

        # # Calculate distance
        # distance = math.sqrt(dx * dx + dy * dy)

        # if distance > 0:
        #     # Normalize direction
        #     norm_dx = dx / distance
        #     norm_dy = dy / distance

        #     # Calculate intersection with screen edges
        #     # Check all four edges and find closest intersection
        #     edge_x = original_x
        #     edge_y = original_y

        #     if norm_dx > 0:  # Moving right
        #         t = (screen.x + screen.width - 1 - center_x) / norm_dx
        #         edge_x = screen.x + screen.width - 1
        #         edge_y = center_y + norm_dy * t
        #     elif norm_dx < 0:  # Moving left
        #         t = (screen.x - center_x) / norm_dx
        #         edge_x = screen.x
        #         edge_y = center_y + norm_dy * t

        #     if norm_dy > 0:  # Moving down
        #         t = (screen.y + screen.height - 1 - center_y) / norm_dy
        #         test_x = center_x + norm_dx * t
        #         test_y = screen.y + screen.height - 1
        #         # Use this edge if it's closer or if x wasn't set
        #         if abs(test_x - original_x) + abs(test_y - original_y) < abs(edge_x - original_x) + abs(edge_y - original_y):
        #             edge_x = test_x
        #             edge_y = test_y
        #     elif norm_dy < 0:  # Moving up
        #         t = (screen.y - center_y) / norm_dy
        #         test_x = center_x + norm_dx * t
        #         test_y = screen.y
        #         if abs(test_x - original_x) + abs(test_y - original_y) < abs(edge_x - original_x) + abs(edge_y - original_y):
        #             edge_x = test_x
        #             edge_y = test_y

        #     # Move mouse to edge, inset by 1 pixel from actual edge
        #     final_x = int(edge_x - norm_dx)
        #     final_y = int(edge_y - norm_dy)
        #     # ctrl.mouse_move(final_x, final_y)
        #     actions.mouse_move(final_x, final_y)

        # # Trigger Windows zoom in
        # actions.sleep("50ms")  # Small delay to ensure mouse move registers
        actions.key("win-keypad_plus")

        # Restore mouse position
        # actions.sleep("300ms")
        # actions.mouse_move(original_x, original_y)

utils = Utils()
