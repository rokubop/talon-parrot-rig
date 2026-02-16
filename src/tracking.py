from talon import actions

class Tracking():
    def __init__(self):
        self.is_tracking = False

    def activate(self):
        if not actions.tracking.control_enabled():
            actions.tracking.control_toggle(True)
        actions.tracking.control_gaze_toggle(True)
        actions.tracking.control_head_toggle(True)
        self.is_tracking = True

    def freeze(self):
        was_tracking = self.is_tracking
        if self.is_tracking:
            actions.tracking.control_head_toggle(False)
            actions.tracking.control_gaze_toggle(False)
            self.is_tracking = False
        return was_tracking

tracking = Tracking()
