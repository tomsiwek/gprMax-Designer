from copy import copy, deepcopy
from math import asin, acos, atan, degrees, sin, cos, radians, ceil, floor, pi
from PIL import Image, ImageDraw
from random import randrange
from tkinter import Tk, Canvas, Menu, messagebox, BooleanVar, Frame, Button
from tkinter import LEFT, TOP, X, FLAT, RAISED, SUNKEN, ARC, PIESLICE, CHORD, W, S

from abc import ABC, abstractmethod
from geometry import TGeometry as TG
from point import TPoint
from random import randrange
from settings import TWindow_Size, TModel_Size, TTicksSettings, TColours


class TShape(ABC):
    """
    An abstract base class for shapes (i.e. rectangles, cylinders, cylinder sectors,
    and polygons).

    :param width: shape outline width in pixels.
    :type width: integer
    :param colour: shape outline colour.
    :type colour: string
    :param fill: shape fill colour.
    :type fill: string
    :param material: shape material.
    :type material: string
    :param shape_type: shape type (ie. rectangle, cylinder etc.).
    :type shape_type: string
    """
    def __init__(self, width = None, colour = None, fill = "", material = "pec", \
                 shape_type = "None"):
        """
        Initialise object variables.
        """
        self.COLOURS = ("red", "blue", "yellow", "green", "orange", "purple", \
                        "indigo", "fuchsia", "white", "navy", "brown")
        self.width = width
        self.colour = colour
        self.type = shape_type
        self.material = material
        num_of_colours = len(self.COLOURS)
        random_index = randrange(0, num_of_colours)
        self.fill = self.COLOURS[random_index]
        # Adjust shape position on screen according to new model coordinates
        self.update_window_positions()
    
    @abstractmethod
    def draw(self):
        """
        Draw a shape.
        """
        pass
    
    @abstractmethod
    def update_window_positions(self):
        """
        Recalculate window positions of the shape from its model positions.
        """
        pass

    @abstractmethod
    def update_model_positions(self):
        """
        Recalculate model positions of the shape from its window positions.
        """
        pass
    
    @abstractmethod
    def visible(self, min_model, max_model):
        """
        Determine whether the shape lies within the visible model area.

        :param min_model: lower left visible model corner.
        :type min_model: TPoint
        :param max_model: upper right visible model corner.
        :type max_model: TPoint

        :rtype: boolean
        """
        pass
    
    @abstractmethod
    def area(self):
        """
        Calculate shape area.

        :rtype: float
        """
        pass
    
    @abstractmethod
    def draw_to_image(self, image, colour):
        """
        Draw the shape to a png image file.

        :param image: png image.
        :type image: PIL.Image
        :param colour: shape colour.
        :type colour: tuple
        """
        pass

class TRect(TShape):
    """
    Class represents a rectangle.
    
    :param point1: lower left rectangle point in pixels.
    :type point1: TPoint
    :param point2: upper right rectangle point in pixels.
    :type point2: TPoint
    :param point1_x: lower left rectangle point x coordinate in pixels.
    :type point1_x: integer
    :param point1_y: lower left rectangle point y coordinate in pixels.
    :type point1_y: integer
    :param point2_x: upper right rectangle point x coordinate in pixels.
    :type point2_x: integer
    :param point2_y: upper right rectangle point y coordinate in pixels.
    :type point2_y: integer
    :param colour: shape outline colour.
    :type colour: string
    :param fill: shape fill colour.
    :type fill: string.
    :param width: shape outline width in pixels.
    :type width: integer
    :param material: shape material.
    :type material: string
    :param point1_mod: lower left rectangle point in metres.
    :type point1_mod: TPoint
    :param point2_mod: upper right rectangle point in metres.
    :type point2_mod: TPoint
    """
    def __init__(self, point1 = None, point2 = None, point1_x = None, \
                 point1_y = None, point2_x = None, point2_y = None, \
                 colour = "black", fill = "", width = 1, material = "pec", \
                 point1_mod = None, point2_mod = None):
        """
        Initialise object variables and call the parent class constructor.
        """
        # Rectangle vertices
        if(point1_mod and point2_mod):
            self.point1_mod = TPoint(min(point1_mod.x, point2_mod.x), min(point1_mod.y, point2_mod.y))
            self.point2_mod = TPoint(max(point1_mod.x, point2_mod.x), max(point1_mod.y, point2_mod.y))
            self.point3_mod = TPoint(self.point1_mod.x, self.point2_mod.y)
            self.point4_mod = TPoint(self.point2_mod.x, self.point1_mod.y)
        else:
            if(point1 and point2):
                self.point1 = TPoint(min(point1.x, point2.x), max(point1.y, point2.y))
                self.point2 = TPoint(max(point1.x, point2.x), min(point1.y, point2.y))
            elif(point1_x and point1_y and point2_x and point2_y):
                self.point1 = TPoint()
                self.point2 = TPoint()
                self.point1.x = min(point1_x, point2_x)
                self.point1.y = max(point1_y, point2_y)
                self.point2.x = max(point1_x, point2_x)
                self.point2.y = min(point1_y, point2_y)
            self.point3 = TPoint(self.point1.x, self.point2.y)
            self.point4 = TPoint(self.point2.x, self.point1.y)
            # Coordinates in model system
            self.update_model_positions()
        super().__init__(colour = colour, width = width, shape_type = "Rectangle", \
                         material = material)

    def draw(self, canvas):
        """
        Draw the rectangle on a canvas.

        :param canvas: canvas on which to draw the rectangle.
        :type canvas: tkinter.Canvas
        """
        min_model = TPoint(TModel_Size.MIN_X, TModel_Size.MIN_Y)
        max_model = TPoint(TModel_Size.MAX_X, TModel_Size.MAX_Y)
        if(TColours.FILL):
            fill = self.fill
        else:
            fill = None
        canvas.create_rectangle(self.point1.x, self.point1.y, self.point2.x, \
                                self.point2.y, outline = self.colour, \
                                fill = fill, width = self.width)
        if(TG.point_visible(self.point1_mod, min_model, max_model)):
            canvas.create_oval(self.point1.x-3, self.point1.y-3, self.point1.x+3, \
                               self.point1.y+3, outline = self.colour, \
                               fill = self.colour, width = 1)
        if(TG.point_visible(self.point2_mod, min_model, max_model)):
            canvas.create_oval(self.point2.x-3, self.point2.y-3, self.point2.x+3, \
                               self.point2.y+3, outline = self.colour, \
                               fill = self.colour, width = 1)
        if(TG.point_visible(self.point3_mod, min_model, max_model)):
            canvas.create_oval(self.point3.x-3, self.point3.y-3, self.point3.x+3, \
                               self.point3.y+3, outline = self.colour, \
                               fill = self.colour, width = 1)
        if(TG.point_visible(self.point4_mod, min_model, max_model)):
            canvas.create_oval(self.point4.x-3, self.point4.y-3, self.point4.x+3, \
                               self.point4.y+3, outline = self.colour, \
                               fill = self.colour, width = 1)

    def update_window_positions(self):
        """
        Recalculate window positions of the rectangle from its model positions.
        """
        min_model = TPoint(TModel_Size.MIN_X, TModel_Size.MIN_Y)
        max_model = TPoint(TModel_Size.MAX_X, TModel_Size.MAX_Y)
        min_window = TPoint(TWindow_Size.BOX_MIN_X, TWindow_Size.BOX_MIN_Y)
        max_window = TPoint(TWindow_Size.BOX_MAX_X, TWindow_Size.BOX_MAX_Y)
        self.point1 = TG.model_to_window(self.point1_mod, min_model, max_model, \
                                         min_window, max_window)
        self.point2 = TG.model_to_window(self.point2_mod, min_model, max_model, \
                                         min_window, max_window)
        self.point3 = TG.model_to_window(self.point3_mod, min_model, max_model, \
                                         min_window, max_window)
        self.point4 = TG.model_to_window(self.point4_mod, min_model, max_model, \
                                         min_window, max_window)

    def update_model_positions(self):
        """
        Recalculate model positions of the rectangle from its window positions.
        """
        min_model = TPoint(TModel_Size.MIN_X, TModel_Size.MIN_Y)
        max_model = TPoint(TModel_Size.MAX_X, TModel_Size.MAX_Y)
        min_window = TPoint(TWindow_Size.BOX_MIN_X, TWindow_Size.BOX_MIN_Y)
        max_window = TPoint(TWindow_Size.BOX_MAX_X, TWindow_Size.BOX_MAX_Y)
        dx = TModel_Size.DX
        dy = TModel_Size.DX
        self.point1_mod = TG.window_to_model(self.point1, min_model, max_model, \
                                             min_window, max_window, dx, dy)
        self.point2_mod = TG.window_to_model(self.point2, min_model, max_model, \
                                             min_window, max_window, dx, dy)
        self.point3_mod = TG.window_to_model(self.point3, min_model, max_model, \
                                             min_window, max_window, dx, dy)
        self.point4_mod = TG.window_to_model(self.point4, min_model, max_model, \
                                             min_window, max_window, dx, dy)
    
    def visible(self, min_model, max_model):
        """
        Determine whether the rectangle lies within the visible model area.

        :param min_model: lower left visible model corner.
        :type min_model: TPoint
        :param max_model: upper right visible model corner.
        :type max_model: TPoint

        :rtype: boolean
        """
        point1 = deepcopy(self.point1_mod)
        point2 = deepcopy(self.point2_mod)
        point3 = TPoint(self.point1_mod.x, self.point2_mod.y)
        point4 = TPoint(self.point2_mod.x, self.point1_mod.y)
        p1_visible = TG.point_visible(point1, min_model, max_model)
        p2_visible = TG.point_visible(point2, min_model, max_model)
        p3_visible = TG.point_visible(point3, min_model, max_model)
        p4_visible = TG.point_visible(point4, min_model, max_model)
        if(p1_visible and p2_visible and p3_visible and p4_visible):
            return True
        elif(p1_visible or p2_visible or p3_visible or p4_visible):
            return True
        else:
            return False
    
    def area(self):
        """
        Calculate rectangle area.

        :rtype: float
        """
        len_x = abs(self.point2_mod.x - self.point1_mod.x)
        len_y = abs(self.point2_mod.y - self.point1_mod.y)
        return len_x*len_y

    def draw_to_image(self, image, colour):
        """
        Draw the rectangle to a png image file.

        :param image: png image.
        :type image: PIL.Image
        :param colour: shape colour.
        :type colour: tuple
        """
        draw = ImageDraw.Draw(image)
        point1_im_x = (self.point1_mod.x/TModel_Size.DOM_X)*image.width
        point1_im_y = (1-(self.point1_mod.y/TModel_Size.DOM_Y))*image.height
        point2_im_x = (self.point2_mod.x/TModel_Size.DOM_X)*image.width
        point2_im_y = (1-(self.point2_mod.y/TModel_Size.DOM_Y))*image.height
        draw.rectangle([point1_im_x, point1_im_y, point2_im_x, point2_im_y], \
                      fill = colour, outline = None)


