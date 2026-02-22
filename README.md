# Parrot Rig

![Version](https://img.shields.io/badge/version-1.3.0-blue)
![Status](https://img.shields.io/badge/status-experimental-orange)
![License](https://img.shields.io/badge/license-Unlicense-green)

A general-purpose 14-noise parrot mode for hands-free mouse control in [Talon](https://talonvoice.com/). This is my daily driver for general mouse use.

You'll need at least 9 noises to use this, 12 recommended for the full experience, or 14 with both utility slots. See remapping instructions below to make it your own.

![preview](./preview.png)

## Installation

### Dependencies

- [**Talon Beta**](https://talon.wiki/Help/beta_talon/)
- **Eye Tracker** (recommended) - Eye tracking device (e.g., Tobii 4C or Tobii 5)
- **Parrot** - Trained parrot model with `parrot_integration.py` and `patterns.json` files
- [**talon-input-map**](https://github.com/rokubop/talon-input-map/) (v0.7.0+)
- [**talon-mouse-rig**](https://github.com/rokubop/talon-mouse-rig) (v2.2.0+)
- [**talon-ui-elements**](https://github.com/rokubop/talon-ui-elements) (v0.14.1+)

### Install

Clone the dependencies and this repo into your [Talon](https://talonvoice.com/) user directory:

```sh
# mac and linux
cd ~/.talon/user

# windows
cd ~/AppData/Roaming/talon/user

# Dependencies
git clone https://github.com/rokubop/talon-input-map/
git clone https://github.com/rokubop/talon-mouse-rig
git clone https://github.com/rokubop/talon-ui-elements

# This repo
git clone https://github.com/rokubop/talon-parrot-rig
```

## How to customize

We'll need to edit 3 files to get started. Everything else is optional.

### File 1: [parrot_rig_actions.py](./parrot_rig_actions.py)

Start here. This defines what every noise does in each mode. You can reassign actions, add new entries, or change the mode structure:

```python
input_map_common = {
    "ee":     ("stop", actions.user.parrot_rig_stop),
    "pop":    ("click exit", actions.user.parrot_rig_click_exit),
    "ah":     ("move left", lambda: actions.user.parrot_rig_move("left")),
    "oh":     ("move right", lambda: actions.user.parrot_rig_move("right")),
    ...
}
```

Each entry is `"noise": ("label", action)`. If you replace a noise, update all instances of it across the file.

Recommended minimum (9 noises):
- 4 cardinal directions (move left/right/up/down)
- 1 stop
- 1 exit
- 1 click
- 2 scroll (down/up, doubles as boost in move mode)

Remove any entries you don't have noises for.

For example, if you want `cluck` to be "click exit" instead of `pop`, change it here:

```python
"cluck": ("click exit", actions.user.parrot_rig_click_exit),
```

Then update File 2 to match:

```talon
parrot(cluck): user.input_map_handle("cluck")
```

See [talon-input-map](https://github.com/rokubop/talon-input-map/) for combos (`"tut ah"`), throttle (`:th_100`), debounce (`:db_170`), and other options.

### File 2: [parrot_rig_input.talon](./parrot_rig_input.talon)

Noises while in parrot rig mode. Change the `parrot(...)` on the left side to your noises. The right side should match the noise names in File 1.

### File 3: [parrot.talon](./parrot.talon)

Noises outside parrot rig mode. The most important thing is having a way to call `user.parrot_rig_enable()` - that's your entry point. This can be a noise or a voice command. Make sure you also have a way to exit (the input map has `parrot_rig_exit` mapped by default, or use `user.parrot_rig_disable()`).

```talon
parrot(cluck): user.parrot_rig_enable()

# or use a voice command
parrot rig start: user.parrot_rig_enable()
```

### Optional: [parrot_rig_settings.py](./parrot_rig_settings.py)

Speeds, timings, colors, and click behavior. Say **"parrot rig reload"** after changing these.

```python
MOVE_SPEED = 3
SLOW_MODE_MULTIPLIER = 0.5
BOOST_AMOUNT = 10
SCROLL_SPEED = 0.4
TRACKING_STOP_MS = 800
CLICK_HOLD_MS = 16000
```

### Optional: [parrot_rig_utilities.py](./parrot_rig_utilities.py)

Two utility slots you can cycle through at runtime using a noise-triggered selector. The first key in each map is the default. Add, remove, or reorder options:

```python
utility_map = {
    "hold_click":  ("Hold Click",  lambda: actions.user.parrot_rig_click(0, True)),
    "click":       ("Click",       lambda: actions.user.parrot_rig_click(0)),
    "right_click": ("Right Click", lambda: actions.user.parrot_rig_click(1)),
    ...
}

utility2_map = {
    "middle_click": ("Middle Click", lambda: actions.user.parrot_rig_click(2)),
    ...
}
```