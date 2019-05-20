from copy import copy, deepcopy
from math import asin, acos, atan, degrees, sin, cos, radians, ceil, floor, pi
from random import randrange
from tkinter import Tk, Canvas, Menu, messagebox, BooleanVar, Frame, Button
from tkinter import LEFT, TOP, X, FLAT, RAISED, SUNKEN, ARC, PIESLICE, CHORD

from settings import TWindow_Size, TModel_Size, TTicksSettings
from point import TPoint
from geometry import TGeometry as TG
from abc import ABC, abstractmethod


class TShape(ABC):
    """
    Abstract base class for shapes (i.e. rectangles, triangles and cylinders).
    """
    def __init__(self, width = None, colour = None, fill = "", material = "pec"):
        self.width = width
        self.colour = colour
        self.fill = fill
        self.type = "None"
        self.material = material
    
    @abstractmethod
    def draw(self):
        "Abstract method"
        pass
    
    @abstractmethod
    def update_window_positions(self):
        pass

    @abstractmethod
    def update_model_positions(self):
        pass
    
    @abstractmethod
    def visible(self, min_model, max_model):
        pass
    
    @abstractmethod
    def area(self):
        pass

class TRect(TShape):
    """
    Class represents single rectangle.
    Each rectangle is described by two vertices (class TPoint), 
    line colour and width (from one to five).
    """    
    def __init__(self, point1 = None, point2 = None, point1_x = None, \
                 point1_y = None, point2_x = None, point2_y = None, \
                 colour = "black", fill = "", width = 1, material = "pec", \
                 point1_mod = None, point2_mod = None):
        # Rectangle vertices
        if(point1_mod and point2_mod):
            self.point1_mod = TPoint(min(point1_mod.x, point2_mod.x), min(point1_mod.y, point2_mod.y))
            self.point2_mod = TPoint(max(point1_mod.x, point2_mod.x), max(point1_mod.y, point2_mod.y))
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
            # Coordinates in model's system
            self.update_model_positions()
        # Material
        self.material = material
        # Line colour and width
        self.colour = colour
        self.fill = fill
        self.width = width
        # Type of shape
        self.type = "Rectangle"
        # Adjust shape's position on screen according to new model coordinates
        self.update_window_positions()

    def draw(self, canvas):
        min_model = TPoint(TModel_Size.MIN_X, TModel_Size.MIN_Y)
        max_model = TPoint(TModel_Size.MAX_X, TModel_Size.MAX_Y)
        # visible = self.visible(min_model, max_model)
        # if(visible):
        canvas.create_rectangle(self.point1.x, self.point1.y, self.point2.x, \
                                self.point2.y, outline = self.colour, \
                                fill = self.fill, width = self.width)
        # elif(visible == "partly"):
        #     lower_x = max(self.point1.x, TWindow_Size.BOX_MIN_X)
        #     lower_y = min(self.point1.y, TWindow_Size.BOX_MIN_Y)
        #     upper_x = min(self.point2.x, TWindow_Size.BOX_MAX_X)
        #     upper_y = max(self.point2.y, TWindow_Size.BOX_MAX_Y)
        #     canvas.create_rectangle(lower_x, lower_y, upper_x, upper_y, \
        #                             outline = self.colour, fill = self.fill, \
        #                             width = self.width)
        if(TG.point_visible(self.point1_mod, min_model, max_model)):
            canvas.create_oval(self.point1.x-3, self.point1.y-3, self.point1.x+3, \
                               self.point1.y+3, outline = self.colour, \
                               fill = self.colour, width = 1)
        if(TG.point_visible(self.point2_mod, min_model, max_model)):
            canvas.create_oval(self.point2.x-3, self.point2.y-3, self.point2.x+3, \
                               self.point2.y+3, outline = self.colour, \
                               fill = self.colour, width = 1)

    def update_window_positions(self):
        min_model = TPoint(TModel_Size.MIN_X, TModel_Size.MIN_Y)
        max_model = TPoint(TModel_Size.MAX_X, TModel_Size.MAX_Y)
        min_window = TPoint(TWindow_Size.BOX_MIN_X, TWindow_Size.BOX_MIN_Y)
        max_window = TPoint(TWindow_Size.BOX_MAX_X, TWindow_Size.BOX_MAX_Y)
        self.point1 = TG.model_to_window(self.point1_mod, min_model, max_model, \
                                         min_window, max_window)
        self.point2 = TG.model_to_window(self.point2_mod, min_model, max_model, \
                                         min_window, max_window)

    def update_model_positions(self):
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
    
    def visible(self, min_model, max_model):
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
        "Calculate rectangle area"
        len_x = abs(self.point2_mod.x - self.point1_mod.x)
        len_y = abs(self.point2_mod.y - self.point1_mod.y)
        return len_x*len_y


