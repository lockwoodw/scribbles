#!/usr/bin/env python3

from random import randint
from datetime import datetime
from turtle import Turtle

"""
Helper functions for rendering Scribbles on screen and saving to disk.
"""

def get_color_point(pt, min_pt, max_pt, range_=10):
    """Randomly generate a new color point close to the given point but
    within given min and max too.
    """
    offset = randint(-range_, range_)
    if offset == 0:
        offset = 1
    new_pt = int(abs(pt + offset))
    return max(min_pt, min(max_pt, new_pt))

def get_new_color(color, range_=50):
    """Randomly generate a new color within given range of the given color."""
    r, g, b = color
    def new_pt(pt, range_):
        offset = randint(-range_, range_)
        return int(abs(pt + offset)) % 255
    new_red = new_pt(r, range_)
    diff = abs(r - new_red)
    return (new_red, new_pt(g, diff), new_pt(b, diff))

def get_max_color_point_index(color):
    """Return the index of the dominant point in the given color, and a set of
    the remaining indices."""
    dominant_index = 0
    remaining = set()
    max_pt = -1
    for i in range(len(color)):
        remaining.add(i)
        if color[i] > max_pt:
            max_pt = color[i]
            dominant_index = i
    remaining.remove(dominant_index)
    return dominant_index, remaining

def get_nearby_color(color, min_pt=40, range_=10):
    """Return a new color that preserves the dominant point (r, g, b) of the
     given color within a given range and minimum."""
    dominant_index, remaining = get_max_color_point_index(color)
    new_dominant = get_color_point(color[dominant_index], min_pt, 255, range_)
    max_other = new_dominant - min_pt
    new_color = list(color)
    new_color[dominant_index] = new_dominant
    for index in remaining:
        new_color[index] = get_color_point(color[index], 0, max_other, range_)
    return new_color

def darken_color(color, min_pt=30, decrement=100):
    "Return a new color that is darker than the given color by a given amount"
    "and minimum value."
    r, g, b = color
    def fn(pt): return int(max(pt - decrement, min_pt))
    return [fn(r), fn(g), fn(b)]

def get_timestamp():
    """Return the current timestamp as a string."""
    return str(datetime.now().timestamp()).replace('.', '-')


class TurtleFactory:
    """Set up a context manager for a Turtle and configure the turtle with some
    reasonable defaults for drawing Scribbles etc.
    """

    WINDOW_BORDER_SIZE = 8

    def __init__(self, width, height, dpi=100, bg_color=(0, 0, 0),
                 canvas_name='Turtle Drawing', border_size=None):
        self._turtle = Turtle()
        self._width = width
        self._height = height
        self._dpi = dpi
        if border_size is None:
            border_size = self.WINDOW_BORDER_SIZE
        # Set canvas size--the drawable area of the turtle.
        self._turtle.screen.screensize(self._width, self._height)
        # Set window size--what is viewable on screen; for dimensions larger
        # than the screen allows, a scroll bar is added.
        self._turtle.screen.setup(self._width + border_size,
                                  self._height + border_size)
        self._turtle.hideturtle()
        self._turtle.screen.title(canvas_name)
        # Turn off turtle animation.
        self._turtle.screen.tracer(0, 0)
        # Allow RGB color.
        self._turtle.screen.colormode(255)
        # Because the canvas background is not exported, we have to draw the
        # background explicitly.
        self.set_background_color(bg_color)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Render the design (tracer was turned off in the init method).
        self._turtle.screen.update()
        # Leave the turtle window on screen until closed by user.
        self._turtle.screen.mainloop()

    def get_turtle(self):
        return self._turtle

    def set_background_color(self, color):
        """Draw the background as a rectangle. The dimensions are larger than
        necessary in case the window is resized.
        """
        self._turtle.pencolor(color)
        self._turtle.fillcolor(color)
        self._turtle.begin_fill()
        self._turtle.penup()
        self._turtle.setpos(-self._width, -self._height)
        self._turtle.pendown()
        self._turtle.setpos(self._width, -self._height)
        self._turtle.setpos(self._width, self._height)
        self._turtle.setpos(-self._width, self._height)
        self._turtle.setpos(-self._width, -self._height)
        self._turtle.end_fill()
        # Reset:
        self._turtle.penup()
        self._turtle.setpos(0, 0)

    def export(self, filename, pagewidth=None):
        """Export the turtle window to EPS file."""
        screen = self._turtle.screen
        if pagewidth is None:
            pagewidth = self._width / self._dpi
        canvas = screen.getcanvas()
        # Scroll to origin because the postscript() method seems to capture what
        # is currently displayed in the window.
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)
        # The combination of pagewidth, width, and height parameters must be
        # specified to ensure the rendered postscript has the same dimensions
        # as the canvas.
        canvas.postscript(file=filename, pagewidth=f"{pagewidth}i",
                          width=self._width, height=self._height)