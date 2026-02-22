# Parrot Rig

![Version](https://img.shields.io/badge/version-1.3.0-blue)
![Status](https://img.shields.io/badge/status-experimental-orange)
![License](https://img.shields.io/badge/license-Unlicense-green)

A general-purpose 14-noise parrot mode for hands-free mouse control in [Talon](https://talonvoice.com/). This is my daily driver for general mouse use.

You'll need at least 9 noises to use this, 14 recommended for the full experience, or 14 with both utility slots. See remapping instructions below to make it your own.

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

This repo ships with my personal noise assignments. Your trained noises will be different. The goal is to **replace each noise with your own equivalent**. The actions and mode structure stay the same; you're just swapping which noise triggers what.

### Noise reference

Use this table to understand what role each noise plays, then decide which of your noises best fits each slot. Listed in priority order, starting from the top.

| Noise | Role | What it does |
|-------|------|-------------|
| `ah` | direction | Move left |
| `oh` | direction | Move right |
| `t` | direction | Move up |
| `guh` | direction | Move down |
| `ee` | stop | Stop all movement and scrolling |
| `pop` | click | Click and exit mode |
| `mm` | click | Click (stay in mode) |
| `hiss` | scroll / boost | Scroll down, boost in move mode |
| `shush` | scroll / boost | Scroll up, boost in move mode |
| `eh` | tracking / glide | Activate tracking, toggle glide in move mode |
| `er` | scroll mode | Toggle scroll mode |
| `cluck` | exit | Exit parrot rig |
| `palate` | utility | Execute utility action |
| `tut` | combo prefix / reset | Reset speed, prefix for combos (e.g. `tut oh` = right click) |

Recommend **at least 9 noises**: 4 directions + stop + click + exit + 2 scrolls.

### Remapping steps

You'll edit 3 files. In each file, replace every occurrence of the old noise name with your noise name.

**1. [parrot_rig_actions.py](./parrot_rig_actions.py)** - Find-and-replace noise names in the input maps. For example, to use `alveolar_click` instead of `pop` for "click exit":

```python
# before
"pop":    ("click exit", actions.user.parrot_rig_click_exit),
# after
"alveolar_click":  ("click exit", actions.user.parrot_rig_click_exit),
```

Replace all instances of that noise throughout the file (it appears in multiple mode maps).

**2. [parrot_rig_input.talon](./parrot_rig_input.talon)** - Match the `parrot(...)` trigger on the left to your noise. The string on the right must match the key you used in step 1:

```talon
parrot(alveolar_click): user.input_map_channel_handle("parrot_rig", "alveolar_click")
```

**3. [parrot.talon](./parrot.talon)** - Noises outside parrot rig mode. You need at least one noise or voice command to call `user.parrot_rig_enable()` as your entry point:

```talon
parrot(cluck): user.parrot_rig_enable()

# or use a voice command instead
parrot rig start: user.parrot_rig_enable()
```

See [talon-input-map](https://github.com/rokubop/talon-input-map/) for the full set of options to fine-tune how each noise behaves:
- **combos** (`"tut ah"`) - trigger an action with a sequence of noises
- **throttle** (`:th_100`) - limit how often a noise fires (e.g. make a continuous noise act like a discrete trigger)
- **debounce** (`:db_170`) - delay firing so brief interruptions don't trigger it (used on `_stop` events like `hiss_stop`, `shush_stop`)
- **hold/release**, **repeat**, and more

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