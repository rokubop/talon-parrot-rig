from talon import actions, cron

two_way_opposites = [
    ("north", "south"),
    ("upper", "downer"),
    ("up", "down"),
    ("left", "right"),
    ("push", "tug"),
    ("drain", "step"),
    ("undo", "redo"),
    ("last", "next"),
    ("forward", "back"),
    ("out", "in"),
    ("close", "reopen"),
]

opposites = {}

for key, value in two_way_opposites:
    opposites[key] = value
    opposites[value] = key

class StateReverse:
    def __init__(self):
        self.is_reverse_active = False
        self.timer_handle = None

    def activate_reverse(self):
        self.is_reverse_active = True
        if self.timer_handle:
            cron.cancel(self.timer_handle)
        self.timer_handle = cron.after("2s", self.deactivate_reverse)

    def deactivate_reverse(self):
        self.is_reverse_active = False
        self.timer_handle = None

    def is_active(self):
        return self.is_reverse_active

stateReverse = StateReverse()

def repeat():
    """Repeat the last command"""
    try:
        actions.core.repeat_phrase()
    except IndexError:
        pass

def reverse():
    """Reverse the last command"""
    stateReverse.activate_reverse()
    try:
        actions.core.repeat_phrase()
    except IndexError:
        pass
