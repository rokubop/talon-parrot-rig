"""
Visual interface for parrot mode v7
Integrates the visual cursor UI with the event system
"""

from .src.visual_ui import visual_ui, MODE_COLORS
from .events import event_manager

class VisualInterface:
    """Manages the visual interface and integrates with events"""

    def __init__(self):
        self._setup_event_listeners()

    def _setup_event_listeners(self):
        """Setup event listeners for mode and modifier changes"""
        event_manager.subscribe("mode_changed", self._on_mode_changed)
        event_manager.subscribe("modifiers_changed", self._on_modifiers_changed)

    def _on_mode_changed(self, data):
        """Handle mode change events"""
        mode = data.get("current_mode", "default")
        color = MODE_COLORS.get(mode, "FF0000")  # Default to red if mode not found
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
visual_interface = VisualInterface()
