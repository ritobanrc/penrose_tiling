#!/usr/bin/python3
"""
Draws a penrose tiling. See http://www.ams.org/publicoutreach/feature-column/fcarc-penrose
"""
import argparse
import cairo
import gi
from collections import namedtuple
import numpy as np
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

small_triangles = []
large_triangles = []

PHI = (1 + np.sqrt(5))/2

line_width = 0.03


def draw(ctx: cairo.Context, width, height):
    ctx.translate(width/2, height/2)
    scale = np.min([width/2, height/2])
    ctx.scale(scale, scale)
    ctx.rotate(-np.pi/10)
    ctx.set_line_width(line_width)
    ctx.set_line_join(cairo.LineJoin.ROUND)


    ctx.set_source_rgb(*background)
    ctx.paint()

    draw_triangles(ctx, large_triangles, color1, (0.8, 0.8, 0.8))
    draw_triangles(ctx, small_triangles, color2, (0.8, 0.8, 0.8))


def draw_triangles(ctx: cairo.Context, arr, fill_color, stroke_color):
    for triangle in arr:
        ctx.set_source_rgb(*fill_color)
        ctx.line_to(triangle[0][0], triangle[0][1])
        ctx.line_to(triangle[1][0], triangle[1][1])
        ctx.line_to(triangle[2][0], triangle[2][1])
        ctx.fill_preserve()
        ctx.set_source_rgb(*stroke_color)
        ctx.stroke()


def initialize(radius, output):
    if tiling == 'p2':
        for i in range(10):
            if i % 2 == 0:
                output.append(np.array([[radius * np.cos(i*np.pi/5), radius * np.sin(i*np.pi/5)],
                                        [radius * np.cos((i+1)*np.pi/5), radius * np.sin((i+1)*np.pi/5)],
                                        [0, 0]]))
            else:
                output.append(np.array([[radius * np.cos((i+1)*np.pi/5), radius * np.sin((i+1)*np.pi/5)],
                                        [radius * np.cos(i*np.pi/5), radius * np.sin(i*np.pi/5)],
                                        [0, 0]]))
    elif tiling == 'p3':
        for i in range(10):
            if i% 2 == 0:
                output.append(np.array([[radius * np.cos(i*np.pi/5), radius * np.sin(i*np.pi/5)],
                                        [0, 0],
                                        [radius * np.cos((i+1)*np.pi/5), radius * np.sin((i+1)*np.pi/5)]]))
            else:
                output.append(np.array([[radius * np.cos((i+1)*np.pi/5), radius * np.sin((i+1)*np.pi/5)],
                                        [0, 0],
                                        [radius * np.cos(i*np.pi/5), radius * np.sin(i*np.pi/5)]]))


def deflate_p2():
    global large_triangles, small_triangles
    new_large_triangles = []
    new_small_triangles = []

    for triangle in large_triangles:
        # D = np.interp((PHI - 1)/PHI, triangle[0], triangle[1])
        # E = np.interp(PHI - 1, triangle[0], triangle[2])
        D = triangle[2] * (1 - (PHI - 1)/PHI) + triangle[1] * (PHI - 1)/PHI
        E = triangle[2] * (1 - (PHI - 1)) + triangle[0] * (PHI - 1)


        new_large_triangles.append(np.vstack((E, D, triangle[1])))
        new_large_triangles.append(np.vstack((E, triangle[0], triangle[1])))
        new_small_triangles.append(np.vstack((E, D, triangle[2])))

    for triangle in small_triangles:
        D = triangle[2] * (1 - 1/PHI) + triangle[0] * (1/PHI)

        new_large_triangles.append(np.vstack((triangle[1], D, triangle[2])))
        new_small_triangles.append(np.vstack((triangle[1], D, triangle[0])))

    large_triangles = new_large_triangles
    small_triangles = new_small_triangles

