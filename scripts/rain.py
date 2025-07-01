#!/usr/bin/env python3

"""
Generate an image of rainfall on pavement.

Recipe: Generate points for a horizontially stretched Scribble. From each point,
draw a short Scribble terminating in a vertical stem.

Generate a mirror image of the first, but stretch it vertically, rotate it -30°,
and render it using a brighter color.
"""

from argparse import ArgumentParser
from random import randint
from context import basename, join
from scribbles.core import LinearScribble
from scribbles.render import get_timestamp, get_nearby_color, TurtleFactory
from scribbles.points import PointTransformer

script_name = basename(__file__)

def draw_rain(width, height, scaling_factor, base_color, background_color,
                 canvas_name, quiet, folder):

    with TurtleFactory(width, height, bg_color=background_color,
                       canvas_name=canvas_name) as tf:

        turtle = tf.get_turtle()

        scribbler = LinearScribble(origin=(10, 10), angle_fn=lambda a: a + randint(1, 5))
        origins = scribbler.get_points(10, 10000)
        transformer = PointTransformer().scale(3, 1)
        origins = transformer.transform(origins)

        def scale_point(p):
            return (x * scaling_factor for x in p)

        def draw(points, color, pensize):
            turtle.pensize(pensize)
            turtle.pencolor(color)
            turtle.penup()
            turtle.setposition(scale_point(points[0]))
            turtle.pendown()
            for point in points[1:]:
                turtle.setposition(scale_point(point))
            turtle.dot(pensize + 4)

        def mirror_color(color):
            r, g, b = color
            fn = lambda pt: min(int(pt + 50), 255)
            return (fn(r), fn(g), fn(b))

        for origin in origins:
            pensize = randint(1, 5)
            scribbler = LinearScribble(origin, angle_fn=lambda a: a + randint(1, 5))
            points = scribbler.get_points(10, 10)
            terminus = points[-1]
            points.append((terminus[0], terminus[1] + randint(3, 20)))
            draw(points, base_color, pensize)
            mirror_transformer = PointTransformer().mirror_vertical().scale(1, 2.5).rotate(-30)
            mirrored = mirror_transformer.transform(points)
            draw(mirrored, mirror_color(base_color), pensize)
            base_color = get_nearby_color(base_color, range_=20)

        if not quiet:
            filename = 'rain-' + get_timestamp() + '.eps'
            pathname = folder if folder else '.'
            tf.export(join(pathname, filename))


def main():
    parser = ArgumentParser(
        prog=script_name,
        description='Generate an image of rainfall on pavement',
    )
    parser.add_argument('-w', '--width', type=int, default=1100,
                        help='width of image in pixels')
    parser.add_argument('-H', '--height', type=int, default=1100,
                        help='height of image in pixels')
    parser.add_argument('-s', '--scale', type=int, default=10,
                        help='scaling factor')
    parser.add_argument('-c', '--base', type=int, nargs=3, default=[100, 149, 237],
                        help='base color of skyline in RGB format')
    parser.add_argument('-g', '--bg', type=int, nargs=3, default=[0, 0, 0],
                        help='background color in RGB format')
    parser.add_argument('-f', '--folder', help='folder to write image to',
                        default='.')
    parser.add_argument('-q', '--quiet', help='do not save image to disk',
                        action='store_true')
    args = parser.parse_args()

    draw_rain(args.width, args.height, args.scale, args.base,
              args.bg, script_name, args.quiet, args.folder)


if __name__ == "__main__":
    main()