class TCylin(TShape):
    """
    Class represents a cylinder.
    
    :param centre: cylinder centre in pixels.
    :type centre: TPoint
    :param radius: cylinder radius in pixels.
    :type radius: float
    :param centre_x: cylinder centre x coordinate in pixels.
    :type centre_x: integer
    :param centre_y: cylinder centre y coordinate in pixels.
    :type centre_y: integer
    :param colour: shape outline colour.
    :type colour: string
    :param fill: shape fill colour.
    :type fill: string
    :param width: shape outline width in pixels.
    :type width: integer
    :param material: shape material.
    :type material: string
    :param centre_mod: cylinder centre in metres.
    :type centre_mod: TPoint
    :param radius_mod: cylinder radius in metres.
    :type radius_mod: float
    """
    def __init__(self, centre = None, radius = None, centre_x = None, centre_y = None, \
                 colour = "black", fill = "", width = 1, material = "pec", \
                 centre_mod = None, radius_mod = None):
        """
        Initialise object variables and call the parent class constructor.
        """
        # Cylinder middle point
        if(centre_mod and radius_mod):
            self.centre_mod = copy(centre_mod)
            self.radius_mod = radius_mod
        else:
            self.centre = TPoint()
            if(centre):
                self.centre = copy(centre)
            elif(centre_x and centre_y):
                self.centre.x = centre_x
                self.centre.y = centre_y
            # Cylinder radius
            self.radius = radius
            # Coordinates in model's system
            self.update_model_positions()
        super().__init__(colour = colour, width = width, shape_type = "Cylinder", \
                         material = material)

    def draw(self, canvas):
        """
        Draw the cylinder on a canvas.

        :param canvas: canvas on which to draw the cylinder.
        :type canvas: tkinter.Canvas
        """
        min_model = TPoint(TModel_Size.MIN_X, TModel_Size.MIN_Y)
        max_model = TPoint(TModel_Size.MAX_X, TModel_Size.MAX_Y)
        if(TColours.FILL):
            fill = self.fill
        else:
            fill = None
        canvas.create_oval(self.centre.x - self.radius, self.centre.y - self.radius, \
                           self.centre.x + self.radius, self.centre.y + self.radius, \
                           outline = self.colour, fill = fill, width = self.width)
        if(TG.point_visible(self.centre_mod, min_model, max_model)):
            canvas.create_oval(self.centre.x-3, self.centre.y-3, self.centre.x+3, \
                               self.centre.y+3, outline = self.colour, \
                               fill = self.colour, width = 1)

    # def _draw_partly_visible(self, canvas):
    #     a, b, r = self.centre.x, self.centre.y, self.radius
    #     if((self.centre_mod.x - self.radius_mod) <= TModel_Size.MIN_X):
    #         border_x = TWindow_Size.BOX_MIN_X
    #     else:
    #         border_x = TWindow_Size.BOX_MAX_X
    #     if((self.centre_mod.y - self.radius_mod) <= TModel_Size.MIN_Y):
    #         border_y = TWindow_Size.BOX_MIN_Y
    #     else:
    #         border_y = TWindow_Size.BOX_MAX_Y
    #     delta_x = (round(r)**2 - (border_y - b)**2)
    #     delta_y = (round(r)**2 - (border_x - a)**2)
    #     if(delta_x >= 0):
    #         x1 = a - delta_x**(0.5)
    #         x2 = a + delta_x**(0.5)
    #     if(delta_y >= 0):
    #         y1 = b - delta_y**(0.5)
    #         y2 = b + delta_y**(0.5)
    #     intersection_type = "both"
    #     if(delta_x > 0 and delta_y <= 0):
    #         intersection_type = "x"
    #     elif(delta_x <= 0 and delta_y > 0):
    #         intersection_type = "y"
    #     if(intersection_type == "x"):
    #         chord_sq = (x1 - x2)**2
    #         start = degrees(asin(abs(border_y - b)/round(r)))
    #         extent = degrees(acos(1 - chord_sq/(2*round(r)**2)))
    #         if(border_y == TWindow_Size.BOX_MIN_Y):
    #             if(b <= TWindow_Size.BOX_MIN_Y):
    #                 start  = -start
    #                 extent = 360 - extent
    #         else:
    #             start = start + extent
    #             extent = 360 - extent
    #             if(b <= TWindow_Size.BOX_MAX_Y):
    #                 start  = -start
    #                 extent = 360 - extent
    #     elif(intersection_type == "y"):
    #         chord_sq = (y1 - y2)**2
    #         start = degrees(asin(abs(min(y1, y2) - b)/round(r)))
    #         extent = 360 - 2*start
    #         if(border_x == TWindow_Size.BOX_MIN_X):
    #             if(a <= TWindow_Size.BOX_MIN_X):
    #                 start  = -start
    #                 extent = 360 - extent
    #         else:
    #             start = start + extent
    #             extent = 360 - extent
    #             if(a <= TWindow_Size.BOX_MAX_X):
    #                 start  = -start
    #                 extent = 360 - extent
    #     elif(intersection_type == "both"):
    #         pass
    #     canvas.create_arc(a - r, b - r, a + r, b + r, 
    #                       start = start, extent = extent, \
    #                       outline = self.colour, fill = self.fill, \
    #                       width = self.width, style = CHORD)
    
    def area(self):
        """
        Calculate cylinder area.

        :rtype: float
        """
        return self.radius_mod**2*pi
    
    def update_window_positions(self):
        """
        Recalculate window positions of the cylinder from its model positions.
        """
        min_model = TPoint(TModel_Size.MIN_X, TModel_Size.MIN_Y)
        max_model = TPoint(TModel_Size.MAX_X, TModel_Size.MAX_Y)
        min_window = TPoint(TWindow_Size.BOX_MIN_X, TWindow_Size.BOX_MIN_Y)
        max_window = TPoint(TWindow_Size.BOX_MAX_X, TWindow_Size.BOX_MAX_Y)
        self.centre = TG.model_to_window(self.centre_mod, min_model, max_model, \
                                         min_window, max_window)
        self.radius = TG.dist_model_to_window(self.radius_mod, min_model, max_model, \
                                              min_window, max_window)

    def update_model_positions(self):
        """
        Recalculate model positions of the cylinder from its window positions.
        """
        min_model = TPoint(TModel_Size.MIN_X, TModel_Size.MIN_Y)
        max_model = TPoint(TModel_Size.MAX_X, TModel_Size.MAX_Y)
        min_window = TPoint(TWindow_Size.BOX_MIN_X, TWindow_Size.BOX_MIN_Y)
        max_window = TPoint(TWindow_Size.BOX_MAX_X, TWindow_Size.BOX_MAX_Y)
        dx = TModel_Size.DX
        dy = TModel_Size.DY
        self.centre_mod = TG.window_to_model(self.centre, min_model, max_model, \
                                             min_window, max_window, dx, dy)
        self.radius_mod = TG.dist_window_to_model(self.radius, min_model, max_model, \
                                                  min_window, max_window, dx, dy)

    def visible(self, min_model, max_model):
        """
        Determine whether the cylinder lies within the visible model area.

        :param min_model: lower left visible model corner.
        :type min_model: TPoint
        :param max_model: upper right visible model corner.
        :type max_model: TPoint

        :rtype: boolean
        """
        point1 = TPoint(self.centre_mod.x - self.radius_mod, \
                        self.centre_mod.y - self.radius_mod)
        point2 = TPoint(self.centre_mod.x + self.radius_mod, \
                        self.centre_mod.y + self.radius_mod)
        point3 = TPoint(self.centre_mod.x + self.radius_mod, \
                        self.centre_mod.y - self.radius_mod)
        point4 = TPoint(self.centre_mod.x - self.radius_mod, \
                        self.centre_mod.y + self.radius_mod)
        p1_visible = TG.point_visible(point1, min_model, max_model)
        p2_visible = TG.point_visible(point2, min_model, max_model)
        p3_visible = TG.point_visible(point3, min_model, max_model)
        p4_visible = TG.point_visible(point4, min_model, max_model)
        if(p1_visible and p2_visible and p3_visible and p4_visible):
            return True
        elif(p1_visible or p2_visible or p3_visible or p4_visible):
            return True
        else:
            return False
    
    def draw_to_image(self, image, colour):
        """
        Draw the cylinder to a png image file.

        :param image: png image.
        :type image: PIL.Image
        :param colour: shape colour.
        :type colour: tuple
        """
        draw = ImageDraw.Draw(image)
        centre_im_x = (self.centre_mod.x/TModel_Size.DOM_X)*image.width
        centre_im_y = (1-(self.centre_mod.y/TModel_Size.DOM_Y))*image.height
        radius_im = (1/TModel_Size.DX)*self.radius_mod
        draw.ellipse([centre_im_x - radius_im, centre_im_y - radius_im, \
                      centre_im_x + radius_im, centre_im_y + radius_im], \
                     fill = colour, outline = None)


