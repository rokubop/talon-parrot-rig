# Fixed: Utility Action Setting Architecture

## Problem
The `set_utility_action` function was incorrectly storing the utility action setting in the `MODE_COLORS` dictionary:

```python
def set_utility_action(action: str):
    """Set the utility action"""
    # Instead of assigning to import, we'll modify the config dict directly
    MODE_COLORS["utility_action"] = action  # This is a workaround since we can't assign to imports
```

This was a red flag because:
1. **Violation of separation of concerns**: Colors dictionary should only contain colors
2. **Poor architecture**: Settings mixed with display configuration
3. **Confusing code**: Future maintainers would be confused by this hack

## Solution
1. **Added runtime settings to EventManager**: Extended the `ParrotEventManager` class to handle runtime settings that can be changed during execution.

2. **Proper settings management**: Added `set_setting()` and `get_setting()` methods to the event manager:
   ```python
   def set_setting(self, setting_name: str, value):
       """Set a runtime setting"""
       self._settings[setting_name] = value
       self.emit("setting_changed", {"setting": setting_name, "value": value})

   def get_setting(self, setting_name: str, default=None):
       """Get a runtime setting"""
       return self._settings.get(setting_name, default)
   ```

3. **Fixed the UI function**: Updated `set_utility_action` to use the proper settings approach:
   ```python
   def set_utility_action(action: str):
       """Set the utility action"""
       event_manager.set_setting("utility_action", action)
   ```

4. **Updated the action handler**: Modified the `utility()` method in `parrot_actions.py` to read from runtime settings:
   ```python
   def utility(self):
       """Execute utility action based on current setting"""
       action = event_manager.get_setting("utility_action", "hold_click")
   ```

5. **Cleaned up imports**: Removed the unused `UTILITY_ACTION` import from `parrot_actions.py`.

## Benefits
- ✅ **Proper separation of concerns**: Settings are now managed separately from display configuration
- ✅ **Event-driven architecture**: Settings changes emit events for potential listeners
- ✅ **Clean code**: No more hacks or workarounds
- ✅ **Maintainable**: Clear, logical structure that's easy to understand and extend
- ✅ **Follows Talon best practices**: No assignments to imported values

## Files Modified
- `events.py`: Added runtime settings management
- `parrot_mode_ui.py`: Fixed `set_utility_action` function
- `parrot_actions.py`: Updated `utility()` method and cleaned up imports
