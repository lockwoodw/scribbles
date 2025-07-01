#!/usr/bin/env python3

"""
Generate an image of insect heads.

Recipe: draw a short Scribble with a small radius; mirror it horizontally to
resemble the head of an insect, seen from the front. Add a blob in the middle
to suggest a thorax or tongue. Add blobs at the origins of the two Scribbles
to suggest eyes. Repeat 3X.
"""

from argparse import ArgumentParser
from random import randint
from context import basename, join
from scribbles.core import CurvyScribble
from scribbles.render import get_timestamp, darken_color, get_nearby_color, TurtleFactory
from scribbles.points import PointTransformer, max_distance

script_name = basename(__file__)

def draw_insects(width, height, scaling_factor, base_color, background_color,
                 canvas_name, quiet, folder):

    with TurtleFactory(width, height, bg_color=background_color,
                       canvas_name=canvas_name) as tf:

        turtle = tf.get_turtle()

        def scale_point(p):
            return (x * scaling_factor for x in p)

        def draw_outline(points, color, pensize):
            turtle.penup()
            turtle.pensize(pensize)
            turtle.pencolor(color)
            if not turtle.filling():
                turtle.setposition(scale_point(points[0]))
            turtle.pendown()
            for point in points[1:]:
                turtle.setposition(scale_point(point))
            turtle.setposition(scale_point(points[0]))

        def fill(points, color, pensize):
            turtle.penup()
            turtle.fillcolor(color)
            turtle.setposition(scale_point(points[0]))
            turtle.begin_fill()
            draw_outline(points, background_color, pensize)
            turtle.end_fill()

        def draw_dot(point, color, size):
            turtle.penup()
            turtle.setposition(scale_point(point))
            turtle.pencolor(color)
            turtle.dot(size)

        def get_colors(color):
            fill_color = darken_color(color, 60, 80)
            shade_color = darken_color(fill_color)
            return fill_color, shade_color

        def draw_background(x, y, points, color):
            turtle.fillcolor(color)
            turtle.setposition(x * scaling_factor, y * scaling_factor - (abs(y) * scaling_factor // 2))
            turtle.pencolor(color)
            turtle.begin_fill()
            turtle.pendown()
            turtle.circle(max_distance(points, (x, y)) * 1.5)
            turtle.end_fill()
            turtle.penup()

        pensize = 1
        eye_color = (255, 255, 0)
        iris_color = (255, 0, 0)
        throat_color = (118, 14, 14)

        def draw_head_at(points, x, y, color):
            fill_color, shade_color = get_colors(color)
            translater = PointTransformer().translate(x, y)
            translated = translater.transform(points)
            draw_background(x, y, points, throat_color)
            mirror = PointTransformer().mirror_horizontal().translate(x, y)
            mirrored = mirror.transform(points)
            fill(translated, fill_color, pensize)
            fill(mirrored, shade_color, pensize)
            draw_outline(translated, color, pensize)
            draw_outline(mirrored, color, pensize)
            eye_size = randint(30, 50)
            draw_dot(translated[0], eye_color, eye_size)
            x, y = translated[0]
            draw_dot((x + 1, y + randint(-1, 1)), iris_color, eye_size // 2.5)
            eye_size += randint(-10, 5)
            draw_dot(mirrored[0], eye_color, eye_size)
            x, y = mirrored[0]
            draw_dot((x - 1, y), iris_color, eye_size // 2.5)

        x_offset = 30
        y_offset = x_offset

        for modifier in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
            scribbler = CurvyScribble(radius_fn=lambda r: min(20, abs(r + randint(-3, 3))))
            points = scribbler.get_points(randint(5, 15), 200)
            x_modifer, y_modifier = modifier
            draw_head_at(points, x_offset*x_modifer, y_offset*y_modifier, base_color)
            base_color = get_nearby_color(base_color, 70, 100)

        if not quiet:
            filename = 'insects-' + get_timestamp() + '.eps'
            pathname = folder if folder else '.'
            tf.export(join(pathname, filename))


def main():
    parser = ArgumentParser(
        prog=script_name,
        description='Generate an image of insect heads',
    )
    parser.add_argument('-w', '--width', type=int, default=1400,
                        help='width of image in pixels')
    parser.add_argument('-H', '--height', type=int, default=1100,
                        help='height of image in pixels')
    parser.add_argument('-s', '--scale', type=int, default=8,
                        help='scaling factor')
    parser.add_argument('-c', '--base', type=int, nargs=3, default=[90, 255, 90],
                        help='base color of insects in RGB format')
    parser.add_argument('-g', '--bg', type=int, nargs=3, default=[10, 40, 10],
                        help='background color in RGB format')
    parser.add_argument('-f', '--folder', help='folder to write image to',
                        default='.')
    parser.add_argument('-q', '--quiet', help='do not save image to disk',
                        action='store_true')
    args = parser.parse_args()

    draw_insects(args.width, args.height, args.scale, args.base,
                 args.bg, script_name, args.quiet, args.folder)


if __name__ == "__main__":
    main()