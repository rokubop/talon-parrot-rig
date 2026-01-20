from talon import Module, actions, storage, ctrl

class Tracking():
    FULL_TRACKING_ID = "parrot_rig.full_tracking"

    def __init__(self):
        self.is_tracking = False
        self.full_tracking = storage.get(self.FULL_TRACKING_ID, False)

    def activate(self, full_tracking=None):
        if not actions.tracking.control_enabled():
            actions.tracking.control_toggle(True)
        if full_tracking is None:
            full_tracking = self.full_tracking

        if full_tracking:
            self.full_track_enable()
        else:
            self.teleport_and_track_head()

    def full_track_enable(self):
        actions.tracking.control_gaze_toggle(True)
        actions.tracking.control_head_toggle(True)
        self.is_tracking = True
        storage.set(self.FULL_TRACKING_ID, True)

    def teleport_and_track_head(self):
        # print("is_tracking:", self.is_tracking)
        # if self.is_tracking:
        actions.tracking.control_mouse_jump_toggle(False)
        actions.tracking.control_head_toggle(False)
        # actions.tracking.control_gaze_toggle(True)
        # actions.sleep("50ms")
        actions.tracking.control_gaze_toggle(False)
        pos = ctrl.mouse_pos()
        actions.tracking.control_head_toggle(True)
        actions.mouse_move(pos[0], pos[1])
        self.is_tracking = True

    def freeze(self):
        was_tracking = self.is_tracking
        if self.is_tracking:
            actions.tracking.control_head_toggle(False)
            actions.tracking.control_gaze_toggle(False)
            self.is_tracking = False
        return was_tracking

    def toggle_full_tracking(self):
        if self.full_tracking:
            self.teleport_and_track_head()
            storage.set(self.FULL_TRACKING_ID, False)
        else:
            self.full_track_enable()

        self.full_tracking = not self.full_tracking

tracking = Tracking()
