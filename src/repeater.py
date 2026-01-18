from talon import actions, cron, Module

mod = Module()

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

last_tut = ""
last_palate = ""

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
    global last_palate, last_tut

    if last_palate:
        actions.repeat_command(last_palate)
    elif last_tut:
        actions.repeat_command(last_tut)
    else:
        try:
            actions.core.repeat_command()
        except IndexError:
            pass  # No command history yet

def reverse():
    """Reverse the last command"""
    global last_palate, last_tut

    stateReverse.activate_reverse()
    if last_palate:
        # Try to reverse the last palate action
        if last_palate in opposites:
            actions.mimic(opposites[last_palate])
        else:
            try:
                actions.core.repeat_command()
            except IndexError:
                pass  # No command history yet
    else:
        try:
            actions.core.repeat_command()
        except IndexError:
            pass  # No command history yet

@mod.action_class
class Actions:
    def parrot_mode_interactive_repeater():
        """Parrot mode v7 repeater"""
        repeat()

    def parrot_mode_interactive_reverser():
        """Parrot mode v7 reverser"""
        reverse()