class TCylin(TShape):
    def __init__(self, centre = None, radius = None, centre_x = None, centre_y = None, colour = "black", fill = "", \
        width = 1, material = "pec", centre_mod = None, radius_mod = None):
        # Cylinder middle point
        if (centre_mod and radius_mod):
            self.centre_mod = copy (centre_mod)
            self.radius_mod = radius_mod
        else:
            self.centre = TPoint ()
            if (centre):
                self.centre = copy (centre)
            elif (centre_x and centre_y):
                self.centre.x = centre_x
                self.centre.y = centre_y
            # Cylinder radius
            self.radius = radius
            # Coordinates in model's system
            self.update_model_positions()
        # Material
        self.material = material
        # Line colour and width
        self.colour = colour
        self.fill = fill
        self.width = width
        # Type of shape
        self.type = "Cylinder"
        # Adjust shape's position on screen according to new model coordinates
        self.update_window_positions()

    def draw(self, canvas):
        min_model = TPoint(TModel_Size.MIN_X, TModel_Size.MIN_Y)
        max_model = TPoint(TModel_Size.MAX_X, TModel_Size.MAX_Y)
        # visible = self.visible(min_model, max_model)
        # if(visible):
        canvas.create_oval(self.centre.x - self.radius, self.centre.y - self.radius, \
                           self.centre.x + self.radius, self.centre.y + self.radius, \
                           outline = self.colour, fill = self.fill, width = self.width)
        # elif(visible == "partly"):
        #     self._draw_partly_visible(canvas)
        if(TG.point_visible(self.centre_mod, min_model, max_model)):
            canvas.create_oval(self.centre.x-3, self.centre.y-3, self.centre.x+3, \
                               self.centre.y+3, outline = self.colour, \
                               fill = self.colour, width = 1)

    def _draw_partly_visible(self, canvas):
        a, b, r = self.centre.x, self.centre.y, self.radius
        if((self.centre_mod.x - self.radius_mod) <= TModel_Size.MIN_X):
            border_x = TWindow_Size.BOX_MIN_X
        else:
            border_x = TWindow_Size.BOX_MAX_X
        if((self.centre_mod.y - self.radius_mod) <= TModel_Size.MIN_Y):
            border_y = TWindow_Size.BOX_MIN_Y
        else:
            border_y = TWindow_Size.BOX_MAX_Y
        delta_x = (round(r)**2 - (border_y - b)**2)
        delta_y = (round(r)**2 - (border_x - a)**2)
        if(delta_x >= 0):
            x1 = a - delta_x**(0.5)
            x2 = a + delta_x**(0.5)
        if(delta_y >= 0):
            y1 = b - delta_y**(0.5)
            y2 = b + delta_y**(0.5)
        intersection_type = "both"
        if(delta_x > 0 and delta_y <= 0):
            intersection_type = "x"
        elif(delta_x <= 0 and delta_y > 0):
            intersection_type = "y"
        if(intersection_type == "x"):
            chord_sq = (x1 - x2)**2
            start = degrees(asin(abs(border_y - b)/round(r)))
            extent = degrees(acos(1 - chord_sq/(2*round(r)**2)))
            if(border_y == TWindow_Size.BOX_MIN_Y):
                if(b <= TWindow_Size.BOX_MIN_Y):
                    start  = -start
                    extent = 360 - extent
            else:
                start = start + extent
                extent = 360 - extent
                if(b <= TWindow_Size.BOX_MAX_Y):
                    start  = -start
                    extent = 360 - extent
        elif(intersection_type == "y"):
            chord_sq = (y1 - y2)**2
            start = degrees(asin(abs(min(y1, y2) - b)/round(r)))
            extent = 360 - 2*start
            if(border_x == TWindow_Size.BOX_MIN_X):
                if(a <= TWindow_Size.BOX_MIN_X):
                    start  = -start
                    extent = 360 - extent
            else:
                start = start + extent
                extent = 360 - extent
                if(a <= TWindow_Size.BOX_MAX_X):
                    start  = -start
                    extent = 360 - extent
        elif(intersection_type == "both"):
            pass
        canvas.create_arc(a - r, b - r, a + r, b + r, 
                          start = start, extent = extent, \
                          outline = self.colour, fill = self.fill, \
                          width = self.width, style = CHORD)
    
    def area(self):
        "Calculate cylinder area"
        return self.radius_mod**2*pi
    
    def update_window_positions(self):
        min_model = TPoint(TModel_Size.MIN_X, TModel_Size.MIN_Y)
        max_model = TPoint(TModel_Size.MAX_X, TModel_Size.MAX_Y)
        min_window = TPoint(TWindow_Size.BOX_MIN_X, TWindow_Size.BOX_MIN_Y)
        max_window = TPoint(TWindow_Size.BOX_MAX_X, TWindow_Size.BOX_MAX_Y)
        self.centre = TG.model_to_window(self.centre_mod, min_model, max_model, \
                                         min_window, max_window)
        self.radius = TG.dist_model_to_window(self.radius_mod, min_model, max_model, \
                                              min_window, max_window)

    def update_model_positions(self):
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


