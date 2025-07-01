#!/usr/bin/env python3

from functools import reduce
from math import cos, sin, sqrt, pi


def distance(point_1, point_2):
    """Return the distance between the two Cartesian coordinates."""
    return sqrt((point_2[0] - point_1[0])**2 + (point_2[1] - point_1[1])**2)


def total_length(points):
    """Return the total distance across the given points in order."""
    total = 0
    point_1 = points[0]
    for point_2 in points[1:]:
        total += distance(point_1, point_2)
        point_1 = point_2
    return total


def max_distance(points, origin=(0, 0)):
    """Return the maximum distance of points from the given origin."""
    return reduce(lambda d, pt: max(d, distance(origin, pt)), points, 0)


class PointTransformer():
    """Use function composition to implement some common transformations of x-y points."""

    RADIANS = pi / 180

    def __init__(self):
        self._fns = [lambda pt: pt]

    def _apply(self, fn):
        self._fns.append(fn)
        return self

    def rotate(self, angle):
        radians = self.RADIANS * angle
        return self._apply(lambda pt: (pt[0] * cos(radians) + pt[1] * sin(radians),
                                       pt[1] * cos(radians) - pt[0] * sin(radians)))

    def translate(self, x, y):
        return self._apply(lambda pt: (pt[0] + x, pt[1] + y))

    def scale(self, x, y):
        return self._apply(lambda pt: (pt[0] * x, pt[1] * y))

    def mirror_horizontal(self):
        return self._apply(lambda pt: (-pt[0], pt[1]))

    def mirror_vertical(self):
        return self._apply(lambda pt: (pt[0], -pt[1]))

    def limit(self, x_max, x_min, y_max, y_min):
        return self._apply(lambda pt: (min(max(pt[0], x_min), x_max),
                                       min(max(pt[1], y_min), y_max)))

    def transform(self, points):
        """Apply accumulated tranformation operations to given points."""
        # Define a function that composes two functions:
        composition = lambda fn1, fn2: lambda pt: fn2(fn1(pt))
        # Use reduce() to create a new function that is the result of composing
        # the accumulated transformation operations in succession:
        transform = reduce(composition, self._fns)
        return [transform(pt) for pt in points]
