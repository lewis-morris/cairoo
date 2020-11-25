import cairocffi as cairo
from PIL import Image
import numpy as np
from shapely.geometry import Point

class Cairoo:

    def __init__(self, w, h, bg_colour=(255, 255, 255)):
        """

        :param w: width of output image in pixels (int)
        :param h: height of output image in pixels (int)
        :param bg_colour: colour of background in rgb(x,x,x) format, for transparent background use None
        """
        self._setup_cairo(w, h)
        if not bg_colour is None:
            self._draw_background(bg_colour)

    def _setup_cairo(self, w, h):
        self.w = w
        self.h = h
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        self.ctx = cairo.Context(self.surface)
        self.ctx.set_antialias(cairo.ANTIALIAS_GOOD)

        self.ctx.scale(w, h)

    def save_png(self,save_path):
        """
        save image as png to path
        :param save_path: path of file to be saved

        """
        if not save_path.endswith(".png"):
            print("path not valid png file")
            return

        buf = self.surface.get_data()
        # self.surface.get_
        Image.frombuffer("RGBA", (self.w, self.h), self.surface.get_data(), "raw", "BGRA", 0, 1).save(save_path)

    def get_pil(self):
        """
        get pil image from the drawn shapes
        :return: PIL Image
        """
        buf = self.surface.get_data()
        # self.surface.get_
        return Image.frombuffer("RGBA", (self.w, self.h), self.surface.get_data(), "raw", "BGRA", 0, 1)

    def get_numpy(self):
        """
        get numpy array from the drawn shapes
        :return: Numpy Array
        """
        buf = self.surface.get_data()
        # self.surface.get_
        return np.array(Image.frombuffer("RGBA", (self.w, self.h), self.surface.get_data(), "raw", "RGBA", 0, 1))

    def _draw_background(self, colour):

        self.draw_polygon(points=[(0, 0), (self.w, 0), (self.w, self.h), (0, self.h)], colour=colour)

    def _convert_colours(self, line_colour, colour):
        # convert colours to between 0-1
        if not line_colour is None:
            line_colour = [x / 255 for x in line_colour]

        if not colour is None:
            colour = [x / 255 for x in colour]

        return line_colour, colour

    def _draw_line(self, line_colour, line_width, line_trans):
        # draw outer line
        if not line_colour is None and not line_width is None and line_width > 0:
            self.ctx.set_source_rgba(*list(line_colour) + [line_trans])  # Solid color
            self.ctx.set_line_width(self._convert_to_xy(line_width))
            self.ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            self.ctx.set_line_join(cairo.LINE_JOIN_ROUND)

            self.ctx.stroke_preserve()

    def _draw_fill(self, colour, fill_trans):
        # fill shape
        if not colour is None:
            self.ctx.set_source_rgba(*list(colour) + [fill_trans])
            self.ctx.fill()

    def draw_circle(self, center, width, line_colour=None, colour=None, line_width=None, fill_trans=1, line_trans=1):
        """
        Used to draw circles to the image

        :param center: center point tuple/list in pixel points
        :param width: diameter of the circle in pixels (int)
        :param line_colour: line colour in rgb(x,x,x) format
        :param colour: colour of inner shape colour in rgb(x,x,x) format
        :param line_width: width of shape outer line (stroke) in pixels (INT)
        :param fill_trans:  alpha channel in range 0-1 for the shape fill
        :param line_trans: alpha channel in range 0-1 for the shape outer line (stroke)
        :return: self
        """
        # convert colours to between 0-1
        line_colour, colour = self._convert_colours(line_colour, colour)

        # get polygon from point
        points = Point(center).buffer(width / 2).exterior.coords

        # draw the points
        self._draw_points(points)

        # stoke if needed
        self._draw_line(line_colour, line_width, line_trans)
        self._draw_fill(colour, fill_trans)

        if colour is None and (line_width is None or line_width == 0):
            print("Warning - no shape drawn. Settings invalid")

        return self
    def draw_polygon(self, points, line_colour=None, colour=None, line_width=None, fill_trans=1, line_trans=1):
        """
        Used to draw polygons to the image

        :param points: array type list of x,y points of shape.
        :param line_colour: line colour in rgb(x,x,x) format
        :param colour: colour of inner shape colour in rgb(x,x,x) format
        :param line_width: width of shape outer line (stroke) in pixels (INT)
        :param fill_trans:  alpha channel in range 0-1 for the shape fill
        :param line_trans: alpha channel in range 0-1 for the shape outer line (stroke)
        :return: self
        """
        # convert colours to between 0-1
        line_colour, colour = self._convert_colours(line_colour, colour)

        # draw the points
        self._draw_points(points)

        # fill and or draw line
        self._draw_line(line_colour, line_width, line_trans)
        self._draw_fill(colour, fill_trans)

        if colour is None and (line_width is None or line_width == 0):
            print("Warning - no shape drawn. Settings invalid")
        return self

    def _draw_points(self, points):

        self.ctx.move_to(*self._convert_to_xy(*points[0]))
        for pn in points[1:]:
            self.ctx.line_to(*self._convert_to_xy(*pn))  # Line to (x,y)

        self.ctx.close_path()

    def _convert_to_xy(self, x, y=None):
        if y is None:
            return x / self.w
        else:
            return (x / self.w, y / self.h)
