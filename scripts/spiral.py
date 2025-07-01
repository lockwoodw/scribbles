#!/usr/bin/env python3
"""
Generate an image of a spiral.

Recipe: Generate an asymmetric Scribble and stretch it slightly horizontally.
Transform it by rotating it and moving it to the left. Redraw it. Repeat.
"""

from argparse import ArgumentParser
from random import randint
from context import basename, join
from scribbles.core import CurvyScribble
from scribbles.render import get_timestamp, get_color_point, TurtleFactory
from scribbles.points import PointTransformer

script_name = basename(__file__)

def draw_nautilus(width, height, origin, radius, length, angle, x_offset,
                  scaling_factor, base_color, background_color,
                  canvas_name, quiet, folder):

    with TurtleFactory(width, height, bg_color=background_color,
                       canvas_name=canvas_name) as tf:

        turtle = tf.get_turtle()

        scribbler = CurvyScribble(origin=origin,
            angle_fn=lambda a: ((a + randint(1, 5)) * randint(1, 2)) % 360)
        points = scribbler.get_points(radius, length)
        transformer = PointTransformer().scale(3, 1)
        points = transformer.transform(points)

        def scale_point(p):
            return (x * scaling_factor for x in p)

        turtle.pensize(1)
        turtle.pencolor(base_color)

        def draw(points):
            turtle.penup()
            turtle.setposition(scale_point(points[0]))
            turtle.pendown()
            for point in points[1:]:
                turtle.setposition(scale_point(point))

        draw(points)

        def get_new_color(color):
            r, g, b, = color
            fn = lambda pt: get_color_point(pt, 90, 255, 50)
            return [fn(r), fn(g), fn(b)]

        angle = abs(angle) % 360
        if angle < 1:
            angle = 360
        revolutions = (360 // angle) * 2
        x_offset = max(1, x_offset)
        for i in range(0, revolutions):
            transformer = PointTransformer().translate(-x_offset*i, 0).rotate(i*angle)
            new_points = transformer.transform(points)
            turtle.pencolor(get_new_color(turtle.pencolor()))
            draw(new_points)

        if not quiet:
            filename = 'spiral-' + get_timestamp() + '.eps'
            pathname = folder if folder else '.'
            tf.export(join(pathname, filename))


def main():
    parser = ArgumentParser(
        prog=script_name,
        description='Generate an image of a spiral',
    )
    parser.add_argument('-w', '--width', type=int, default=1100,
                        help='width of image in pixels')
    parser.add_argument('-H', '--height', type=int, default=1100,
                        help='height of image in pixels')
    parser.add_argument('-x', '--origin_x', type=int, default=30,
                        help='x coordinate of the origin')
    parser.add_argument('-y', '--origin_y', type=int, default=-30,
                        help='y coordinate of the origin')
    parser.add_argument('-r', '--radius', type=int, default=10,
                        help='radius of scribble in pixels')
    parser.add_argument('-L', '--length', type=int, default=2000,
                        help='max. length of scribble in pixels')
    parser.add_argument('-a', '--angle', type=int, default=15,
                        help='angle of rotation')
    parser.add_argument('-o', '--x_offset', type=int, default=2,
                        help='x offset per rotation')
    parser.add_argument('-s', '--scale', type=int, default=7,
                        help='scaling factor')
    parser.add_argument('-c', '--base', type=int, nargs=3, default=[255, 0, 0],
                        help='base color of spiral in RGB format')
    parser.add_argument('-g', '--bg', type=int, nargs=3, default=[70, 70, 70],
                        help='background color in RGB format')
    parser.add_argument('-f', '--folder', help='folder to write image to',
                        default='.')
    parser.add_argument('-q', '--quiet', help='do not save image to disk',
                        action='store_true')
    args = parser.parse_args()

    draw_nautilus(args.width, args.height, (args.origin_x, args.origin_y),
                  args.radius, args.length, args.angle, args.x_offset,
                  args.scale, args.base, args.bg, script_name, args.quiet,
                  args.folder)


if __name__ == "__main__":
    main()