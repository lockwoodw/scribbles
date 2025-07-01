#!/usr/bin/env python3

from math import cos, sin, pi
from random import randint
from scribbles.points import distance, total_length

"""
A Scribble is a design based on the parametric equations for generating the x-y
coordinates of a circle, where the radius and angle can change randomly between
successive coordinates.
"""

class LinearScribble:
    """Generate the points for a Scribble composed of straight lines."""

    RADIANS = pi / 180

    def __init__(self, origin=(0, 0), radius_fn=lambda r: abs(r + randint(-3, 3)),
                 angle_fn=lambda a: a + randint(1, 50)):
        self.origin = origin
        self.radius_modifier_fn = radius_fn
        self.angle_modifier_fn = angle_fn

    def _get_new_point(self, angle, radius):
        # Apply formula for x-y coordinates for point along circumference
        # of circle.
        radians = angle * self.RADIANS
        x = radius * cos(radians) + self.origin[0]
        y = radius * sin(radians) + self.origin[1]
        new_point = (x, y)
        # Randomly adjust radius and angle used to calculate next point.
        new_radius = self.radius_modifier_fn(radius)
        new_angle = self.angle_modifier_fn(angle)
        return new_point, new_angle, new_radius

    def get_points(self, initial_radius, max_length):
        if initial_radius <= 0:
            raise ValueError('initial_radius must be > 0')
        if max_length <= 0:
            raise ValueError('max_length must be > 0')
        points = []
        length = 0
        radius = initial_radius
        angle = 0
        while length < max_length:
            new_point, angle, radius = self._get_new_point(angle, radius)
            if len(points) > 0:
                new_length = length + distance(points[-1], new_point)
                if new_length > max_length:
                    break
                length = new_length
            points.append(new_point)
        return points



class BunchedScribble(LinearScribble):
    """Generate a Scribble composed of a bunch of quadratic Bezier curves."""

    MINIMUM_STEPS = 10

    def _min_steps(self, steps):
        return max(steps, self.MINIMUM_STEPS)

    def bezier_curve_points(self, terminus_1, control, terminus_2, n_steps):
        """Generate points along a quadratic Bezier curve for given control and
        terminal points, with given number of steps between terminal points.
        """
        def gen_coord(i, t):
            # Quadratic polynomial to calculate x or y coordinate of a point on
            # the curve.
            return (terminus_1[i] * (1-t)**2) + \
                (control[i] * 2 * (1-t) * t) + \
                (terminus_2[i] * t**2)
        def gen_x(t):
            return gen_coord(0, t)
        def gen_y(t):
            return gen_coord(1, t)
        curve_points = [terminus_1]
        step_distance = 1.0 / n_steps
        for i in range(1, n_steps + 1):
            t = i * step_distance
            curve_points.append((gen_x(t), gen_y(t)))
        return curve_points

    def _shorten_curve(self, points, curve_length, max_length):
        # Remove points from the end of the curve until it fits within the max_length.
        n_points = len(points)
        while n_points > 0 and curve_length > max_length:
            removed = points.pop()
            n_points = len(points)
            if n_points > 0:
                last_segment_length = distance(points[-1], removed)
                curve_length -= last_segment_length
        if n_points > 0:
            return points, curve_length
        return [], 0

    def get_points(self, initial_radius, max_length, steps=10):
        """Generate points for a Scribble by taking 3 points at a time using
        the LinearScribble algorithm, and producing a new set of points for
        the Bezier curve defined by those 3 points. Repeat until the max
        length is approached.
        """
        if initial_radius <= 0:
            raise ValueError('initial_radius must be > 0')
        if max_length <= 0:
            raise ValueError('max_length must be > 0')
        length = 0
        radius = initial_radius
        angle = 0
        point_pool = []
        points = []
        n_steps = self._min_steps(steps)
        while length < max_length:
            # Generate three points to form a quadratic Bezier curve: two
            # terminal points and one control point.
            while len(point_pool) < 3:
                new_point, angle, radius = self._get_new_point(angle, radius)
                point_pool.append(new_point)
            terminus_1, control = point_pool.pop(0), point_pool.pop(0)
            # The end point for this curve becomes the starting point for the next curve.
            terminus_2 = point_pool[0]
            new_points = self.bezier_curve_points(terminus_1, control, terminus_2, n_steps)
            # Ensure adding the new curve won't exceed the given max_length.
            remaining = max_length - length
            curve_length = total_length(new_points)
            if curve_length > remaining:
                new_points, curve_length = self._shorten_curve(new_points, curve_length, remaining)
                length += curve_length
                points += new_points
                break # This is the last curve we'll add.
            length += curve_length
            points += new_points
        return points


class CurvyScribble(BunchedScribble):
    """Generate a curvy Scribble using Bezier curves.

    To avoid sharp corners between two generated curves (which can happen with
    the BunchedScribble), take a point about ~5/6ths along the first curve, and
    use it as the first terminus of the next curve. In this way, the final
    terminus of the first curve will become the control point of the next curve.
    """
    def get_points(self, initial_radius, max_length, n_steps=10):
        if initial_radius <= 0:
            raise ValueError('initial_radius must be > 0')
        if max_length <= 0:
            raise ValueError('max_length must be > 0')
        length = 0
        radius = initial_radius
        angle = 0
        point_pool = []
        points = []
        # Determine the index of the point ~5/6ths along the curve;
        # there are n_steps between the curve terminals, so there are
        # n_steps+1 points; subtract 1 to get the index.
        n_steps = self._min_steps(n_steps)
        new_terminus_index = int((n_steps + 1) * 5 / 6) - 1
        while length < max_length:
            # Generate three points to form a quadratic Bezier curve: two
            # terminal points and one control point.
            while len(point_pool) < 3:
                new_point, angle, radius = self._get_new_point(angle, radius)
                point_pool.append(new_point)
            # Preserve the final point in the pool: it will become the control
            # point of the next curve.
            terminus_1, control = point_pool.pop(0), point_pool.pop(0)
            terminus_2 = point_pool[0]
            new_points = self.bezier_curve_points(terminus_1, control, terminus_2, n_steps)
            # Include the new terminus_1 in the list of points for the purposes
            # of calculating the current curve's length.
            new_points = new_points[:new_terminus_index + 1]
            # Ensure adding the current curve won't exceed the given max_length.
            remaining = max_length - length
            curve_length = total_length(new_points)
            if curve_length > remaining:
                new_points, curve_length = self._shorten_curve(new_points, curve_length, remaining)
                length += curve_length
                points += new_points
                break # This is the last curve we'll add.
            # Add the current curve up to but not including the terminus_1 of the new curve.
            new_terminus_1 = new_points.pop()
            points += new_points
            length += curve_length
            # Insert the new terminus_1 before the control point.
            point_pool.insert(0, new_terminus_1)
        return points
