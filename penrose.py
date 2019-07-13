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


def draw(drawing_area: Gtk.DrawingArea, ctx: cairo.Context):
    alloc = drawing_area.get_allocation()
    width = alloc.width
    height = alloc.height

    ctx.translate(width/2, height/2)
    ctx.scale(width/2, height/2)
    ctx.rotate(-np.pi/10)
    ctx.set_line_width(line_width)
    # ctx.set_line_cap(cairo.LineCap.SQUARE)
    ctx.set_line_join(cairo.LineJoin.ROUND)


    ctx.set_source_rgb(0, 0, 0)
    ctx.paint()

    draw_triangles(ctx, large_triangles, (0, 0.3, 0.1), (0.8, 0.8, 0.8))
    draw_triangles(ctx, small_triangles, (0, 0.1, 0.3), (0.8, 0.8, 0.8))


def draw_triangles(ctx: cairo.Context, arr, fill_color, stroke_color):
    for triangle in arr:
        ctx.set_source_rgb(*fill_color)
        ctx.line_to(triangle[0][0], triangle[0][1])
        ctx.line_to(triangle[1][0], triangle[1][1])
        ctx.line_to(triangle[2][0], triangle[2][1])
        ctx.fill_preserve()
        ctx.set_source_rgb(*stroke_color)
        ctx.stroke()


def initialize(radius = PHI):
    for i in range(10):
        if i % 2 == 0:
            large_triangles.append(np.array([[radius * np.cos(i*np.pi/5), radius * np.sin(i*np.pi/5)],
                                             [radius * np.cos((i+1)*np.pi/5), radius * np.sin((i+1)*np.pi/5)],
                                             [0, 0]]))
        else:
            large_triangles.append(np.array([[radius * np.cos((i+1)*np.pi/5), radius * np.sin((i+1)*np.pi/5)],
                                             [radius * np.cos(i*np.pi/5), radius * np.sin(i*np.pi/5)],
                                             [0, 0]]))


def subdivide():
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

    # print(new_large_triangles, new_small_triangles)


def on_mouse_pressed(da, event, *data):
    global line_width
    subdivide()
    line_width *= 0.5
    da.queue_draw()


def main():
    """
    The main function
    """
    parser = argparse.ArgumentParser(description='Creates and displays a penrose tiling.')

    output_format = parser.add_mutually_exclusive_group()
    output_format.add_argument('--gtk',
                               action='store_true',
                               help='Display the result in an interactive Gtk drawing area.',
                               default=True
                               )

    args = parser.parse_args()
    if args.gtk:
        win = Gtk.Window()
        win.connect('destroy', Gtk.main_quit)
        win.set_default_size(800, 800)

        drawingarea = Gtk.DrawingArea()
        win.add(drawingarea)
        drawingarea.connect('draw', draw)

        drawingarea.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        drawingarea.connect('button-press-event', on_mouse_pressed)

        initialize()

        drawingarea.queue_draw()

        win.show_all()
        Gtk.main()


if __name__ == '__main__':
    main()
