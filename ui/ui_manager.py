from talon import actions
from .cursor import cursor_ui_instance
from ..parrot_rig_settings import MODE_COLORS
from ..src.events import event_manager

class UIManager:
    """Manages the visual interface and integrates with events"""

    def __init__(self):
        self._event_callbacks = []  # Track our event subscriptions
        self._setup_event_listeners()

    def _setup_event_listeners(self):
        """Setup event listeners for mode and modifier changes"""
        # Store callbacks so we can unsubscribe later
        self._mode_callback = self._on_mode_changed
        self._modifiers_callback = self._on_modifiers_changed
        self._speed_level_callback = self._on_speed_level_changed
        self._scroll_direction_callback = self._on_scroll_direction_changed

        event_manager.subscribe("mode_changed", self._mode_callback)
        event_manager.subscribe("modifiers_changed", self._modifiers_callback)
        event_manager.subscribe("speed_level_changed", self._speed_level_callback)
        event_manager.subscribe("scroll_direction_changed", self._scroll_direction_callback)

        # Track subscriptions for cleanup
        self._event_callbacks = [
            ("mode_changed", self._mode_callback),
            ("modifiers_changed", self._modifiers_callback),
            ("speed_level_changed", self._speed_level_callback),
            ("scroll_direction_changed", self._scroll_direction_callback),
        ]

    def cleanup(self):
        for event_type, callback in self._event_callbacks:
            event_manager.unsubscribe(event_type, callback)
        self._event_callbacks.clear()

    def _on_mode_changed(self, data):
        mode = data.get("current_mode", "default")
        color = MODE_COLORS.get(mode, "#FF0000")
        cursor_ui_instance.set_mode(mode)
        cursor_ui_instance.color(color)

    def _on_modifiers_changed(self, data):
        modifiers = data.get("modifiers", set())
        cursor_ui_instance.clear_modifiers()
        for modifier in modifiers:
            cursor_ui_instance.add_modifier(modifier)

    def _on_speed_level_changed(self, data):
        level = data.get("level", 0)
        cursor_ui_instance.set_speed_level(level)

    def _on_scroll_direction_changed(self, data):
        direction = data.get("direction", "down")
        cursor_ui_instance.set_scroll_direction(direction)

    def show(self):
        cursor_ui_instance.show()

    def hide(self):
        cursor_ui_instance.hide()

    def show_border(self):
        cursor_ui_instance.show_border()

    def hide_border(self):
        cursor_ui_instance.hide_border()

    def show_cheatsheet(self):
        """Show the cheatsheet UI"""
        from .cheatsheet import cheatsheet_ui
        actions.user.ui_elements_toggle(cheatsheet_ui)

    def hide_cheatsheet(self):
        """Hide the cheatsheet UI"""
        if actions.user.ui_elements_is_active("cheatsheet"):
            actions.user.ui_elements_hide("cheatsheet")

    def is_cheatsheet_active(self):
        """Check if cheatsheet is currently active"""
        return actions.user.ui_elements_is_active("cheatsheet")

    def show_utility_selector(self, title: str = "Utility"):
        """Show the utility selector UI"""
        from .utility_selector import show_utility_selector
        show_utility_selector(title)

    def show_utility2_selector(self, title: str = "Utility 2"):
        """Show the utility2 selector UI"""
        from .utility_selector import show_utility2_selector
        show_utility2_selector(title)

    def hide_utility_selector(self):
        """Hide the utility selector UI"""
        from .utility_selector import hide_utility_selector
        hide_utility_selector()

    def hide_utility2_selector(self):
        """Hide the utility2 selector UI"""
        from .utility_selector import hide_utility2_selector
        hide_utility2_selector()

# Create global instance
# Clean up previous instance if it exists (for module reloads)
try:
    if 'ui_manager' in globals() and hasattr(globals()['ui_manager'], 'cleanup'):
        globals()['ui_manager'].cleanup()
except Exception as e:
    print(f"Error cleaning up previous ui_manager: {e}")
    import traceback
    traceback.print_exc()

ui_manager = UIManager()
