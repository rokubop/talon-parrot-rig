from talon import actions, cron, ctrl
from talon.canvas import Canvas
from talon.skia.canvas import Canvas as SkiaCanvas
from .utils import get_screen

canvas_cursor = None
canvas_cursor_job = None
default_cursor_color = "FF0000"
default_border_color = "FFFFFF"

class Cursor:
    def __init__(self):
        self._color = default_cursor_color
        self._border_color = default_border_color
        self._border_show = False
        self._canvas = None
        self._update_job = None
        self._modifiers = set()

    def on_update(self, c: SkiaCanvas):
        (x, y) = ctrl.mouse_pos()

        # border
        if self._border_show:
            c.paint.color = "000000"
            c.paint.style = c.paint.Style.FILL
            c.draw_circle(x + 20, y + 20, 11)

            c.paint.color = self._border_color
            c.paint.style = c.paint.Style.FILL
            c.draw_circle(x + 20, y + 20, 10)

            c.paint.color = "000000"
            c.paint.style = c.paint.Style.FILL
            c.paint.textsize = 15
            c.draw_circle(x + 20, y + 20, 8)

        # main circle
        c.paint.color = self._color
        c.paint.style = c.paint.Style.FILL
        c.paint.textsize = 15
        c.draw_circle(x + 20, y + 20, 7)

        # modifier circles (shift, ctrl, alt)
        offset_x = 31
        offset_increment = 11
        if "shift" in self._modifiers:
            c.paint.color = "0490c9"
            c.draw_circle(x + offset_x, y + 30, 5)
            offset_x += offset_increment

        if "ctrl" in self._modifiers:
            c.paint.color = "84E773"
            c.draw_circle(x + offset_x, y + 30, 5)
            offset_x += offset_increment

        if "alt" in self._modifiers:
            c.paint.color = "FF6DD9"
            c.draw_circle(x + offset_x, y + 30, 5)
            offset_x += offset_increment

    def show(self):
        if self._canvas is None:
            self._canvas = Canvas.from_screen(get_screen())
            self._canvas.register("draw", self.on_update)
            self._update_job = cron.interval("16ms", self._canvas.freeze)
        else:
            self._canvas.show()

    def hide(self):
        if self._canvas is not None:
            self._canvas.close()
            self._canvas = None
            if self._update_job:
                cron.cancel(self._update_job)
                self._update_job = None

    def color(self, color):
        self._color = color

    def show_border(self):
        self._border_show = True

    def hide_border(self):
        self._border_show = False

    def add_modifier(self, modifier):
        self._modifiers.add(modifier)

    def remove_modifier(self, modifier):
        self._modifiers.discard(modifier)

    def clear_modifiers(self):
        self._modifiers.clear()

cursor = Cursor()
