#!/usr/bin/env python3

"""
Generate a stylized image of a brain.

Recipe: Generate a short linear Scribble with a large radius. Randomly select
X points along this Scribble as the origins for X new Scribbles. For each of
these, randomly select X-1 points as origins for new Scribbles and repeat
recursively.

Place a circular splat at the starting point of each Scribble to add volume
to the drawing.

Progressively darken the color of Scribbles at each iteration.

Periodically force the Scribble color to yellow to suggest neurons firing.
"""

from argparse import ArgumentParser
from random import randint
from context import basename, join
from scribbles.core import LinearScribble
from scribbles.render import get_timestamp, darken_color, TurtleFactory
from scribbles.points import PointTransformer, distance

script_name = basename(__file__)

def draw_brain(width, height, depth, scaling_factor, base_color, background_color,
               canvas_name, quiet, folder):

    with TurtleFactory(width, height, bg_color=background_color,
                       canvas_name=canvas_name) as tf:

        turtle = tf.get_turtle()

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

        def get_new_color(color):
            r, g, b = color
            fn = lambda pt: min(max(pt + randint(-50, 50), 20), 255)
            return (fn(r), fn(g), fn(b))

        def draw_dot(point, size):
            turtle.penup()
            turtle.setposition(scale_point(point))
            turtle.dot(size)

        def draw_branch(origin, color, n_children):
            scribbler = LinearScribble(origin=origin, angle_fn=lambda a: (a + randint(1, 50)))
            points = scribbler.get_points(20 + n_children, max(10, 50 * n_children))
            n_points = len(points)

            # move the Scribble over to the left so its first point coincides
            # with the given origin
            transformer = PointTransformer().translate(-distance(points[0], origin), 0)
            translated = transformer.transform(points)
            pensize = max(n_children * 3, 1)

            draw(translated, color, pensize)
            draw_dot(translated[0], pensize * 10)

            for _ in range(n_children):
                origin_index = randint(1, n_points - 1) if n_points >= 2 else 0
                new_origin = translated[origin_index]
                new_color = get_new_color(color)
                if randint(1, 10) <= 8:
                    new_color = darken_color(new_color, decrement=40)
                elif randint(1, 20) == 5:
                    new_color = (255, 255, 0)
                draw_branch(new_origin, new_color, n_children - 1)

        depth = max(min(depth, 7), 1)
        origin = (depth * scaling_factor * 4, -depth * scaling_factor)
        draw_branch(origin, base_color, depth)

        if not quiet:
            filename = 'brain-' + get_timestamp() + '.eps'
            pathname = folder if folder else '.'
            tf.export(join(pathname, filename))


def main():
    parser = ArgumentParser(
        prog=script_name,
        description='Generate a stylized image of a brain',
    )
    parser.add_argument('-w', '--width', type=int, default=1000,
                        help='width of image in pixels')
    parser.add_argument('-H', '--height', type=int, default=800,
                        help='height of image in pixels')
    parser.add_argument('-d', '--depth', type=int, default=6,
                        help='max. recursion depth')
    parser.add_argument('-s', '--scale', type=int, default=4,
                        help='scaling factor')
    parser.add_argument('-c', '--base', type=int, nargs=3, default=[255, 0, 0],
                        help='base color of brain in RGB format')
    parser.add_argument('-g', '--bg', type=int, nargs=3, default=[190, 190, 190],
                        help='background color in RGB format')
    parser.add_argument('-f', '--folder', help='folder to write image to',
                        default='.')
    parser.add_argument('-q', '--quiet', help='do not save image to disk',
                        action='store_true')
    args = parser.parse_args()

    draw_brain(args.width, args.height, args.depth, args.scale, args.base,
               args.bg, script_name, args.quiet, args.folder)


if __name__ == "__main__":
    main()