from talon import ui, ctrl

def get_screen():
    current_screen = None
    (x, y) = ctrl.mouse_pos()
    for screen in ui.screens():
        if screen.contains(x, y):
            current_screen = screen

    return current_screen
