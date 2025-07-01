#!/usr/bin/env python3

import unittest
from math import sqrt, cos, pi
import context
import scribbles.core as core
import scribbles.points

class TestCoreFunctions(unittest.TestCase):
    RADIANS = pi / 180
    N_REPS = 25

    def confirm_coords_almost_equal(self, point_1, point_2):
        for i in range(2):
            self.assertAlmostEqual(point_1[i], point_2[i])

    def length_of_third_side(self, length_a, length_c, theta):
        # Use Law of Cosines to calculate the length of the third side of a
        # triangle given the lengths of the other sides, a and c, and the angle
        # theta between them: b² = a² + c² −2ac*cos(Θ)
        return sqrt(length_a**2 + length_c**2 - 2*length_a*length_c*cos(theta * self.RADIANS))

    def test_linear_scribble_get_points_circle(self):
        # For this Scribble, increase the angle by a constant and keep the radius
        # the same. So we're really just generating the points for a circle.
        angle = 15
        scribbler = core.LinearScribble(
            radius_fn=lambda r: r,
            angle_fn=lambda a: a + angle
        )
        radius = 10
        length_per_arc = self.length_of_third_side(radius, radius, angle)
        n_arcs = 360 // angle
        max_length = length_per_arc * n_arcs
        points = scribbler.get_points(radius, max_length)
        total_length = scribbles.points.total_length(points)
        self.assertAlmostEqual(max_length, total_length)
        # Spot-check some points
        self.confirm_coords_almost_equal(points[0], (radius, 0))
        self.confirm_coords_almost_equal(points[6], (0, radius))
        self.confirm_coords_almost_equal(points[12], (-radius, 0))
        self.confirm_coords_almost_equal(points[18], (0, -radius))

    def test_linear_scribble_get_points_given_origin(self):
        angle = 15
        origin_x = 10
        origin_y = -5
        origin = (origin_x, origin_y)
        scribbler = core.LinearScribble(
            origin,
            radius_fn=lambda r: r,
            angle_fn=lambda a: a + angle
        )
        radius = 10
        max_length = 63 # Big enough to generate points along full circumference
        points = scribbler.get_points(radius, max_length)
        total_length = scribbles.points.total_length(points)
        self.assertLess(total_length, max_length)
        # Spot-check some points
        self.confirm_coords_almost_equal(points[0], (radius + origin_x, origin_y))
        self.confirm_coords_almost_equal(points[6], (origin_x, radius + origin_y))
        self.confirm_coords_almost_equal(points[12], (-radius + origin_x, origin_y))
        self.confirm_coords_almost_equal(points[18], (origin_x, -radius + origin_y))

    def test_linear_scribble_get_points_increasing_radius(self):
        # For this Scribble, increase the angle and the radius by constant amounts.
        angle = 15
        radius_offset = 10
        scribbler = core.LinearScribble(
            radius_fn=lambda r: r + radius_offset,
            angle_fn=lambda a: a + angle
        )
        initial_radius = 10
        n_arcs = 90 // angle
        expected_length = 0
        for i in range(n_arcs):
            side_a = initial_radius + i*radius_offset
            side_c = side_a + radius_offset
            arc_length = self.length_of_third_side(side_a, side_c, angle)
            expected_length += arc_length
        max_length = expected_length + 1 # Add 1 to ensure all points are generated
        points = scribbler.get_points(initial_radius, max_length)
        total_length = scribbles.points.total_length(points)
        self.assertAlmostEqual(expected_length, total_length)

    def test_linear_scribble_get_points_max_length(self):
        scribbler = core.LinearScribble()
        max_length = 1000
        for i in range(self.N_REPS):
            with self.subTest(i=i):
                points = scribbler.get_points(10, max_length)
                total_length = scribbles.points.total_length(points)
                self.assertLessEqual(total_length, max_length)

    def test_linear_scribble_invalid_params(self):
        scribbler = core.LinearScribble()
        self.assertRaises(ValueError, scribbler.get_points, 0, 1000)
        self.assertRaises(ValueError, scribbler.get_points, 10, 0)

    def test_bunched_scribble_invalid_params(self):
        scribbler = core.BunchedScribble()
        self.assertRaises(ValueError, scribbler.get_points, 0, 1000)
        self.assertRaises(ValueError, scribbler.get_points, 10, 0)

    def test_bunched_scribble_get_points_max_length(self):
        scribbler = core.BunchedScribble()
        max_length = 1000
        for i in range(self.N_REPS):
            with self.subTest(i=i):
                points = scribbler.get_points(10, max_length)
                total_length = scribbles.points.total_length(points)
                self.assertLessEqual(total_length, max_length)

    def test_bunched_scribble_bezier_curve_points(self):
        scribbler = core.BunchedScribble()
        terminus_1 = (10, 5)
        control = (7, 20)
        terminus_2 = (2, 14)
        n_steps = 10
        curve_points = scribbler.bezier_curve_points(terminus_1, control, terminus_2, n_steps)
        self.assertEqual(len(curve_points), n_steps + 1)
        self.confirm_coords_almost_equal(curve_points[0], terminus_1)
        self.confirm_coords_almost_equal(curve_points[-1], terminus_2)
        origin = (0, 0)
        max_distance = scribbles.points.distance(origin, control)
        # Confirm all points between the terminals are closer to origin than
        # the control point.
        for i in range(1, n_steps):
            self.assertLess(scribbles.points.distance(origin, curve_points[i]), max_distance)

    def test_bunch_scribble_shorten_curve(self):
        points = [
            (0, 0),
            (3, 5),
            (20, 9),
            (-10, 9),
            (-5, -5)
        ]
        curve_length = scribbles.points.total_length(points)
        distance_last_3 = scribbles.points.total_length(points[2:])
        max_length = curve_length - distance_last_3 + 1
        scribbler = core.BunchedScribble()
        new_points, new_curve_length = scribbler._shorten_curve(points, curve_length, max_length)
        self.assertEqual(len(new_points), 3)
        self.assertEqual(new_points, points[:3])
        self.assertAlmostEqual(new_curve_length, scribbles.points.total_length(points[:3]))

    def test_curvy_scribble_invalid_params(self):
        scribbler = core.CurvyScribble()
        self.assertRaises(ValueError, scribbler.get_points, 0, 1000)
        self.assertRaises(ValueError, scribbler.get_points, 10, 0)

    def test_curvy_scribble_get_points_max_length(self):
        scribbler = core.CurvyScribble()
        max_length = 1000
        for i in range(self.N_REPS):
            with self.subTest(i=i):
                points = scribbler.get_points(10, max_length)
                total_length = scribbles.points.total_length(points)
                self.assertLessEqual(total_length, max_length)


if __name__ == '__main__':
    unittest.main()