class TCylinSector(TCylin):
    """
    Class represents 2-dimensional cylinder sector (slice).
    Inherits after TCylin class.
    Described with parameters as in TCylin and additionaly by location of 2 boundary points defining angle of the sector.
    """
    def __init__(self, centre = None, radius = None, centre_x = None, centre_y = None, colour = "black", fill = "", width = 1, \
        boundary_pt1 = None, boundary_pt2 = None, start = None, extent = None, material = "pec", centre_mod = None, radius_mod = None):
        self.boundary_pt1 = TPoint()
        self.boundary_pt2 = TPoint()
        if (centre_mod and radius_mod and start != None and extent):
            self.centre_mod = copy(centre_mod)
            self.radius_mod = radius_mod
            self.start = start
            self.extent = extent
        else:
            self.centre = TPoint()
            if(centre):
                self.centre = copy(centre)
            elif (centre_x and centre_y):
                self.centre.x = centre_x
                self.centre.y = centre_y
            if (radius is not None):
                # Cylinder radius
                self.radius = round(radius)
            if (boundary_pt1):
                self.boundary_pt1 = copy(boundary_pt1)
            if (boundary_pt2):
                self.boundary_pt2 = copy(boundary_pt2)
            elif (boundary_pt1 and start and extent):
                self.boundary_pt1.x = int (self.centre.x + cos(radians(start))*self.radius)
                self.boundary_pt1.y = int (self.centre.y - sin(radians(start))*self.radius)
            elif (not boundary_pt2 and start and extent):
                self.boundary_pt2.x = int(self.centre.x + cos(radians(start + extent))*self.radius)
                self.boundary_pt2.y = int(self.centre.y - sin(radians(start + extent))*self.radius)
            # Compute start and extent angles
            if(start != None):
                self.start = start
            elif(start == None and boundary_pt1 and boundary_pt2):
                if(self.boundary_pt1.x >= self.centre.x):
                    self.start = degrees (asin((self.centre.y-self.boundary_pt1.y)/self.radius))
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
                # Check wether boundry points and centre are colinear
                try:
                    self.extent = degrees(acos(-((b1**2 -b2**2-self.radius**2)/(2*b2*self.radius))))
                except ValueError:
                    self.extent = 180
                # Check wether second boundary point is located to the right of the centre -- first boundary point line
                if(((self.boundary_pt2.x-self.centre.x)*sin (radians(self.start)) + (self.boundary_pt2.y-self.centre.y)*cos(radians(self.start))) > 0):
                    self.extent = (360 - self.extent)
            if(self.extent > 360):
                self.extent -= 360
            self.start = TG.round_to_multiple(self.start, min(TModel_Size.DX, TModel_Size.DY))
            # self.start = round (self.start, TTicksSettings.ROUND_DIGITS)
            self.extent = TG.round_to_multiple(self.extent, min(TModel_Size.DX, TModel_Size.DY))
            # self.extent = round (self.extent, TTicksSettings.ROUND_DIGITS)
            self.boundary_pt2.x = int (self.centre.x + cos (radians (self.start + self.extent) )*self.radius )
            self.boundary_pt2.y = int (self.centre.y - sin (radians (self.start + self.extent) )*self.radius )
            # Coordinates in model's system
            self.update_model_positions()
        # Material
        self.material = material
        # Line colour and width
        self.colour = colour
        self.fill = fill
        self.width = width
        # Shape type
        self.type = "CylinSector"
        # Material
        self.material = material
        # Two boundary points defining slice angle
        # TODO: Add posibility to pass boundry points coordinates as separate real numbers, like centre
        self.update_window_positions ()

    def draw (self, canvas):
        canvas.create_arc (self.centre.x - self.radius, self.centre.y - self.radius, self.centre.x + self.radius, self.centre.y + self.radius, \
            outline = self.colour, fill = self.fill, width = self.width, style = PIESLICE, start = self.start, extent = self.extent)
        canvas.create_oval (self.centre.x-3, self.centre.y-3, self.centre.x+3, self.centre.y+3, outline = self.colour, fill = self.colour, width = 1)
        canvas.create_oval (self.boundary_pt1.x-3, self.boundary_pt1.y-3, self.boundary_pt1.x+3, self.boundary_pt1.y+3, outline = self.colour, fill = self.colour, width = 1)
        canvas.create_oval (self.boundary_pt2.x-3, self.boundary_pt2.y-3, self.boundary_pt2.x+3, self.boundary_pt2.y+3, outline = self.colour, fill = self.colour, width = 1)

    def update_window_positions (self):
        min_model = TPoint(TModel_Size.MIN_X, TModel_Size.MIN_Y)
        max_model = TPoint(TModel_Size.MAX_X, TModel_Size.MAX_Y)
        min_window = TPoint(TWindow_Size.BOX_MIN_X, TWindow_Size.BOX_MIN_Y)
        max_window = TPoint(TWindow_Size.BOX_MAX_X, TWindow_Size.BOX_MAX_Y)
        self.centre = TG.model_to_window (self.centre_mod, min_model, max_model, \
                                          min_window, max_window)
        self.radius = TG.dist_model_to_window (self.radius_mod, min_model, max_model, \
                                               min_window, max_window) 
        self.boundary_pt1.x = int(self.centre.x + cos(radians (self.start))*self.radius)
        self.boundary_pt1.y = int(self.centre.y - sin(radians (self.start))*self.radius)
        self.boundary_pt2.x = int(self.centre.x + cos(radians (self.start + self.extent))*self.radius)
        self.boundary_pt2.y = int(self.centre.y - sin(radians (self.start + self.extent))*self.radius)

    def update_model_positions(self):
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
        self.Boundary_pt2_mod = TG.window_to_model(self.boundary_pt2, min_model, max_model, \
                                                   min_window, max_window, dx, dy)
        self.radius_mod = TG.dist_window_to_model(self.radius,  min_model, max_model, \
                                                  min_window, max_window, dx, dy)
    
    def visible(self, min_model, max_model):
        min_x = min(self.centre_mod.x - self.radius_mod, self.boundary_pt1_mod.x, \
                    self.Boundary_pt2_mod.x)
        min_y = min(self.centre_mod.y - self.radius_mod, self.boundary_pt1_mod.y, \
                    self.Boundary_pt2_mod.y)
        max_x = max(self.centre_mod.x + self.radius_mod, self.boundary_pt1_mod.x, \
                    self.Boundary_pt2_mod.x)
        max_y = max(self.centre_mod.y + self.radius_mod, self.boundary_pt1_mod.y, \
                    self.Boundary_pt2_mod.y)
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
        "Calculate cylindrical sector area"
        return (self.extent/360.0)*self.radius_mod**2*pi


