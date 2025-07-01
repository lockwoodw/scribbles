#!/usr/bin/env python3

"""
Generate an image of a ring of grass.

Recipe: Generate the points for a Scribble but do not draw it. Taking each of
these points as origins, draw shorter Scribbles; progressively darken each line
segment in these Scribbles as they move away from their origins.
"""

from argparse import ArgumentParser
from context import basename, join
from scribbles.core import CurvyScribble
from scribbles.render import get_timestamp, get_nearby_color, darken_color, TurtleFactory
from scribbles.points import PointTransformer

script_name = basename(__file__)

def draw_grass(width, height, origin, radius, max_length, xscale, scaling_factor,
               pensize, base_color, background_color, canvas_name, quiet, folder):

    with TurtleFactory(width, height, bg_color=background_color,
                       canvas_name=canvas_name) as tf:

        turtle = tf.get_turtle()

        turtle.pensize(pensize)
        turtle.pencolor(base_color)
        min_bg_color = min(background_color)
        background_color_limit = [min_bg_color, min_bg_color, min_bg_color]

        scribbler = CurvyScribble(origin=origin)
        origins = scribbler.get_points(radius, max_length)
        transformer = PointTransformer()
        if xscale > 1:
            transformer.scale(xscale, 1)
        origins = transformer.rotate(-15).transform(origins)

        def scale_point(p):
            return (x * scaling_factor for x in p)
        
        def draw(points):
            saved_color = [int(x) for x in turtle.pencolor()]
            turtle.penup()
            turtle.setposition(scale_point(points[0]))
            turtle.dot(pensize + 3)
            turtle.pendown()
            color_pt_decrement = 4
            for point in points[1:]:
                turtle.setposition(scale_point(point))
                color = darken_color(turtle.pencolor(), min_bg_color, color_pt_decrement)
                if color == background_color_limit:
                    break
                turtle.pencolor(color)
            turtle.pencolor(saved_color)
        
        for origin in origins:
            scribbler = CurvyScribble(origin)
            points = scribbler.get_points(15, 50)
            turtle.pencolor(get_nearby_color(turtle.pencolor()))
            draw(points)        

        if not quiet:
            filename = 'grass-' + get_timestamp() + '.eps'
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
    parser.add_argument('-x', '--origin_x', type=int, default=0,
                        help='x coordinate of the origin')
    parser.add_argument('-y', '--origin_y', type=int, default=0,
                        help='y coordinate of the origin')    
    parser.add_argument('-r', '--radius', type=int, default=10,
                        help='radius of grass ring in pixels')
    parser.add_argument('-L', '--length', type=int, default=70,
                        help='max. length of grass ring in pixels')
    parser.add_argument('--xscale', type=int, default=4,
                        help='horizontal scale factor of grass ring')
    parser.add_argument('-s', '--scale', type=int, default=7,
                        help='scaling factor')
    parser.add_argument('-p', '--pensize', type=int, default=2,
                        help='pensize reduction factor')
    parser.add_argument('-c', '--base', type=int, nargs=3, default=[152, 255, 152],
                        help='base color of grass in RGB format')
    parser.add_argument('-g', '--bg', type=int, nargs=3, default=[40, 40, 40],
                        help='background color in RGB format')
    parser.add_argument('-f', '--folder', help='folder to write image to',
                        default='.')
    parser.add_argument('-q', '--quiet', help='do not save image to disk',
                        action='store_true')
    args = parser.parse_args()

    draw_grass(args.width, args.height, (args.origin_x, args.origin_y),
               args.radius, args.length, args.xscale, args.scale,args.pensize,
               args.base, args.bg, script_name, args.quiet, args.folder)


if __name__ == "__main__":
    main()