#import matplotlib.pyplot as plt
from tkinter import messagebox

from settings import TModel_Size, TSurveySettings
from triangulate import make_monotone, split_polygons, triangulate_monotone_polygon, Polygon


class TParser (object):
    """
    Class contains statics methods designed for parsing in-program objects into gprMax commands.
    """

    FRONT_2D = 0.0
    THICKNESS_2D = 0.0
    SOURCE_NAME = "mysource"
    PARSE_STRING = ""

    @staticmethod
    def parse_shapes (materials, shapes, title):
        """
        Parses given model to a gprMax compliant file.

        Arguments:
        materials -- list of materials (TMaterial),
        shapes -- list of shapes (TShape subclasses: TRect, TCylin, TCylinSector, TTriangle, TPolygon)
        """
        TParser.PARSE_STRING = ""
        TParser.THICKNESS_2D = min (TModel_Size.DX, TModel_Size.DY)
        # Title
        if (title):
            TParser.PARSE_STRING += "#title: " + title + "\n"
        # Domain
        TParser.PARSE_STRING += "#domain: " + str(TModel_Size.DOM_X) + " " + str(TModel_Size.DOM_Y) + \
            " " + str(TParser.THICKNESS_2D) + "\n"
        # dx_dy_dz
        TParser.PARSE_STRING += "#dx_dy_dz: " + str(TModel_Size.DX) + " " + str(TModel_Size.DY) + \
            " " + str(TParser.THICKNESS_2D) + "\n"
        # Time window
        TParser.PARSE_STRING += "#time_window: " + str(TSurveySettings.TIME_WINDOW) + "\n"
        TParser.PARSE_STRING += "\n"
        # Wavefrom
        TParser.PARSE_STRING += "#waveform: " + TSurveySettings.WAVE_TYPE + " " + str(TSurveySettings.AMPLITUDE) + " " + str(TSurveySettings.FREQUENCY) + " mysource\n"
        # Transmitter
        TParser.PARSE_STRING += "#" + TSurveySettings.SRC_TYPE + ": z " + str(TSurveySettings.SRC_X) + " " + str(TSurveySettings.SRC_Y) + " " + str(TParser.FRONT_2D) + " mysource\n"
        # Receiver
        TParser.PARSE_STRING += "#rx: " + str(TSurveySettings.RX_X) + " " + str(TSurveySettings.RX_Y) + " " + str(TParser.FRONT_2D) + "\n"
        # rx array
        if(TSurveySettings.TYPE == "rx_array"):
            TParser.PARSE_STRING += "#rx_array: " + str(TSurveySettings.RX_X) + " " + str(TSurveySettings.RX_Y) + " " + str(TParser.FRONT_2D) + \
                                    " " + str(TSurveySettings.RX_MAX_X) + " " + str(TSurveySettings.RX_MAX_Y) + " " + str(TParser.FRONT_2D) + \
                                    " " + str(TSurveySettings.RX_STEP_X) + " " + str(TSurveySettings.RX_STEP_Y) + " " + str(TParser.FRONT_2D) + "\n"
        # bscan
        if(TSurveySettings.TYPE == "bscan"):
            TParser.PARSE_STRING += "#src_steps: " + str(TSurveySettings.SRC_STEP_X) + " " + str(TSurveySettings.SRC_STEP_Y) + " " + str(TParser.FRONT_2D) + "\n"
            TParser.PARSE_STRING += "#rx_steps: " + str(TSurveySettings.RX_STEP_X) + " " + str(TSurveySettings.RX_STEP_Y) + " " + str(TParser.FRONT_2D) + "\n"
        TParser.PARSE_STRING += "\n"
        # try:
        # Materials
        for single_material in materials:
            TParser.PARSE_STRING += "#material: " + str(single_material.epsilon_r) + " " + \
                str(single_material.sigma) + " " + str(single_material.mu_r) + " " + \
                str(single_material.sigma_mag) + " " + str(single_material.name) + "\n"
        TParser.PARSE_STRING += "\n"
        # Shapes
        for single_shape in shapes:
            if (single_shape.type == "Rectangle"):
                TParser.parse_rectangle(single_shape)
            elif (single_shape.type == "Cylinder"):
                TParser.parse_cylinder(single_shape)
            elif (single_shape.type == "CylinSector"):
                TParser.parse_cylinSector(single_shape)
            # elif (single_shape.type == "Triangle"):
            #     TParser.parse_triangle(single_shape)
            elif (single_shape.type == "Polygon"):
                TParser.parse_polygon(single_shape)
            else:
                raise Exception ("Invalid shape in shapes' list!")
        # except Exception as message:
            # messagebox.showerror ("Parser error!", message)
        return TParser.PARSE_STRING

    @staticmethod
    def parse_rectangle(rectangle):
        TParser.PARSE_STRING += "#box: " + str(rectangle.point1_mod.x) + " " + str(rectangle.point1_mod.y) + " " + str(TParser.FRONT_2D) + \
            " " + str(rectangle.point2_mod.x) + " " + str(rectangle.point2_mod.y) + " " + str(TParser.THICKNESS_2D) + " " + rectangle.material + "\n"

    @staticmethod
    def parse_cylinder(cylinder):
        TParser.PARSE_STRING += "#cylinder: " + str(cylinder.centre_mod.x) + " " + str(cylinder.centre_mod.y) + " " + \
            str(TParser.FRONT_2D) + " " + str(cylinder.centre_mod.x) + " " + str(cylinder.centre_mod.y) + " " + \
            str(TParser.THICKNESS_2D) + " " + str(cylinder.radius_mod) + " " + str(cylinder.material) + "\n"
    
    @staticmethod
    def parse_cylinSector(cylinSector):
        TParser.PARSE_STRING += "#cylindrical_sector: z " + str(cylinSector.centre_mod.x) + " " + str(cylinSector.centre_mod.y) + " " +\
            str(TParser.FRONT_2D) + " " + str(TParser.THICKNESS_2D) + " " + str(cylinSector.radius_mod) + " " + \
            str(cylinSector.start) + " " + str(cylinSector.extent) + " " + str(cylinSector.material) + "\n"

    # @staticmethod
    # def parse_triangle (triangle):
    #     TParser.PARSE_STRING += "#triangle: " + str(triangle.point1_mod.x) + " " + str(triangle.point1_mod.y) + " " +\
    #         str(TParser.FRONT_2D) + " " + str(triangle.point2_mod.x) + " " + str(triangle.point2_mod.y) + " " +\
    #         str(TParser.FRONT_2D) + " " + str(triangle.point3_mod.x) + " " + str(triangle.point3_mod.y) + " " +\
    #         str(TParser.FRONT_2D) + str(TParser.THICKNESS_2D - TParser.FRONT_2D) + " " + str(triangle.material) + "\n"
    
    @staticmethod
    def parse_polygon(polygon):
        tt = TParser.triangulate(polygon)
        for tr in tt:
            TParser.PARSE_STRING += "#triangle: " + str(tr[0].x) + " " + \
                                    str(tr[0].y) + " " + str(TParser.FRONT_2D) + \
                                    " " + str (tr[1].x) + " " + str(tr[1].y) + " " +\
                                    str(TParser.FRONT_2D) + " " + str(tr[2].x) + " " + \
                                    str(tr[2].y) + " " + str(TParser.FRONT_2D) + " " +\
                                    str(TParser.THICKNESS_2D - TParser.FRONT_2D) + " " + \
                                    str(polygon.material) + "\n"
    
    @staticmethod
    def triangulate(polygon):
        debug = False
        if(debug):
            from timeit import default_timer as timer
            start = timer()
        polygon_obj = Polygon(polygon.points_mod)
        edges = make_monotone(polygon_obj)
        monotone_polygons = split_polygons(polygon_obj, edges)
        edges2 = []
        for poly in monotone_polygons:
            edges2 += triangulate_monotone_polygon(poly)
        triangles = split_polygons(polygon_obj, edges + edges2)
        if(debug):
            end = timer()
            print("n vertices:", len(polygon.points_mod))
            print("elapsed time:", end-start)
        return triangles
