from tkinter import messagebox

from settings import TModel_Size, TSurveySettings
from triangulate import make_monotone, split_polygons, triangulate_monotone_polygon, Polygon


class TParser(object):
    """
    Class contains statics methods designed for parsing in-program objects into
    gprMax commands.
    """

    FRONT_2D = 0.0              #: minimal z coordinate.
    THICKNESS_2D = 0.0          #: maximal z coordinate, set to lesser value from (dx, dy).
    SOURCE_NAME = "mysource"    #: name of the em wave source.
    PARSE_STRING = ""           #: string containing lines of the output file.

    @staticmethod
    def parse_shapes (materials, shapes, title):
        """
        Parses given model to a gprMax compliant file.

        :param materials: list of materials.
        :type materials: TMaterial
        :param shapes: list of shapes.
        :type shapes: TShape, TRect, TCylin, TCylinSector, TPolygon

        :rtype: string
        """
        TParser.PARSE_STRING = ""
        TParser.THICKNESS_2D = min(TModel_Size.DX, TModel_Size.DY)
        # Title
        if (title):
            TParser.PARSE_STRING += "#title: " + title + "\n"
        # Domain
        TParser.PARSE_STRING += "#domain: " + str(TModel_Size.DOM_X) + " " + \
                                str(TModel_Size.DOM_Y) + " " + \
                                str(TParser.THICKNESS_2D) + "\n"
        # dx_dy_dz
        TParser.PARSE_STRING += "#dx_dy_dz: " + str(TModel_Size.DX) + " " + \
                                str(TModel_Size.DY) + " " + \
                                str(TParser.THICKNESS_2D) + "\n"
        # Time window
        TParser.PARSE_STRING += "#time_window: " + str(TSurveySettings.TIME_WINDOW) + "\n"
        # Time stability factor
        if(TSurveySettings.TSF != 1.0):
            TParser.PARSE_STRING += "#time_stability_factor: " + str(TSurveySettings.TSF) + "\n"
        TParser.PARSE_STRING += "\n"
        # Wavefrom
        TParser.PARSE_STRING += "#waveform: " + TSurveySettings.WAVE_TYPE + " " + \
                                str(TSurveySettings.AMPLITUDE) + " " + \
                                str(TSurveySettings.FREQUENCY) + " mysource\n"
        # Transmitter
        TParser.PARSE_STRING += "#" + TSurveySettings.SRC_TYPE + ": z " + \
                                str(TSurveySettings.SRC_X) + " " + \
                                str(TSurveySettings.SRC_Y) + " " + \
                                str(TParser.FRONT_2D) + " mysource\n"
        # Receiver
        TParser.PARSE_STRING += "#rx: " + str(TSurveySettings.RX_X) + " " + \
                                str(TSurveySettings.RX_Y) + " " + \
                                str(TParser.FRONT_2D) + "\n"
        # rx array
        if(TSurveySettings.TYPE == "rx_array"):
            TParser.PARSE_STRING += "#rx_array: " + str(TSurveySettings.RX_X) + \
                                    " " + str(TSurveySettings.RX_Y) + " " + \
                                    str(TParser.FRONT_2D) + " " + \
                                    str(TSurveySettings.RX_MAX_X) + " " + \
                                    str(TSurveySettings.RX_MAX_Y) + " " + \
                                    str(TParser.FRONT_2D) + " " + \
                                    str(TSurveySettings.RX_STEP_X) + " " + \
                                    str(TSurveySettings.RX_STEP_Y) + " " + \
                                    str(TParser.FRONT_2D) + "\n"
        # bscan
        if(TSurveySettings.TYPE == "bscan"):
            TParser.PARSE_STRING += "#src_steps: " + str(TSurveySettings.SRC_STEP_X) + \
                                    " " + str(TSurveySettings.SRC_STEP_Y) + " " + \
                                    str(TParser.FRONT_2D) + "\n"
            TParser.PARSE_STRING += "#rx_steps: " + str(TSurveySettings.RX_STEP_X) + \
                                    " " + str(TSurveySettings.RX_STEP_Y) + " " + \
                                    str(TParser.FRONT_2D) + "\n"
        TParser.PARSE_STRING += "\n"
        # Materials
        for single_material in materials:
            TParser.PARSE_STRING += "#material: " + str(single_material.epsilon_r) + " " + \
                str(single_material.sigma) + " " + str(single_material.mu_r) + " " + \
                str(single_material.sigma_mag) + " " + str(single_material.name) + "\n"
        TParser.PARSE_STRING += "\n"
        # Shapes
        for single_shape in shapes:
            if(single_shape.type == "Rectangle"):
                TParser.parse_rectangle(single_shape)
            elif(single_shape.type == "Cylinder"):
                TParser.parse_cylinder(single_shape)
            elif(single_shape.type == "CylinSector"):
                TParser.parse_cylinSector(single_shape)
            elif(single_shape.type == "Polygon"):
                TParser.parse_polygon(single_shape)
            else:
                raise Exception("Invalid shape in shapes' list!")
        # Messages:
        if(TSurveySettings.MESSAGES == "no"):
            TParser.PARSE_STRING += "#messages: n\n"
        # Geometry view
        if(TSurveySettings.GEOM_VIEW == "yes"):
            TParser.PARSE_STRING += "#geometry_view: 0.0 0.0 0.0 " + str(TModel_Size.DOM_X) + \
                                    " " + str(TModel_Size.DOM_Y) + " " + \
                                    str(TParser.THICKNESS_2D) + " " + \
                                    str(TModel_Size.DX) + " " + str(TModel_Size.DY) + \
                                    " " + str(TParser.THICKNESS_2D) + " " + \
                                    TSurveySettings.GEOM_FILE + " n\n"
        # Snapshot
        if(TSurveySettings.SNAPSHOT == "yes"):
            TParser.PARSE_STRING += "#snapshot: 0.0 0.0 0.0 " + str(TModel_Size.DOM_X) + \
                                    " " + str(TModel_Size.DOM_Y) + " " + \
                                    str(TParser.THICKNESS_2D) + " " + \
                                    str(TModel_Size.DX) + " " + str(TModel_Size.DY) + \
                                    " " + str(TParser.THICKNESS_2D) + " " + \
                                    str(TSurveySettings.SNAP_TIME) + " " + \
                                    TSurveySettings.SNAP_FILE + " n\n"
        return TParser.PARSE_STRING

    @staticmethod
    def parse_rectangle(rectangle):
        """
        Introduce a rectangle into the input file.

        :param rectangle: examined rectangle object.
        :type rectangle: TRect
        """
        TParser.PARSE_STRING += "#box: " + str(rectangle.point1_mod.x) + " " + \
                                str(rectangle.point1_mod.y) + " " + str(TParser.FRONT_2D) + \
                                " " + str(rectangle.point2_mod.x) + " " + str(rectangle.point2_mod.y) + \
                                " " + str(TParser.THICKNESS_2D) + " " + rectangle.material + "\n"

    @staticmethod
    def parse_cylinder(cylinder):
        """
        Introduce a cylinder into the input file.

        :param cylinder: examined cylinder object.
        :type cylinder: TCylin
        """
        TParser.PARSE_STRING += "#cylinder: " + str(cylinder.centre_mod.x) + " " + \
                                str(cylinder.centre_mod.y) + " " + str(TParser.FRONT_2D) + \
                                " " + str(cylinder.centre_mod.x) + " " + str(cylinder.centre_mod.y) + \
                                " " + str(TParser.THICKNESS_2D) + " " + str(cylinder.radius_mod) + \
                                " " + str(cylinder.material) + "\n"
    
    @staticmethod
    def parse_cylinSector(cylinSector):
        """
        Introduce a cylinder sector into the input file.

        :param cylinsector: examined cylinder sector object.
        :type cylinsector: TCylinSector
        """
        TParser.PARSE_STRING += "#cylindrical_sector: z " + str(cylinSector.centre_mod.x) + \
                                " " + str(cylinSector.centre_mod.y) + " " + str(TParser.FRONT_2D) + \
                                " " + str(TParser.THICKNESS_2D) + " " + str(cylinSector.radius_mod) + " " + \
                                str(cylinSector.start) + " " + str(cylinSector.extent) + \
                                " " + str(cylinSector.material) + "\n"
    
    @staticmethod
    def parse_polygon(polygon):
        """
        Introduce a polygon into the input file as a series of triangles.

        :param polygon: examined polygon object.
        :type polygon: TPolygon
        """
        # Triangulate the polygon
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
        """
        Divide an input polygon into triangles using triangulate module.

        :param polygon: examined polygon object.
        :type polygon: TPolygon

        :rtype: list
        """
        debug = False
        if(debug):
            from timeit import default_timer as timer
            start = timer()
        try:
            polygon_obj = Polygon(polygon.points_mod)
            edges_monotone = make_monotone(polygon_obj)
            monotone_polygons = split_polygons(polygon_obj, edges_monotone)
            edges_triangles = []
            triangles = []
            for poly in monotone_polygons:
                edges_triangles = triangulate_monotone_polygon(poly)
                triangles += split_polygons(poly, edges_triangles)
        except Exception as message:
            messagebox.showerror("Error while triangulating polygon!", message)
        if(debug):
            end = timer()
            print("n vertices:", len(polygon.points_mod))
            print("elapsed time:", end-start)
        return triangles