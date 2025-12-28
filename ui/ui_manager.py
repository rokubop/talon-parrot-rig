from talon import actions
from .cursor import cursor_ui_instance
from .colors import get_mode_color
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

        event_manager.subscribe("mode_changed", self._mode_callback)
        event_manager.subscribe("modifiers_changed", self._modifiers_callback)

        # Track subscriptions for cleanup
        self._event_callbacks = [
            ("mode_changed", self._mode_callback),
            ("modifiers_changed", self._modifiers_callback)
        ]

    def cleanup(self):
        for event_type, callback in self._event_callbacks:
            event_manager.unsubscribe(event_type, callback)
        self._event_callbacks.clear()

    def _on_mode_changed(self, data):
        mode = data.get("current_mode", "default")
        color = get_mode_color(mode)
        cursor_ui_instance.set_mode(mode)
        cursor_ui_instance.color(color)

    def _on_modifiers_changed(self, data):
        modifiers = data.get("modifiers", set())
        cursor_ui_instance.clear_modifiers()
        for modifier in modifiers:
            cursor_ui_instance.add_modifier(modifier)

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

    def show_utility_selector(self):
        """Show the utility selector UI"""
        from .utility_selector import utility_selector
        actions.user.ui_elements_toggle(utility_selector, show_hints="numbers")

    def show_mouse_pos_marks(self, mouse_pos_ui):
        """Show mouse position marks UI"""
        actions.user.ui_elements_show(mouse_pos_ui)

    def hide_mouse_pos_marks(self, mouse_pos_ui):
        """Hide mouse position marks UI"""
        actions.user.ui_elements_hide(mouse_pos_ui)

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
