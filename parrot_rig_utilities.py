from talon import actions

# Utility map (first key is default mode)
utility_map = {
    "hold_click":       ("Hold Click",       lambda: actions.user.parrot_rig_click(0, True)),
    "click":            ("Click",            lambda: actions.user.parrot_rig_click(0)),
    "right_click":      ("Right Click",      lambda: actions.user.parrot_rig_click(1)),
    "hold_right_click": ("Hold Right Click", lambda: actions.user.parrot_rig_click(1, True)),
    "middle_click":     ("Middle Click",     lambda: actions.user.parrot_rig_click(2)),
    "middle_hold":      ("Middle Hold",      lambda: actions.user.parrot_rig_click(2, True)),
    "repeat_last":      ("Repeat Last",      lambda: actions.core.repeat_command()),
    "repeat_phrase":    ("Repeat Phrase",    lambda: actions.user.parrot_rig_repeat_phrase()),
}

# Utility2 map (first key is default mode)
utility2_map = {
    "middle_click":     ("Middle Click",     lambda: actions.user.parrot_rig_click(2)),
    "click":            ("Click",            lambda: actions.user.parrot_rig_click(0)),
    "hold_click":       ("Hold Click",       lambda: actions.user.parrot_rig_click(0, True)),
    "right_click":      ("Right Click",      lambda: actions.user.parrot_rig_click(1)),
    "hold_right_click": ("Hold Right Click", lambda: actions.user.parrot_rig_click(1, True)),
    "middle_hold":      ("Middle Hold",      lambda: actions.user.parrot_rig_click(2, True)),
    "repeat_last":      ("Repeat Last",      lambda: actions.core.repeat_command()),
    "repeat_phrase":    ("Repeat Phrase",    lambda: actions.user.parrot_rig_repeat_phrase()),
}
