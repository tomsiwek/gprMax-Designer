from copy import copy, deepcopy
from decimal import Decimal
import h5py
from math import asin, acos, atan, degrees, sin, cos, radians, log10
import os
from random import randrange
import subprocess
import sys
from tkinter import Tk, Canvas, Menu, messagebox, BooleanVar, Frame, Button, \
                    Toplevel, Text, Label, PanedWindow, PhotoImage, simpledialog, \
                    colorchooser, filedialog, Scrollbar
from tkinter import LEFT, TOP, X, Y, FLAT, RAISED, SUNKEN, ARC, PIESLICE, INSERT, \
                    END, RIGHT, BOTTOM, VERTICAL, N, S, E, W, NS, EW, NSEW, BOTH, \
                    ACTIVE, HORIZONTAL, VERTICAL

from displaysettingswindow import TDisplaySettingsWindow
from echogramwindow import TEchogramWindow
from geometry import TGeometry as TG
from materials import TMaterial
from materialswindow import TMaterialsWindow
from modelsettingswindow import TModelSettingsWindow
from operation import TOperation
from outputpreviewwindow import TOutputPreviewWindow
from parsetofile import TParser
from point import TPoint
from polygonwindow import TPolygonWindow
from settings import TWindow_Size, TModel_Size, TTicksSettings, TSurveySettings
from shapes import TRect, TCylin, TCylinSector, TPolygon, TCoordSys
from shapeswindow import TShapesWindow
from surveysettingswindow import TSurveySettingsWindow
from tracewindow import TTraceWindow


