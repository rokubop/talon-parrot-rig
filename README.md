# Parrot Rig

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Status](https://img.shields.io/badge/status-experimental-orange)

A general-purpose 14-noise parrot mode for hands-free mouse control in [Talon](https://talonvoice.com/).

Install it, remap the noises to your own, and you're good to go. This is my daily driver for general computer use. Swap noises, remap actions, tune settings - make it yours.

## Installation

### Dependencies

- [**Talon Beta**](https://talon.wiki/Help/beta_talon/)
- **Eye Tracker** - Eye tracking device (e.g., Tobii 4C or Tobii 5)
- **Parrot** - Trained parrot model with `parrot_integration.py` and `patterns.json` files
- [**talon-input-map**](https://github.com/rokubop/talon-input-map/) (v0.6.1+)
- [**talon-mouse-rig**](https://github.com/rokubop/talon-mouse-rig) (v2.0.0+)
- [**talon-ui-elements**](https://github.com/rokubop/talon-ui-elements) (v0.14.0+)

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
git clone <github_url>  # Add github URL to manifest.json
```

> **Note**: Review code from unfamiliar sources before installing.


## How to customize

### Step 1: Remap noises to your own

Update these two files to use noises you can produce:

- **`parrot_rig_input.talon`** — noises used inside parrot rig mode
- **`parrot.talon`** — noises used outside parrot rig mode

Just change the `parrot(...)` noise on the left side of each line. The right side (the input name in quotes) stays the same.

### Step 2: Set up your entry point (`parrot.talon`)

The most important thing is having a way to call `user.parrot_rig_enable()` — that's your entry point into parrot rig mode. This can be a noise or a voice command. Make sure you also have a way to exit (the input map has `parrot_rig_exit` mapped to `cluck` by default, but you can also use `user.parrot_rig_disable()`).

```talon
parrot(cluck): user.parrot_rig_enable()

# or use a voice command
parrot rig start: user.parrot_rig_enable()
```

### Step 3: Customize the input map (`parrot_rig_actions.py`)

This defines what every noise does in each mode. You can reassign actions, add new entries, or change the mode structure:

```python
input_map_common = {
    "ee":     ("stop", actions.user.parrot_rig_stop),
    "pop":    ("click exit", actions.user.parrot_rig_click_exit),
    "ah":     ("move left", lambda: actions.user.parrot_rig_move("left")),
    "oh":     ("move right", lambda: actions.user.parrot_rig_move("right")),
    ...
}
```

Each entry is `"input_name": ("label", action)`. The label shows up in the cheatsheet UI. There are three mode-specific maps (`input_map_default`, `input_map_move`, `input_map_tracking`) that override entries from `input_map_common`.

See [talon-input-map](https://github.com/rokubop/talon-input-map/) for combos (`"tut ah"`), throttle (`:th_100`), debounce (`:db_170`), and other options.

### Step 4: Tune settings (`parrot_rig_settings.py`)

Speeds, timings, colors, and click behavior. Say **"parrot rig reload"** after changing these.

```python
MOVE_SPEED = 3
SLOW_MODE_MULTIPLIER = 0.5
BOOST_AMOUNT = 10
SCROLL_SPEED = 0.4
TRACKING_STOP_MS = 800
CLICK_HOLD_MS = 16000
```

### Step 5: Configure utilities (`parrot_rig_utilities.py`)

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