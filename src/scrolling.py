from talon import actions
from ..user_settings import SCROLLING_SETTINGS

class Scrolling():
    def __init__(self):
        self._is_scrolling = False
        self._scroll_speed = SCROLLING_SETTINGS["speed"]

    def scroll_start(self, direction: str):
        self._is_scrolling = True
        actions.user.mouse_rig_scroll_go(direction, self._scroll_speed)

    def scroll_stop_soft(self):
        """Called on noise stop — instant stop (debounce handled by input_map)"""
        self._is_scrolling = False
        actions.user.mouse_rig_scroll_stop()

    def scroll_stop_hard(self):
        """Immediate stop"""
        self._is_scrolling = False
        actions.user.mouse_rig_scroll_stop()

    def is_scrolling(self):
        return self._is_scrolling

scrolling = Scrolling()
