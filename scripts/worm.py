#!/usr/bin/env python3

"""
Generate an image of a coiled worm.

Recipe: Generate the points for a long scribble. At each point, draw a
circular splat; increase the size of splats as they move away from the origin
and slowly vary their colour.
"""

from argparse import ArgumentParser
from context import basename, join
from scribbles.core import CurvyScribble
from scribbles.render import get_nearby_color, get_new_color, get_timestamp, TurtleFactory
from scribbles.points import distance

script_name = basename(__file__)


class ColorOption:
    """
    Defines color settings for default worm
    """
    def __init__(self, base_color, background_color, color_fn=get_nearby_color):
        self.base_color = base_color
        self.background_color = background_color
        self.color_fn = color_fn


def draw_worm(width, height, origin, radius, max_length, minimum_dot_size,
              scaling_factor, canvas_name, color_option, quiet, folder):

    with TurtleFactory(width, height, bg_color=color_option.background_color,
                       canvas_name=canvas_name) as tf:
        turtle = tf.get_turtle()
        turtle.pencolor(color_option.base_color)
        scribbler = CurvyScribble(origin)
        points = scribbler.get_points(radius, max_length)
        n_points = len(points)

        def scale_point(p):
            return (x * scaling_factor for x in p)

        dot_gradient = minimum_dot_size / n_points

        for i in range(n_points):
            point = points[i]
            # increase dot size as it moves further from origin and also as it
            # progresses through series of points
            d = distance(origin, point)
            dot_size = minimum_dot_size + ((i+d) * dot_gradient) if d > radius \
                else minimum_dot_size
            turtle.setposition(scale_point(point))
            turtle.dot(dot_size)
            turtle.pencolor(color_option.color_fn(turtle.pencolor()))

        if not quiet:
            filename = 'worm-' + get_timestamp() + '.eps'
            pathname = folder if folder else '.'
            tf.export(join(pathname, filename))


def main():
    parser = ArgumentParser(
        prog=script_name,
        description='Generate an image of a coiled worm',
    )
    parser.add_argument('-w', '--width', type=int, default=1000,
                        help='width of image in pixels')
    parser.add_argument('-H', '--height', type=int, default=800,
                        help='height of image in pixels')
    parser.add_argument('-x', '--origin_x', type=int, default=0,
                        help='x coordinate of the origin')
    parser.add_argument('-y', '--origin_y', type=int, default=0,
                        help='y coordinate of the origin')
    parser.add_argument('-r', '--radius', type=int, default=10,
                        help='radius of scribble in pixels')
    parser.add_argument('-L', '--length', type=int, default=10000,
                        help='max. length of scribble in pixels')
    parser.add_argument('-d', '--dotsize', type=int, default=100,
                        help='minimum dot diameter in pixels')
    parser.add_argument('-s', '--scale', type=int, default=10,
                        help='scaling factor')
    parser.add_argument('-c', '--base', type=int, nargs=3, default=[152, 255, 152],
                        help='base color of worm in RGB format')
    parser.add_argument('-g', '--bg', type=int, nargs=3, default=[75, 0, 0],
                        help='background color in RGB format')
    parser.add_argument('--rainbow', default=False, help='draw a rainbow worm',
                        action='store_true')
    parser.add_argument('-f', '--folder', help='folder to write image to',
                        default='.')
    parser.add_argument('-q', '--quiet', help='do not save image to disk',
                        action='store_true')
    args = parser.parse_args()

    color_option = ColorOption(base_color=(255, 0, 0), background_color=(0, 0, 0),
                               color_fn=get_new_color) if args.rainbow else ColorOption(args.base, args.bg)

    draw_worm(
        width=args.width,
        height=args.height,
        origin=(args.origin_x, args.origin_y),
        radius=args.radius,
        max_length=args.length,
        minimum_dot_size=args.dotsize,
        scaling_factor=args.scale,
        canvas_name=script_name,
        color_option=color_option,
        quiet=args.quiet,
        folder=args.folder
    )


if __name__ == "__main__":
    main()