class TCylinSector(TShape):
    """
    Class represents a cylinder sector.
    
    :param centre: cylinder centre in pixels.
    :type centre: TPoint
    :param radius: cylinder radius in pixels.
    :type radius: float
    :param centre_x: cylinder centre x coordinate in pixels.
    :type centre_x: integer
    :param centre_y: cylinder centre y coordinate in pixels.
    :type centre_y: integer
    :param colour: shape outline colour.
    :type colour: string
    :param fill: shape fill colour.
    :type fill: string
    :param width: shape outline width in pixels.
    :type width: integer
    :param boundary_pt1: sector first boundary point.
    :type boundary_pt1: TPoint
    :param boundary_pt2: sector first boundary point.
    :type boundary_pt2: TPoint
    :param start: angle between positive x direction and first sector radius.
    :type start: float
    :param extent: angle between first and second sector radius.
    :type extent: float
    :param material: shape material.
    :type material: string
    :param centre_mod: cylinder centre in metres.
    :type centre_mod: TPoint
    :param radius_mod: cylinder radius in metres.
    :type radius_mod: float
    """
    def __init__(self, centre = None, radius = None, centre_x = None, \
        centre_y = None, colour = "black", fill = "", width = 1, \
        boundary_pt1 = None, boundary_pt2 = None, start = None, extent = None, \
        material = "pec", centre_mod = None, radius_mod = None):
        """
        Initialise object variables and call the parent class constructor.
        """
        self.boundary_pt1 = TPoint()
        self.boundary_pt2 = TPoint()
        if(centre_mod and radius_mod and start != None and extent):
            self.centre_mod = copy(centre_mod)
            self.radius_mod = radius_mod
            self.start = start
            self.extent = extent
            self.update_window_positions()
        else:
            self.centre = TPoint()
            if(centre):
                self.centre = copy(centre)
            elif(centre_x and centre_y):
                self.centre.x = centre_x
                self.centre.y = centre_y
            if(radius is not None):
                # Cylinder radius
                self.radius = round(radius)
            if(boundary_pt1):
                self.boundary_pt1 = copy(boundary_pt1)
            if(boundary_pt2):
                self.boundary_pt2 = copy(boundary_pt2)
            elif(boundary_pt1 and start and extent):
                self.boundary_pt1.x = int(self.centre.x + cos(radians(start))*self.radius)
                self.boundary_pt1.y = int(self.centre.y - sin(radians(start))*self.radius)
            elif(not boundary_pt2 and start and extent):
                self.boundary_pt2.x = int(self.centre.x + cos(radians(start + extent))*self.radius)
                self.boundary_pt2.y = int(self.centre.y - sin(radians(start + extent))*self.radius)
            # Compute start and extent angles
            if(start != None):
                self.start = start
            elif(start == None and boundary_pt1 and boundary_pt2):
                if(self.boundary_pt1.x >= self.centre.x):
                    self.start = degrees(asin((self.centre.y-self.boundary_pt1.y)/self.radius))
                else:
                    self.start = (180 - degrees(asin((self.centre.y-self.boundary_pt1.y)/self.radius)))
                if(self.start < 0):
                    self.start += 360
                if(self.start > 360):
                    self.start -= 360
            if(extent is not None):
                self.extent = extent
            elif(extent == None and boundary_pt2 is not None):
                b1 = ((self.boundary_pt1.x-self.boundary_pt2.x)**2 + (self.boundary_pt1.y-self.boundary_pt2.y)**2)**(0.5)
                b2 = ((self.boundary_pt2.x-self.centre.x)**2 + (self.boundary_pt2.y-self.centre.y)**2)**(0.5)
                # Check whether boundry points and centre are colinear
                try:
                    self.extent = degrees(acos(-((b1**2 -b2**2-self.radius**2)/(2*b2*self.radius))))
                except ValueError:
                    self.extent = 180
                # Check whether second boundary point is located to the right of the centre -- first boundary point line
                if(((self.boundary_pt2.x-self.centre.x)*sin (radians(self.start)) + (self.boundary_pt2.y-self.centre.y)*cos(radians(self.start))) > 0):
                    self.extent = (360 - self.extent)
            if(self.extent > 360):
                self.extent -= 360
            self.start = TG.round_to_multiple(self.start, min(TModel_Size.DX, TModel_Size.DY))
            self.extent = TG.round_to_multiple(self.extent, min(TModel_Size.DX, TModel_Size.DY))
            self.boundary_pt2.x = int (self.centre.x + cos (radians (self.start + self.extent) )*self.radius )
            self.boundary_pt2.y = int (self.centre.y - sin (radians (self.start + self.extent) )*self.radius )
            # Coordinates in model system
            self.update_model_positions()
        super().__init__(colour = colour, width = width, shape_type = "CylinSector", \
                         material = material)

    def draw (self, canvas):
        """
        Draw the cylinder sector on a canvas.

        :param canvas: canvas on which to draw the cylinder sector.
        :type canvas: tkinter.Canvas
        """
        if(TColours.FILL):
            fill = self.fill
        else:
            fill = None
        canvas.create_arc(self.centre.x - self.radius, self.centre.y - self.radius, \
                          self.centre.x + self.radius, self.centre.y + self.radius, \
                          outline = self.colour, fill = fill, width = self.width, \
                          style = PIESLICE, start = self.start, extent = self.extent)
        canvas.create_oval(self.centre.x-3, self.centre.y-3, self.centre.x+3, \
                           self.centre.y+3, outline = self.colour, fill = self.colour, \
                           width = 1)
        canvas.create_oval(self.boundary_pt1.x-3, self.boundary_pt1.y-3, \
                           self.boundary_pt1.x+3, self.boundary_pt1.y+3, \
                           outline = self.colour, fill = self.colour, width = 1)
        canvas.create_oval(self.boundary_pt2.x-3, self.boundary_pt2.y-3, \
                           self.boundary_pt2.x+3, self.boundary_pt2.y+3, \
                           outline = self.colour, fill = self.colour, width = 1)

    def update_window_positions (self):
        """
        Recalculate window positions of the cylinder sector from its model positions.
        """
        min_model = TPoint(TModel_Size.MIN_X, TModel_Size.MIN_Y)
        max_model = TPoint(TModel_Size.MAX_X, TModel_Size.MAX_Y)
        min_window = TPoint(TWindow_Size.BOX_MIN_X, TWindow_Size.BOX_MIN_Y)
        max_window = TPoint(TWindow_Size.BOX_MAX_X, TWindow_Size.BOX_MAX_Y)
        self.centre = TG.model_to_window(self.centre_mod, min_model, max_model, \
                                         min_window, max_window)
        self.radius = TG.dist_model_to_window(self.radius_mod, min_model, max_model, \
                                              min_window, max_window) 
        self.boundary_pt1.x = TG.round_to_multiple(self.centre.x + cos(radians(self.start))*self.radius, 1)
        self.boundary_pt1.y = TG.round_to_multiple(self.centre.y - sin(radians(self.start))*self.radius, 1)
        self.boundary_pt2.x = TG.round_to_multiple(self.centre.x + cos(radians(self.start + self.extent))*self.radius, 1)
        self.boundary_pt2.y = TG.round_to_multiple(self.centre.y - sin(radians(self.start + self.extent))*self.radius, 1)

    def update_model_positions(self):
        """
        Recalculate model positions of the cylinder sector from its window positions.
        """
        min_model = TPoint(TModel_Size.MIN_X, TModel_Size.MIN_Y)
        max_model = TPoint(TModel_Size.MAX_X, TModel_Size.MAX_Y)
        min_window = TPoint(TWindow_Size.BOX_MIN_X, TWindow_Size.BOX_MIN_Y)
        max_window = TPoint(TWindow_Size.BOX_MAX_X, TWindow_Size.BOX_MAX_Y)
        dx = TModel_Size.DX
        dy = TModel_Size.DY
        self.centre_mod = TG.window_to_model(self.centre, min_model, max_model, \
                                             min_window, max_window, dx, dy)
        self.boundary_pt1_mod = TG.window_to_model(self.boundary_pt1, min_model, max_model, \
                                                   min_window, max_window, dx, dy)
        self.boundary_pt2_mod = TG.window_to_model(self.boundary_pt2, min_model, max_model, \
                                                   min_window, max_window, dx, dy)
        self.radius_mod = TG.dist_window_to_model(self.radius,  min_model, max_model, \
                                                  min_window, max_window, dx, dy)
    
    def visible(self, min_model, max_model):
        """
        Determine whether the cylinder sector lies within the visible model area.

        :param min_model: lower left visible model corner.
        :type min_model: TPoint
        :param max_model: upper right visible model corner.
        :type max_model: TPoint

        :rtype: boolean
        """
        min_x = min(self.centre_mod.x - self.radius_mod, self.boundary_pt1_mod.x, \
                    self.boundary_pt2_mod.x)
        min_y = min(self.centre_mod.y - self.radius_mod, self.boundary_pt1_mod.y, \
                    self.boundary_pt2_mod.y)
        max_x = max(self.centre_mod.x + self.radius_mod, self.boundary_pt1_mod.x, \
                    self.boundary_pt2_mod.x)
        max_y = max(self.centre_mod.y + self.radius_mod, self.boundary_pt1_mod.y, \
                    self.boundary_pt2_mod.y)
        min_pt = TPoint(min_x, min_y)
        max_pt = TPoint(max_x, max_y)
        if(min_pt.x >= min_model.x and min_pt.y >= min_model.y and \
           max_pt.x <= max_model.x and max_pt.y <= max_model.y):
            return "entirely"
        elif(min_pt.x < min_model.x or min_pt.y < min_model.y or \
             max_pt.x > max_model.x or min_pt.y > max_model.y):
            return "partly"
        else:
            return "invisible"

    def area(self):
        """
        Calculate cylinder sector area.

        :rtype: float
        """
        return (self.extent/360.0)*self.radius_mod**2*pi
    
    def draw_to_image(self, image, colour):
        """
        Draw the cylinder sector to a png image file.

        :param image: png image.
        :type image: PIL.Image
        :param colour: shape colour.
        :type colour: tuple
        """
        draw = ImageDraw.Draw(image)
        centre_im_x = (self.centre_mod.x/TModel_Size.DOM_X)*image.width
        centre_im_y = (1-(self.centre_mod.y/TModel_Size.DOM_Y))*image.height
        radius_im = (1/TModel_Size.DX)*self.radius_mod
        start_im = -(self.start + self.extent)
        end_im = 0 - (self.start)
        draw.pieslice([centre_im_x - radius_im, centre_im_y - radius_im, \
                       centre_im_x + radius_im, centre_im_y + radius_im], \
                      start = start_im, end = end_im, fill = colour, outline = None)


