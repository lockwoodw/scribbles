#!/usr/bin/env python3

import unittest
from math import sqrt
import context
import scribbles.points

class TestPointFunctions(unittest.TestCase):

    def confirm_coords_almost_equal(self, point_1, point_2):
        for i in range(2):
            self.assertAlmostEqual(point_1[i], point_2[i])

    def test_distance(self):
        point_1 = (0, 0)
        point_2 = (4, 3)
        self.assertAlmostEqual(scribbles.points.distance(point_1, point_2), 5)

    def test_distance_floating_point(self):
        point_1 = (3, 2)
        point_2 = (9, 7)
        self.assertAlmostEqual(scribbles.points.distance(point_1, point_2), sqrt(61))

    def test_total_length(self):
        points = [
            (0, 0),
            (3, 5),
            (20, 9),
            (-10, 9),
            (-5, -5)
        ]
        expected = sqrt(9 + 25) + sqrt(17**2 + 16) + sqrt(30**2) + sqrt(25 + 14**2)
        self.assertAlmostEqual(scribbles.points.total_length(points), expected)

    def test_max_distance(self):
        y2 = -5.01
        points = [
            (5, 5),
            (-5, y2),
            (-5, 5)
        ]
        expected = sqrt(25 + y2**2)
        self.assertAlmostEqual(scribbles.points.max_distance(points, (0, 0)), expected)

    def confirm_points_are_equal(self, expected, actual):
        n_points = len(expected)
        self.assertEqual(n_points, len(actual))
        for i in range(n_points):
            self.confirm_coords_almost_equal(expected[i], actual[i])

    def test_point_transformer_translate(self):
        points = [
            (0, 0),
            (3, 5),
            (10, -12),
            (-50, -15),
            (-40, 16)
        ]
        x_offset = 5
        y_offset = -10
        expected = [(x + x_offset, y + y_offset) for x,y in points]
        transformer = scribbles.points.PointTransformer().translate(x_offset, y_offset)
        translated = transformer.transform(points)
        self.confirm_points_are_equal(expected, translated)

    def test_point_transformer_scale(self):
        points = [
            (0, 0),
            (3, 5),
            (10, -12),
            (-50, -15),
            (-40, 16)
        ]
        x_scale = 5
        y_scale = 0.5
        expected = [(x * x_scale, y * y_scale) for x,y in points]
        transformer = scribbles.points.PointTransformer().scale(x_scale, y_scale)
        translated = transformer.transform(points)
        self.confirm_points_are_equal(expected, translated)

    def test_point_transformer_mirror_horizontal(self):
        points = [
            (0, 0),
            (3, 5),
            (10, -12),
            (-50, -15),
            (-40, 16)
        ]
        expected = [(-x, y) for x,y in points]
        transformer = scribbles.points.PointTransformer().mirror_horizontal()
        translated = transformer.transform(points)
        self.confirm_points_are_equal(expected, translated)

    def test_point_transformer_mirror_vertical(self):
        points = [
            (0, 0),
            (3, 5),
            (10, -12),
            (-50, -15),
            (-40, 16)
        ]
        expected = [(x, -y) for x,y in points]
        transformer = scribbles.points.PointTransformer().mirror_vertical()
        translated = transformer.transform(points)
        self.confirm_points_are_equal(expected, translated)

    def test_point_transformer_rotate(self):
        eighth_rotation_magnitude = sqrt(2) / 2
        points = [
            (0, 1),
            (-eighth_rotation_magnitude, eighth_rotation_magnitude)
        ]
        expected = [
            (-eighth_rotation_magnitude, eighth_rotation_magnitude),
            (-1, 0)
        ]
        transformer = scribbles.points.PointTransformer().rotate(-45)
        translated = transformer.transform(points)
        self.confirm_points_are_equal(expected, translated)

    def test_point_transformer_operation_order(self):
        points = [
            (0, 0),
            (3, 5),
            (10, -12),
            (-50, -15),
            (-40, 16)
        ]
        x_offset = 5
        y_offset = -10
        x_scale = 3.5
        y_scale = 0.5
        with self.subTest(order="translate, scale"):
            expected = [((x + x_offset) * x_scale, (y + y_offset) * y_scale) for x,y in points]
            transformer = scribbles.points.PointTransformer()\
                .translate(x_offset, y_offset)\
                .scale(x_scale, y_scale)
            translated = transformer.transform(points)
            self.confirm_points_are_equal(expected, translated)
        with self.subTest(order="scale, translate"):
            expected = [(x * x_scale + x_offset, y * y_scale + y_offset) for x,y in points]
            transformer = scribbles.points.PointTransformer()\
                .scale(x_scale, y_scale)\
                .translate(x_offset, y_offset)
            translated = transformer.transform(points)
            self.confirm_points_are_equal(expected, translated)

    def test_point_transformer_limit(self):
        points = [
            (0, 0),
            (3, 5),
            (10, -12),
            (-50, -15),
            (-40, 16)
        ]
        x_min = -15
        x_max = 8
        y_min = -10
        y_max = 15
        expected = list(map(lambda pt: (min(max(x_min, pt[0]), x_max), min(max(y_min, pt[1]), y_max)), points))
        transformer = scribbles.points.PointTransformer().limit(x_max, x_min, y_max, y_min)
        translated = transformer.transform(points)
        self.confirm_points_are_equal(expected, translated)

    def test_point_transformer_reusing_a_transform(self):
        points_1 = [
            (0, 0),
            (3, 5),
            (10, -12),
            (-50, -15),
            (-40, 16)
        ]
        points_2 = [
            (4, 9),
            (42, 1968),
            (-17, -21)
        ]
        x_offset = 5
        y_offset = -10
        x_scale = 3.5
        y_scale = 0.5
        transformer = scribbles.points.PointTransformer()\
            .translate(x_offset, y_offset)\
            .scale(x_scale, y_scale)
        with self.subTest(points=points_1):
            expected = [((x + x_offset) * x_scale, (y + y_offset) * y_scale) for x,y in points_1]
            translated = transformer.transform(points_1)
            self.confirm_points_are_equal(expected, translated)
        with self.subTest(points=points_2):
            expected = [((x + x_offset) * x_scale, (y + y_offset) * y_scale) for x,y in points_2]
            translated = transformer.transform(points_2)
            self.confirm_points_are_equal(expected, translated)


if __name__ == '__main__':
    unittest.main()