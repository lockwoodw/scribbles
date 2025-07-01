#!/usr/bin/env python3

"""
Generate an image of a swarm.

Recipe: Draw a Scribble with a circular splat at its head. Randomly select X
points along this Scribble as the origins for X new Scribbles; draw them with
smaller splats. Repeat, reducing X by one at each iteration.
"""

from argparse import ArgumentParser
from random import randint
from context import basename, join
from scribbles.core import CurvyScribble
from scribbles.render import get_timestamp, darken_color, TurtleFactory
from scribbles.points import PointTransformer, distance

script_name = basename(__file__)

def draw_swarm(width, height, depth, scaling_factor, base_color,
               background_color, canvas_name, quiet, folder):

    with TurtleFactory(width, height, bg_color=background_color,
                       canvas_name=canvas_name) as tf:

        turtle = tf.get_turtle()
        angle_offset = randint(50, 286)
        color_pt_decrement = randint(1, 10)
        min_bg_color = min(background_color)
        background_color_limit = [min_bg_color, min_bg_color, min_bg_color]

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
                new_color = darken_color(turtle.pencolor(), min_bg_color, color_pt_decrement)
                if new_color == background_color_limit:
                    break
                turtle.pencolor(new_color)
            # reset
            turtle.pencolor(color)

        def get_new_color(color):
            r, g, b = color
            fn = lambda pt: min(max(pt + randint(-40, 40), 50), 255)
            return (fn(r), fn(g), fn(b))

        def draw_dot(point, size):
            turtle.penup()
            turtle.setposition(scale_point(point))
            turtle.dot(size)

        def get_points(origin):
            scribbler = CurvyScribble(origin=origin, angle_fn=lambda a: a + angle_offset)
            points = scribbler.get_points(15, 150)
            transformer = PointTransformer().translate(-distance(points[0], origin), 0)
            return transformer.transform(points)

        depth = max(min(depth, 7), 1)
        origin = [10 * depth, 0]
        color = base_color
        queue = [ ( depth, get_points(origin) ) ]

        while len(queue) > 0:
            n_children, points = queue.pop(0)
            n_points = len(points)
            pensize = max(n_children, 1)
            draw(points, color, pensize)
            draw_dot(points[0], pensize * scaling_factor)
            color = get_new_color(color)

            for _ in range(n_children):
                origin_index = randint(1, n_points - 1) if n_points >= 2 else 0
                new_origin = points[origin_index]
                queue.append((
                    n_children - 1, get_points(new_origin)
                ))

        if not quiet:
            filename = 'swarm-' + get_timestamp() + '.eps'
            pathname = folder if folder else '.'
            tf.export(join(pathname, filename))


def main():
    parser = ArgumentParser(
        prog=script_name,
        description='Generate an image of a swarm',
    )
    parser.add_argument('-w', '--width', type=int, default=1100,
                        help='width of image in pixels')
    parser.add_argument('-H', '--height', type=int, default=1100,
                        help='height of image in pixels')
    parser.add_argument('-d', '--depth', type=int, default=4,
                        help='max. recursion depth')
    parser.add_argument('-s', '--scale', type=int, default=10,
                        help='scaling factor')
    parser.add_argument('-c', '--base', type=int, nargs=3, default=[128, 192, 255],
                        help='base color of spiral in RGB format')
    parser.add_argument('-g', '--bg', type=int, nargs=3, default=[0, 0, 0],
                        help='background color in RGB format')
    parser.add_argument('-f', '--folder', help='folder to write image to',
                        default='.')
    parser.add_argument('-q', '--quiet', help='do not save image to disk',
                        action='store_true')
    args = parser.parse_args()

    draw_swarm(args.width, args.height, args.depth, args.scale, args.base,
               args.bg, script_name, args.quiet, args.folder)


if __name__ == "__main__":
    main()