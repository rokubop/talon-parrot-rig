# Parrot Mode v7

An advanced parrot mode implementation with 7 distinct modes and an event-driven HUD system.

## Features

- **7 Distinct Modes**: Each with unique colors and behaviors
  - DEF (Default): Basic mode with limited actions
  - MOV (Move): Movement mode with boosting
  - HEAD (Head): Head tracking mode
  - FULL (Full): Full tracking mode with temporary stops
  - WIN (Window): Window management mode
  - KEYB (Keyboard): Keyboard navigation mode
  - NUMB (Number): Number input mode

- **Event-Driven HUD**: Bottom-right corner display showing:
  - Current mode with color-coded circle
  - Mode code (DEF, MOV, etc.)
  - Active modifier keys (Shift, Ctrl, Alt)

- **Configurable Settings**: All constants stored in `config.py`
- **Dynamic UI Dialogs**: For utility selection, settings, and noise reference
- **Mode Memory**: Returns to previous mode with `cluck`

## Modes

### Command Mode (Outside Parrot Mode)
- `cluck`: Start parrot mode
- `palate`: Repeater
- `tut`: Reverser

### Default Mode
- Basic clicking and scrolling
- All movement is stopped
- Entry point for other modes

### Move Mode
- Activated by movement noises (ah, oh, t, guh)
- Includes boost controls (hiss=small, shush=large)
- Configurable click behavior

### Head Mode
- Activated by `eh` noise
- Teleport and head tracking
- Scroll actions stop and return to default

### Full Mode
- Activated by `er` noise
- Full tracking with temporary stops
- Actions pause tracking briefly, then resume

### Window Mode
- Activated by `tut cluck`
- Window snapping and management
- Application switching with `tut + number`

### Keyboard Mode
- Activated by `tut pop`
- Arrow key navigation
- Standard keyboard actions

### Number Mode
- Activated by `tut t`
- Number input with specific noise mappings
- Quick numeric entry

## Configuration

All settings are in `config.py`:

- `MODE_COLORS`: Colors for each mode
- `MOVEMENT_SETTINGS`: Speed and boost values
- `CLICK_BEHAVIOR`: Click behavior per mode
- `UTILITY_ACTION`: Default utility action
- `SETTINGS_OPTIONS`: UI setting options

## UI Dialogs

- `tut palate`: Utility action selector
- `tut tut`: Noise reference for current mode
- `tut hiss/shush`: Settings UI with 5-button selections

## Common Noises (All Modes)

- `ah/oh/t/guh`: Activate move mode and move
- `eh`: Activate head mode
- `er`: Activate full mode
- `ee`: Stop all actions
- `pop`: Click and exit (remembers last mode)
- `cluck`: Exit and return to previous mode
- `palate`: Dynamic utility action

## Installation

1. Place in your Talon user directory
2. Requires `actions.user.ui_elements` for UI
3. Requires mouse movement actions from Talon Community

## Usage

1. Say `cluck` to enter parrot mode
2. Use movement noises to navigate
3. Switch modes with mode-specific noises
4. Use `tut` combinations for advanced features
5. Exit with `cluck` to return to previous mode