class TApp(object):
    """
    Class represents application as a whole. It handles events.
    """

    # Make this a Frame
    # Change all names of entities regarding shapes as a whole

    # Static (not so) variables
    first_click = False
    first_click_pos = None
    second_click = False
    second_click_pos = None
    resize = False
    resize_const_pos = None
    resize_const_pos2 = None
    resize_shape_num = -1
    resize_start = 0.0
    resize_extent = 0.0
    move = False
    move_const_point = None
    move_shape_num = -1
    move_points = []
    move_const_radius = 0.0
    manipulated_shape_num = -1
    move_start = 0
    move_extent = 0
    polygon_points = []
    double_click = False
    resize_const_points = []
    resize_moving_point = -1
    sector_point_type = ""
    resize_const_radius = 0.0
    shape_buffer = None
    resized_point = None
    AVAILABLE_COLOURS = ("red", "blue", "yellow", "green", "orange", "purple", "indigo", "fuchsia", "white", "navy", "brown")
    scale = 100.0
    len_tot_x = 10.0
    len_tot_y = 10.0

    def __init__ (self, master):
        self.master = master
        master.title("gprMax Designer")

        # Configure grid cells weights
        self.init_grid()

        # Main canvas
        self.init_canvas()

        # Main menu
        self.init_main_menu()

        # Display the menu
        master.config(menu=self.main_menubar)

        # Popup menu
        self.init_popup_menu()

        # Main toolbar
        self.init_main_toolbar()

        # Bind events to methods
        self.bind_canvas_events()

        # Bind events to application 
        self.bind_application_events()
        
        # List of shapes
        self.shapes = []

        # List of materials
        self.materials = []

        # Rectangle drawing parameters
        self.shapes_colour = "black"
        self.shapes_width = 1

        # Grid colour
        self.grid_colour = "grey"

        # Vertices search radius
        self.radius = 10

        # Active mouse operation mode
        self.mouse_mode = "draw"

        # Active drawing mode
        self.mode = "Rectangle"

        # Model's title
        self.title = ""

        # Create coordinate system
        self.coordsys = TCoordSys(self.shapes_colour, self.shapes_width, grid_colour = self.grid_colour)

        self.shapes_frame = TShapesWindow(self.master, self)
        self.shapes_frame.grid(row = 0, column = 1, rowspan = 2, sticky = NSEW)

        self.materials_frame = TMaterialsWindow(self.master, self, self.shapes_frame)
        self.materials_frame.grid(row = 2, column = 1, rowspan = 2, sticky = NSEW)

        self.init_status_bar()

        self.canvas_refresh()

        # Try to load toolbar icons
        self.load_toolbar_icons()

        # Initialize operation queue
        self.operations = []

    def init_grid(self):
        self.master.rowconfigure(1, weight = 1)
        self.master.rowconfigure(2, weight = 1)
        self.master.columnconfigure(0, weight = 1)

    def init_canvas(self):
        "Inits frame containing main canvas and its scrollbars"
        self.canvas_frame = Frame(self.master)
        self.main_canvas = Canvas(self.canvas_frame, width = TWindow_Size.MAX_X, \
                                  height = TWindow_Size.MAX_Y, bd = 0, \
                                  highlightthickness = 0)
        self.main_canvas.configure(background = 'white')
        self.main_horizontal_scrollbar = Scrollbar(self.canvas_frame, \
                                                   orient = HORIZONTAL, \
                                                   command = self.model_horizontal_scroll)
        self.main_horizontal_scrollbar.set(0, 1)
        self.main_vertical_scrollbar = Scrollbar(self.canvas_frame, \
                                                 orient = VERTICAL, \
                                                 command = self.model_vertical_scroll)
        self.main_vertical_scrollbar.set(0, 1)
        self.canvas_frame.rowconfigure(1, weight = 1)
        self.canvas_frame.columnconfigure(1, weight = 1)
        self.main_horizontal_scrollbar.grid(row = 0, column = 1, sticky = EW)
        self.main_vertical_scrollbar.grid(row = 1, column = 0, sticky = NS)
        self.main_canvas.grid(row = 1, column = 1, sticky = NSEW)
        self.canvas_frame.grid(row = 1, column = 0, rowspan = 2, sticky = NSEW)

    def init_main_menu(self):
        self.main_menubar = Menu(self.master)
        self.file_menu = Menu(self.main_menubar, tearoff = 0)
        self.edit_menu = Menu(self.main_menubar, tearoff = 0)
        self.view_menu = Menu(self.main_menubar, tearoff = 0)
        self.settings_menu = Menu(self.main_menubar, tearoff = 0)
        self.file_menu.add_command(label = "Read model file", \
                                   command = self.read_model_file)
        self.file_menu.add_command(label = "Open materials")
        self.file_menu.add_command(label = "Save materials")
        self.file_menu.add_command(label = "Parse to gprMax", command = self.parse_to_gprmax)
        self.file_menu.add_command(label = "Run gprMax in terminal", command = self.run_gprmax_terminal)
        self.file_menu.add_command(label = "Export hdf5 to ascii", command = self.export_hdf5_to_ascii)
        self.file_menu.add_command(label = "Merge traces", command = self.merge_traces)
        self.file_menu.add_command(label = "Plot trace", command = self.display_trace)
        self.file_menu.add_command(label = "Plot echogram", command = self.display_echogram)
        self.file_menu.add_command(label = "Quit!", command = self.master.destroy)
        self.edit_menu.add_command(label = "Undo", command = self.undo_operation)
        self.edit_menu.add_command(label = "Create rectangle", command = self.create_rectangle)
        self.edit_menu.add_command(label = "Create cylinder", command = self.create_cylin)
        self.edit_menu.add_command(label = "Create cylindrical sector", command = self.create_cylin_sector)
        self.edit_menu.add_command(label = "Create polygon", command = self.create_polygon)
        self.edit_menu.add_command(label = "Recolour randomly", command = self.recolour_randomly)
        self.edit_menu.add_command(label = "Delete all", command = self.remove_all_shapes)
        # self.edit_menu.add_command(label = "Refresh_canvas", command = self.canvas_refresh)
        self.view_menu.add_command(label = "Display", command = self.display_settings)
        self.view_menu.add_command(label = "Toogle grid", command = self.toogle_grid)
        self.view_menu.add_command(label = "Zoom in", command = self.view_zoom_in)
        self.view_menu.add_command(label = "Zoom out", command = self.view_zoom_out)
        self.view_menu.add_command(label = "Reset zoom", command = self.view_zoom_reset)
        self.settings_menu.add_command(label = "Edit title", command = self.edit_title)
        self.settings_menu.add_command(label = "Model", command = self.change_model_size)
        self.settings_menu.add_command(label = "Survey", command = self.survey_settings)
        self.main_menubar.add_cascade(label = "File", menu = self.file_menu)
        self.main_menubar.add_cascade(label = "Edit", menu = self.edit_menu)
        self.main_menubar.add_cascade(label = "View", menu = self.view_menu)
        self.main_menubar.add_cascade(label = "Settings", menu = self.settings_menu)

    def init_popup_menu(self):
        # Crates a right-click popup menu
        self.mode_rectangle = BooleanVar()
        self.mode_rectangle.set(True)
        self.mode_cylinder = BooleanVar()
        self.mode_cylinder.set(False)
        self.mode_cylin_sector = BooleanVar()
        self.mode_cylin_sector.set(False)
        self.mode_polygon = BooleanVar()
        self.mode_polygon.set(False)

        self.right_button_popup = Menu(self.master, tearoff = 0)
        
        self.right_button_popup.add_command(label = "Select shape")
        self.right_button_popup.add_command(label = "Edit shape")
        self.right_button_popup.add_command(label = "Change shape colour")
        self.right_button_popup.add_command(label = "Remove shape")
        self.right_button_popup.add_separator()
        self.right_button_popup.add_command(label = "Add vertex to polygon")
        self.right_button_popup.add_command(label = "Edit polygon vertex")
        self.right_button_popup.add_command(label = "Remove polygon vertex")
        self.right_button_popup.add_separator()
        self.right_button_popup.add_command(label = "Copy shape")
        self.right_button_popup.add_command(label = "Paste shape")
        self.right_button_popup.add_separator()
        
        self.right_button_popup.add_checkbutton(label = "Rectangle", \
                                                command = self.set_mode_rectangle, \
                                                onvalue = True, offvalue = False, \
                                                variable = self.mode_rectangle)
        self.right_button_popup.add_checkbutton(label = "Cylinder", command = self.set_mode_cylinder, onvalue = True, \
                                                offvalue = False, variable = self.mode_cylinder)
        self.right_button_popup.add_checkbutton(label = "Cylinder sector", command = self.set_mode_cylin_sector, onvalue = True, \
                                                offvalue = False, variable = self.mode_cylin_sector)
        self.right_button_popup.add_checkbutton(label = "Polygon", command = self.set_mode_polygon, onvalue = True, \
                                                offvalue = False, variable = self.mode_polygon)
    
    def init_main_toolbar(self):
        self.main_toolbar = Frame(self.master, bd = 1, relief = RAISED)
        self.rectangleButton = Button(self.main_toolbar, text = "R", relief=SUNKEN, command = self.set_mode_rectangle)
        self.rectangleButton.grid(row = 0, column = 0, padx=2, pady=2)
        self.cylinderButton = Button(self.main_toolbar, text = "C", relief=FLAT, command = self.set_mode_cylinder)
        self.cylinderButton.grid(row = 0, column = 1, padx=2, pady=2)
        self.cylinSectorButton = Button(self.main_toolbar, text = "S", relief=FLAT, command = self.set_mode_cylin_sector)
        self.cylinSectorButton.grid(row = 0, column = 2, padx=2, pady=2)
        self.polygonButton = Button(self.main_toolbar, text = "P", relief = FLAT, command = self.set_mode_polygon)
        self.polygonButton.grid(row = 0, column = 4, padx=2, pady=2)
        Label(self.main_toolbar, text = "|").grid(row = 0, column = 5, padx=2, pady=2)
        self.draw_button = Button(self.main_toolbar, text = "D", relief = SUNKEN, command = self.set_mouse_mode_draw)
        self.draw_button.grid(row = 0, column = 6, padx = 2, pady = 2)
        self.move_button = Button(self.main_toolbar, text = "M", relief = FLAT, command = self.set_mouse_mode_move)
        self.move_button.grid(row = 0, column = 7, padx = 2, pady = 2)
        self.resize_button = Button(self.main_toolbar, text = "R", relief = FLAT, command = self.set_mouse_mode_resize)
        self.resize_button.grid(row = 0, column = 8, padx = 2, pady = 2)
        Label(self.main_toolbar, text = "|").grid(row = 0, column = 9, padx=2, pady=2)
        self.parseToGprMaxButton = Button(self.main_toolbar, text = "Parse to gprMax", relief = FLAT, command = self.parse_to_gprmax)
        self.parseToGprMaxButton.grid(row = 0, column = 10, padx = 2, pady = 2)
        Label(self.main_toolbar, text = "|").grid(row = 0, column = 11, padx = 2, pady = 2)
        self.zoom_in_button = Button(self.main_toolbar, text = "+", relief = FLAT, command = self.view_zoom_in)
        self.zoom_in_button.grid(row = 0, column = 12, padx = 2, pady = 2)
        self.zoom_out_button = Button(self.main_toolbar, text = "-", relief = FLAT, command = self.view_zoom_out)
        self.zoom_out_button.grid(row = 0, column = 13, padx = 2, pady = 2)
        Label(self.main_toolbar, text = "|").grid(row = 0, column = 14, padx=2, pady=2)
        self.exitButton = Button(self.main_toolbar, text = "Q", relief=FLAT, command = self.master.destroy)
        self.exitButton.grid(row = 0, column = 15, padx=2, pady=2)
        self.main_toolbar.grid(row = 0, column = 0, sticky = EW)

    
    def init_status_bar(self):
        self.status_bar = Frame(self.master, bd = 1)
        self.pos_x_label = Label(self.status_bar, text = "X: -", width = 5, anchor = W)
        self.pos_x_label.grid(row = 0, column = 0)
        self.pos_y_label = Label(self.status_bar, text = "Y: -", width = 5, anchor = W)
        self.pos_y_label.grid(row = 0, column = 1)
        self.status_bar.grid(row = 3, column = 0, sticky = EW)

    def bind_canvas_events(self):
        self.main_canvas.bind("<Button-1>", self.canvas_click)
        self.main_canvas.bind("<Button-3>", self.display_right_button_popup)
        self.main_canvas.bind("<Motion>", self.canvas_mouse_move)
        self.main_canvas.bind("<Double-Button-1>", self.canvas_double_click)
        self.main_canvas.bind("<Configure>", self.canvas_resize)
    
    def bind_application_events(self):
        self.master.bind("<Up>", self.move_cursor_up)
        self.master.bind("<Down>", self.move_cursor_down)
        self.master.bind("<Left>", self.move_cursor_left)
        self.master.bind("<Right>", self.move_cursor_right)
        self.master.bind("<Control-Key-z>", self.undo_operation)
        self.master.bind("<Control-Key-c>", self.copy_ctrl_c)
        self.master.bind("<Control-Key-v>", self.paste_ctrl_v)

    def load_toolbar_icons(self):
        try:
            self.rectangleIcon = PhotoImage (file = "./icons/icon_rectangle.gif")
            self.cylinderIcon = PhotoImage (file = "./icons/icon_cylinder.gif")
            self.cylinSectorIcon = PhotoImage (file = "./icons/icon_cylinder_sector.gif")
            self.polygonIcon = PhotoImage (file = "./icons/icon_polygon.gif")
            self.exitIcon = PhotoImage (file = "./icons/icon_exit.gif")
            self.rectangleButton.config (image = self.rectangleIcon)
            self.cylinderButton.config (image = self.cylinderIcon)
            self.cylinSectorButton.config (image = self.cylinSectorIcon)
            self.polygonButton.config (image = self.polygonIcon)
            self.exitButton.config (image = self.exitIcon)
        except Exception as message:
            messagebox.showerror ("Error while loading icons", message)
        
    def canvas_refresh(self, *, swap = False):
        "Redraw all shapes on canvas"
        for single_shape in self.shapes:
            single_shape.draw(self.main_canvas)
        if(not self.move and not self.resize):
            self.shapes_frame.update_list(self.shapes, swap = swap)
        self.coordsys.draw(self.main_canvas)
        self.coordsys.draw_ticks(self.main_canvas)
        self.coordsys.obscure_protruding_edges(self.main_canvas)
        self.coordsys.write_axis_labels(self.main_canvas)
                         
    def canvas_click(self, event):
        "Left mouse click event "
        self.main_canvas.focus_force()
        min_window = TPoint(TWindow_Size.BOX_MIN_X, TWindow_Size.BOX_MIN_Y)
        max_window = TPoint(TWindow_Size.BOX_MAX_X, TWindow_Size.BOX_MAX_Y)
        in_model = TG.position_in_boundries(TPoint(event.x, event.y), \
                                            min_window, max_window)
        if(in_model):
            if(self.mouse_mode == "draw"):
                self.draw_click(event)
            elif(self.mouse_mode == "move"):
                self.move_click(event)
            elif(self.mouse_mode == "resize"):
                self.resize_click(event)
            else:
                raise Exception("Invalid mouse working mode!")
    
    def canvas_mouse_move(self, event):
        "Mouse move event"
        if(self.mouse_mode == "draw"):
            self.draw_mouse_move(event)
        elif(self.mouse_mode == "move"):
            self.move_mouse_move(event)
        elif(self.mouse_mode == "resize"):
            self.resize_mouse_move(event)
        else:
            raise Exception("Invalid mouse working mode!")
        # Display mouse cursor's position
        self.display_mouse_position(event)

    def display_mouse_position(self, event):
        min_model = TPoint(TModel_Size.MIN_X, TModel_Size.MIN_Y)
        max_model = TPoint(TModel_Size.MAX_X, TModel_Size.MAX_Y)
        min_window = TPoint(TWindow_Size.BOX_MIN_X, TWindow_Size.BOX_MIN_Y)
        max_window = TPoint(TWindow_Size.BOX_MAX_X, TWindow_Size.BOX_MAX_Y)
        if(TG.position_in_boundries(TPoint(event.x, event.y), \
                                    min_window, max_window)):
            dx = TModel_Size.DX
            dy = TModel_Size.DY
            mouse_pos_mod = TG.window_to_model(TPoint(event.x, event.y), min_model, \
                                               max_model, min_window, max_window, \
                                               dx, dy)
            self.pos_x_label.config(text = "X: " + str (mouse_pos_mod.x) )
            self.pos_y_label.config(text = "Y: " + str (mouse_pos_mod.y) )
        else:
            self.pos_x_label.config(text = "X: -" )
            self.pos_y_label.config(text = "Y: -" )
            
    def remove_all_shapes(self):
        "Removes all shapes"
        # Register every single deletion operation in stack
        for i, single_shape in enumerate(self.shapes):
            self.operations.append(TOperation("remove_all", shape = deepcopy(single_shape), \
                                              num = i))
        self.shapes = []
        self.main_canvas.delete("all")
        self.canvas_refresh()

    def remove_top_shape(self):
        "Right mouse button click event"
        try:
            self.shapes.pop()
        except IndexError:
            messagebox.showerror("Error!", "There are no shapes!")
        self.main_canvas.delete("all")
        self.canvas_refresh()
    
    def remove_shape(self, event):
        "Remove shape if mouse overlapses it"
        shape_num = self.mouse_overlaps_shape(event.x, event.y, self.radius)
        if(shape_num > -1):
            try:
                self.operations.append(TOperation("remove", shape = deepcopy(self.shapes[shape_num]), \
                                                  num = shape_num))
                del self.shapes[shape_num]
            except ValueError:
                messagebox.showerror("Error!", "Something went wrong while manipulating shapes list")
            else:
                self.main_canvas.delete("all")
                self.canvas_refresh()

    def toogle_grid (self):
        if (self.coordsys.grid):
            self.coordsys.toogle_grid ("Off")
        else:
            self.coordsys.toogle_grid ("On")
        self.main_canvas.delete ("all")
        self.canvas_refresh ()

    # Keyboard up arrow press event
    def increase_shapes_width(self, event):
        self.shapes_width += 1
        for single_rectangle in self.shapes:
            single_rectangle.width = self.shapes_width

        self.main_canvas.delete("all")
        self.canvas_refresh ()
            
    # Keyboard down arrow press event
    def decrease_shapes_width(self, event):
        self.shapes_width -= 1
        for single_rectangle in self.shapes:
            single_rectangle.width = self.shapes_width

        self.main_canvas.delete("all")
        self.canvas_refresh()

    # Property fot self.shapes_width
    @property
    def shapes_width (self):
        return self.__rectangles_width

    # Setter for self.rectangles_width 
    @shapes_width.setter
    def shapes_width (self, shapes_width):
        if (shapes_width <= 5 and shapes_width >= 1):
            self.__rectangles_width = shapes_width
        else:
            self.__rectangles_width = self.__rectangles_width
    
    # Checks whether mouse pointer overlaps a shape
    def mouse_overlaps_shape(self, x, y, radius):
        shape_num = -1
        for single_shape in self.shapes:
            shape_num += 1
            if(single_shape.type == "Rectangle"):
                if(self.mouse_overlaps_rectangle(self.shapes[shape_num], \
                                                 x, y, radius)):
                    return shape_num
            elif(single_shape.type == "Cylinder"):
                if(self.mouse_overlaps_cylinder(self.shapes[shape_num], \
                                                x, y, radius)):
                    return shape_num
            elif(single_shape.type == "CylinSector"):
                if(self.mouse_overlaps_cylinder_sector(self.shapes[shape_num], \
                                                       x, y, radius)):
                    return shape_num
            elif(single_shape.type == "Triangle"):
                if(self.mouse_overlaps_triangle(self.shapes[shape_num], \
                                                x, y, radius)): 
                    return shape_num
            elif(single_shape.type == "Polygon"):
                if(self.mouse_overlaps_polygon(self.shapes[shape_num], \
                                               x, y, radius)): 
                    return shape_num
        return -1

    # Check wether mouse overlaps rectangle
    def mouse_overlaps_rectangle(self, shape, x, y, radius):
        if((x >= shape.point1.x - radius and x <= shape.point1.x + radius \
            and y >= shape.point1.y - radius and y <= shape.point1.y + radius) or \
            (x >= shape.point2.x - radius and x <= shape.point2.x + radius \
            and y >= shape.point2.y - radius and y <= shape.point2.y + radius)):
            return True
        return False
    
    # Check wether mouse overlaps cylinder
    def mouse_overlaps_cylinder(self, shape, x, y, radius):
        if(((x - shape.centre.x)**2 + (y - shape.centre.y)**2 >= (shape.radius - radius)**2 and \
            (x - shape.centre.x)**2 + (y - shape.centre.y)**2 <= (shape.radius + radius)**2  ) or\
            (x >= shape.centre.x - radius and x <= shape.centre.x + radius \
            and y >= shape.centre.y - radius and y <= shape.centre.y + radius)):
            return True
        return False
    
    # Check wether mouse overlaps cylinder sector
    def mouse_overlaps_cylinder_sector(self, shape, x, y, radius):
        if((x <= shape.centre.x + radius and x >= shape.centre.x - radius \
            and y <= shape.centre.y + radius and y >= shape.centre.y - radius) or\
            (x <= shape.boundary_pt1.x + radius and x >= shape.boundary_pt1.x - radius \
            and y <= shape.boundary_pt1.y + radius and y >= shape.boundary_pt1.y - radius) or\
            (x <= shape.boundary_pt2.x + radius and x >= shape.boundary_pt2.x - radius \
            and y <= shape.boundary_pt2.y + radius and y >= shape.boundary_pt2.y - radius)):
            return True
        return False
    
    # Check wether mouse overlaps triangle
    def mouse_overlaps_triangle (self, shape, x, y, radius):
        if ( (x <= shape.point1.x + radius and x >= shape.point1.x - radius \
            and y <= shape.point1.y + radius and y >= shape.point1.y - radius) or\
            (x <= shape.point2.x + radius and x >= shape.point2.x - radius \
            and y <= shape.point2.y + radius and y >= shape.point2.y - radius) or\
            (x <= shape.point3.x + radius and x >= shape.point3.x - radius \
            and y <= shape.point3.y + radius and y >= shape.point3.y - radius) ):
            return True
        return False
    
    # Check wether mouse overlaps polygon
    def mouse_overlaps_polygon(self, shape, x, y, radius):
        for pt in shape.points:
            if (x <= pt.x + radius and x >= pt.x - radius \
                and y <= pt.y + radius and y >= pt.y - radius):
                return True
        return False

    # Displays right mouse button popup (context) menu
    def display_right_button_popup(self, event):
        self.canvas_interrupt()
        try:
            self.right_button_popup.entryconfig("Select shape", command = lambda: \
                                                self.select_shape(event))
            self.right_button_popup.entryconfig("Edit shape", command = lambda: \
                                                self.edit_shape(event))
            self.right_button_popup.entryconfig("Change shape colour", command = \
                                                lambda: self.change_shape_colour(event))
            self.right_button_popup.entryconfig("Remove shape", command = lambda: \
                                                self.remove_shape(event))
            self.right_button_popup.entryconfig("Add vertex to polygon", command = \
                                                lambda: self.add_vertex_to_polygon(event))
            self.right_button_popup.entryconfig("Edit polygon vertex", command = \
                                                lambda: self.edit_polygon_vertex(event))
            self.right_button_popup.entryconfig("Remove polygon vertex", command = \
                                                lambda: self.remove_polygon_vertex(event))
            self.right_button_popup.entryconfig("Copy shape", command = lambda: \
                                                self.copy_shape(event))
            self.right_button_popup.entryconfig("Paste shape", command = lambda: \
                                                self.paste_shape(event))
            self.right_button_popup.post(event.x_root, event.y_root)
        finally:
            self.right_button_popup.grab_release()
    
    def set_mode_rectangle(self):
        self.mode = "Rectangle"
        self.mode_rectangle.set(True)
        self.mode_cylinder.set(False)
        self.mode_cylin_sector.set(False)
        # self.mode_triangle.set (False)
        self.mode_polygon.set(False)
        self.rectangleButton.config(relief = SUNKEN)
        self.cylinderButton.config(relief = FLAT)
        self.cylinSectorButton.config(relief = FLAT)
        # self.triangleButton.config (relief = FLAT)
        self.polygonButton.config(relief = FLAT)
    
    def set_mode_cylinder (self):
        self.mode = "Cylinder"
        self.mode_rectangle.set (False)
        self.mode_cylinder.set (True)
        self.mode_cylin_sector.set (False)
        # self.mode_triangle.set (False)
        self.mode_polygon.set (False)
        self.rectangleButton.config (relief = FLAT)
        self.cylinderButton.config (relief = SUNKEN)
        self.cylinSectorButton.config (relief = FLAT)
        # self.triangleButton.config (relief = FLAT)
        self.polygonButton.config (relief = FLAT)

    def set_mode_cylin_sector (self):
        self.mode = "CylinSector"
        self.mode_rectangle.set (False)
        self.mode_cylinder.set (False)
        self.mode_cylin_sector.set (True)
        # self.mode_triangle.set (False)
        self.mode_polygon.set (False)
        self.rectangleButton.config (relief = FLAT)
        self.cylinderButton.config (relief = FLAT)
        self.cylinSectorButton.config (relief = SUNKEN)
        # self.triangleButton.config (relief = FLAT)
        self.polygonButton.config (relief = FLAT)
    
    def set_mode_triangle (self):
        self.mode = "Triangle"
        self.mode_rectangle.set (False)
        self.mode_cylinder.set (False)
        self.mode_cylin_sector.set (False)
        # self.mode_triangle.set (True)
        self.mode_polygon.set (False)
        self.rectangleButton.config (relief = FLAT)
        self.cylinderButton.config (relief = FLAT)
        self.cylinSectorButton.config (relief = FLAT)
        # self.triangleButton.config (relief = SUNKEN)
        self.polygonButton.config (relief = FLAT)

    def set_mode_polygon(self):
        self.mode = "Polygon"
        self.mode_rectangle.set(False)
        self.mode_cylinder.set(False)
        self.mode_cylin_sector.set(False)
        # self.mode_triangle.set (False)
        self.mode_polygon.set(True)
        self.rectangleButton.config(relief = FLAT)
        self.cylinderButton.config(relief = FLAT)
        self.cylinSectorButton.config(relief = FLAT)
        # self.triangleButton.config (relief = FLAT)
        self.polygonButton.config(relief = SUNKEN)

    def set_mouse_mode_draw(self):
        self.mouse_mode = "draw"
        self.draw_button.config(relief = SUNKEN)
        self.move_button.config(relief = FLAT)
        self.resize_button.config(relief = FLAT)

    def set_mouse_mode_move(self):
        self.mouse_mode = "move"
        self.draw_button.config(relief = FLAT)
        self.move_button.config(relief = SUNKEN)
        self.resize_button.config(relief = FLAT)

    def set_mouse_mode_resize(self):
        self.mouse_mode = "resize"
        self.draw_button.config(relief = FLAT)
        self.move_button.config(relief = FLAT)
        self.resize_button.config(relief = SUNKEN)

    def canvas_double_click(self, event):
        if(self.mouse_mode == "draw" and self.mode == "Polygon"):
            self.polygon_double_click_draw(event)

    def assign_material_to_shape(self, shape_num, material):
        self.shapes [shape_num].material = str(material)
    
    def parse_to_gprmax(self):
        "Parses model created in program to gprMax compliant text file"
        parser_string = TParser.parse_shapes(self.materials, self.shapes, self.title)
        preview_window = TOutputPreviewWindow(self.master, parser_string)
        output_file_name = preview_window.result
        if(output_file_name is not None):
            self.run_gprmax(filename = output_file_name)
    
    def change_model_size(self):
        input_dialog = TModelSettingsWindow(self.master, TModel_Size.DOM_X, \
                                            TModel_Size.DOM_Y, TModel_Size.DX, \
                                            TModel_Size.DY)
        result = input_dialog.result
        if (result != None):
            try:
                TModel_Size.DOM_X = result[0]
                TModel_Size.DOM_Y = result[1]
                TModel_Size.DX = result[2]
                TModel_Size.DY = result[3]
                self.len_tot_x = result[0]
                self.len_tot_y = result[1]
                TModel_Size.MIN_X = 0.0
                TModel_Size.MIN_Y = 0.0
                TModel_Size.MAX_X = TModel_Size.DOM_X
                TModel_Size.MAX_Y = TModel_Size.DOM_Y
                self.view_zoom_reset()
            except Exception as message:
                messagebox.showerror("Error while changing model size!", message)
    
    def canvas_resize(self, event):
        # Resize canvas, should the window resize occur
        try:
            TWindow_Size.MAX_X = event.width
            TWindow_Size.MAX_Y = event.height
            self.coordsys.window_size_update()
            for single_shape in self.shapes:
                single_shape.update_window_positions()
            self.main_canvas.delete("all")
            self.canvas_refresh()
        except Exception as message:
            messagebox.showerror("Error while changing canvas size!", message)
    
    def display_settings (self):
        input_dialog = TDisplaySettingsWindow(self.master, TTicksSettings.INT_X, \
                                              TTicksSettings.INT_Y, \
                                              TTicksSettings.ROUND_DIGITS, \
                                              TModel_Size.MIN_X, TModel_Size.MIN_Y, \
                                              TModel_Size.MAX_X, TModel_Size.MAX_Y)
        result = input_dialog.result
        if(result != None):
            try:
                TTicksSettings.INT_X = result[0]
                TTicksSettings.INT_Y = result[1]
                TTicksSettings.ROUND_DIGITS = result[2]
                TModel_Size.MIN_X = result[3]
                TModel_Size.MIN_Y = result[4]
                TModel_Size.MAX_X = result[5]
                TModel_Size.MAX_Y = result[6]
                self.coordsys.model_size_update()
                self.coordsys.window_size_update()
                for single_shape in self.shapes:
                    single_shape.update_window_positions()
                self.coordsys.display_settings_update()
                self.main_canvas.delete("all")
                self.canvas_refresh()
            except Exception as message:
                messagebox.showerror("Error while adjusting display settings!", message)
    
    def remove_polygon_vertex(self, event):
        "Provisional version. Must be rewritten."
        shape_num = self.mouse_overlaps_shape (event.x, event.y, self.radius)
        if (shape_num > -1):
            if (self.shapes [shape_num].type == "Polygon"):
                self.operations.append(TOperation("edit", shape = deepcopy(self.shapes[shape_num]), \
                                                  num = shape_num))
                for i, pt in enumerate(self.shapes[shape_num].points):
                    if (event.x <= pt.x + self.radius and event.x >= pt.x - self.radius \
                        and event.y <= pt.y + self.radius and event.y >= pt.y - self.radius):
                        break
                self.shapes [shape_num].remove_vertex (i)
                self.main_canvas.delete ("all")
                self.canvas_refresh ()

    def canvas_interrupt(self):
        self.first_click = False
        self.second_click = False
        self.resize = False
        self.move = False
        self.double_click = False
        self.move_points = []
        self.polygon_points = []
        self.resize_const_points = []
        self.resize_shape_num = -1
        self.manipulated_shape_num = -1
        self.resize_moving_point = -1
        self.main_canvas.config(cursor = "arrow")
        self.main_canvas.delete("all")
        self.copy_pos = None
        # self.canvas_refresh()
        if(self.mouse_mode == "move" or self.mouse_mode == "resize"):
            if(self.shape_buffer is not None):
                self.shapes.append(self.shape_buffer)
                self.shape_buffer = None
                self.main_canvas.delete("all")
        self.canvas_refresh()

    def create_rectangle(self):
        input_str = simpledialog.askstring("Input coordinates", "Give rectangle's coordinates")
        try:
            tokens = input_str.split()
            xs = [float (x) for x in tokens[0::2] ]
            ys = [float (y) for y in tokens[1::2] ]
            points = [TPoint (x, y) for x, y in zip (xs, ys) ]
            self.shapes.append (TRect (point1_mod = points [0], point2_mod = points [1], \
                colour = self.shapes_colour, width = self.shapes_width))
            self.main_canvas.delete("all")
            self.canvas_refresh()
        except Exception as message:
            messagebox.showerror("Error while creating rectangle!", message)
        else:
            self.operations.append(TOperation("draw", shape = deepcopy(self.shapes[-1]), \
                                              num = len(self.shapes) - 1))

    def create_cylin(self):
        input_str = simpledialog.askstring("Input coordinates", "Give cylinder's centre coordinates and radius")
        try:
            tokens = input_str.split()
            centre = TPoint(float(tokens[0]), float(tokens[1]))
            radius = float(tokens[2])
            self.shapes.append(TCylin(centre_mod = centre, radius_mod = radius, \
                                      colour = self.shapes_colour, width = self.shapes_width))
            self.main_canvas.delete("all")
            self.canvas_refresh()
        except Exception as message:
            messagebox.showerror("Error while creating cylinder!", message)
        else:
            self.operations.append(TOperation("draw", shape = deepcopy(self.shapes[-1]), \
                                              num = len(self.shapes) - 1))

    def create_cylin_sector(self):
        input_str = simpledialog.askstring ("Input coordinates", "Give cylinder sector's centre coordinates,\nradius, start and extent angles")
        try:
            tokens = input_str.split ()
            centre = TPoint (float (tokens [0] ), float(tokens [1] ) )
            radius = float(tokens[2])
            start =  float(tokens[3])
            extent = float(tokens[4])
            self.shapes.append (TCylinSector (centre_mod = centre, radius_mod = radius, start = start, extent = extent, \
                colour = self.shapes_colour, width = self.shapes_width) )
            self.main_canvas.delete ("all")
            self.canvas_refresh ()
        except Exception as message:
            messagebox.showerror("Error while creating polygon!", message)
        else:
            self.operations.append(TOperation("draw", shape = deepcopy(self.shapes[-1]), \
                                              num = len(self.shapes) - 1))

    def create_polygon(self):
        input_str = simpledialog.askstring("Input coordinates", "Give polygon's coordinates")
        try:
            tokens = input_str.split()
            xs = [float(x) for x in tokens[0::2] ]
            ys = [float(y) for y in tokens[1::2] ]
            points = [TPoint(x, y) for x, y in zip(xs, ys)]
            self.shapes.append(TPolygon(points_mod = points, \
                                        colour = self.shapes_colour, \
                                        width = self.shapes_width))
            self.main_canvas.delete("all")
            self.canvas_refresh()
        except Exception as message:
            messagebox.showerror("Error while creating polygon!", message)
        else:
            self.operations.append(TOperation("draw", shape = deepcopy(self.shapes[-1]), \
                                              num = len(self.shapes) - 1))
        
    def edit_title(self):
        self.title = simpledialog.askstring("Title", "Give model's title")
        if(self.title):
            self.master.title("gprMax Designer: " + self.title)

    def recolour_randomly(self):
        num_of_colours = len(self.AVAILABLE_COLOURS)
        for single_shape in self.shapes:
            random_index = randrange(0, num_of_colours)
            single_shape.fill = self.AVAILABLE_COLOURS[random_index]
        self.main_canvas.delete("all")
        self.canvas_refresh()

    def select_shape(self, event):
        shape_num = self.mouse_overlaps_shape(event.x, event.y, self.radius)
        if (shape_num > -1):
            try:
                for single_shape in self.shapes:
                    single_shape.width = 1
                self.shapes [shape_num].width = 2
                self.main_canvas.delete("all")
                self.canvas_refresh()
                self.select_shape_on_list(shape_num)
            except Exception as message:
                messagebox.showerror("Error!", message)
    
    def select_shape_on_list(self, shape_num):
        self.shapes_frame.material_box.set(str(self.shapes[shape_num].material))
        self.shapes_frame.shapes_list.select_clear(0, END)
        self.shapes_frame.shapes_list.selection_set(shape_num)
        self.shapes_frame.shapes_list.activate(shape_num)

    def survey_settings(self):
        input_dialog = TSurveySettingsWindow(self.master, self)
        result = input_dialog.result
        if(result):
            TSurveySettings.TYPE = result[0]
            TSurveySettings.DT = result[1]
            TSurveySettings.TIME_WINDOW = result[2]
            TSurveySettings.WAVE_TYPE = result[3]
            TSurveySettings.AMPLITUDE = result[4]
            TSurveySettings.FREQUENCY = result[5]
            TSurveySettings.SRC_TYPE = result[6]
            TSurveySettings.SRC_X = result[7]
            TSurveySettings.SRC_Y = result[8]
            TSurveySettings.RX_X = result[9]
            TSurveySettings.RX_Y = result[10]
            if(result[0] == "rx_array"):
                TSurveySettings.RX_STEP_X = result[11]
                TSurveySettings.RX_STEP_Y = result[12]
                TSurveySettings.RX_MAX_X = result[13]
                TSurveySettings.RX_MAX_Y = result[14]
            elif(result[0] == "bscan"):
                TSurveySettings.SRC_STEP_X = result[11]
                TSurveySettings.SRC_STEP_Y = result[12]
                TSurveySettings.RX_STEP_X = result[13]
                TSurveySettings.RX_STEP_Y = result[14]
    
    def edit_shape(self, event):
        shape_num = self.mouse_overlaps_shape(event.x, event.y, self.radius)
        if(shape_num > -1):
            self.select_shape(event)
            self.operations.append(TOperation("edit", shape = deepcopy(self.shapes[shape_num]), \
                                              num = shape_num))
            if(self.shapes[shape_num].type == "Rectangle"):
                self.edit_rectangle(shape_num)
            elif(self.shapes[shape_num].type == "Cylinder"):
                self.edit_cylin(shape_num)
            elif(self.shapes[shape_num].type == "CylinSector"):
                self.edit_cylin_sector(shape_num)
            elif(self.shapes[shape_num].type == "Polygon"):
                self.edit_polygon(shape_num)
    
    def edit_rectangle(self, shape_num):
        initialvalue = str(self.shapes[shape_num].point1_mod.x) + " " + str(self.shapes[shape_num].point1_mod.y) + " " + \
                       str(self.shapes[shape_num].point2_mod.x) + " " + str(self.shapes[shape_num].point2_mod.y)
        input_str = simpledialog.askstring("Input coordinates", "Give rectangles's coordinates", initialvalue = initialvalue)
        fill = self.shapes[shape_num].fill
        try:
            point1_mod_x, point1_mod_y, point2_mod_x, point2_mod_y =  [float(x) for x in input_str.split ()]
            del self.shapes[shape_num]
            self.shapes.insert(shape_num, TRect(point1_mod = TPoint(point1_mod_x, point1_mod_y), \
                                                point2_mod = TPoint(point2_mod_x, point2_mod_y), \
                                                colour = self.shapes_colour, width = self.shapes_width + 1,\
                                                fill = fill))
            self.main_canvas.delete("all")
            self.canvas_refresh()
            self.select_shape_on_list(shape_num)
        except Exception as message:
            messagebox.showerror("Error while editing rectangle!", message)
    
    def edit_cylin(self, shape_num):
        initialvalue = str(self.shapes[shape_num].centre_mod.x) + " " + str(self.shapes[shape_num].centre_mod.y) + " " + \
                       str(self.shapes[shape_num].radius_mod)
        fill = self.shapes[shape_num].fill
        input_str = simpledialog.askstring("Input coordinates", "Give cylinder's coordinates", initialvalue = initialvalue)
        try:
            point1_mod_x, point1_mod_y, radius_mod =  [float(x) for x in input_str.split ()]
            del self.shapes[shape_num]
            self.shapes.insert(shape_num, TCylin(centre_mod = TPoint(point1_mod_x, point1_mod_y), \
                                                 radius_mod = radius_mod, colour = self.shapes_colour, \
                                                 width = self.shapes_width + 1, fill = fill))
            self.main_canvas.delete("all")
            self.canvas_refresh()
            self.select_shape_on_list(shape_num)
        except Exception as message:
            messagebox.showerror("Error while editing cylinder!", message)
    
    def edit_cylin_sector(self, shape_num):
        initialvalue = str(self.shapes[shape_num].centre_mod.x) + " " + str(self.shapes[shape_num].centre_mod.y) + " " + \
                       str(self.shapes[shape_num].radius_mod) + " " + str(self.shapes[shape_num].start) + " " + \
                       str(self.shapes[shape_num].extent)
        fill = self.shapes[shape_num].fill
        input_str = simpledialog.askstring("Input coordinates", "Give cylinder sector's coordinates", initialvalue = initialvalue)
        try:
            point1_mod_x, point1_mod_y, radius_mod, start, extent =  [float(x) for x in input_str.split ()]
            del self.shapes[shape_num]
            self.shapes.insert(shape_num, TCylinSector(centre_mod = TPoint(point1_mod_x, point1_mod_y), \
                                                       radius_mod = radius_mod, start = start, extent = extent, \
                                                       colour = self.shapes_colour, width = self.shapes_width + 1, fill = fill))
            self.main_canvas.delete("all")
            self.canvas_refresh()
            self.select_shape_on_list(shape_num)
        except Exception as message:
            messagebox.showerror("Error while editing cylinder sector!", message)

    def edit_polygon(self, shape_num):
        "Displays polygon vertices coordinates and enables to change them manually"
        vertices_dialog = TPolygonWindow(self.master, self, self.shapes[shape_num])
        self.select_shape_on_list(shape_num) 
        # initialvalue = " ".join([str(pt.x) + " " + str(pt.y) for pt in self.shapes[shape_num].points_mod])
        # fill = self.shapes[shape_num].fill
        # input_str = simpledialog.askstring("Input coordinates", "Give polygon coordinates", initialvalue = initialvalue)
        # try:
        #     tokens = input_str.split()
        #     points_mod = [TPoint(float(x), float(y)) for x, y in zip(tokens[::2], tokens[1::2])]
        #     del self.shapes[shape_num]
        #     self.shapes.insert(shape_num, \
        #                        TPolygon(points_mod = points_mod, \
        #                                 colour = self.shapes_colour, \
        #                                 width = self.shapes_width + 1, \
        #                                 fill = fill))
        #     self.main_canvas.delete("all")
        #     self.canvas_refresh()
        #     self.select_shape_on_list(shape_num)
        # except Exception as message:
        #     messagebox.showerror("Error while editing polygon!", message)
    
    def change_shape_colour(self, event = None, shape_num = None):
        if(shape_num is None):
            shape_num = self.mouse_overlaps_shape(event.x, event.y, self.radius)
        if(shape_num > -1):
            if(event is not None):
                self.select_shape(event)
            _, hx = colorchooser.askcolor()
            self.shapes[shape_num].fill = hx
            self.main_canvas.delete("all")
            self.canvas_refresh()

    # --------------------------------------------------------------------------

    def edit_polygon_vertex(self, event):
        """Ask for new coordinates of a selected polygon vertex
        Provisional version. Must be rewritten."""
        shape_num = self.mouse_overlaps_shape (event.x, event.y, self.radius)
        if(shape_num > -1):
            self.select_shape(event)
            self.operations.append(TOperation("edit", shape = deepcopy(self.shapes[shape_num]), \
                                              num = shape_num))
            if(self.shapes [shape_num].type == "Polygon"):
                for i, pt in enumerate(self.shapes[shape_num].points):
                    if (event.x <= pt.x + self.radius and event.x >= pt.x - self.radius \
                        and event.y <= pt.y + self.radius and event.y >= pt.y - self.radius):
                        break
                initialvalue = str(self.shapes[shape_num].points_mod[i].x) + " " + str(self.shapes[shape_num].points_mod[i].y)
                input_str = simpledialog.askstring("Input coordinates", "Give polygons vertex's coordinates", initialvalue = initialvalue)
                try:
                    x, y = [float(x) for x in input_str.split()]
                    self.shapes[shape_num].edit_vertex(vertex_num = i, x = x, y = y)
                except Exception as message:
                    messagebox.showerror("Error while manipulating vertex", message)
                self.main_canvas.delete ("all")
                self.canvas_refresh ()
                self.select_shape_on_list(shape_num)
    
    def add_vertex_to_polygon(self, event):
        "Add signle vertex to polygon based on current mouse position"
        try:
            shape_num = self.shapes_frame.shapes_list.curselection()[0]
        except:
            shape_num = -1
        else:
            if(self.shapes[shape_num].type == "Polygon" and shape_num > -1):
                self.operations.append(TOperation("edit", shape = deepcopy(self.shapes[shape_num]), \
                                                  num = shape_num))
                self.shapes[shape_num].add_vertex(x = event.x, y = event.y)
            self.main_canvas.delete("all")
            self.canvas_refresh()
    
    # --------------------------------------------------------------------------
    
    def overlap_coord(self, shape, x, y, radius):
        "Return coordinates of shapes's characteristic point or vertex overlaped by mouse"
        if(shape.type == "Rectangle"):
            return self.rectangle_overlap_coord(shape, x, y, radius)
        elif(shape.type == "Cylinder"):
            try:
                return self.cylinder_overlap_coord(shape, x, y, radius)
            except:
                return TPoint(x, y)
        elif(shape.type == "CylinSector"):
            return self.cylin_sector_overlap_coord(shape, x, y, radius)
        elif(shape.type == "Polygon"):
            return self.polygon_overlap_coord(shape, x, y, radius)
    
    def rectangle_overlap_coord(self, shape, x, y, radius):
        "Return coordinates of rectangle's vertex overlaped by mouse"
        if(x >= shape.point1.x - radius and x <= shape.point1.x + radius \
           and y >= shape.point1.y - radius and y <= shape.point1.y + radius):
            return deepcopy(shape.point1)
        elif(x >= shape.point2.x - radius and x <= shape.point2.x + radius \
             and y >= shape.point2.y - radius and y <= shape.point2.y + radius):
            return deepcopy(shape.point2)

    def cylinder_overlap_coord(self, shape, x, y, radius):
        "Return coordinates of cylinder's characteristic point overlaped by mouse"
        if(x >= shape.centre.x - radius and x <= shape.centre.x + radius \
           and y >= shape.centre.y - radius and y <= shape.centre.y + radius):
            return deepcopy(shape.centre)
        elif(x >= shape.centre.x + shape.radius - radius and \
             x <= shape.centre.x + shape.radius + radius and \
             y >= shape.centre.y - radius and y <= shape.centre.y + radius):
             return TPoint(shape.centre.x + shape.radius, shape.centre.y)
        elif(x >= shape.centre.x - shape.radius - radius and \
             x <= shape.centre.x - shape.radius + radius and \
             y >= shape.centre.y - radius and y <= shape.centre.y + radius):
             return TPoint(shape.centre.x - shape.radius, shape.centre.y)
        elif(x >= shape.centre.x - radius and x <= shape.centre.x  + radius and \
             y >= shape.centre.y + shape.radius - radius and \
             y <= shape.centre.y + shape.radius + radius):
             return TPoint(shape.centre.x, shape.centre.y + shape.radius)
        elif(x >= shape.centre.x - radius and x <= shape.centre.x  + radius and \
             y >= shape.centre.y - shape.radius - radius and \
             y <= shape.centre.y - shape.radius + radius):
             return TPoint(shape.centre.x, shape.centre.y - shape.radius)
        else:
            raise Exception("Can't stick to circle's edge")
    
    def cylin_sector_overlap_coord(self, shape, x, y, radius):
        "Return coordinates of cylinder sector's characteristic point overlaped by mouse"
        if(x >= shape.centre.x - radius and x <= shape.centre.x + radius \
           and y >= shape.centre.y - radius and y <= shape.centre.y + radius):
            return deepcopy(shape.centre)
        elif(x >= shape.boundary_pt1.x - radius and x <= shape.boundary_pt1.x + radius \
             and y >= shape.boundary_pt1.y - radius and y <= shape.boundary_pt1.y + radius):
            return deepcopy(shape.boundary_pt1)
        elif(x >= shape.boundary_pt2.x - radius and x <= shape.boundary_pt2.x + radius \
             and y >= shape.boundary_pt2.y - radius and y <= shape.boundary_pt2.y + radius):
            return deepcopy(shape.boundary_pt2)
    
    def polygon_overlap_coord(self, shape, x, y, radius):
        "Return coordinates of polygon's vertex overlaped by mouse"
        for pt in shape.points:
            if(x >= pt.x - radius and x <= pt.x + radius \
               and y >= pt.y - radius and y <= pt.y + radius):
                return deepcopy(pt)
    
    # --------------------------------------------------------------------------

    def draw_click(self, event):
        "Click event while active mouse working mode is set to 'draw'"
        overlap_num = self.mouse_overlaps_shape(event.x, event.y, self.radius)
        if(self.mode == "Rectangle"):
            self.rectangle_click_draw(event, overlap_num)
        elif(self.mode == "Cylinder"):
            self.cylinder_click_draw(event, overlap_num)
        elif(self.mode == "CylinSector"):
            self.cylin_sector_click_draw(event, overlap_num)
        elif(self.mode == "Polygon"):
            self.polygon_click_draw(event, overlap_num)
        else:
            raise NotImplementedError("Invalid shape type")
    
    def rectangle_click_draw(self, event, overlap_num = -1):
        "Click event while active mouse working mode is set to 'draw' and shape mode is set to 'Rectangle'"
        if(not self.first_click):
            if(overlap_num > -1):
                self.first_click_pos = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
            else:
                self.first_click_pos = TPoint(event.x, event.y)
            self.first_click = True
        else:
            self.main_canvas.delete ("all")
            if(overlap_num > -1):
                pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
                self.shapes.append(TRect(point1_x = self.first_click_pos.x, point1_y = self.first_click_pos.y, \
                                         point2_x = pt.x, point2_y = pt.y, colour = self.shapes_colour, \
                                         width = self.shapes_width) )
            else:
                self.shapes.append(TRect(point1_x = self.first_click_pos.x, point1_y = self.first_click_pos.y, \
                                         point2_x = event.x, point2_y = event.y, colour = self.shapes_colour, \
                                         width = self.shapes_width) )
            self.operations.append(TOperation("draw", shape = deepcopy(self.shapes[-1]), \
                                              num = len(self.shapes)-1))
            self.first_click = False
            self.first_click_pos = None
            self.canvas_refresh()
    
    def cylinder_click_draw(self, event, overlap_num = -1):
        "Click event while active mouse working mode is set to 'draw' and shape mode is set to 'Cylinder'"
        if(not self.first_click):
            if(overlap_num > -1):
                self.first_click_pos = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
            else:
                self.first_click_pos = TPoint(event.x, event.y)
            self.first_click = True
        else:
            self.main_canvas.delete("all")
            if(overlap_num > -1):
                pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
                radius = ((pt.x - self.first_click_pos.x)**2 + (pt.y - self.first_click_pos.y)**2)**0.5
                self.shapes.append (TCylin (centre = self.first_click_pos, radius = radius, \
                    colour = self.shapes_colour, width = self.shapes_width) )
            else:
                radius = ((event.x - self.first_click_pos.x)**2 + (event.y - self.first_click_pos.y)**2)**0.5
                self.shapes.append(TCylin(centre = self.first_click_pos, radius = radius, \
                                          colour = self.shapes_colour, width = self.shapes_width))
            self.operations.append(TOperation("draw", shape = deepcopy(self.shapes[-1]), \
                                              num = len(self.shapes)-1))
            self.first_click = False
            self.file_click_pos = None
            self.canvas_refresh()
    
    def cylin_sector_click_draw(self, event, overlap_num = -1):
        "Click event while active mouse working mode is set to 'draw' and shape mode is set to 'CylinSector'"
        if(not self.first_click and not self.second_click):
            if(overlap_num > -1):
                self.first_click_pos = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
            else:
                self.first_click_pos = TPoint(event.x, event.y)
            self.first_click = True
            self.second_click = False
        elif (self.first_click and not self.second_click):
            if(overlap_num > -1):
                self.second_click_pos = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
            else:
                self.second_click_pos = TPoint(event.x, event.y)
            self.first_click = False
            self.second_click = True
        elif(not self.first_click and self.second_click):
            self.main_canvas.delete ("all")
            radius = round(((self.second_click_pos.x - self.first_click_pos.x)**2 + (self.second_click_pos.y - self.first_click_pos.y)**2)**0.5, 0)
            if(overlap_num > -1):
                pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
                self.shapes.append(TCylinSector(centre = self.first_click_pos, radius = radius, \
                                                colour = self.shapes_colour, width = self.shapes_width, \
                                                boundary_pt1 = self.second_click_pos, boundary_pt2 = pt))
            else:
                self.shapes.append(TCylinSector(centre = self.first_click_pos, radius = radius, \
                                                colour = self.shapes_colour, width = self.shapes_width, \
                                                boundary_pt1 = self.second_click_pos, boundary_pt2 = TPoint(event.x, event.y)))
            self.operations.append(TOperation("draw", shape = deepcopy(self.shapes[-1]), \
                                              num = len(self.shapes)-1))
            self.first_click = False
            self.first_click_pos = None
            self.second_click = False
            self.second_click_pos = None
            self.canvas_refresh()
    
    def polygon_click_draw(self, event, overlap_num = -1):
        "Click event while active mouse working mode is set to 'draw' and shape mode is set to 'Polygon'"
        self.main_canvas.delete("all")
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
            self.polygon_points.append(pt)
        else:
            self.polygon_points.append(TPoint(event.x, event.y))
        for i, _ in enumerate(self.polygon_points[1:], 1):
            self.main_canvas.create_line(self.polygon_points[i-1].x, self.polygon_points [i-1].y, \
                self.polygon_points [i].x, self.polygon_points [i].y, fill = self.shapes_colour, width = self.shapes_width)
        self.main_canvas.create_line (self.polygon_points [-1].x, self.polygon_points [-1].y, event.x, event.y, fill = self.shapes_colour, width = self.shapes_width)
        self.canvas_refresh ()

    def polygon_double_click_draw(self, event):
        "Double click event while active mouse working mode is set to 'draw' and shape mode is set to 'Polygon'"
        overlap_num = self.mouse_overlaps_shape(event.x, event.y, self.radius)
        if(overlap_num > -1 and self.shapes[overlap_num].type == "Polygon"):
            if(overlap_num == self.mouse_overlaps_shape(self.polygon_points[0].x, \
                                                        self.polygon_points[0].y, \
                                                        self.radius)):
                # Move to separate function
                self.adjacent_polygon(event, overlap_num)
        try:
            self.shapes.append(TPolygon(self.polygon_points, colour = self.shapes_colour, width = self.shapes_width))
        except Exception as message:
            messagebox.showwarning("Cannot create polygon!", message)
        else:
            self.operations.append(TOperation("draw", shape = deepcopy(self.shapes[-1]), \
                                              num = len(self.shapes)-1))
            self.main_canvas.delete("all")
            self.canvas_refresh()
            self.polygon_points = []
    
    # --------------------------------------------------------------------------

    def adjacent_polygon(self, event, overlap_num = -1):
        "Completes one polygon using points from adjacent one"
        pt_beg = self.overlap_coord(self.shapes[overlap_num], \
                                            self.polygon_points[0].x, \
                                            self.polygon_points[0].y, \
                                            self.radius)
        pt_end = self.overlap_coord(self.shapes[overlap_num], event.x, \
                                    event.y, self.radius)
        i_beg, i_end, reverse = self.detect_shared_points_begin_end(self.shapes[overlap_num], pt_beg, pt_end)
        if(not(i_beg + 1 == i_end)):
            if(not reverse):
                # TODO: Calculating areas to one veratile and easy to read function
                area1 = TG.polygon_area(self.polygon_points + \
                                        self.shapes[overlap_num].points[i_end:i_beg:-1])  
                area2 = TG.polygon_area(self.polygon_points + \
                                        self.shapes[overlap_num].points[i_end + 1:] +
                                        self.shapes[overlap_num].points[:i_beg + 1])
                if(area1 < area2):
                    self.polygon_points += self.shapes[overlap_num].points[i_end:i_beg:-1]
                else:
                    self.polygon_points += self.shapes[overlap_num].points[i_end + 1:] + \
                                           self.shapes[overlap_num].points[:i_beg + 1]                 
            else:
                area1 = TG.polygon_area(self.polygon_points + \
                                        self.shapes[overlap_num].points[i_end:i_beg:-1])  
                area2 = TG.polygon_area(self.polygon_points + \
                                        self.shapes[overlap_num].points[i_beg + 1:] +
                                        self.shapes[overlap_num].points[:i_end + 1])
                if(area1 < area2):
                    self.polygon_points += self.shapes[overlap_num].points[i_beg::-1] + \
                                           self.shapes[overlap_num].points[:i_end:-1]
                else:
                    self.polygon_points += self.shapes[overlap_num].points[i_beg+1:i_end]

    def detect_shared_points_begin_end(self, polygon = None, pt_beg = None, pt_end = None):
        "Detects first and last of vertices shared by 2 polygons"
        try:
            reverse = False
            for i, pt in enumerate(polygon.points):
                if(pt.x == pt_beg.x and pt.y == pt_beg.y):
                    i_beg = i
                if(pt.x == pt_end.x and pt.y == pt_end.y):
                    i_end = i
            if(i_beg > i_end):
                i_beg, i_end = i_end, i_beg
                reverse = True
            return i_beg, i_end, reverse
        except Exception as message:
            raise TypeError(message)
        
    # --------------------------------------------------------------------------

    def draw_mouse_move(self, event):
        "Mouse move event while active mouse working mode is set to 'draw'"
        overlap_num = self.mouse_overlaps_shape(event.x, event.y, self.radius)
        if(self.mode == "Rectangle"):
            self.rectangle_mouse_move_draw(event, overlap_num)
        elif(self.mode == "Cylinder"):
            self.cylinder_mouse_move_draw(event, overlap_num)
        elif(self.mode == "CylinSector"):
            self.cylin_sector_mouse_move_draw(event, overlap_num)
        elif(self.mode == "Polygon"):
            self.polygon_mouse_move_draw(event, overlap_num)
        else:
            raise NotImplementedError("Invalid shape type")
    
    def rectangle_mouse_move_draw(self, event, overlap_num = -1):
        "Mouse move event while active mouse working mode is set to 'draw' and shape mode is set to 'Rectangle'"
        if(self.first_click == True):
            self.main_canvas.delete("all")
            self.canvas_refresh()
            if(overlap_num > -1):
                pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
                self.main_canvas.create_rectangle (self.first_click_pos.x, self.first_click_pos.y, pt.x, pt.y, \
                    outline = self.shapes_colour, width = self.shapes_width)
            else:
                self.main_canvas.create_rectangle (self.first_click_pos.x, self.first_click_pos.y, event.x, event.y, \
                    outline = self.shapes_colour, width = self.shapes_width)
    
    def cylinder_mouse_move_draw(self, event, overlap_num = -1):
        "Mouse move event while active mouse working mode is set to 'draw' and shape mode is set to 'Cylinder'"
        if (self.first_click == True):
            radius = ((event.x - self.first_click_pos.x)**2 + (event.y - self.first_click_pos.y)**2)**0.5
            self.main_canvas.delete ("all")
            self.canvas_refresh ()
            if(overlap_num > -1):
                pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
                radius = ((pt.x - self.first_click_pos.x)**2 + (pt.y - self.first_click_pos.y)**2)**0.5
                self.main_canvas.create_oval(self.first_click_pos.x - radius, self.first_click_pos.y -  radius, \
                                             self.first_click_pos.x + radius, self.first_click_pos.y + radius, outline = self.shapes_colour, \
                                             width = self.shapes_width)
            else:
                self.main_canvas.create_oval(self.first_click_pos.x - radius, self.first_click_pos.y -  radius, \
                                             self.first_click_pos.x + radius, self.first_click_pos.y + radius, outline = self.shapes_colour, \
                                             width = self.shapes_width)

    def cylin_sector_mouse_move_draw(self, event, overlap_num = -1):
        "Mouse move event while active mouse working mode is set to 'draw' and shape mode is set to 'CylindSector'"
        self.main_canvas.delete ("all")
        self.canvas_refresh ()
        if (self.first_click):
            if(overlap_num > -1):
                pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
                self.main_canvas.create_line (self.first_click_pos.x, self.first_click_pos.y, pt.x, pt.y, fill = self.shapes_colour, \
                                              width = self.shapes_width)
            else:
                self.main_canvas.create_line (self.first_click_pos.x, self.first_click_pos.y, event.x, event.y, fill = self.shapes_colour, \
                                              width = self.shapes_width)
        if(self.second_click):
            if(overlap_num > -1):
                pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
                event.x = pt.x
                event.y = pt.y
            radius = ((self.second_click_pos.x - self.first_click_pos.x)**2 + (self.second_click_pos.y - self.first_click_pos.y)**2)**0.5
            start, extent = self.calculate_cylin_sector_start_extent(self.first_click_pos, self.second_click_pos, event, radius)
            self.main_canvas.create_arc(self.first_click_pos.x - radius, self.first_click_pos.y - radius, self.first_click_pos.x + radius, self.first_click_pos.y + radius, \
                                        outline = self.shapes_colour, width = self.shapes_width, style = PIESLICE, start = start, extent = extent)

    def polygon_mouse_move_draw(self, event, overlap_num = -1):
        "Mouse move event while active mouse working mode is set to 'draw' and shape mode is set to 'Polygon'"
        if(self.polygon_points):
            self.main_canvas.delete("all")
            self.canvas_refresh()
            for i, _ in enumerate(self.polygon_points[1:], 1):
                self.main_canvas.create_line(self.polygon_points [i-1].x, self.polygon_points [i-1].y, \
                    self.polygon_points [i].x, self.polygon_points [i].y, fill = self.shapes_colour, width = self.shapes_width)
            if(overlap_num > -1):
                pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
                self.main_canvas.create_line (self.polygon_points [-1].x, self.polygon_points [-1].y, pt.x, pt.y, fill = self.shapes_colour, width = self.shapes_width)
            else:
                self.main_canvas.create_line (self.polygon_points [-1].x, self.polygon_points [-1].y, event.x, event.y, fill = self.shapes_colour, width = self.shapes_width)

    # --------------------------------------------------------------------------

    def move_click(self, event):
        "Mouse move event while active mouse working mode is set to 'move'"
        overlap_num = self.mouse_overlaps_shape(event.x, event.y, self.radius)
        if(not self.move):
            if(overlap_num > -1):
                self.click_move_shape_select(event, overlap_num)
            else:
                self.manipulated_shape_num = -1
                self.move = False
                self.move_const_point = None
                self.shape_buffer = None
        else:
            if(self.shape_buffer.type == "Rectangle"):
                self.rectangle_click_move_insert(event, overlap_num)
            elif(self.shape_buffer.type == "Cylinder"):
                self.cylinder_click_move_insert(event, overlap_num)
            elif(self.shape_buffer.type == "CylinSector"):
                self.cylin_sector_click_move_insert(event, overlap_num)
            elif(self.shape_buffer.type == "Polygon"):
                self.polygon_click_move_insert(event, overlap_num)
            else:
                raise NotImplementedError("Invalid shape type")
    
    def click_move_shape_select(self, event, overlap_num = -1):
        "Copies shape to be moved"
        self.shape_buffer = deepcopy(self.shapes[overlap_num]) 
        if(overlap_num > -1):
            self.operations.append(TOperation("move", shape = deepcopy(self.shapes[overlap_num]), \
                                  num = overlap_num))
        try:
            del self.shapes[overlap_num]
        except Exception as message:
            messagebox.showerror("Error while manipulating shapes list!", message)
            self.shape_buffer = None
        else:
            self.manipulated_shape_num = overlap_num
            self.move = True
            self.move_const_point = self.overlap_coord(self.shape_buffer, event.x, event.y, self.radius)
    
    def rectangle_click_move_insert(self, event, overlap_num = -1):
        "Click event while active mouse working mode is set to 'move', there is a shape being moved and shape mode is set to 'Rectangle'"
        self.main_canvas.delete("all")
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
            offset_x = pt.x - self.move_const_point.x
            offset_y = pt.y - self.move_const_point.y
        else:
            offset_x = event.x - self.move_const_point.x
            offset_y = event.y - self.move_const_point.y
        self.shape_buffer.point1.x += offset_x
        self.shape_buffer.point1.y += offset_y
        self.shape_buffer.point2.x += offset_x
        self.shape_buffer.point2.y += offset_y
        self.shape_buffer.update_model_positions()
        self.shapes.insert(self.manipulated_shape_num, self.shape_buffer)
        self.shape_buffer = None
        self.move_const_point = None
        self.manipulated_shape_num = -1
        self.move = False
        self.canvas_refresh()

    def cylinder_click_move_insert(self, event, overlap_num):
        "Click event while active mouse working mode is set to 'move', there is a shape being moved and shape mode is set to 'Cylinder'"
        self.main_canvas.delete("all")
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
            offset_x = pt.x - self.move_const_point.x
            offset_y = pt.y - self.move_const_point.y
        else:
            offset_x = event.x - self.move_const_point.x
            offset_y = event.y - self.move_const_point.y
        self.shape_buffer.centre.x += offset_x
        self.shape_buffer.centre.y += offset_y
        self.shape_buffer.update_model_positions()
        self.shapes.insert(self.manipulated_shape_num, self.shape_buffer)
        self.shape_buffer = None
        self.move_const_point = None
        self.manipulated_shape_num = -1
        self.move = False
        self.canvas_refresh()

    def cylin_sector_click_move_insert(self, event, overlap_num):
        "Click event while active mouse working mode is set to 'move', there is a shape being moved and shape mode is set to 'CylinSector'"
        self.main_canvas.delete("all")
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
            offset_x = pt.x - self.move_const_point.x
            offset_y = pt.y - self.move_const_point.y
        else:
            offset_x = event.x - self.move_const_point.x
            offset_y = event.y - self.move_const_point.y
        self.shape_buffer.centre.x += offset_x
        self.shape_buffer.centre.y += offset_y
        bp1, bp2 = self.calculate_cylin_sector_boundary_pts_window(self.shape_buffer.centre,\
                                                                   self.shape_buffer.radius, \
                                                                   self.shape_buffer.start, \
                                                                   self.shape_buffer.extent)
        self.shape_buffer.boundary_pt1 = bp1
        self.shape_buffer.boundary_pt2 = bp2
        self.shape_buffer.update_model_positions()
        self.shapes.insert(self.manipulated_shape_num, self.shape_buffer)
        self.shape_buffer = None
        self.move_const_point = None
        self.manipulated_shape_num = -1
        self.move = False
        self.canvas_refresh()
    
    def polygon_click_move_insert(self, event, overlap_num):
        "Click event while active mouse working mode is set to 'move', there is a shape being moved and shape mode is set to 'Polygon'"
        self.main_canvas.delete("all")
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
            offset_x = pt.x - self.move_const_point.x
            offset_y = pt.y - self.move_const_point.y
        else:
            offset_x = event.x - self.move_const_point.x
            offset_y = event.y - self.move_const_point.y
        for pt in self.shape_buffer.points:
            pt.x += offset_x
            pt.y += offset_y
        self.shape_buffer.update_model_positions()
        self.shape_buffer.update_window_positions()
        self.shapes.insert(self.manipulated_shape_num, self.shape_buffer)
        self.shape_buffer = None
        self.move_const_point = None
        self.manipulated_shape_num = -1
        self.move = False
        self.canvas_refresh()

    # --------------------------------------------------------------------------

    def move_mouse_move(self, event):
        "Mouse move event while active mouse working mode is set to 'draw'"
        if(self.move):
            overlap_num = self.mouse_overlaps_shape(event.x, event.y, self.radius)
            if(self.shape_buffer.type == "Rectangle"):
                self.rectangle_mouse_move_move(event, overlap_num)
            elif(self.shape_buffer.type == "Cylinder"):
                self.cylinder_mouse_move_move(event, overlap_num)
            elif(self.shape_buffer.type == "CylinSector"):
                self.cylin_sector_mouse_move_move(event, overlap_num)
            elif(self.shape_buffer.type == "Polygon"):
                pass
                self.polygon_mouse_move_move(event, overlap_num)
            else:
                raise NotImplementedError("Invalid shape type")

    def rectangle_mouse_move_move(self, event, overlap_num):
        "Mouse move event while active mouse working mode is set to 'move' and moved shape type is 'Rectangle'"
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
            offset_x = pt.x - self.move_const_point.x
            offset_y = pt.y - self.move_const_point.y
        else:
            offset_x = event.x - self.move_const_point.x
            offset_y = event.y - self.move_const_point.y
        self.main_canvas.delete("all")
        self.canvas_refresh()
        self.main_canvas.create_rectangle(self.shape_buffer.point1.x + offset_x, \
                                          self.shape_buffer.point1.y + offset_y, \
                                          self.shape_buffer.point2.x + offset_x, \
                                          self.shape_buffer.point2.y + offset_y, \
                                          outline = self.shape_buffer.colour, \
                                          width = self.shape_buffer.width)
    
    def cylinder_mouse_move_move(self, event, overlap_num):
        "Mouse move event while active mouse working mode is set to 'move' and moved shape type is 'Cylinder'"
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
            offset_x = pt.x - self.move_const_point.x
            offset_y = pt.y - self.move_const_point.y
        else:
            offset_x = event.x - self.move_const_point.x
            offset_y = event.y - self.move_const_point.y
        self.main_canvas.delete("all")
        self.canvas_refresh()
        self.main_canvas.create_oval(self.shape_buffer.centre.x + offset_x + self.shape_buffer.radius, \
                                     self.shape_buffer.centre.y + offset_y + self.shape_buffer.radius, \
                                     self.shape_buffer.centre.x + offset_x - self.shape_buffer.radius, \
                                     self.shape_buffer.centre.y + offset_y - self.shape_buffer.radius, \
                                     outline = self.shape_buffer.colour, width = self.shape_buffer.width)
    
    def cylin_sector_mouse_move_move(self, event, overlap_num):
        "Mouse move event while active mouse working mode is set to 'move' and moved shape type is 'CylinSector'"
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
            offset_x = pt.x - self.move_const_point.x
            offset_y = pt.y - self.move_const_point.y
        else:
            offset_x = event.x - self.move_const_point.x
            offset_y = event.y - self.move_const_point.y
        self.main_canvas.delete("all")
        self.canvas_refresh ()
        self.main_canvas.create_arc(self.shape_buffer.centre.x + offset_x + self.shape_buffer.radius, \
                                    self.shape_buffer.centre.y + offset_y + self.shape_buffer.radius, \
                                    self.shape_buffer.centre.x + offset_x - self.shape_buffer.radius, \
                                    self.shape_buffer.centre.y + offset_y - self.shape_buffer.radius, \
                                    start = self.shape_buffer.start, extent = self.shape_buffer.extent, \
                                    outline = self.shape_buffer.colour, width = self.shape_buffer.width)

    def polygon_mouse_move_move(self, event, overlap_num):
        "Mouse move event while active mouse working mode is set to 'move' and moved shape type is 'Polygon'"
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
            offset_x = pt.x - self.move_const_point.x
            offset_y = pt.y - self.move_const_point.y
        else:
            offset_x = event.x - self.move_const_point.x
            offset_y = event.y - self.move_const_point.y
        self.main_canvas.delete("all")
        self.canvas_refresh()
        points_unwrapped = [xs for pt in self.shape_buffer.points for xs in (pt.x + offset_x, pt.y + offset_y)]
        self.main_canvas.create_polygon(points_unwrapped, outline = self.shape_buffer.colour, \
                                        width = self.shape_buffer.width, fill = "")

    # --------------------------------------------------------------------------

    def resize_click(self, event):
        "Click event while active mouse working mode is set to 'resize'"
        overlap_num = self.mouse_overlaps_shape(event.x, event.y, self.radius)
        if(not self.resize):
            if(overlap_num > -1):
                self.click_resize_shape_select(event, overlap_num)
            else:
                self.manipulated_shape_num = -1
                self.resize = False
                self.resized_point = None
                self.shape_buffer = None
        else:
            if(self.shape_buffer.type == "Rectangle"):
                self.rectangle_click_resize_insert(event, overlap_num)
            elif(self.shape_buffer.type == "Cylinder"):
                self.cylinder_click_resize_insert(event, overlap_num)
            elif(self.shape_buffer.type == "CylinSector"):
                self.cylin_sector_click_resize_insert(event, overlap_num)
            elif(self.shape_buffer.type == "Polygon"):
                self.polygon_click_resize_insert(event, overlap_num)
            else:
                raise NotImplementedError("Invalid shape type")
    
    def click_resize_shape_select(self, event, overlap_num):
        "Copies shape to be resized"
        self.shape_buffer = deepcopy(self.shapes[overlap_num])
        if(overlap_num > -1):
            self.operations.append(TOperation("resize", shape = deepcopy(self.shapes[overlap_num]), \
                                          num = overlap_num))
        try:
            del self.shapes[overlap_num]
        except Exception as message:
            messagebox.showerror("Error while manipulating shapes list!", message)
            self.shape_buffer = None
        else:
            self.manipulated_shape_num = overlap_num
            self.resize = True
            self.resized_point = self.overlap_coord(self.shape_buffer, event.x, event.y, self.radius)

    def rectangle_click_resize_insert(self, event, overlap_num = -1):
        "Click event while active mouse working mode is set to 'resize', there is a shape being moved and shape mode is set to 'Rectangle'"
        self.main_canvas.delete("all")
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
            offset_x = pt.x - self.resized_point.x
            offset_y = pt.y - self.resized_point.y
        else:
            offset_x = event.x - self.resized_point.x
            offset_y = event.y - self.resized_point.y
        if(self.resized_point.x == self.shape_buffer.point1.x and \
           self.resized_point.y == self.shape_buffer.point1.y):
            self.shape_buffer.point1.x += offset_x
            self.shape_buffer.point1.y += offset_y
        else:
            self.shape_buffer.point2.x += offset_x
            self.shape_buffer.point2.y += offset_y
        self.shape_buffer.update_model_positions()
        self.shapes.insert(self.manipulated_shape_num, self.shape_buffer)
        self.shape_buffer = None
        self.resized_point = None
        self.manipulated_shape_num = -1
        self.resize = False
        self.canvas_refresh()

    def cylinder_click_resize_insert(self, event, overlap_num = -1):
        "Click event while active mouse working mode is set to 'resize', there is a shape being moved and shape mode is set to 'Cylinder'"
        self.main_canvas.delete("all")
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
            offset_x = pt.x - self.resized_point.x
            offset_y = pt.y - self.resized_point.y
        else:
            offset_x = event.x - self.resized_point.x
            offset_y = event.y - self.resized_point.y
        radius = ((self.resized_point.x + offset_x - self.shape_buffer.centre.x)**2 + \
                  (self.resized_point.y + offset_y - self.shape_buffer.centre.y)**2)**0.5
        self.shape_buffer.radius = radius
        self.shape_buffer.update_model_positions()
        self.shapes.insert(self.manipulated_shape_num, self.shape_buffer)
        self.shape_buffer = None
        self.resized_point = None
        self.manipulated_shape_num = -1
        self.resize = False
        self.canvas_refresh()

    def cylin_sector_click_resize_insert(self, event, overlap_num = -1):
        "Click event while active mouse working mode is set to 'resize', there is a shape being moved and shape mode is set to 'CylinSector'"
        self.main_canvas.delete ("all")
        radius = ((event.x - self.shape_buffer.centre.x)**2 + \
                  (event.y - self.shape_buffer.centre.y)**2)**0.5
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
            radius = ((pt.x - self.shape_buffer.centre.x)**2 + \
                      (pt.y - self.shape_buffer.centre.y)**2)**0.5
            event.x = pt.x
            event.y = pt.y
        if(self.resized_point.x == self.shape_buffer.boundary_pt1.x and \
           self.resized_point.y == self.shape_buffer.boundary_pt1.y):
            start, extent = self.calculate_cylin_sector_start_extent(self.shape_buffer.centre, \
                                                                     event, \
                                                                     self.shape_buffer.boundary_pt2, \
                                                                     radius)
            start = TG.round_to_multiple(start, min(TModel_Size.DX, TModel_Size.DY))
            extent = TG.round_to_multiple(extent, min(TModel_Size.DX, TModel_Size.DY))
            self.shape_buffer.radius = radius
            self.shape_buffer.start = start
            self.shape_buffer.extent = extent
            bp1, bp2 = self.calculate_cylin_sector_boundary_pts_window(self.shape_buffer.centre, \
                                                                       radius, start, extent)
            self.shape_buffer.boundary_pt1 = bp1
            self.shape_buffer.boundary_pt2 = bp2
        elif(self.resized_point.x == self.shape_buffer.boundary_pt2.x and \
             self.resized_point.y == self.shape_buffer.boundary_pt2.y):
            radius = ((self.shape_buffer.boundary_pt1.x - self.shape_buffer.centre.x)**2 + \
                      (self.shape_buffer.boundary_pt1.y - self.shape_buffer.centre.y)**2)**(0.5)
            start, extent = self.calculate_cylin_sector_start_extent(self.shape_buffer.centre, \
                                                                     self.shape_buffer.boundary_pt1, \
                                                                     TPoint(event.x, event.y), \
                                                                     self.shape_buffer.radius)
            start = TG.round_to_multiple(start, min(TModel_Size.DX, TModel_Size.DY))
            extent = TG.round_to_multiple(extent, min(TModel_Size.DX, TModel_Size.DY))
            self.shape_buffer.extent = extent
            _, bp2 = self.calculate_cylin_sector_boundary_pts_window(self.shape_buffer.centre, \
                                                                     radius, start, extent)
            self.shape_buffer.boundary_pt2 = bp2
        else:
            self.shape_buffer.radius = radius
            bp1, bp2 = self.calculate_cylin_sector_boundary_pts_window(self.shape_buffer.centre, \
                                                                       radius, \
                                                                       self.shape_buffer.start, \
                                                                       self.shape_buffer.extent)
            self.shape_buffer.boundary_pt1 = bp1
            self.shape_buffer.boundary_pt2 = bp2
        self.shape_buffer.update_model_positions()
        self.shapes.insert(self.manipulated_shape_num, self.shape_buffer)
        self.shape_buffer = None
        self.resized_point = None
        self.manipulated_shape_num = -1
        self.resize = False
        self.canvas_refresh()

    def polygon_click_resize_insert(self, event, overlap_num = -1):
        "Click event while active mouse working mode is set to 'resize', there is a shape being moved and shape mode is set to 'Polygon'"
        self.main_canvas.delete("all")
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
            offset_x = pt.x - self.resized_point.x
            offset_y = pt.y - self.resized_point.y
        else:
            offset_x = event.x - self.resized_point.x
            offset_y = event.y - self.resized_point.y
        for num, pt in enumerate(self.shape_buffer.points):
            if(pt.x == self.resized_point.x and pt.y == self.resized_point.y):
                break
        self.shape_buffer.points[num] = TPoint(self.resized_point.x + offset_x, \
                                               self.resized_point.y + offset_y)
        self.shape_buffer.update_model_positions()
        self.shape_buffer.update_window_positions()
        self.shapes.insert(self.manipulated_shape_num, self.shape_buffer)
        self.shape_buffer = None
        self.resized_point = None
        self.manipulated_shape_num = -1
        self.resize = False
        self.canvas_refresh()

    # --------------------------------------------------------------------------

    def resize_mouse_move(self, event):
        "Mouse move event while active mouse working mode is set to 'resize'"
        if(self.resize):
            overlap_num = self.mouse_overlaps_shape(event.x, event.y, self.radius)
            if(self.shape_buffer.type == "Rectangle"):
                self.rectangle_mouse_move_resize(event, overlap_num)
            elif(self.shape_buffer.type == "Cylinder"):
                self.cylinder_mouse_move_resize(event, overlap_num)
            elif(self.shape_buffer.type == "CylinSector"):
                self.cylin_sector_mouse_move_resize(event, overlap_num)
            elif(self.shape_buffer.type == "Polygon"):
                self.polygon_mouse_move_resize(event, overlap_num)
            else:
                raise NotImplementedError("Invalid shape type")
    
    def rectangle_mouse_move_resize(self, event, overlap_num):
        "Mouse move event while active mouse working mode is set to 'resize' and resized shape type is 'Rectangle'"
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
            offset_x = pt.x - self.resized_point.x
            offset_y = pt.y - self.resized_point.y
        else:
            offset_x = event.x - self.resized_point.x
            offset_y = event.y - self.resized_point.y
        self.main_canvas.delete("all")
        self.canvas_refresh ()
        if(self.resized_point.x == self.shape_buffer.point1.x and \
           self.resized_point.y == self.shape_buffer.point1.y):
            pt1_x = self.shape_buffer.point1.x + offset_x
            pt1_y = self.shape_buffer.point1.y + offset_y
            pt2_x = self.shape_buffer.point2.x
            pt2_y = self.shape_buffer.point2.y
        else:
            pt1_x = self.shape_buffer.point1.x
            pt1_y = self.shape_buffer.point1.y
            pt2_x = self.shape_buffer.point2.x + offset_x
            pt2_y = self.shape_buffer.point2.y + offset_y
        self.main_canvas.create_rectangle(pt1_x, pt1_y, pt2_x, pt2_y, \
                                          outline = self.shape_buffer.colour, \
                                          width = self.shape_buffer.width)

    def cylinder_mouse_move_resize(self, event, overlap_num):
        "Mouse move event while active mouse working mode is set to 'resize' and resized shape type is 'Cylinder'"
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
            offset_x = pt.x - self.resized_point.x
            offset_y = pt.y - self.resized_point.y
        else:
            offset_x = event.x - self.resized_point.x
            offset_y = event.y - self.resized_point.y
        self.main_canvas.delete("all")
        self.canvas_refresh ()
        radius = ((self.resized_point.x + offset_x - self.shape_buffer.centre.x)**2 + \
                  (self.resized_point.y + offset_y - self.shape_buffer.centre.y)**2)**0.5
        self.main_canvas.create_oval(self.shape_buffer.centre.x + radius, \
                                     self.shape_buffer.centre.y + radius, \
                                     self.shape_buffer.centre.x - radius, \
                                     self.shape_buffer.centre.y - radius, \
                                     outline = self.shape_buffer.colour, width = self.shape_buffer.width)

    def cylin_sector_mouse_move_resize(self, event, overlap_num):
        "Mouse move event while active mouse working mode is set to 'resize' and resized shape type is 'CylinSector'"
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
            radius = ((pt.x - self.shape_buffer.centre.x)**2 + \
                      (pt.y - self.shape_buffer.centre.y)**2)**0.5
            event.x = pt.x
            event.y = pt.y
        radius = ((event.x - self.shape_buffer.centre.x)**2 + \
                  (event.y - self.shape_buffer.centre.y)**2)**0.5
        self.main_canvas.delete("all")
        self.canvas_refresh ()
        if(self.resized_point.x == self.shape_buffer.boundary_pt1.x and \
           self.resized_point.y == self.shape_buffer.boundary_pt1.y):
            start, extent = self.calculate_cylin_sector_start_extent(self.shape_buffer.centre, \
                                                                     event, \
                                                                     self.shape_buffer.boundary_pt2, \
                                                                     radius)
        elif(self.resized_point.x == self.shape_buffer.boundary_pt2.x and \
             self.resized_point.y == self.shape_buffer.boundary_pt2.y):
            radius = ((self.shape_buffer.boundary_pt1.x - self.shape_buffer.centre.x)**2 + \
                      (self.shape_buffer.boundary_pt1.y - self.shape_buffer.centre.y)**2)**(0.5)
            start, extent = self.calculate_cylin_sector_start_extent(self.shape_buffer.centre, \
                                                                     self.shape_buffer.boundary_pt1, \
                                                                     TPoint(event.x, event.y), \
                                                                     self.shape_buffer.radius)
        else:
            start = self.shape_buffer.start
            extent = self.shape_buffer.extent
        self.main_canvas.create_arc(self.shape_buffer.centre.x + radius, \
                                    self.shape_buffer.centre.y + radius, \
                                    self.shape_buffer.centre.x - radius, \
                                    self.shape_buffer.centre.y - radius, \
                                    start = start, extent = extent, \
                                    outline = self.shape_buffer.colour, width = self.shape_buffer.width)

    def polygon_mouse_move_resize(self, event, overlap_num):
        "Mouse move event while active mouse working mode is set to 'resize' and moved shape type is 'Polygon'"
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
            offset_x = pt.x - self.resized_point.x
            offset_y = pt.y - self.resized_point.y
        else:
            offset_x = event.x - self.resized_point.x
            offset_y = event.y - self.resized_point.y
        points_unwrapped = [xs for pt in self.shape_buffer.points for xs in (pt.x, pt.y)]
        for num, pt in enumerate(self.shape_buffer.points):
            if(pt.x == self.resized_point.x and pt.y == self.resized_point.y):
                points_unwrapped[2*num] += offset_x
                points_unwrapped[2*num + 1] += offset_y                
        self.main_canvas.delete("all")
        self.canvas_refresh ()
        self.main_canvas.create_polygon(points_unwrapped, outline = self.shape_buffer.colour, \
                                        width = self.shape_buffer.width, fill = "")
    
    # --------------------------------------------------------------------------

    def calculate_cylin_sector_start_extent(self, centre, bp1, bp2, radius):
        """Auxiliary method used to calculate cylinder sector's start and extent 
           angles given 3 points constituing it"""
        if(bp1.x >= centre.x):
            start = degrees(asin((centre.y - bp1.y)/radius))
        else:
            start = 180 - degrees(asin((centre.y - bp1.y)/radius))
        if(start < 0):
            start += 360
        b1 = ((bp1.x - bp2.x)**2 + (bp1.y - bp2.y)**2)**(0.5)
        b2 = ((bp2.x - centre.x)**2 + (bp2.y - centre.y)**2)**(0.5)
        # Check wether boundry points and centre are colinear
        try:
            extent = degrees(acos(-((b1**2 - b2**2 - radius**2)/(2*b2*radius))))
        except ValueError:
            extent = 180
        # Check wether second boundary point is located to the right of the centre -- first boundary point line
        if(((bp2.x - centre.x)*sin(radians(start)) + (bp2.y - centre.y)*cos(radians(start))) > 0 and extent != 180):
            extent = 360 - extent
        return start, extent
    
    def calculate_cylin_sector_boundary_pts_window(self, centre, radius, start, extent):
        """Auxiliary method used to calculate cylinder sector's boundary points in window's 
           coordinates system given its centre, radius, start and extent angles"""
        bp1 = TPoint(int(centre.x + cos(radians(start))*radius), \
                     int(centre.y - sin(radians(start))*radius))
        bp2 = TPoint(int(centre.x + cos(radians(start + extent))*radius), \
                     int(centre.y - sin(radians(start + extent))*radius))
        return bp1, bp2
    
    # --------------------------------------------------------------------------

    def move_cursor_up(self, event):
        "Manually move mouse cursor one pixel up with keystroke"
        x = self.master.winfo_pointerx()
        y = self.master.winfo_pointery()
        abs_coord_x = x - self.master.winfo_rootx()
        abs_coord_y = y - self.master.winfo_rooty()
        self.master.event_generate('<Motion>', warp = True, x = abs_coord_x, y = abs_coord_y - 1)
    
    def move_cursor_down(self, event):
        "Manually move mouse cursor one pixel down with keystroke"
        x = self.master.winfo_pointerx()
        y = self.master.winfo_pointery()
        abs_coord_x = x - self.master.winfo_rootx()
        abs_coord_y = y - self.master.winfo_rooty()
        self.master.event_generate('<Motion>', warp = True, x = abs_coord_x, y = abs_coord_y + 1)

    def move_cursor_left(self, event):
            "Manually move mouse cursor one pixel left with keystroke"
            x = self.master.winfo_pointerx()
            y = self.master.winfo_pointery()
            abs_coord_x = x - self.master.winfo_rootx()
            abs_coord_y = y - self.master.winfo_rooty()
            self.master.event_generate('<Motion>', warp = True, x = abs_coord_x - 1, y = abs_coord_y)

    def move_cursor_right(self, event):
        "Manually move mouse cursor one pixel right with keystroke"
        x = self.master.winfo_pointerx()
        y = self.master.winfo_pointery()
        abs_coord_x = x - self.master.winfo_rootx()
        abs_coord_y = y - self.master.winfo_rooty()
        self.master.event_generate('<Motion>', warp = True, x = abs_coord_x + 1, y = abs_coord_y)

    # --------------------------------------------------------------------------

    def undo_operation(self, event = None):
        "Undo last operation"
        try:
            operation = self.operations.pop()
        except IndexError:
            pass
        else:
            if(operation.o_type == "draw"):
                self.shapes.pop()
            elif(operation.o_type == "move" or operation.o_type == "resize" or \
                 operation.o_type == "edit"):
                del self.shapes[operation.num]
                self.shapes.insert(operation.num, operation.shape)
            elif(operation.o_type == "remove_all"):
                while(operation is not None and operation.o_type == "remove_all"):
                    self.shapes.insert(operation.num, operation.shape)
                    try:
                        operation = self.operations.pop()
                    except IndexError:
                        operation = None
                if(operation is not None):
                    self.operations.append(operation)
            elif(operation.o_type == "remove"):
                self.shapes.insert(operation.num, operation.shape)
            else:
                self.operations.append(operation)
            self.main_canvas.delete("all")
            self.canvas_refresh()
    
    def run_gprmax_terminal(self):
        self.run_gprmax()
    
    def run_gprmax(self, filename = None):
        if(filename is None):
            filename = filedialog.askopenfilename()
        if(filename is None):
            return
        if(TSurveySettings.TYPE == "bscan"):
            init_iter = int(abs(TModel_Size.DOM_X - TSurveySettings.RX_X - \
                                10*TModel_Size.DX)/(TSurveySettings.RX_STEP_X)) + 1
        else:
            init_iter = 1
        n_iter = simpledialog.askinteger("Give number of iterations", "n: ", \
                                         initialvalue = init_iter)
        if(n_iter is not None):
            command = "start cmd /K run_gprmax.bat compute " + "\"" + filename + "\"" + \
                      " -n " + str(n_iter) + " --geometry-fixed"
            sts = subprocess.call(command, shell = True)
    
    def view_zoom_in(self):
        self.scale *= 2
        x_lenght = TModel_Size.MAX_X - TModel_Size.MIN_X
        y_lenght = TModel_Size.MAX_Y - TModel_Size.MIN_Y
        x_min_new = TModel_Size.MIN_X + x_lenght/4
        x_max_new = TModel_Size.MAX_X - x_lenght/4
        y_min_new = TModel_Size.MIN_Y + y_lenght/4
        y_max_new = TModel_Size.MAX_Y - y_lenght/4
        TModel_Size.MIN_X = x_min_new
        TModel_Size.MAX_X = x_max_new
        TModel_Size.MIN_Y = y_min_new
        TModel_Size.MAX_Y = y_max_new
        TTicksSettings.INT_X /= 2
        TTicksSettings.INT_Y /= 2
        TTicksSettings.ROUND_DIGITS = int(log10(self.scale)) + 1
        self.scrollbars_zoom_in()
        self.coordsys.model_size_update()
        self.coordsys.window_size_update()
        for single_shape in self.shapes:
            single_shape.update_window_positions()
        self.coordsys.display_settings_update()
        self.main_canvas.delete("all")
        self.canvas_refresh()

    def view_zoom_out(self):
        self.scale /= 2
        if(self.scale > 100.0):
            x_lenght = TModel_Size.MAX_X - TModel_Size.MIN_X
            y_lenght = TModel_Size.MAX_Y - TModel_Size.MIN_Y
            x_min_new = TModel_Size.MIN_X - x_lenght/2
            x_max_new = TModel_Size.MAX_X + x_lenght/2
            y_min_new = TModel_Size.MIN_Y - y_lenght/2
            y_max_new = TModel_Size.MAX_Y + y_lenght/2
            TModel_Size.MIN_X = x_min_new
            TModel_Size.MAX_X = x_max_new
            TModel_Size.MIN_Y = y_min_new
            TModel_Size.MAX_Y = y_max_new
        elif(self.scale < 100.0):
            self.scale = 100.0
            self.view_zoom_reset()
            return
        else:
            TModel_Size.MIN_X = 0.0
            TModel_Size.MAX_X = self.len_tot_x
            TModel_Size.MIN_Y = 0.0
            TModel_Size.MAX_Y = self.len_tot_y
        TTicksSettings.INT_X *= 2
        TTicksSettings.INT_Y *= 2
        self.scrollbars_zoom_out()
        self.coordsys.model_size_update()
        self.coordsys.window_size_update()
        for single_shape in self.shapes:
            single_shape.update_window_positions()
        self.coordsys.display_settings_update()
        self.main_canvas.delete("all")
        self.canvas_refresh()
    
    def view_zoom_reset(self):
        TModel_Size.MIN_X = 0.0
        TModel_Size.MAX_X = self.len_tot_x
        TModel_Size.MIN_Y = 0.0
        TModel_Size.MAX_Y = self.len_tot_y
        TTicksSettings.INT_X *= self.scale/100.0
        TTicksSettings.INT_Y *= self.scale/100.0
        self.scale = 100.0
        self.scrollbars_zoom_out()
        self.coordsys.model_size_update()
        self.coordsys.window_size_update()
        for single_shape in self.shapes:
            single_shape.update_window_positions()
        self.coordsys.display_settings_update()
        self.main_canvas.delete("all")
        self.canvas_refresh()
    
    def scrollbars_zoom_in(self):
        if(self.scale > 100.0):
            hsbar_pos = self.main_horizontal_scrollbar.get()
            hsbar_len = hsbar_pos[1] - hsbar_pos[0]
            hsbar_new_lo = hsbar_pos[0] + hsbar_len/4
            hsbar_new_hi = hsbar_pos[1] - hsbar_len/4
            self.main_horizontal_scrollbar.set(hsbar_new_lo, hsbar_new_hi)
            vsbar_pos = self.main_vertical_scrollbar.get()
            vsbar_len = vsbar_pos[1] - vsbar_pos[0]
            vsbar_new_lo = vsbar_pos[0] + vsbar_len/4
            vsbar_new_hi = vsbar_pos[1] - vsbar_len/4
            self.main_vertical_scrollbar.set(vsbar_new_lo, vsbar_new_hi)
    
    def scrollbars_zoom_out(self):
        if(self.scale > 100.0):
            hsbar_pos = self.main_horizontal_scrollbar.get()
            hsbar_len = hsbar_pos[1] - hsbar_pos[0]
            hsbar_new_lo = hsbar_pos[0] - hsbar_len/2
            hsbar_new_hi = hsbar_pos[1] + hsbar_len/2
            self.main_horizontal_scrollbar.set(hsbar_new_lo, hsbar_new_hi)
            vsbar_pos = self.main_vertical_scrollbar.get()
            vsbar_len = vsbar_pos[1] - vsbar_pos[0]
            vsbar_new_lo = vsbar_pos[0] - vsbar_len/2
            vsbar_new_hi = vsbar_pos[1] + vsbar_len/2
            self.main_vertical_scrollbar.set(vsbar_new_lo, vsbar_new_hi)
        elif(self.scale == 100.0):
            self.main_horizontal_scrollbar.set(0, 1)
            self.main_vertical_scrollbar.set(0, 1)

    
    def model_horizontal_scroll(self, action, number, units = ""):
        "Handle visible model area move in x direction"
        hbar_pos = self.main_horizontal_scrollbar.get()
        hbar_pos = (Decimal(str(hbar_pos[0])), Decimal(str(hbar_pos[1])))
        hbar_len = Decimal(str(1/(self.scale/100)))
        scale_dec = Decimal(str(self.scale))/Decimal('100.0')
        try:
            dx_float = self.main_horizontal_scrollbar.delta(int(number), 0)
            dx = Decimal(str(dx_float))
        except:
            # Dragging the scrollbar
            new_pos_lower = Decimal(number)
            new_pos_upper = new_pos_lower + Decimal(str(hbar_len))
        else:
            new_pos_lower = hbar_pos[0] + dx
            new_pos_upper = hbar_pos[1] + dx
        if(new_pos_lower < 0):
            self.main_horizontal_scrollbar.set(0, hbar_len)
            new_min_x = Decimal('0.0')
            new_max_x = Decimal(str(self.len_tot_x))/scale_dec
        elif(new_pos_upper > 1):
            self.main_horizontal_scrollbar.set(1 - hbar_len, 1)
            factor = Decimal('1.0') - scale_dec**(Decimal('-1.0')) 
            new_min_x = Decimal(str(self.len_tot_x))*factor
            new_max_x = Decimal(str(self.len_tot_x))
        else:
            self.main_horizontal_scrollbar.set(new_pos_lower, new_pos_upper)
            new_min_x = (new_pos_lower)*Decimal(str(self.len_tot_x))
            new_max_x = (new_pos_upper)*Decimal(str(self.len_tot_x))
        TModel_Size.MIN_X = float(round(new_min_x, TTicksSettings.ROUND_DIGITS))
        TModel_Size.MAX_X = float(round(new_max_x, TTicksSettings.ROUND_DIGITS))
        # Pack set of instructions below into a single function
        self.coordsys.model_size_update()
        self.coordsys.window_size_update()
        for single_shape in self.shapes:
            single_shape.update_window_positions()
        self.coordsys.display_settings_update()
        self.main_canvas.delete("all")
        self.canvas_refresh()

    def model_vertical_scroll(self, action, number, units = ""):
        "Handle visible model area move in y direction"
        # Convert used quantities to decimal in order to obtain higher
        # floating point accuracy
        vbar_pos = self.main_vertical_scrollbar.get()
        vbar_pos = (Decimal(str(vbar_pos[0])), Decimal(str(vbar_pos[1])))
        vbar_len = Decimal(str(1/(self.scale/100)))
        scale_dec = Decimal(str(self.scale))/Decimal('100.0')
        try:
            dy_float = self.main_horizontal_scrollbar.delta(int(number), 0)
            dy = Decimal(str(dy_float))
        except:
            new_pos_lower = Decimal(number)
            new_pos_upper = new_pos_lower + Decimal(str(vbar_len))
        else:
            new_pos_lower = vbar_pos[0] + dy
            new_pos_upper = vbar_pos[1] + dy
        if(new_pos_lower < 0):
            self.main_vertical_scrollbar.set(0, vbar_len)
            factor = Decimal('1.0') - scale_dec**(Decimal('-1.0')) 
            new_min_y = Decimal(str(self.len_tot_y))*factor
            new_max_y = Decimal(str(self.len_tot_y))
        elif(new_pos_upper > 1):
            self.main_vertical_scrollbar.set(1 - vbar_len, 1)
            new_min_y = Decimal('0.0')
            new_max_y = Decimal(str(self.len_tot_y))/scale_dec
        else:
            self.main_vertical_scrollbar.set(new_pos_lower, new_pos_upper)
            new_min_y = (Decimal('1.0') - new_pos_upper)*Decimal(str(self.len_tot_y))
            new_max_y = (Decimal('1.0') - new_pos_lower)*Decimal(str(self.len_tot_y))
        TModel_Size.MIN_Y = float(round(new_min_y, TTicksSettings.ROUND_DIGITS))
        TModel_Size.MAX_Y = float(round(new_max_y, TTicksSettings.ROUND_DIGITS))
        # Pack set of instructions below into a single function
        self.coordsys.model_size_update()
        self.coordsys.window_size_update()
        for single_shape in self.shapes:
            single_shape.update_window_positions()
        self.coordsys.display_settings_update()
        self.main_canvas.delete("all")
        self.canvas_refresh()
    
    def read_model_file(self):
        "Reads and loads a GprMax compliant input file"
        filename = filedialog.askopenfilename(initialdir = '.', title = "Select file", \
                    filetypes = [("gprMax input files", "*.in"), ("All files", "*.*")])
        
        with open(filename) as infile:
            self.remove_all_shapes()
            line_num = 1
            for line in infile:
                if(line[0] == "#"):
                    # Omit lines that don't begin with hash sign (comments)
                    self.handle_input_command(line, line_num)
                line_num += 1
            self.view_zoom_reset()
            # self.materials_frame.update_list(self.materials)
            # self.shapes_frame.update_list(self.shapes)
            # self.canvas_refresh()

    def handle_input_command(self, line, line_num):
        "Recognises and handles a command given in a line"
        tokens = line.split()
        command = (tokens[0])[1:-1]
        if(command == "title"):
            self.title = " ".join(tokens[1:])
            self.master.title("gprMax Designer: " + self.title)
        elif(command == "domain"):
            TModel_Size.DOM_X = float(tokens[1])
            TModel_Size.DOM_Y = float(tokens[2])
            TModel_Size.MIN_X = 0.0
            TModel_Size.MIN_Y = 0.0
            TModel_Size.MAX_X = TModel_Size.DOM_X
            TModel_Size.MAX_Y = TModel_Size.DOM_Y
            self.len_tot_x = TModel_Size.DOM_X
            self.len_tot_y = TModel_Size.DOM_Y
        elif(command == "dx_dy_dz"):
            TModel_Size.DX = float(tokens[1])
            TModel_Size.DY = float(tokens[2])
        elif(command == "time_window"):
            TSurveySettings.TIME_WINDOW = float(tokens[1])
        elif(command == "waveform"):
            TSurveySettings.WAVE_TYPE = tokens[1]
            TSurveySettings.AMPLITUDE = float(tokens[2])
            TSurveySettings.FREQUENCY = float(tokens[3])
        elif(command == "hertzian_dipole"):
            TSurveySettings.SRC_TYPE = command
        elif(command == "magnetic_dipole"):
            TSurveySettings.SRC_TYPE = command
        elif(command == "rx"):
            TSurveySettings.RX_X = float(tokens[1])
            TSurveySettings.RX_Y = float(tokens[2])
            TSurveySettings.TYPE = "ascan"
        elif(command == "rx_array"):
            TSurveySettings.RX_X = float(tokens[1])
            TSurveySettings.RX_Y = float(tokens[2])
            TSurveySettings.RX_MAX_X = float(tokens[4])
            TSurveySettings.RX_MAX_Y = float(tokens[5])
            TSurveySettings.RX_STEP_X = float(tokens[7])
            TSurveySettings.RX_STEP_Y = float(tokens[8])
            TSurveySettings.TYPE = "rx_array"
        elif(command == "src_steps"):
            TSurveySettings.SRC_STEP_X = float(tokens[1])
            TSurveySettings.SRC_STEP_Y = float(tokens[2])
            TSurveySettings.TYPE = "bscan"
        elif(command == "rx_steps"):
            TSurveySettings.RX_STEP_X = float(tokens[1])
            TSurveySettings.RX_STEP_Y = float(tokens[2])
            TSurveySettings.TYPE = "bscan"
        elif(command == "material"):
            epsilon_r = float(tokens[1])
            sigma = float(tokens[2])
            mu_r = float(tokens[3])
            sigma_mag = float(tokens[4])
            name = tokens[5]
            self.materials.append(TMaterial(epsilon_r, sigma, mu_r, sigma_mag, \
                                            name))
        elif(command == "box"):
            pt1 = TPoint(float(tokens[1]), float(tokens[2]))
            pt2 = TPoint(float(tokens[4]), float(tokens[5]))
            mat = tokens[7]
            self.shapes.append(TRect(point1_mod = pt1, point2_mod = pt2, \
                                     material = mat))
        elif(command == "cylinder"):
            cen = TPoint(float(tokens[1]), float(tokens[2]))
            rad = float(tokens[7])
            mat = tokens[8]
            self.shapes.append(TCylin(centre_mod = cen, radius_mod = rad, \
                                      material = mat))
        elif(command == "cylindrical_sector"):
            cen = TPoint(float(tokens[2]), float(tokens[3]))
            rad = float(tokens[6])
            sta = float(tokens[7])
            ext = float(tokens[8])
            mat = tokens[9]
            self.shapes.append(TCylinSector(centre_mod = cen, radius_mod = rad, \
                                            start = sta, extent = ext, \
                                            material = mat))
        elif(command == "triangle"):
            pts = []
            pts.append(TPoint(float(tokens[1]), float(tokens[2])))
            pts.append(TPoint(float(tokens[4]), float(tokens[5])))
            pts.append(TPoint(float(tokens[7]), float(tokens[8])))
            mat = tokens[11]
            self.shapes.append(TPolygon(points_mod = pts, material = mat))
        elif(command == "geometry_view"):
            pass
        else:
            messagebox.showwarning("Input error", \
                                   "Invalid input {} in line {}.".format(line, line_num))

    def export_hdf5_to_ascii(self):
        "Export a gprMax output file in HDF5 format to ASCII"
        filename = filedialog.askopenfilename(initialdir = '.', title = "Select file", \
                    filetypes = [("gprMax output files", "*.out"), ("All files", "*.*")])
        h5file = h5py.File(filename)
        iterations = h5file.attrs["Iterations"]
        title = h5file.attrs["Title"]
        dt = h5file.attrs["dt"]
        ver = h5file.attrs["gprMax"]
        nrx = h5file.attrs["nrx"]
        traces = h5file["rxs"]["rx1"]["Ez"].shape[1]
        metafilename = (filename.split("."))[0] + "_meta.txt"
        with open(metafilename, "w") as metafile:
            metafile.write("title: {}\n".format(title))
            metafile.write("gprMax version: {}\n".format(ver))
            metafile.write("no of iterations: {}\n".format(iterations))
            metafile.write("time increment: {}\n".format(dt))
            metafile.write("total time: {}\n".format(dt*iterations))
            metafile.write("no of traces: {}\n".format(traces))
            metafile.write("no of rxs per src: {}\n".format(nrx))
        ezfilename = (filename.split("."))[0] + "_ez.txt"
        ezdata = h5file["rxs"]["rx1"]["Ez"]
        ezdata = ezdata[()].transpose()
        with open(ezfilename, "w") as ezfile:
            self.write_array_to_file(ezfile, ezdata)
        hxfilename = (filename.split("."))[0] + "_hx.txt"
        hxdata = h5file["rxs"]["rx1"]["Hx"]
        hxdata = hxdata[()].transpose()
        with open(hxfilename, "w") as hxfile:
            self.write_array_to_file(hxfile, hxdata)
        hyfilename = (filename.split("."))[0] + "_hy.txt"
        hydata = h5file["rxs"]["rx1"]["Hy"]
        hydata = hydata[()].transpose()
        with open(hyfilename, "w") as hyfile:
            self.write_array_to_file(hyfile, hydata)
        
    def write_array_to_file(self, fileh, array):
        length = len(array)
        for i, row in enumerate(array):
            for elem in row[:-1]:
                fileh.write(str(elem) + ", ")
            fileh.write(str(row[-1]))
            if(i != (length - 1)):
                fileh.write("\n")
    
    def merge_traces(self):
        "Invoke gprMax tools to merge output files containing traces"
        remove_files = messagebox.askyesno("Merge files", "Do you wish to remove merged files?")
        filename = filedialog.askopenfilename(initialdir = '.', title = "Select file", \
                    filetypes = [("gprMax output files", "*.out"), ("All files", "*.*")])
        basename = (filename.split("."))[0]
        if(basename != ""):
            command = "start cmd /K run_gprmax.bat merge " + "\"" + basename[:-1] + "\""
            if(remove_files == True):
                command += " --remove-files"
            sts = subprocess.call(command, shell = True)
    
    def display_trace(self):
        components_dialog = TTraceWindow(self.master)
        components = components_dialog.result
        filename = filedialog.askopenfilename(initialdir = '.', title = "Select file", \
                    filetypes = [("gprMax output files", "*.out"), ("All files", "*.*")])
        if(filename != ""):
            command = "start cmd /K run_gprmax.bat ascan " + "\"" + filename + "\"" + \
                      " " + components
            sts = subprocess.call(command, shell = True)
    
    def display_echogram(self):
        component_dialog = TEchogramWindow(self.master)
        component = component_dialog.result
        filename = filedialog.askopenfilename(initialdir = '.', title = "Select file", \
                    filetypes = [("gprMax output files", "*.out"), ("All files", "*.*")])
        if(filename != ""):
            command = "start cmd /K run_gprmax.bat bscan " + "\"" + filename + "\"" + \
                      " " + component
            sts = subprocess.call(command, shell = True)
    
    def copy_shape(self, event = None, *, shape_num = -1):
        "Copies shape overlaped by mouse pointer to buffer or specified by given number"
        self.canvas_interrupt()
        if(shape_num == -1 and event is not None):
            shape_num = self.mouse_overlaps_shape(event.x, event.y, self.radius)
        if(shape_num > -1):
            if(event is not None):
                self.move_const_point = TPoint(event.x, event.y)
            else:
                if(self.shapes[shape_num].type == "Rectangle"):
                    self.move_const_point = self.shapes[shape_num].point1
                elif(self.shapes[shape_num].type == "Cylinder" or \
                     self.shapes[shape_num].type == "CylinSector"):
                    self.move_const_point = self.shapes[shape_num].centre
                elif(self.shapes[shape_num].type == "Polygon"):
                    self.move_const_point = self.shapes[shape_num].points[0]
                else:
                    raise NotImplementedError("Invalid shape type")
            self.manipulated_shape_num = len(self.shapes)
            self.shape_buffer = deepcopy(self.shapes[shape_num])
    
    def paste_shape(self, event = None, *, deltax = 15, deltay = 15):
        "Paste shape into model"
        if(event is not None):
            shape_num = self.mouse_overlaps_shape(event.x, event.y, self.radius)
        if(self.shape_buffer is not None and event is not None):
            if(self.shape_buffer.type == "Rectangle"):
                self.rectangle_click_move_insert(event, shape_num)
            elif(self.shape_buffer.type == "Cylinder"):
                self.cylinder_click_move_insert(event, shape_num)
            elif(self.shape_buffer.type == "CylinSector"):
                self.cylin_sector_click_move_insert(event, shape_num)
            elif(self.shape_buffer.type == "Polygon"):
                self.polygon_click_move_insert(event, shape_num)
            else:
                raise NotImplementedError("Invalid shape type")
    
    def copy_ctrl_c(self, event):
        "ctrl+z keystroke event"
        try:
            shape_num = (self.shapes_frame.shapes_list.curselection())[0]
        except IndexError:
            return
        self.copy_shape(shape_num = shape_num)

    def paste_ctrl_v(self, event):
        "ctrl+v keystroke event"
        pass


def centre_window(window):
    # Gets the requested values of the height and widht.
    window.update_idletasks()
    windowWidth = window.winfo_width()
    windowHeight = window.winfo_height()
    # Gets both half the screen width/height and window width/height
    positionRight = int(window.winfo_screenwidth()/2 - windowWidth/2)
    positionDown = int(window.winfo_screenheight()/2 - windowHeight*0.56)
    # Positions the window in the centre of the page.
    window.geometry("+{}+{}".format(positionRight, positionDown))


def main():
    root = Tk()
    myApp = TApp(root)
    centre_window(root)
    # root.eval ('tk::PlaceWindow %s center' % root.winfo_toplevel() )
    # Mainloop
    root.mainloop()


if __name__ == "__main__":
    main()