from talon import actions
from ..events import event_manager

class Keys:
    def __init__(self):
        self.modifiers = set()

    def toggle_modifier(self, key: str):
        if key in self.modifiers:
            self.modifiers.remove(key)
            actions.key(f"{key}:up")
            event_manager.remove_modifier(key)
        else:
            self.modifiers.add(key)
            actions.key(f"{key}:down")
            event_manager.add_modifier(key)

        return key in self.modifiers

    def clear_modifiers(self):
        for key in self.modifiers:
            actions.key(f"{key}:up")
        self.modifiers.clear()
        event_manager.clear_modifiers()

keys = Keys()
