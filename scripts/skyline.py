#!/usr/bin/env python3

"""
Generate an image of a skyline with reflection.

Recipe: Generate points for a squashed and stretched Scribble. From each point,
draw a short Scribble terminating in a vertical stem.

Mirror and stretch these points/Scribbles/stems vertically and darken them.
"""

from argparse import ArgumentParser
from random import randint
from context import basename, join
from scribbles.core import LinearScribble
from scribbles.render import get_timestamp, get_nearby_color, darken_color, TurtleFactory
from scribbles.points import PointTransformer

script_name = basename(__file__)

def draw_skyline(width, height, scaling_factor, base_color, background_color,
                 canvas_name, quiet, folder):

    with TurtleFactory(width, height, bg_color=background_color,
                       canvas_name=canvas_name) as tf:

        turtle = tf.get_turtle()

        y_offset = 10
        max_height = 10
        scribbler = LinearScribble(origin=(0, y_offset), angle_fn=lambda a: a + randint(1, 5))
        origins = scribbler.get_points(10, 500)
        transformer = PointTransformer()\
            .scale(3.5, 1)\
            .limit(width, -width, y_offset + max_height, y_offset)
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
        
        for origin in origins:
            pensize = randint(1, 5)
            scribbler = LinearScribble(origin, angle_fn=lambda a: a + randint(1, 5))
            points = scribbler.get_points(10, 10)
            # add vertical stem originating from last point
            terminus = points[-1]
            points.append((terminus[0], terminus[1] + randint(3, 20)))
            draw(points, base_color, pensize)
            # take points, mirror them vertically, stretch them vertically,
            # shift them up, and ensure they don't cross over into original image
            mirror_transformer = PointTransformer()\
                .mirror_vertical()\
                .scale(1, 2.5)\
                .translate(0, 35)\
                .limit(width, -width, y_offset - 1, -height)            
            mirrored = mirror_transformer.transform(points)
            draw(mirrored, darken_color(base_color, decrement=60), pensize)
            base_color = get_nearby_color(base_color, range_=20)

        if not quiet:
            filename = 'skyline-' + get_timestamp() + '.eps'
            pathname = folder if folder else '.'
            tf.export(join(pathname, filename))


def main():
    parser = ArgumentParser(
        prog=script_name,
        description='Generate a skyline with reflection',
    )
    parser.add_argument('-w', '--width', type=int, default=1000,
                        help='width of image in pixels')
    parser.add_argument('-H', '--height', type=int, default=800,
                        help='height of image in pixels')
    parser.add_argument('-s', '--scale', type=int, default=7,
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

    draw_skyline(args.width, args.height, args.scale, args.base,
                 args.bg, script_name, args.quiet, args.folder)
    

if __name__ == "__main__":
    main()