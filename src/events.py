from talon import actions
from typing import Dict, Set, Optional, Callable
from ..user_settings import UTILITY_ACTION

class ParrotEventManager:
    def __init__(self):
        self._current_mode = "default"
        self._previous_mode = "default"
        self._active_modifiers: Set[str] = set()
        self._event_listeners: Dict[str, list] = {}
        self._settings = {
            "utility_action": UTILITY_ACTION
        }

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self._event_listeners:
            self._event_listeners[event_type] = []
        self._event_listeners[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable):
        if event_type in self._event_listeners:
            try:
                self._event_listeners[event_type].remove(callback)
                # Clean up empty event type lists
                if not self._event_listeners[event_type]:
                    del self._event_listeners[event_type]
            except ValueError:
                # Callback not found, ignore
                pass

    def emit(self, event_type: str, data: Optional[dict] = None):
        if event_type in self._event_listeners:
            for callback in self._event_listeners[event_type]:
                try:
                    callback(data or {})
                except Exception as e:
                    import traceback
                    print(f"Error in event callback: {e}")
                    traceback.print_exc()

    def set_mode(self, mode: str, update_ui: bool = True):
        if mode != self._current_mode:
            print("Setting mode to:", mode)
            has_parrot_config = not mode in ["boost", "glide"]
            self._previous_mode = self._current_mode
            self._current_mode = mode

            if has_parrot_config:
                actions.user.parrot_config_set_mode(mode)

            self.emit("mode_changed", {
                "current_mode": self._current_mode,
                "previous_mode": self._previous_mode
            })

    def get_mode(self) -> str:
        return self._current_mode

    def get_previous_mode(self) -> str:
        return self._previous_mode

    def return_to_previous_mode(self):
        self.set_mode(self._previous_mode)

    def add_modifier(self, modifier: str):
        self._active_modifiers.add(modifier)
        self.emit("modifiers_changed", {"modifiers": self._active_modifiers})

    def remove_modifier(self, modifier: str):
        self._active_modifiers.discard(modifier)
        self.emit("modifiers_changed", {"modifiers": self._active_modifiers})

    def get_modifiers(self) -> Set[str]:
        return self._active_modifiers.copy()

    def clear_modifiers(self):
        self._active_modifiers.clear()
        self.emit("modifiers_changed", {"modifiers": self._active_modifiers})

    def set_setting(self, setting_name: str, value):
        self._settings[setting_name] = value
        self.emit("setting_changed", {"setting": setting_name, "value": value})

    def get_setting(self, setting_name: str, default=None):
        return self._settings.get(setting_name, default)

    def debug_listeners(self):
        print("Current event listeners:")
        for event_type, callbacks in self._event_listeners.items():
            print(f"  {event_type}: {len(callbacks)} listeners")
        return self._event_listeners

event_manager = ParrotEventManager()
