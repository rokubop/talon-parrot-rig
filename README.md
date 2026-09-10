# Parrot Rig

![Version](https://img.shields.io/badge/version-2.1.0-blue)
![Status](https://img.shields.io/badge/status-experimental-orange)
![License](https://img.shields.io/badge/license-Unlicense-green)

A general-purpose 14-noise parrot mode for hands-free mouse control in [Talon](https://talonvoice.com/). This is my daily driver for general mouse use.

You'll need at least 9 noises to use this, 14 recommended for the full experience. See remapping instructions below to make it your own.

![preview](./preview.png)

## Installation

### Dependencies

- [**Talon Beta**](https://talon.wiki/Help/beta_talon/)
- **Eye Tracker** - Eye tracking device (e.g., Tobii 4C or Tobii 5)
- **Parrot** - Trained parrot model with `parrot_integration.py` and `patterns.json` files
- [**talon-input-map**](https://github.com/rokubop/talon-input-map/) (v1.0.1+)
- [**talon-mouse-rig**](https://github.com/rokubop/talon-mouse-rig) (v4.1.1+)
- [**talon-ui-elements**](https://github.com/rokubop/talon-ui-elements) (v0.16.0+)
- [**talon-rig-core**](https://github.com/rokubop/talon-rig-core) (v0.6.5+) - required by talon-mouse-rig

### Optional

- [**BentoLaunch**](https://github.com/rokubop/bentolaunch) - Windows app launcher on ``alt+` ``. That is the key the app picker presses, so any launcher bound to it works.

### Install

Clone the dependencies and this repo into your [Talon](https://talonvoice.com/) user directory:

```sh
# Mac/Linux
cd ~/.talon/user

# Windows
cd ~/AppData/Roaming/talon/user

# Dependencies
git clone https://github.com/rokubop/talon-input-map/
git clone https://github.com/rokubop/talon-mouse-rig
git clone https://github.com/rokubop/talon-ui-elements
git clone https://github.com/rokubop/talon-rig-core

# This repo
git clone https://github.com/rokubop/talon-parrot-rig
```

## How to customize

This repo ships with my personal noise assignments. Your trained noises will be different. The goal is to **replace each noise with your own equivalent**. The actions and mode structure stay the same; you're just swapping which noise triggers what.

### Noise reference

Use this table to understand what role each noise plays, then decide which of your noises best fits each slot. Listed in priority order, starting from the top.

| Noise | Role | General behavior |
|-------|------|-------------|
| `ah` | direction | left |
| `oh` | direction | right |
| `t` | direction | up |
| `guh` | direction | down |
| `ee` | stop | Stop movement, scrolling |
| `pop` | return | Either click and exit, or return to an anchor position |
| `mm` | click | Click (stay in mode) |
| `hiss` | scroll / boost | Scroll down, boost in move mode |
| `shush` | scroll / boost | Scroll up, boost in move mode |
| `eh` | tracking / glide | Activate tracking, toggle glide in move mode |
| `er` | mode gateway | Canvas and back. On arrival, `hiss` `mm` `ee` redirect elsewhere for 300ms |
| `cluck` | Start or exit parrot mode | any context |
| `palate` | utility 1 | App picker by default. `tut palate` rebinds it. |
| `tut` | cancel / combo prefix | General cancel action (after 300ms) or prefix for combos. |

Recommend **at least 9 noises**: 4 directions + stop + click + exit + 2 scrolls.

Say **"parrot help"** to see the full input map reference in-app:

![parrot rig help](./parrot_rig_help_preview.png)

### Remapping steps

You'll edit 3 files. In each file, replace every occurrence of the old noise name with your noise name.

**1. [parrot_rig_actions.py](./parrot_rig_actions.py)** - Find-and-replace noise names in the input maps. For example, to use `alveolar_click` instead of `pop` for "click exit":

```python
# before
"pop":    ("click exit", parrot_actions.click_exit),
# after
"alveolar_click":  ("click exit", parrot_actions.click_exit),
```

Replace all instances of that noise throughout the file (it appears in multiple mode maps).

If you don't have enough noises, you can use combos to free up single noises for more actions. For example, `"tut ah"`, `"tut oh"`, `"tut mm"` as combos instead of using those noises alone.

**Mac users:** Change `"ctrl"` to `"cmd"` in the modifier toggle for `tut ee` in `input_map_common`.

**2. [parrot_rig_input.talon](./parrot_rig_input.talon)** - Match the `parrot(...)` trigger on the left to your noise. The string on the right must match the key you used in step 1:

```talon
parrot(alveolar_click): user.input_map_channel_handle("parrot_rig", "alveolar_click")
```

**3. [parrot.talon](./parrot.talon)** - Noises outside parrot rig mode. Only use noises here that won't interfere with your voice commands. You need at least one noise or voice command to call `user.parrot_rig_enable()` as your entry point:

```talon
parrot(cluck): user.parrot_rig_enable()

# or use a voice command instead
parrot rig start: user.parrot_rig_enable()
```

These go through their own input map channel, `input_map_global` in
[parrot_rig_actions.py](./parrot_rig_actions.py), so they get combos too:

| | |
|---|---|
| `pop` | click |
| `cluck` | parrot rig |
| `palate` | whatever the picker says, Repeat Phrase out of the box |
| `tut` | reverse command, or back out of a menu |
| `tut pop` | next anchor |
| `tut palate` | palate picker, borrowing the rig to aim it |

`tut` is a combo prefix, which normally makes a noise wait out the combo window
before it fires. `":now"` opts out: `tut` fires straight away and the combo
still lands after it. The cost is that a combo runs `tut` first, so `tut pop`
reverses and then steps the anchor. Drop the `":now"` if you would rather wait
out the window and have the combos land clean.

Anchors survive leaving parrot mode, so `tut pop` cycles the ones you already
set.

With the rig off nothing is aiming, so `tut palate` turns parrot mode and the
tracker on for the picker and back off when it closes. From the settings hub,
where the rig is already running, nothing changes.

See [talon-input-map](https://github.com/rokubop/talon-input-map/) for the full set of options to fine-tune how each noise behaves:
- **combos** (`"tut ah"`) - trigger an action with a sequence of noises
- **throttle** (`:th_100`) - limit how often a noise fires (e.g. make a continuous noise act like a discrete trigger)
- **debounce** (`:db_170`) - delay firing so brief interruptions don't trigger it (used on `_stop` events like `hiss_stop`, `shush_stop`)
- **hold/release**, **repeat**, and more

> **Important:** After any changes to this repo, say **"parrot reload"** (or **"parrot reset"**). Talon often won't pick up mapping changes automatically due to how the repo is structured.

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

## Reference

### Modes

| Mode | Enter | Details |
|------|-------|---------|
| Enter parrot mode | `cluck` | |
| Exit parrot mode | `cluck` | |
| Stopped | - | |
| Cursor move | use a direction noise `ah`, `oh`, `t`, `guh` | |
| Canvas scroll | `er`, or `tut shush` | Like moving 2 fingers on a trackpad |
| Canvas scale | `er` then `hiss`, or `tut hiss` | 6 noises to account for [ctrl, alt, shift] + [scroll up/down] |
| Canvas drag | `er` then `mm`, or `tut guh` | Hold middle mouse and movement. **Drag** in settings holds left, right, or space instead |
| Window control | `tut t`, or `er` then `shush` | Directions nudge the window. Inside, `tut` + a direction is the screens and the two closes, alt+tab on `pop`, tabs on `hiss` and `shush` |
| App picker (using [BentoLaunch](https://github.com/rokubop/bentolaunch)) | `palate` | Easy to click app launcher |
| Utility 1 picker | `tut palate` | Assign the utility 1 noise. See below. |
| Settings | `tut cluck` | Speeds, click behavior, profiles, cheatsheet |
| Exit mode | `tut` or `er` | |

The cheatsheet is the last tile in settings, or say **"parrot help"**. Both
open the same one, and `tut` backs out of it like any other menu.

### The `er` gateway

`er` goes to canvas and back. Always canvas, never whatever you used last, so it
is a door you can aim at rather than guess.

The other modes come from the moment right after. For 300ms after `er` lands you
in canvas, three noises go somewhere else instead of doing their canvas job:

| | |
|---|---|
| `hiss` | canvas scale |
| `shush` | window |
| `mm` | canvas drag |

After that they go back to canvas resume, canvas resume, and click. The cheatsheet shows
both meanings in the canvas column, the redirect under the window it lasts.

This is [talon-input-map](https://github.com/rokubop/talon-input-map/)'s `":init"`.
`user.input_map_init_window` changes the 300ms.

### Modifiers

`tut eh` shift, `tut ee` ctrl, `tut er` alt. They stack, and `tut` on its own
clears them.

### Utility 1 picker

Utility 1 is the one noise you reassign as you go. `tut palate` opens the
picker.

Out of the box it presses ``alt+` `` and starts tracking, so you look at the
app you want and click it. Same in every mode, window mode included, and no
mode change. `APP_PICKER_KEY` in
[parrot_rig_settings.py](./parrot_rig_settings.py) is the key. Swap utility 1
for a repeat, or anything below.

Three sources, all on one screen:

- **Presets** - app picker, plus the eight mouse actions
- **Last voice commands** - your last 5 commands, bound as a `mimic`
- **Last parrot rig actions** - your last 5 rig actions, bound as the action itself

Built for an eye tracker. Big tiles, no hints, nothing on a noise.

**Two slots, one picker.** `tut palate` inside parrot mode picks for utility 1.
`tut palate` with the rig off picks for palate out there, its own binding and
its own preset list, and neither slot knows about the other. Both save with the
profile. `UTILITY_SLOTS` in
[parrot_rig_settings.py](./parrot_rig_settings.py) names them.

Every menu works this way. Opening one takes no noise and puts the rig in
tracking, so you look at a tile and click it. `tut` is the only noise a menu
takes, and it always means back.

Commands, not phrases. Talon keeps recognising while the rig runs, and
`^<phrase>$: skip()` swallows it so talking cannot fire noises. Those
recognitions are still recorded, and they are the recogniser guessing at a
mouth noise, so they are filtered out. What is left is what you meant to say.

Rig actions already on a bare noise are left out of the list - binding `move
left` to it gains nothing. `UTILITY_HISTORY_SKIP` in
[parrot_rig_settings.py](./parrot_rig_settings.py) is the filter.

Whatever you pick is saved with your profile.

## More Talon packages
Check out my other Talon packages for UI, mouse control, input mapping, and more at [talon-hub-roku](https://github.com/rokubop/talon-hub-roku).
