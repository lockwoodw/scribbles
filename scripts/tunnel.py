#!/usr/bin/env python3

"""
Generate an image of a tunnel, lighter at the far end.

Recipe: Draw a Scribble with a large radius and length. Transform this Scribble
repeatedly, at each iteration rotating it 15°, translating it one pixel to the
left, increasing its size and thickness, and darkening its color.
"""

from argparse import ArgumentParser
from random import randint
from context import basename, join
from scribbles.core import CurvyScribble
from scribbles.render import get_timestamp, TurtleFactory
from scribbles.points import PointTransformer

script_name = basename(__file__)

def draw_tunnel(width, height, radius, max_length, scaling_factor, pen_factor,
                base_color, background_color, canvas_name, quiet, folder):

    with TurtleFactory(width, height, bg_color=background_color,
                       canvas_name=canvas_name) as tf:

        turtle = tf.get_turtle()
        pensize = 1

        def scale_point(p):
            return (x * scaling_factor for x in p)

        def draw(points, color):
            turtle.pensize(pensize)
            turtle.penup()
            start = list(scale_point(points[0]))
            turtle.setposition(start)
            turtle.pencolor(color)
            turtle.pendown()
            for point in points[1:]:
                turtle.setposition(scale_point(point))
            turtle.setposition(start)

        def get_new_color(color):
            r, g, b = color
            fn = lambda pt: int(min(max(pt + randint(-30, 10), 50), 255))
            return (fn(r), fn(g), fn(b))

        scribbler = CurvyScribble(angle_fn=lambda a: a + randint(1, 30))
        points = scribbler.get_points(radius, max_length)
        draw(points, base_color)

        scale = 1
        angle = 15
        iterations = 360 // 15
        for i in range(1, iterations):
            x = i + 1
            transformer = PointTransformer().translate(-x, 0).rotate(-i * angle).scale(scale, scale)
            new_points = transformer.transform(points)
            draw(new_points, get_new_color(turtle.pencolor()))
            scale = scale + i/randint(5, 10)
            pensize += i / iterations / pen_factor

        if not quiet:
            filename = 'tunnel-' + get_timestamp() + '.eps'
            pathname = folder if folder else '.'
            tf.export(join(pathname, filename))


def main():
    parser = ArgumentParser(
        prog=script_name,
        description='Generate an image of a wireframe tunnel',
    )
    parser.add_argument('-w', '--width', type=int, default=1000,
                        help='width of image in pixels')
    parser.add_argument('-H', '--height', type=int, default=800,
                        help='height of image in pixels')
    parser.add_argument('-r', '--radius', type=int, default=30,
                        help='radius of scribbles in pixels')
    parser.add_argument('-L', '--length', type=int, default=500,
                        help='max. length of scribbles in pixels')
    parser.add_argument('-s', '--scale', type=int, default=1,
                        help='scaling factor')
    parser.add_argument('-p', '--pensize', type=int, default=1,
                        help='pensize reduction factor')
    parser.add_argument('-c', '--base', type=int, nargs=3, default=[255, 100, 0],
                        help='base color of shards in RGB format')
    parser.add_argument('-g', '--bg', type=int, nargs=3, default=[0, 0, 0],
                        help='background color in RGB format')
    parser.add_argument('-f', '--folder', help='folder to write image to',
                        default='.')
    parser.add_argument('-q', '--quiet', help='do not save image to disk',
                        action='store_true')
    args = parser.parse_args()

    draw_tunnel(args.width, args.height, args.radius, args.length, args.scale,
                args.pensize, args.base, args.bg, script_name, args.quiet,
                args.folder)


if __name__ == "__main__":
    main()