# class TTriangle (TShape):
#     """
#     Class represents 2-dimensional triangle.
#     """
#     def __init__ (self, point1 = None, point2 = None, point3 = None, point1_x = None, point1_y = None, point2_x = None, point2_y = None, \
#         point3_x = None, point3_y = None, colour = "black", fill = "", width = 1, material = "pec"):
#         super ().__init__ (width, colour, fill)
#         self.type = "Triangle"
#         self.point1 = TPoint ()
#         self.point2 = TPoint ()
#         self.point3 = TPoint ()
#         if (point1 == None):
#             self.point1.x = point1_x
#             self.point1.y = point1_y
#         else:
#             self.point1 = copy (point1)
#         if (point2 == None):
#             self.point2.x = point2_x
#             self.point2.y = point2_y
#         else:
#             self.point2 = copy (point2)
#         if (point3 == None):
#             self.point3.x = point3_x
#             self.point3.y = point3_y
#         else:
#             self.point3 = copy (point3)
#         # Material
#         self.material = material
#         # Coordinates in model's system
#         self.point1_mod = TGeometry.window_to_model (self.point1, TPoint (TModel_Size.MAX_X, TModel_Size.MAX_Y), \
#             TPoint (TWindow_Size.BOX_MIN_X, TWindow_Size.BOX_MIN_Y), TPoint(TWindow_Size.BOX_MAX_X, TWindow_Size.BOX_MAX_Y), \
#             TModel_Size.DX, TModel_Size.DY)
#         self.point2_mod = TGeometry.window_to_model (self.point2, TPoint (TModel_Size.MAX_X, TModel_Size.MAX_Y), \
#             TPoint (TWindow_Size.BOX_MIN_X, TWindow_Size.BOX_MIN_Y), TPoint(TWindow_Size.BOX_MAX_X, TWindow_Size.BOX_MAX_Y), \
#             TModel_Size.DX, TModel_Size.DY)
#         self.point3_mod = TGeometry.window_to_model (self.point3, TPoint (TModel_Size.MAX_X, TModel_Size.MAX_Y), \
#             TPoint (TWindow_Size.BOX_MIN_X, TWindow_Size.BOX_MIN_Y), TPoint(TWindow_Size.BOX_MAX_X, TWindow_Size.BOX_MAX_Y), \
#             TModel_Size.DX, TModel_Size.DY)
#         # Adjust shape's position on screen according to new model coordinates
#         self.update_window_positions ()    
        