class TPolygon(TShape):
    """
    Class represents a polygon.
    
    :param points: list of polygon vertices in window coordinates system.
    :type points: list of TPoint
    :param colour: shape outline colour.
    :type colour: string
    :param fill: shape fill colour.
    :type fill: string
    :param width: shape outline width in pixels.
    :type width: integer
    :param material: shape material.
    :type material: string
    :param points_mod: list of polygon vertices in model coordinates system.
    :type points_mod: list of TPoint
    """
    def __init__(self, points = [], colour = "black", fill = "", width = 1, \
                 material = "pec", points_mod = []):
        """
        Initialise object variables and call the parent class constructor.
        """
        if(points_mod):
            self.points_mod = self._remove_duplicates(points_mod)
            self.update_window_positions()
        else:
            if(len (points)  < 3):
                raise Exception ('Polygon requires at least 3 vertices to be given.')
            else:
                self.points = self._remove_duplicates(points)
            self.unwrap_points()
            # Coordinates in model's system
            self.update_model_positions()
        super().__init__(colour = colour, width = width, shape_type = "Polygon", \
                         material = material)

    def draw(self, canvas):
        """
        Draw the polygon on a canvas.

        :param canvas: canvas on which to draw the polygon.
        :type canvas: tkinter.Canvas
        """
        if(TColours.FILL):
            fill = self.fill
        else:
            fill = ""
        canvas.create_polygon(self.points_unwrapped, outline = self.colour, \
                              fill = fill, width = self.width)
        for pt in self.points:
            canvas.create_oval(pt.x-3, pt.y-3, pt.x+3, pt.y+3, outline = self.colour, \
                               fill = self.colour, width = 1)
    
    def update_window_positions(self):
        """
        Recalculate window positions of the polygon from its model positions.
        """
        min_model = TPoint(TModel_Size.MIN_X, TModel_Size.MIN_Y)
        max_model = TPoint(TModel_Size.MAX_X, TModel_Size.MAX_Y)
        min_window = TPoint(TWindow_Size.BOX_MIN_X, TWindow_Size.BOX_MIN_Y)
        max_window = TPoint(TWindow_Size.BOX_MAX_X, TWindow_Size.BOX_MAX_Y)
        self.points = []
        for pt in self.points_mod:
            self.points.append(TG.model_to_window(pt, min_model, max_model, \
                                                  min_window, max_window))
        self.points_unwrapped = []
        for pt in self.points:
            self.points_unwrapped.append(pt.x)
            self.points_unwrapped.append(pt.y)
    
    def remove_vertex(self, vertex_num):
        """
        Remove a vertex from the polygon.

        :param vertex_num: index of a vertex to be removed.
        :type vertex_num: integer
        """
        if(len (self.points) <= 3):
            messagebox.showerror ("Cannot remove vertex!", "Polygon must have at least 3 vertices")
        else:
            try:
                del(self.points[vertex_num])
            except Exception as message:
                messagebox.showerror("Error while manipulating polygon!", message)
            self.unwrap_points()
            self.update_model_positions()
    
    def _remove_duplicates(self, points_list):
        """
        Remove any duplicated points from vertices list.

        :param points_list: vertices list to be examined.
        :type points_list: list of TPoint
        """
        filtered = []
        for pt in points_list:
            if(pt not in filtered):
                filtered.append(pt)
        return filtered

    def edit_vertex(self, *, vertex_num, x, y):
        """
        Edit seleted vertex coordimates.

        :param vertex_num: list index of a vertex to be modified.
        :type vertex_num: integer
        :param x: new vertex x coordinate.
        :type x: float
        :param y: new vertex y coordinate.
        :type y: float
        """
        try:
            self.points_mod[vertex_num].x = x
            self.points_mod[vertex_num].y = y
        except Exception as message:
            messagebox.showerror("Error while manipulating polygon!", message)
        self.update_window_positions()
        self.unwrap_points()

    def add_vertex(self, **kwargs):
        """
        Add a vertex to the polygon.

        :param x: vertex x coordinate in pixels.
        :type x: integer
        :param y: vertex y coordinate in pixels.
        :type y: integer
        :param x_mod: vertex x coordinate in metres.
        :type x_mod: float
        :param y_mod: vertex y coordinate in metres.
        :type y_mod: float
        """
        x = kwargs.pop('x', None)
        y = kwargs.pop('y', None)
        x_mod = kwargs.pop('x_mod', None)
        y_mod = kwargs.pop('y_mod', None)
        min_model = TPoint(TModel_Size.MIN_X, TModel_Size.MIN_Y)
        max_model = TPoint(TModel_Size.MAX_X, TModel_Size.MAX_Y)
        min_window = TPoint(TWindow_Size.BOX_MIN_X, TWindow_Size.BOX_MIN_Y)
        max_window = TPoint(TWindow_Size.BOX_MAX_X, TWindow_Size.BOX_MAX_Y)
        if(x_mod is not None and y_mod is not None):
            pt_win = TG.model_to_window(TPoint(x_mod, y_mod), min_model, max_model, \
                                        min_window, max_window)
            x, y = pt_win.x, pt_win.y
        def dist_to_segment(v1, v2, v3):
            """
            Calculate a distence from a point to a line segment.
            https://stackoverflow.com/questions/849211/shortest-distance-between-a-point-and-a-line-segment#1501725

            :param v1: first line segment point.
            :type v1: TPoint
            :param v2: second line segment point.
            :type v2: TPoint
            :param v3: single point.
            :type v3: TPoint
            """
            def dist2(v1, v2):
                """
                Calculate distance between two points.

                :param v1: first point.
                :type v1: TPoint
                :param v2: second point.
                :type v2: TPoint
                """
                return (v1.x - v2.x)**2 + (v1.y - v2.y)**2
            l2 = dist2(v1, v2)
            t = ((v3.x - v1.x) * (v2.x - v1.x) + (v3.y - v1.y) * (v2.y - v1.y)) / l2
            t = max(0, min(1, t))
            squared = dist2(v3, TPoint(v1.x + t*(v2.x - v1.x), v1.y + t*(v2.y - v1.y)))
            return squared**(0.5)
        dist = [dist_to_segment(pt1, pt2, TPoint(x, y)) for pt1, pt2 in zip(self.points, self.points[1:] + self.points[:1])]
        pos = dist.index(min(dist))
        new_point = TPoint(x, y)
        if (pos + 1 == len(dist)):
            self.points.append(new_point)
        else:
            self.points.insert(pos + 1, new_point)
        self.update_model_positions()
        self.update_window_positions()

    def unwrap_points(self):
        """
        Unwrap list of points into a list of alternating x and y coordinates.
        """
        self.points_unwrapped = []
        for pt in self.points:
            self.points_unwrapped.append(pt.x)
            self.points_unwrapped.append(pt.y)
    
    def update_model_positions(self):
        """
        Recalculate model positions of the polygon from its window positions.
        """
        min_model = TPoint(TModel_Size.MIN_X, TModel_Size.MIN_Y)
        max_model = TPoint(TModel_Size.MAX_X, TModel_Size.MAX_Y)
        min_window = TPoint(TWindow_Size.BOX_MIN_X, TWindow_Size.BOX_MIN_Y)
        max_window = TPoint(TWindow_Size.BOX_MAX_X, TWindow_Size.BOX_MAX_Y)
        dx = TModel_Size.DX
        dy = TModel_Size.DY
        self.points_mod = []
        for pt in self.points:
            self.points_mod.append(TG.window_to_model(pt, min_model, max_model, \
                                                      min_window, max_window, \
                                                      dx, dy))
    
    def visible(self, min_model, max_model):
        """
        Determine whether the polygon lies within the visible model area.

        :param min_model: lower left visible model corner.
        :type min_model: TPoint
        :param max_model: upper right visible model corner.
        :type max_model: TPoint

        :rtype: boolean
        """
        xs = [pt.x for pt in self.points_mod]
        ys = [pt.y for pt in self.points_mod]
        min_x = min(xs)
        min_y = min(ys)
        max_x = max(xs)
        max_y = max(ys)
        min_pt = TPoint(min_x, min_y)
        max_pt = TPoint(max_x, max_y)
        if(min_pt.x >= min_model.x and min_pt.y >= min_model.y and \
           max_pt.x <= max_model.x and max_pt.y <= max_model.y):
            return "entirely"
        elif(min_pt.x < min_model.x or min_pt.y < min_model.y or \
             max_pt.x > max_model.x or min_pt.y > max_model.y):
            return "partly"
        else:
            return "invisible"

    def area(self):
        """
        Calculate cylinder sector area.

        :rtype: float
        """
        darea = 0.0
        for v1, v2 in zip(self.points_mod, self.points_mod[1:] + \
                          self.points_mod[:1]):
                darea += (v2.x - v1.x)*(v2.y + v1.y)
        return darea/2.0
    
    def draw_to_image(self, image, colour):
        """
        Draw the polygon to a png image file.

        :param image: png image.
        :type image: PIL.Image
        :param colour: shape colour.
        :type colour: tuple
        """
        draw = ImageDraw.Draw(image)
        coords = []
        for pt_mod in self.points_mod:
            coords.append((pt_mod.x/TModel_Size.DOM_X)*image.width)
            coords.append((1-(pt_mod.y/TModel_Size.DOM_Y))*image.height)
        draw.polygon(coords, fill = colour, outline = None)


