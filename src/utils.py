from talon import ui, ctrl, actions
import os

def get_screen():
    current_screen = None
    (x, y) = ctrl.mouse_pos()
    for screen in ui.screens():
        if screen.contains(x, y):
            current_screen = screen

    return current_screen

def update_time_of_file(filepath, filename):
    try:
        # Touch the file by updating its modification time
        import time
        os.utime(filepath, None)  # Updates to current time
    except Exception as e:
        print(f"Error updating {filename}: {e}")

def reload_files():
    actions.user.parrot_mode_v7_disable()

    src_dir = os.path.dirname(__file__)
    main_dir = os.path.dirname(os.path.join("..", __file__))

    touched_count = 0

    for filename in os.listdir(src_dir):
        if filename.endswith('.py'):
            filepath = os.path.join(src_dir, filename)
            update_time_of_file(filepath, filename)
            touched_count += 1

    for filename in os.listdir(main_dir):
        if filename.endswith('.py'):
            filepath = os.path.join(main_dir, filename)
            update_time_of_file(filepath, filename)
            touched_count += 1

    print(f"✓ Parrot mode reset and {touched_count} files touched for reload")