#     def draw (self, canvas):
#         canvas.create_polygon (self.point1.x, self.point1.y, self.point2.x, self.point2.y, self.point3.x, self.point3.y, \
#            outline = self.colour, fill = self.fill, width = self.width)
#         canvas.create_oval (self.point1.x-3, self.point1.y-3, self.point1.x+3, self.point1.y+3, outline = self.colour, fill = self.colour, width = 1)
#         canvas.create_oval (self.point2.x-3, self.point2.y-3, self.point2.x+3, self.point2.y+3, outline = self.colour, fill = self.colour, width = 1)
#         canvas.create_oval (self.point3.x-3, self.point3.y-3, self.point3.x+3, self.point3.y+3, outline = self.colour, fill = self.colour, width = 1)

#     def update_window_positions (self):
#         self.point1 = TGeometry.model_to_window (self.point1_mod, TPoint (TModel_Size.MAX_X, TModel_Size.MAX_Y), \
#             TPoint (TWindow_Size.BOX_MIN_X, TWindow_Size.BOX_MIN_Y), TPoint(TWindow_Size.BOX_MAX_X, TWindow_Size.BOX_MAX_Y) )
#         self.point2 = TGeometry.model_to_window (self.point2_mod, TPoint (TModel_Size.MAX_X, TModel_Size.MAX_Y), \
#             TPoint (TWindow_Size.BOX_MIN_X, TWindow_Size.BOX_MIN_Y), TPoint(TWindow_Size.BOX_MAX_X, TWindow_Size.BOX_MAX_Y) )
#         self.point3 = TGeometry.model_to_window (self.point3_mod, TPoint (TModel_Size.MAX_X, TModel_Size.MAX_Y), \
#             TPoint (TWindow_Size.BOX_MIN_X, TWindow_Size.BOX_MIN_Y), TPoint(TWindow_Size.BOX_MAX_X, TWindow_Size.BOX_MAX_Y) )


