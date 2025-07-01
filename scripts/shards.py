#!/usr/bin/env python3

"""
Create an image of a clump of colored shards.

Recipe: Generate and fill-in a Scribble. Randomly select X of that Scribble's
points as the origins for new Scribbles; repeat recursively for each new Scribble,
reducing X by one at each iteration, stopping at X=0.
"""

from argparse import ArgumentParser
from random import randint
from context import basename, join
from scribbles.core import LinearScribble, BunchedScribble
from scribbles.render import get_timestamp, darken_color, TurtleFactory
from scribbles.points import PointTransformer, distance

script_name = basename(__file__)

def draw_shards(width, height, radius, max_length, scaling_factor, depth,
                base_color, background_color, canvas_name, quiet, folder):

    with TurtleFactory(width, height, bg_color=background_color,
                       canvas_name=canvas_name) as tf:

        turtle = tf.get_turtle()

        def scale_point(p):
            return (x * scaling_factor for x in p)

        def draw(points, color, pensize):
            turtle.pensize(pensize)
            # make the border for each shard slightly darker
            turtle.pencolor(darken_color(color))
            turtle.penup()
            turtle.fillcolor(color)
            turtle.setposition(scale_point(points[0]))
            turtle.begin_fill()
            turtle.pendown()
            for point in points[1:]:
                turtle.setposition(scale_point(point))
            turtle.setposition(scale_point(points[0]))
            turtle.end_fill()
            turtle.pencolor(color)

        def get_new_color(color):
            r, g, b = color
            fn = lambda pt: min(max(pt + randint(-50, 50), 20), 255)
            return (fn(r), fn(g), fn(b))

        class_ = [BunchedScribble, LinearScribble]

        def draw_branch(origin, color, n_children):
            # randomly alternate between linear and bunched scribbles
            class_name = class_[randint(0, len(class_) - 1)]
            scribbler = class_name(origin=origin, angle_fn=lambda a: (a + randint(1, 286)))
            points = scribbler.get_points(radius, max_length)
            n_points = len(points)

            # move the scribble over so it is coincident with the point in the
            # scribble
            transformer = PointTransformer().translate(-distance(points[0], origin), 0)
            translated = transformer.transform(points)
            pensize = max(n_children, 3)
            draw(translated, color, pensize)

            for _ in range(n_children):
                origin_index = randint(1, n_points - 1) if n_points >= 2 else 0
                new_origin = translated[origin_index]
                draw_branch(new_origin, get_new_color(color), n_children - 1)

        origin = (5 * depth, -2 * depth)
        draw_branch(origin, base_color, depth)

        if not quiet:
            filename = 'shards-' + get_timestamp() + '.eps'
            pathname = folder if folder else '.'
            tf.export(join(pathname, filename))


def main():
    parser = ArgumentParser(
        prog=script_name,
        description='Generate an image of glass-like shards',
    )
    parser.add_argument('-w', '--width', type=int, default=1000,
                        help='width of image in pixels')
    parser.add_argument('-H', '--height', type=int, default=800,
                        help='height of image in pixels')
    parser.add_argument('-r', '--radius', type=int, default=20,
                        help='radius of scribbles in pixels')
    parser.add_argument('-L', '--length', type=int, default=200,
                        help='max. length of scribbles in pixels')
    parser.add_argument('-s', '--scale', type=int, default=10,
                        help='scaling factor')
    parser.add_argument('-d', '--depth', type=int, default=6,
                        help='maximum recursion depth')
    parser.add_argument('-c', '--base', type=int, nargs=3, default=[255, 0, 0],
                        help='base color of shards in RGB format')
    parser.add_argument('-g', '--bg', type=int, nargs=3, default=[0, 255, 255],
                        help='background color in RGB format')
    parser.add_argument('-f', '--folder', help='folder to write image to',
                        default='.')
    parser.add_argument('-q', '--quiet', help='do not save image to disk',
                        action='store_true')
    args = parser.parse_args()

    draw_shards(args.width, args.height, args.radius, args.length, args.scale,
                args.depth, args.base, args.bg, script_name, args.quiet,
                args.folder)


if __name__ == "__main__":
    main()