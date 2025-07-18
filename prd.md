# Parrot mode v7

Our goal is to create a new version of parrot_mode_14_noise_v6, using it as a starting point, but with modifications to match our new guidelines.
I like the general structure already of parrot_mode_14_noise_v6, but it relies too much on dynamic if/else conditions, and we want 4 distinct parrot modes this time + 3 new modes, all using parrot_config.

## Modes

### Command mode
The default talon mode when parrot mode is not active.
Probably nothing needs to change compared to parrot_mode_14_noise_v6. This is the `parrot.talon` file.
In this mode, there will be limited noises active
# pop to click # dont worry about this
palate for repeater
cluck to start parrot mode
tut to reverse

### Parrot mode

There are sub parrot modes once inside parrot mode

#### Common noises for every mode
ah - activate move mode if not active and go left
oh - activate move mode if not active and go right
t - activate move mode if not active and go up
guh - activate move mode if not active and go down

ee - stop all, and usually go to default mode, but it depends on the current mode
eh - activate head mode if not active and teleport
er - activate full mode if not active

pop - stop all, click and exit, but remember last mode
cluck - exit and remember last mode

tut mm  -      ("left click drag", lambda: parrot_actions.click(hold=True)),
tut oh  -      ("right click", lambda: parrot_actions.click(button=1)),
tut t   -      ("toggle shift", lambda: parrot_actions.toggle_modifier("shift")),
tut guh -      ("toggle control", lambda: parrot_actions.toggle_modifier("ctrl")),
tut ah  -      ("toggle alt", lambda: parrot_actions.toggle_modifier("alt")),

tut cluck - window mode
tut pop - keyboard mode
tut er - number mode

palate - dynamic utility - default is to hold click. but can choose among
- click
- hold click
- right click
- hold right click
- middle click
- middle hold
- talon repeat last
- talon repeat phrase

tut palate - brings up a UI to select the palate action
should use actions.user.ui_elements inspired by parrot_tester.
should use a `screen` with a small `window` and a `table` with buttons that select, update our preference in a global variable or something, and close the window when clicked, no cancel button needed.

tut tut - brings up a window UI table to view all noises and their mapping of commands in each column to briefly say what it does.

tut hiss OR tut shush - brings up a window UI to change
- change speed of movement
- small boost multiplier
- large boost multiplier
- the time of stop temporarily in full mode.
all options should be a 5 button selection of discrete values. no inputs.

and the time of stop temporarily in full mode.

#### default mode - all movement should always be stopped
...common noises
mm - click
hiss - scroll down
shush - scroll up

#### move mode - ah, oh, t, guh
...common noises
mm - there is a dynamic setting whether click should (stop and go to default mode) or not for this particular mode.  (stop by default) -> click.
hiss - small boost
shush - big boost

#### head mode - eh
...common noises
mm - there is a dynamic setting whether click should (stop and go to default mode) or not for this particular mode.  (stop by default) -> click.
hiss - (stop and go to default mode), and scroll down
shush - (stop and go to default mode), and scroll up

#### full mode - er
...common noises
mm - stop temporarily (NOT default mode) (configurable x seconds - default 1 second), and click
hiss - stop temporarily (NOT default mode) (configurable x seconds - default 1 second), and scroll down
shush - stop temporarily (NOT default mode) (configurable x seconds - default 1 second), and scroll up

#### window mode - tut cluck
ah - snap window left
oh - snap window right
t - screen right
guh - screen left
pop - snap window full
er - window close
tut <number noise> - application switch #
tut - window swap (alt tab)
palate - alt tab
cluck - return to previous mode

#### keyboard mode - tut pop
ah - left arrow
oh - right arrow
t - up arrow
guh - down arrow
palate - tab
hiss - backspace
shush - delete
tut - escape
pop - enter
cluck - return to previous mode

#### number mode - tut t
oh - 0
ee - 1
er - 2
ah - 3
hiss - 4
shush - 5
mm - 6
guh - 7
t - 8
eh - 9
palate - tab
tut - escape
pop - enter
cluck - return to previous mode

### New design changes
Instead of manually setting a color, let's introduce events. we will have a small hud in the corner, using actions.user.ui_elements, that will have a circle there with the color of the mode, and a char code representing the mode.
DEF, MOV, HEAD, FULL, WIN, KEYB, NUMB. The HUD can be pretty simply, I think just color and code is enough for now. it should not use window or be draggable, just simple hud like it is now, but without SVGs.
hud will have the colors now INSTEAD of following the cursor around.
oh we also need state in the hud if a key is held using, an appended rectangle + 1 letter. like we're already doing for the shift key.

- 7 modes, each with a different color, instead of the current 2 modes.
- events so that the hud can control itself.
- use actions.user.ui_elements for any UI elements, referencing parrot_mode_ui, and parrot_tester for any inspiration.
- Do Not do any tests. defer testing to the user at the very end.

Work until all requirements are met, and then we can test it together.
All code will go in `parrot_mode_v7`, following a similar structure to `parrot_mode_14_noise_v6`, but with the new modes and features as described above.

- Do not create any test files.
- Ignore any Talon import errors.