class TPolygon(TShape):
    """
    Class represents discretionary polygon.
    """
    def __init__(self, points = [], colour = "black", fill = "", width = 1, material = "pec", points_mod = []):
        super().__init__(width, colour, fill)
        self.type = "Polygon"
        if(points_mod):
            self.points_mod = self._remove_duplicates(points_mod)
            self.update_window_positions()
        else:
            if(len (points)  < 3):
                raise Exception ('Polygon requires at least 3 vertices to be given.')
            else:
                self.points = self._remove_duplicates(points)
            self.unwrap_points ()
            # Coordinates in model's system
            self.update_model_positions()
            self.update_window_positions()
        # Material
        self.material = material

    def draw(self, canvas):
        canvas.create_polygon(self.points_unwrapped, outline = self.colour, fill = self.fill, width = self.width)
        for pt in self.points:
            canvas.create_oval(pt.x-3, pt.y-3, pt.x+3, pt.y+3, outline = self.colour, fill = self.colour, width = 1)
    
    def update_window_positions(self):
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
            self.points_unwrapped.append (pt.x)
            self.points_unwrapped.append (pt.y)
    
    def remove_vertex(self, vertex_num):
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
        filtered = []
        for pt in points_list:
            if(pt not in filtered):
                filtered.append(pt)
        return filtered

    def edit_vertex(self, *, vertex_num, x, y):
        try:
            self.points_mod[vertex_num].x = x
            self.points_mod[vertex_num].y = y
        except Exception as message:
            messagebox.showerror("Error while manipulating polygon!", message)
        self.update_window_positions()
        self.unwrap_points()

    def add_vertex(self, **kwargs):
        "Adds vertex to polygon"
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
            "https://stackoverflow.com/questions/849211/shortest-distance-between-a-point-and-a-line-segment#1501725"
            def dist2(v1, v2):
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

    def unwrap_points (self):
        self.points_unwrapped = []
        for pt in self.points:
            self.points_unwrapped.append (pt.x)
            self.points_unwrapped.append (pt.y)
    
    def update_model_positions (self):
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
        "Calculate polygon area"
        darea = 0.0
        for v1, v2 in zip(self.points_mod, self.points_mod[1:] + \
                          self.points_mod[:1]):
                darea += (v2.x - v1.x)*(v2.y + v1.y)
        return darea/2.0


