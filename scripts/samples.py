#!/usr/bin/env python3

"""
Generate some sample Scribbles illustrating their variety.
"""

from argparse import ArgumentParser
from random import randint
from context import basename, join
from scribbles.core import LinearScribble, BunchedScribble, CurvyScribble
from scribbles.points import PointTransformer
from scribbles.render import TurtleFactory, get_timestamp

script_name = basename(__file__)

def draw_samples(width, height, scaling_factor, base_color, background_color,
                 canvas_name, quiet, folder):

    with TurtleFactory(width, height, bg_color=background_color,
                       canvas_name=canvas_name) as tf:

        turtle = tf.get_turtle()
        turtle.pensize(2)
        turtle.pencolor(base_color)

        def scale_point(p):
            return (x * scaling_factor for x in p)

        def draw(points):
            turtle.penup()
            turtle.setposition(scale_point(points[0]))
            turtle.pendown()
            for point in points[1:]:
                turtle.setposition(scale_point(point))

        angle_fn_1 = lambda a: a + randint(229, 286)
        angle_fn_2 = lambda a: (a + randint(1, 5)) % 180
        radius_fn = lambda r: r + 0.5

        rows = [
            (-35, 40, LinearScribble()),
            (0, 40, LinearScribble(angle_fn=angle_fn_1, radius_fn=radius_fn)),
            (35, 40, LinearScribble(angle_fn=angle_fn_2)),
            (-35, 0, BunchedScribble()),
            (0, 0, BunchedScribble(angle_fn=angle_fn_1, radius_fn=radius_fn)),
            (35, 0, BunchedScribble(angle_fn=angle_fn_2)),
            (-35, -40, CurvyScribble()),
            (0, -40, CurvyScribble(angle_fn=angle_fn_1, radius_fn=radius_fn)),
            (35, -40, CurvyScribble(angle_fn=angle_fn_2))
        ]

        for x_offset, y_offset, scribbler in rows:
            points = scribbler.get_points(5, 250)
            top_left = PointTransformer().translate(x_offset, y_offset)
            draw(top_left.transform(points))
            # Rotate color points for variety
            color = [int(pt) for pt in turtle.pencolor()]
            color.append(color.pop(0))
            turtle.pencolor(color)

        if not quiet:
            filename = 'samples-' + get_timestamp() + '.eps'
            pathname = folder if folder else '.'
            tf.export(join(pathname, filename))


def main():
    parser = ArgumentParser(
        prog=script_name,
        description='Generate samples of the various Scribble classes',
    )
    parser.add_argument('-w', '--width', type=int, default=1000,
                        help='width of image in pixels')
    parser.add_argument('-H', '--height', type=int, default=1000,
                        help='height of image in pixels')
    parser.add_argument('-s', '--scale', type=int, default=8,
                        help='scaling factor')
    parser.add_argument('-c', '--base', type=int, nargs=3, default=[0, 0, 0],
                        help='base color of scribbles in RGB format')
    parser.add_argument('-g', '--bg', type=int, nargs=3, default=[255, 255, 255],
                        help='background color in RGB format')
    parser.add_argument('-f', '--folder', help='folder to write image to',
                        default='.')
    parser.add_argument('-q', '--quiet', help='do not save image to disk',
                        action='store_true')
    args = parser.parse_args()

    draw_samples(args.width, args.height, args.scale, args.base, args.bg,
                 script_name, args.quiet, args.folder)

if __name__ == "__main__":
    main()