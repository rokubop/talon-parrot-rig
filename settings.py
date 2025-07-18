from talon import Module
mod = Module()

mod.setting(
    name="parrot_mode_v7_mouse_scroll_speed",
    type=float,
    default=0.8,
    desc="Setting for parrot mode v7 mouse scroll speed"
)

mod.setting(
    name="parrot_mode_v7_movement_speed",
    type=int,
    default=60,
    desc="Setting for parrot mode v7 movement speed"
)

mod.setting(
    name="parrot_mode_v7_boost_small",
    type=int,
    default=100,
    desc="Setting for parrot mode v7 small boost amount"
)

mod.setting(
    name="parrot_mode_v7_boost_large",
    type=int,
    default=200,
    desc="Setting for parrot mode v7 large boost amount"
)

mod.setting(
    name="parrot_mode_v7_full_stop_time",
    type=float,
    default=1.0,
    desc="Setting for parrot mode v7 full mode stop time"
)