class TCoordSys(TRect):
    """
    Class represents the coordinates system.

    :param colour: coordinate system box outline colour.
    :type colour: string
    :param width: coordinate system box outline width.
    :type width: integer
    :param minx: minimal x coordinate of coordinate system box in pixels.
    :type minx: integer
    :param miny: minimal y coordinate of coordinate system box in pixels.
    :type miny: integer
    :param maxx: maxmial x coordinate of coordinate system box in pixels.
    :type maxx: integer
    :param maxy: maximal y coordinate of coordinate system box in pixels.
    :type maxy: integer
    :param margx: coordinate system box margin in x direction.
    :type margx: integer
    :param margy: coordinate system box margin in y direction.
    :type margy: integer
    :param model_min_x: minimal visible x coordinate in metres.
    :type model_min_x: float
    :param model_min_y: minimal visible y coordinate in metres.
    :type model_min_y: float
    :param model_max_x: maximal visible x coordinate in metres.
    :type model_max_x: float
    :param model_max_y: maximal visible y coordinate in metres.
    :type model_max_y: float
    :param ticintmetx: tick interval in x direction in metres.
    :type ticintmetx: float
    :param ticintmety: tick interval in y direction in metres.
    :type ticintmety: float
    :param ticlenx: x-ticks length in pixels.
    :type ticlenx: integer
    :param ticleny: x-ticks length in pixels.
    :type ticleny: integer
    :param grid: grid diplay toggle.
    :type grid: boolean
    :param grid_colour: grid lines colour.
    :type grid_colour: string
    :param round_digits: tick labels precision.
    :type round_digits: integer
    """
    def __init__(self, colour = "black", width = 1, minx = 0, miny = 0, \
                 maxx = TWindow_Size.MAX_X, maxy = TWindow_Size.MAX_Y,\
                 margx = TWindow_Size.MARG_X, margy = TWindow_Size.MARG_Y, \
                 model_min_x = 0.0, model_min_y = 0.0, model_max_x = TModel_Size.MAX_X, \
                 model_max_y = TModel_Size.MAX_Y, ticintmetx = TTicksSettings.INT_X, \
                 ticintmety = TTicksSettings.INT_Y, ticlenx = 5, ticleny = 5, \
                 grid = False, grid_colour = "grey", round_digits = TTicksSettings.ROUND_DIGITS):
        """
        Initialise object variables and call the parent class constructor.
        """
        super().__init__(self, point1_x = minx + margx, point1_y = miny + margy, \
                         point2_x = maxx-margx, point2_y = maxy-margy, \
                         colour = colour, width = width)
        self.type = "CoordSys"
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy
        self.margx = margx
        self.margy = margy
        self.model_min_x = model_min_x
        self.model_min_y = model_min_y
        self.model_max_x = model_max_x
        self.model_max_y = model_max_y
        self.ticintmetx = ticintmetx
        self.ticintmety = ticintmety
        self.ticintx = (((self.maxx - self.minx - 2*self.margx)/(self.model_max_x))*self.ticintmetx)
        self.ticinty = (((self.maxy - self.miny - 2*self.margx)/(self.model_max_y))*self.ticintmety)
        self.ticlenx = ticlenx
        self.ticleny = ticleny
        self.grid = grid
        self.grid_colour = grid_colour
        self.round_digits = round_digits

    def draw(self, canvas):
        """
        Draw the coordinate system box on a canvas.

        :param canvas: canvas on which to draw the coordinate system box.
        :type canvas: tkinter.Canvas
        """
        canvas.create_rectangle(self.point1.x, self.point1.y, self.point2.x, \
                                self.point2.y, outline = self.colour, \
                                width = self.width)
    
    def draw_ticks(self, canvas, grid = False):
        """
        Draw the axis ticks on a canvas.

        :param canvas: canvas on which to draw the ticks.
        :type canvas: tkinter.Canvas
        :param grid: grid diplay toggle.
        :type grid: boolean
        """
        fsize = 7
        fname = "Arial"
        text_offset = 20
        width = abs(self.point2.x - self.point1.x)
        height = abs(self.point1.y - self.point2.y)
        current_tick_x = TG.round_to_multiple(self.model_min_x, self.ticintmetx)
        current_pos_x = round((current_tick_x - self.model_min_x)*width/ \
                              (self.model_max_x - self.model_min_x)) + TWindow_Size.BOX_MIN_X
        current_tick_y = TG.round_to_multiple(self.model_min_y, self.ticintmety)
        current_pos_y = TWindow_Size.BOX_MIN_Y - round((current_tick_y - self.model_min_y)*\
                        height/(self.model_max_y - self.model_min_y))
        if(current_tick_x < self.model_min_x):
            current_tick_x += self.ticintmetx
            current_pos_x += self.ticintx
        if(current_tick_y < self.model_min_y):
            current_tick_y += self.ticintmety
            current_pos_y -= self.ticinty
        border_x = min(self.point1.x, self.point2.x)
        border_y = max(self.point1.y, self.point2.y)
        while(current_tick_x <= self.model_max_x):
            if(grid):
                canvas.create_line(round(current_pos_x),  border_y - self.ticlenx, \
                                   round(current_pos_x), self.margy, \
                                   fill = self.grid_colour, width = self.width)
            else:
                canvas.create_line(round(current_pos_x), border_y, \
                                round(current_pos_x), border_y - \
                                self.ticlenx, fill = self.colour, width = self.width)
                label_x = str(self.label_round(current_tick_x, self.round_digits))
                if(current_tick_x % TTicksSettings.LABEL_INT == 0.0):
                    canvas.create_text(round(current_pos_x), border_y + text_offset, \
                                    text = label_x, font = (fname, fsize), anchor = S)
            current_tick_x += self.ticintmetx
            current_pos_x += self.ticintx
        while(current_tick_y <= self.model_max_y):
            if(grid):
                canvas.create_line(border_x + self.ticleny, round(current_pos_y), \
                                   self.maxx - self.margx, round(current_pos_y), \
                                   fill = self.grid_colour, width = self.width)
            else:
                canvas.create_line(border_x, round(current_pos_y), \
                                   border_x + self.ticleny, round(current_pos_y), \
                                   fill = self.colour, width = self.width)
                label_y = str(self.label_round(current_tick_y, self.round_digits))
                if(current_tick_y % TTicksSettings.LABEL_INT == 0.0):
                    canvas.create_text(border_x - text_offset, round(current_pos_y), \
                                    text = label_y, font = (fname, fsize), anchor = W)
            current_tick_y += self.ticintmety
            current_pos_y -= self.ticinty
    
    def obscure_protruding_edges(self, canvas):
        """
        Obscure edges protruding from model area with background-coloured rectangles.

        :param canvas: canvas on which to perform the obscuring.
        :type canvas: tkinter.Canvas
        """
        bgcolour = canvas["background"]
        canvas.create_rectangle(0, 0, self.maxx, TWindow_Size.BOX_MAX_Y - 1, \
                                outline = bgcolour, fill = bgcolour)
        canvas.create_rectangle(0, TWindow_Size.BOX_MIN_Y + 1, self.maxx, self.maxy, \
                                outline = bgcolour, fill = bgcolour)
        canvas.create_rectangle(0, TWindow_Size.BOX_MAX_Y - 1, \
                                TWindow_Size.BOX_MIN_X - 1, \
                                TWindow_Size.BOX_MIN_Y + 1, \
                                outline = bgcolour, fill = bgcolour)
        canvas.create_rectangle(TWindow_Size.BOX_MAX_X + 1, \
                                TWindow_Size.BOX_MAX_Y - 1, \
                                self.maxx, TWindow_Size.BOX_MIN_Y + 1, \
                                outline = bgcolour, fill = bgcolour)
    
    def toggle_grid(self, state):
        """
        Toggle displaying of the coordinate system grid.

        :param state: new grid state.
        :type state: boolean
        """
        if(state == "On" or state == "on"):
            self.grid = True
        elif(state == "Off" or state == "off"):
            self.grid = False
        else:
            raise Exception("Improper argument {}.".format (state))

    def draw_grid(self, canvas):
        """
        Draw coordinate system grid on a canvas.

        :param canvas: canvas on which to draw the grid.
        :type canvas: tkinter.Canvas
        """
        width = abs(self.point2.x - self.point1.x)
        height = abs(self.point1.y - self.point2.y)
        start_x = min(self.point1.x, self.point2.x)
        end_x = max(self.point1.x, self.point2.x)
        start_y = max(self.point1.y, self.point2.y)
        end_y = min(self.point1.y, self.point2.y)
        for i in range(ceil((width)/(self.ticintx)) - 1):
            canvas.create_line(start_x + (i + 1)*self.ticintx, start_y, start_x + (i + 1)*self.ticintx, \
                end_y, fill = self.grid_colour, width = self.width)
        for i in range(ceil ((height)/(self.ticinty)) - 1):
            canvas.create_line (start_x, start_y - (i + 1)*self.ticinty, end_x, \
                start_y - (i + 1)*self.ticinty, fill = self.grid_colour, width = self.width)
    
    def write_axis_labels(self, canvas):
        """
        Write axis labels on a canvas.

        :param canvas: canvas on which to draw the grid.
        :type canvas: tkinter.Canvas
        """
        debug = True
        if(debug):
            marg = 5
            start_x = min(self.point1.x, self.point2.x)
            start_y = max(self.point1.y, self.point2.y)
            end_x = max(self.point1.x, self.point2.x)
            end_y = min(self.point1.y, self.point2.y)
            canvas.create_text(start_x, start_y + marg, \
                               text = str(self.label_round(self.model_min_x, \
                                                           self.round_digits)))
            canvas.create_text(end_x, start_y + marg, \
                               text = str(self.label_round(self.model_max_x, \
                                                           self.round_digits)))
            canvas.create_text(start_x - marg, start_y, \
                               text = str(self.label_round(self.model_min_y, \
                                                           self.round_digits)))
            canvas.create_text(start_x - marg, end_y, \
                               text = str(self.label_round(self.model_max_y, \
                                                           self.round_digits)))
        else:
            width = abs(self.point2.x - self.point1.x)
            height = abs(self.point1.y - self.point2.y)
            start_x = min(self.point1.x, self.point2.x)
            start_y = max(self.point1.y, self.point2.y)
            try:
                for i in range(round((width)/(self.ticintx)) + 1):
                    canvas.create_text(start_x + i*self.ticintx, start_y + 7, \
                                    text = str(self.label_round(i*self.ticintmetx + \
                                                                self.model_min_x, \
                                                                self.round_digits)))
                for i in range(round((height)/(self.ticinty)) + 1):
                    canvas.create_text(start_x - 7, start_y - i*self.ticinty, \
                                    text = str(self.label_round(self.model_min_y + \
                                                                i*self.ticintmety, \
                                                                self.round_digits)))
            except Exception as message:
                messagebox.showerror("Error while writing axis labels!", message)
    
    def label_round(self, label, digits):
        """
        Round axis labels.

        :param label: label too be rounded.
        :type label: float
        :param digits: rounding precision.
        :type digits: integer
        """
        if(isinstance(label, float)):
            label = round(label, digits)
            if(label.is_integer()):
                return int(label)
            else:
                return label
        else:
            raise Exception ("Input is not float!")
    
    def model_size_update(self):
        """
        Update model size.
        """
        self.model_max_x = TModel_Size.MAX_X
        self.model_max_y = TModel_Size.MAX_Y
        self.ticintx = float((self.maxx - self.minx - 2*self.margx)/(self.model_max_x - self.model_min_x))
        self.ticinty = float((self.maxy - self.miny - 2*self.margx)/(self.model_max_y - self.model_min_y))

    def window_size_update(self):
        """
        Update window size.
        """
        self.minx = TWindow_Size.MIN_X
        self.miny = TWindow_Size.MIN_Y
        self.maxx = TWindow_Size.MAX_X
        self.maxy = TWindow_Size.MAX_Y
        self.margx = TWindow_Size.MARG_X
        self.margy = TWindow_Size.MARG_Y
        centre_x = int((TWindow_Size.MAX_X - TWindow_Size.MIN_X)/2)
        centre_y = int((TWindow_Size.MAX_Y - TWindow_Size.MIN_Y)/2)
        canvas_width = self.maxx - self.minx - 2*self.margx
        canvas_height = self.maxy - self.miny - 2*self.margy
        mod_max_x = TModel_Size.MAX_X
        mod_max_y = TModel_Size.MAX_Y 
        mod_min_x = TModel_Size.MIN_X
        mod_min_y = TModel_Size.MIN_Y
        len_x = round(mod_max_x - mod_min_x, TTicksSettings.ROUND_DIGITS)
        len_y = round(mod_max_y - mod_min_y, TTicksSettings.ROUND_DIGITS)
        if(TModel_Size.FIT):
            if(len_x > len_y):
                # Model box extends in x direction
                if((len_y/len_x)*canvas_width > canvas_height):
                    box_half_width = int((canvas_height)/2)
                else:
                    box_half_width = int((canvas_width)/2)
                box_half_height = int((len_y/len_x)*(box_half_width))
            elif(len_x < len_y):
                # Model box extends in y direction
                if((len_x/len_y)*canvas_height > canvas_width):
                    box_half_height = int((canvas_width)/2)
                else:
                    box_half_height = int((canvas_height)/2)
                box_half_width = int((len_x/len_y)*(box_half_height))
            else:
                # Model box extends euqally in both directions
                box_half_width = int(min(self.maxx - self.minx - 2*self.margx, \
                                     self.maxy - self.miny - 2*self.margy)/2)
                box_half_height = box_half_width
        else:
            # View is magnified and window area is fully covered
            box_half_width = int((self.maxx - self.minx - 2*self.margx)/2)
            box_half_height = int((self.maxy - self.miny - 2*self.margy)/2)
        self.point1.x = centre_x - box_half_width
        self.point1.y = centre_y - box_half_height
        self.point2.x = centre_x + box_half_width
        self.point2.y = centre_y + box_half_height
        self.ticintx = (2*box_half_width*self.ticintmetx)/(self.model_max_x - self.model_min_x)
        self.ticinty = (2*box_half_height*self.ticintmety)/(self.model_max_y)
        try:
            TWindow_Size.BOX_MIN_X = min(self.point1.x, self.point2.x)
            TWindow_Size.BOX_MIN_Y = max(self.point1.y, self.point2.y)
            TWindow_Size.BOX_MAX_X = max(self.point1.x, self.point2.x)
            TWindow_Size.BOX_MAX_Y = min(self.point1.y, self.point2.y)
        except Exception as message:
            messagebox.showerror ("Error while handling settings!", message)
        
    def display_settings_update(self):
        """
        Update display settings.
        """
        self.model_min_x = TModel_Size.MIN_X
        self.model_min_y = TModel_Size.MIN_Y
        self.model_max_x = TModel_Size.MAX_X
        self.model_max_y = TModel_Size.MAX_Y
        self.ticintmetx = TTicksSettings.INT_X
        self.ticintmety = TTicksSettings.INT_Y
        self.round_digits = TTicksSettings.ROUND_DIGITS
        self.ticintx = (abs(TWindow_Size.BOX_MAX_X - TWindow_Size.BOX_MIN_X)*\
                       self.ticintmetx)/(self.model_max_x - self.model_min_x)
        self.ticinty = (abs(TWindow_Size.BOX_MAX_Y - TWindow_Size.BOX_MIN_Y)*\
                       self.ticintmety)/(self.model_max_y - self.model_min_y)