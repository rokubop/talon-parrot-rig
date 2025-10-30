"""
Visual interface for parrot mode v7
Integrates the visual cursor UI with the event system
"""

from .src.visual_ui import visual_ui
from .colors import get_mode_color
from .events import event_manager

class VisualInterface:
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
        """Cleanup event listeners to prevent memory leaks"""
        for event_type, callback in self._event_callbacks:
            event_manager.unsubscribe(event_type, callback)
        self._event_callbacks.clear()

    def _on_mode_changed(self, data):
        """Handle mode change events"""
        mode = data.get("current_mode", "default")
        color = get_mode_color(mode)
        visual_ui.set_mode(mode)
        visual_ui.color(color)

    def _on_modifiers_changed(self, data):
        """Handle modifier change events"""
        modifiers = data.get("modifiers", set())
        visual_ui.clear_modifiers()
        for modifier in modifiers:
            visual_ui.add_modifier(modifier)

    def show(self):
        """Show the visual UI"""
        visual_ui.show()

    def hide(self):
        """Hide the visual UI"""
        visual_ui.hide()

    def show_border(self):
        """Show border around cursor"""
        visual_ui.show_border()

    def hide_border(self):
        """Hide border around cursor"""
        visual_ui.hide_border()

# Create global instance
# Clean up previous instance if it exists (for module reloads)
try:
    # Check if previous instance exists and has cleanup method
    if 'visual_interface' in globals() and hasattr(globals()['visual_interface'], 'cleanup'):
        globals()['visual_interface'].cleanup()
except:
    pass  # Ignore any errors during cleanup

visual_interface = VisualInterface()
