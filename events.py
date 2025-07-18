from talon import actions
from typing import Dict, Set, Optional, Callable
from .config import MODE_COLORS, MODE_CODES, MODIFIER_COLORS

class ParrotEventManager:
    """Manages events for parrot mode v7"""

    def __init__(self):
        self._current_mode = "default"
        self._previous_mode = "default"
        self._active_modifiers: Set[str] = set()
        self._event_listeners: Dict[str, list] = {}

    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to an event"""
        if event_type not in self._event_listeners:
            self._event_listeners[event_type] = []
        self._event_listeners[event_type].append(callback)

    def emit(self, event_type: str, data: Optional[dict] = None):
        """Emit an event to all listeners"""
        if event_type in self._event_listeners:
            for callback in self._event_listeners[event_type]:
                try:
                    callback(data or {})
                except Exception as e:
                    print(f"Error in event callback: {e}")

    def set_mode(self, mode: str):
        """Set the current mode and emit events"""
        if mode != self._current_mode:
            print("Setting mode to:", mode)
            self._previous_mode = self._current_mode
            self._current_mode = mode
            self.emit("mode_changed", {
                "current_mode": self._current_mode,
                "previous_mode": self._previous_mode
            })
            self._update_hud()

    def get_mode(self) -> str:
        """Get the current mode"""
        return self._current_mode

    def get_previous_mode(self) -> str:
        """Get the previous mode"""
        return self._previous_mode

    def return_to_previous_mode(self):
        """Return to the previous mode"""
        self.set_mode(self._previous_mode)

    def add_modifier(self, modifier: str):
        """Add an active modifier"""
        self._active_modifiers.add(modifier)
        self.emit("modifiers_changed", {"modifiers": self._active_modifiers})
        self._update_hud()

    def remove_modifier(self, modifier: str):
        """Remove an active modifier"""
        self._active_modifiers.discard(modifier)
        self.emit("modifiers_changed", {"modifiers": self._active_modifiers})
        self._update_hud()

    def get_modifiers(self) -> Set[str]:
        """Get active modifiers"""
        return self._active_modifiers.copy()

    def clear_modifiers(self):
        """Clear all active modifiers"""
        self._active_modifiers.clear()
        self.emit("modifiers_changed", {"modifiers": self._active_modifiers})
        self._update_hud()

    def _update_hud(self):
        """Update the HUD display"""
        try:
            actions.user.ui_elements_set_state({
                "mode": self._current_mode,
                "color": MODE_COLORS[self._current_mode],
                "code": MODE_CODES[self._current_mode],
                "modifiers": list(self._active_modifiers)
            })
        except Exception as e:
            print(f"Error updating HUD: {e}")

    def _hide_hud(self):
        """Hide the HUD"""
        try:
            actions.user.parrot_v7_hide_hud()
        except Exception as e:
            print(f"Error hiding HUD: {e}")

# Global event manager instance
event_manager = ParrotEventManager()
