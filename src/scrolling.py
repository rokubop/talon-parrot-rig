from talon import cron, settings, actions
import time
from ..user_settings import SCROLLING_SETTINGS

class Scrolling():
    def __init__(self):
        self.scroll_job = None
        self.scroll_dir = 1
        self.scroll_start_ts = None
        self.scroll_stop_soft_ts = None
        self.debounce_start_duration = 0.0
        self.debounce_stop_duration = 0.170
        self.scroll_stop_soft_callbacks = []

    def scroll_start(self, direction: str):
        """Start scrolling until stop is called"""
        new_scroll_dir = -1 if direction == "up" else 1
        self.scroll_stop_soft_ts = None

        if self.scroll_job:
            if new_scroll_dir != self.scroll_dir:
                self.scroll_dir = new_scroll_dir
                self.scroll_start_ts = time.perf_counter()
            # scroll_job already exists
            return

        self.scroll_dir = new_scroll_dir
        self.scroll_start_ts = time.perf_counter()
        self._scroll_tick()
        self.scroll_job = cron.interval("16ms", self._scroll_tick)

    def _scroll_tick(self):
        ts = time.perf_counter()
        if self.scroll_start_ts is None:
            return
        if ts - self.scroll_start_ts < self.debounce_start_duration:
            return

        if self.scroll_stop_soft_ts and ts - self.scroll_stop_soft_ts > self.debounce_stop_duration:
            self.scroll_stop_hard()
            if self.scroll_stop_soft_callbacks:
                for callback in self.scroll_stop_soft_callbacks:
                    callback()
            return

        acceleration_speed = 1 + min((ts - self.scroll_start_ts) / 0.5, 4)
        y = (
            SCROLLING_SETTINGS["speed"]
            * acceleration_speed
            * self.scroll_dir
        )
        actions.mouse_scroll(y, by_lines=True)

    def scroll_stop_soft(self):
        self.scroll_stop_soft_ts = time.perf_counter()

    def scroll_stop_hard(self):
        if self.scroll_job:
            cron.cancel(self.scroll_job)
            self.scroll_start_ts = None
            self.scroll_stop_soft_ts = None
            self.scroll_job = None

    def is_scrolling(self):
        return self.scroll_job is not None

    def register_scroll_stop_soft_callback(self, callback):
        self.scroll_stop_soft_callbacks.append(callback)

    def clear_scroll_stop_soft_callbacks(self):
        self.scroll_stop_soft_callbacks.clear()

scrolling = Scrolling()