def deflate_p3():
    global large_triangles, small_triangles
    new_large_triangles = []
    new_small_triangles = []

    for triangle in small_triangles:
        D = triangle[0] * (1 - (PHI - 1)/PHI) + triangle[1] * (PHI - 1)/PHI

        new_large_triangles.append(np.vstack((triangle[2], D, triangle[1])))
        new_small_triangles.append(np.vstack((D, triangle[2], triangle[0])))

    for triangle in large_triangles:
        D = triangle[1] * (1/PHI) + triangle[0] * (1 - 1/PHI)
        E = triangle[2] * (PHI/(PHI + 1)) + triangle[0] * (1/(PHI + 1))

        new_large_triangles.append(np.vstack((E, D, triangle[0])))
        new_large_triangles.append(np.vstack((triangle[2], E, triangle[1])))
        new_small_triangles.append(np.vstack((D, E, triangle[1])))


    large_triangles = new_large_triangles
    small_triangles = new_small_triangles



def deflate():
    if tiling == 'p2':
        deflate_p2()
    elif tiling == 'p3':
        deflate_p3()
    global line_width
    line_width *= 0.65
    # print(new_large_triangles, new_small_triangles)


def on_mouse_pressed(da, event, *data):
    deflate()
    da.queue_draw()

def on_draw(da: Gtk.DrawingArea, ctx: cairo.Context):
    alloc = da.get_allocation()
    width = alloc.width
    height = alloc.height

    draw(ctx, width, height)

def hex_to_rgb(hex_code):
    h = hex_code.lstrip('#')
    return tuple(int(h[i:i+2], 16)/255 for i in (0, 2, 4))

def main():
    """
    The main function
    """
    parser = argparse.ArgumentParser(description='Creates and displays a penrose tiling.')

    output_format = parser.add_mutually_exclusive_group()
    output_format.add_argument('--gtk',
                               action='store_true',
                               help='Display the result in an interactive Gtk drawing area. ',
                               )
    output_format.add_argument('--svg',
                               help='Output to an svg file specified by this option.',
                               )
    tiling_group = parser.add_mutually_exclusive_group()
    tiling_group.add_argument('--p2', dest='tiling', action='store_const', const='p2')
    tiling_group.add_argument('--p3', dest='tiling', action='store_const', const='p3')

    parser.add_argument('--width', default=800, type=int, help='The width of the drawing area.')
    parser.add_argument('--height', default=800, type=int, help='The height of the drawing area.')

    parser.add_argument('-i', '--iters', default=5, type=int, help='The number of times to deflate. ')

    parser.add_argument('--color1', default='#7B9F35', help='The color of the larger prototiles.')
    parser.add_argument('--color2', default='#226666', help='The color of the smaller prototiles.')

    parser.add_argument('-r', '--radius', default=1, type=float, help='The radius of the tiling. A radius of 1 will fit exactly in a square canvas, while a radius greater than sqrt(2) will completely cover a square canvas.')

    parser.add_argument('-b', '--background', default='#000000', help='The background color.')


    args = parser.parse_args('--gtk --p3 -r 1 --color1 #224466 --color2 #7B9F35'.split())

    global color1, color2, background
    color1 = hex_to_rgb(args.color1)
    color2 = hex_to_rgb(args.color2)
    background = hex_to_rgb(args.background)

    global tiling
    tiling = args.tiling


    if args.gtk:
        win = Gtk.Window()
        win.connect('destroy', Gtk.main_quit)
        win.set_default_size(args.width, args.height)

        drawingarea = Gtk.DrawingArea()
        win.add(drawingarea)
        drawingarea.connect('draw', on_draw)

        drawingarea.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        drawingarea.connect('button-press-event', on_mouse_pressed)

        if args.tiling == 'p2':
            initialize(args.radius, large_triangles)
        elif args.tiling == 'p3':
            initialize(args.radius, small_triangles)

        drawingarea.queue_draw()

        win.show_all()
        Gtk.main()
    elif args.svg:
        with cairo.SVGSurface(args.svg, args.width, args.height) as surface:
            ctx = cairo.Context(surface)

            if args.tiling == 'p2':
                initialize(args.radius, large_triangles)
            elif args.tiling == 'p3':
                initialize(args.radius, small_triangles)
            for _ in range(args.iters):
                deflate()
            draw(ctx, args.width, args.height)



if __name__ == '__main__':
    main()