class TCoordSys(TRect):
    """
    Class represents coordinates system.
    """
    def __init__(self, colour = "black", width = 1, minx = 0, miny = 0, \
                 maxx = TWindow_Size.MAX_X, maxy = TWindow_Size.MAX_Y,\
                 margx = TWindow_Size.MARG_X, margy = TWindow_Size.MARG_Y, \
                 model_min_x = 0.0, model_min_y = 0.0, model_max_x = TModel_Size.MAX_X, \
                 model_max_y = TModel_Size.MAX_Y, ticintmetx = TTicksSettings.INT_X, \
                 ticintmety = TTicksSettings.INT_Y, ticlenx = 5, ticleny = 5, \
                 grid = False, grid_colour = "grey", round_digits = TTicksSettings.ROUND_DIGITS):
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
        if(self.grid):
            self.draw_grid(canvas)
        # self.write_axis_labels(canvas)
        canvas.create_rectangle(self.point1.x, self.point1.y, self.point2.x, self.point2.y, outline = self.colour, width = self.width)
    
    def draw_ticks(self, canvas):
        width = abs(self.point2.x - self.point1.x)
        height = abs(self.point1.y - self.point2.y)
        start_x = min(self.point1.x, self.point2.x)
        start_y = max(self.point1.y, self.point2.y)
        for i in range(round((width)/(self.ticintx)) - 1):
            canvas.create_line (start_x + (i + 1)*self.ticintx, start_y, start_x + (i + 1)*self.ticintx, \
                start_y - self.ticlenx, fill = self.colour, width = self.width)
        for i in range(round((height)/(self.ticinty)) - 1):
            canvas.create_line (start_x, start_y - (i + 1)*self.ticinty, start_x + self.ticleny, \
                start_y - (i + 1)*self.ticinty, fill = self.colour, width = self.width)
    
    def obscure_protruding_edges(self, canvas):
        "Obscures edges protruding from model area with background-coloured rectangles"
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
    
    def toogle_grid(self, state):
        if(state == "On" or state == "on"):
            self.grid = True
        elif(state == "Off" or state == "off"):
            self.grid = False
        else:
            raise Exception("Improper argument {}.".format (state))

    def draw_grid(self, canvas):
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
        if(isinstance(label, float)):
            label = round(label, digits)
            if(label.is_integer()):
                return int(label)
            else:
                return label
        else:
            raise Exception ("Input is not float!")
    
    def model_size_update(self):
        self.model_max_x = TModel_Size.MAX_X
        self.model_max_y = TModel_Size.MAX_Y
        self.ticintx = float((self.maxx - self.minx - 2*self.margx)/(self.model_max_x - self.model_min_x))
        self.ticinty = float((self.maxy - self.miny - 2*self.margx)/(self.model_max_y - self.model_min_y))
        # self.draw_grid ()

    def window_size_update(self):
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
        if(len_x > len_y):
            # Model box extends in x direction
            if((len_y/len_x)*canvas_width > canvas_height):
                box_half_width = int((canvas_height)/2)
            else:
                box_half_width = int((canvas_width)/2)
            box_half_height = int((len_y/len_x)*(box_half_width))
        elif((mod_max_x - mod_min_x) < (mod_max_y - mod_min_y)):
            # Model box extends in y direction
            if((len_x/len_y)*canvas_height > canvas_width):
                box_half_height = int((canvas_width)/2)
            else:
                box_half_height = int((canvas_height)/2)
            box_half_width = int((len_x/len_y)*(box_half_height))
        else:
            # Model box extends euqally in both directions
            box_half_width = int(min(self.maxx - self.minx - 2*self.margx, self.maxy - self.miny - 2*self.margy)/2)
            box_half_height = box_half_width
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
        self.model_min_x = TModel_Size.MIN_X
        self.model_min_y = TModel_Size.MIN_Y
        self.model_max_x = TModel_Size.MAX_X
        self.model_max_y = TModel_Size.MAX_Y
        self.ticintmetx = TTicksSettings.INT_X
        self.ticintmety = TTicksSettings.INT_Y
        self.round_digits = TTicksSettings.ROUND_DIGITS
        self.ticintx = (abs(TWindow_Size.BOX_MAX_X - TWindow_Size.BOX_MIN_X)*self.ticintmetx)/(self.model_max_x - self.model_min_x)
        self.ticinty = (abs(TWindow_Size.BOX_MAX_Y - TWindow_Size.BOX_MIN_Y)*self.ticintmety)/(self.model_max_y - self.model_min_y)

if __name__ == "__main__":
    assert TG.intersect(TPoint(1,1), TPoint(5,5), TPoint(1,5), TPoint(5,1)) == True
    assert TG.intersect(TPoint(1,1), TPoint(1,5), TPoint(5,5), TPoint(5,1)) == False
    assert TG.intersect(TPoint(2.15,0.75), TPoint(5,0.8), TPoint(2.95,0.55), TPoint(3.25,1.75)) == True
    assert TG.intersect(TPoint(3.8,2.1), TPoint(6.05,1.25), TPoint(3.0,1.25), TPoint(4.7,2.7)) == True