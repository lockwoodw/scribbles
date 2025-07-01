#!/usr/bin/env python3

import unittest
from random import randint
import context
import scribbles.render as render

class TestRenderFunctions(unittest.TestCase):

    def test_get_color_point_default_range(self):
        pt = 100
        min_pt = 30
        max_pt = 200
        default_range = 10
        # Run a bunch of times because the color point is generated randomly.
        for i in range(100):
            with self.subTest(i=i):
                new_pt = render.get_color_point(pt, min_pt, max_pt)
                self.assertLessEqual(new_pt, pt + default_range)
                self.assertGreaterEqual(new_pt, pt - default_range)

    def test_get_color_point_given_range(self):
        pt = 100
        min_pt = 30
        max_pt = 200
        range_ = 50
        for i in range(100):
            with self.subTest(i=i):
                new_pt = render.get_color_point(pt, min_pt, max_pt, range_)
                self.assertLessEqual(new_pt, pt + range_)
                self.assertGreaterEqual(new_pt, pt - range_)

    def test_get_color_point_min_max(self):
        pt = 70
        min_pt = 30
        max_pt = 100
        range_ = 100
        for i in range(100):
            with self.subTest(i=i):
                new_pt = render.get_color_point(pt, min_pt, max_pt, range_)
                self.assertLessEqual(new_pt, max_pt)
                self.assertGreaterEqual(new_pt, min_pt)

    def confirm_new_color_in_range(self, old_color, new_color, range_):
        n_pts = len(old_color)
        self.assertEqual(n_pts, len(new_color))
        diff = [abs(new_color[x] - old_color[x]) for x in range(n_pts)]
        max_diff = diff[0] # Delta for any color point should not exceed red delta.
        for index in range(n_pts):
            self.assertLessEqual(diff[index], range_)
            self.assertLessEqual(diff[index], max_diff)

    def test_get_new_color_default_range(self):
        color = (100, 120, 200)
        default_range = 50
        for i in range(100):
            with self.subTest(i=i):
                new_color = render.get_new_color(color)
                self.confirm_new_color_in_range(color, new_color, default_range)

    def test_get_new_color_given_range(self):
        color = (100, 120, 200)
        range_ = 30
        for i in range(100):
            with self.subTest(i=i):
                new_color = render.get_new_color(color, range_)
                self.confirm_new_color_in_range(color, new_color, range_)

    def test_get_max_color_point_index(self):
        with self.subTest(name="dominant blue"):
            color = (100, 150, 200)
            index, remaining = render.get_max_color_point_index(color)
            self.assertEqual(index, 2)
            self.assertEqual(len(remaining), 2)
            self.assertIn(0, remaining)
            self.assertIn(1, remaining)
        with self.subTest(name="dominant green"):
            color = (100, 200, 150)
            index, remaining = render.get_max_color_point_index(color)
            self.assertEqual(index, 1)
            self.assertEqual(len(remaining), 2)
            self.assertIn(0, remaining)
            self.assertIn(2, remaining)

    def test_get_nearby_color_default_params(self):
        color = (255, 100, 40) # Mostly red.
        default_range = 10
        min_pt = 40
        def confirm_color_point(pt, original_pt):
            self.assertGreaterEqual(pt, original_pt - default_range)
            self.assertLessEqual(pt, original_pt + default_range)
        for i in range(100):
            with self.subTest(i=i):
                new_color = render.get_nearby_color(color)
                red_pt = new_color[0]
                self.assertGreaterEqual(red_pt, min_pt)
                confirm_color_point(red_pt, color[0])
                max_diff = red_pt - min_pt
                for index in range(1, 3):
                    self.assertGreaterEqual(new_color[index], 0)
                    confirm_color_point(new_color[index], color[index])
                    # Confirm the new color is still predominantly red.
                    self.assertGreater(red_pt, new_color[index])
                    # Confirm the change in color per point does not exceed the
                    # maximum possible change for the dominant point.
                    self.assertLessEqual(new_color[index], max_diff)

    def test_get_nearby_color_given_params(self):
        color = (120, 100, 240) # Mostly blue.
        range_ = 50
        min_pt = 30
        def confirm_color_point(pt, original_pt):
            self.assertGreaterEqual(pt, original_pt - range_)
            self.assertLessEqual(pt, original_pt + range_)
        for i in range(100):
            with self.subTest(i=i):
                new_color = render.get_nearby_color(color)
                blue_pt = new_color[2]
                self.assertGreaterEqual(blue_pt, min_pt)
                confirm_color_point(blue_pt, color[2])
                max_diff = blue_pt - min_pt
                for index in range(2):
                    self.assertGreaterEqual(new_color[index], 0)
                    confirm_color_point(new_color[index], color[index])
                    # Confirm the new color is still predominantly blue.
                    self.assertGreater(blue_pt, new_color[index])
                    # Confirm the change in color per point does not exceed the
                    # maximum possible change for the dominant point.
                    self.assertLessEqual(new_color[index], max_diff)

    def test_darken_color_default(self):
        decrement = 100
        min_pt = 30
        color = (randint(0, 255), randint(0, 255), randint(0, 255))
        new_color = render.darken_color(color)
        for i in range(len(color)):
            with self.subTest(index=i):
                self.assertEqual(new_color[i], max(min_pt, color[i] - decrement))

    def test_darken_color(self):
        decrement = 50
        min_pt = 50
        color = (randint(0, 255), randint(0, 255), randint(0, 255))
        new_color = render.darken_color(color, min_pt, decrement)
        for i in range(len(color)):
            with self.subTest(index=i):
                self.assertEqual(new_color[i], max(min_pt, color[i] - decrement))


if __name__ == '__main__':
    unittest.main()