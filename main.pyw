"""
.. module:: Main program module.
:synopsis: Module contains main class TApp, responsible for handling events.

.. moduleauthor:: Tomasz Siwek <tsiwek@g.pl>
"""

from copy import copy, deepcopy
from decimal import Decimal
import h5py
from math import asin, acos, atan, degrees, sin, cos, radians, log10, log2, ceil
import os
from PIL import Image, ImageDraw
from random import randrange
import subprocess
import sys
from tkinter import Tk, Canvas, Menu, messagebox, BooleanVar, Frame, Button, \
                    Toplevel, Text, Label, PanedWindow, PhotoImage, simpledialog, \
                    colorchooser, filedialog, Scrollbar, Event
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
from settings import TWindow_Size, TModel_Size, TTicksSettings, TSurveySettings, \
                     TColours
from shapes import TRect, TCylin, TCylinSector, TPolygon, TCoordSys
from shapeswindow import TShapesWindow
from surveysettingswindow import TSurveySettingsWindow
from tracewindow import TTraceWindow


class TApp(object):
    """
    Class represents application as a whole. It handles events.

    :param master: tk root object.
    :type master: Tk()
    """

    # Make this a Frame
    # Change all names of entities regarding shapes as a whole

    # Static variables
    first_click = False         #: first LMB click flag.
    first_click_pos = None      #: position of first click in pixels.
    second_click = False        #: second LMB click flag.
    second_click_pos = None     #: position of second click in pixels.
    resize = False              #: shape resize mouse mode flag.
    move = False                #: shape move mouse mode flag.
    move_const_point = None     #: reference point dor calculating move offset.
    manipulated_shape_num = -1  #: list index of the manipulated (moved/resized) shape.
    polygon_points = []         #: buffor containing vertices of polygon being drawn.
    double_click = False        #: double LMB click flag.
    shape_buffer = None         #: buffor containing shape being manipulated (/moved/resized).
    resized_point = None        #: coordinates of manipulated shape point/vertex.
    AVAILABLE_COLOURS = ("red", "blue", "yellow", "green", "orange", "purple", \
                         "indigo", "fuchsia", "white", "navy", "brown")
    """List of named colours from which a randome one will be drawn."""
    scale = 100.0                   #: zoom scale in percent.
    len_tot_x = TModel_Size.MAX_X   #: total model length in x direction.
    len_tot_y = TModel_Size.MAX_Y   #: total model length in y direction.
    prev_mouse_pos = None           #: previous mouse position.

    def __init__(self, master):
        self.master = master

        # Window title
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

        # Model title
        self.title = ""

        # Create coordinate system
        self.coordsys = TCoordSys(self.shapes_colour, self.shapes_width, \
                                  grid_colour = self.grid_colour)

        # Shapes frame
        self.shapes_frame = TShapesWindow(self.master, self)
        self.shapes_frame.grid(row = 0, column = 1, rowspan = 2, sticky = NSEW)

        # Materials frame
        self.materials_frame = TMaterialsWindow(self.master, self, self.shapes_frame)
        self.materials_frame.grid(row = 2, column = 1, rowspan = 2, sticky = NSEW)

        self.init_status_bar()

        self.canvas_refresh()

        # Try to load toolbar icons
        self.load_toolbar_icons()

        # Initialise operation queue
        self.operations = []

    def init_grid(self):
        """
        Init main window grid properties.
        """
        self.master.rowconfigure(1, weight = 1)
        self.master.rowconfigure(2, weight = 1)
        self.master.columnconfigure(0, weight = 1)

    def init_canvas(self):
        """
        Init frame containing main canvas and its scrollbars.
        """
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
        self.main_canvas.config(cursor = "pencil")

    def init_main_menu(self):
        """
        Create main menu and its positions.
        """
        self.main_menubar = Menu(self.master)
        self.file_menu = Menu(self.main_menubar, tearoff = 0)
        self.edit_menu = Menu(self.main_menubar, tearoff = 0)
        self.view_menu = Menu(self.main_menubar, tearoff = 0)
        self.settings_menu = Menu(self.main_menubar, tearoff = 0)
        self.file_menu.add_command(label = "Read model file", \
                                   command = self.read_model_file)
        self.file_menu.add_command(label = "Open materials")
        self.file_menu.add_command(label = "Save materials")
        self.file_menu.add_command(label = "Parse to gprMax", \
                                   command = self.parse_to_gprmax)
        self.file_menu.add_command(label = "Run gprMax in terminal", \
                                   command = self.run_gprmax)
        self.file_menu.add_command(label = "Export hdf5 to ascii", \
                                   command = self.export_hdf5_to_ascii)
        self.file_menu.add_command(label = "Merge traces", \
                                   command = self.merge_traces)
        self.file_menu.add_command(label = "Plot trace", \
                                   command = self.display_trace)
        self.file_menu.add_command(label = "Plot echogram", \
                                   command = self.display_echogram)
        self.file_menu.add_command(label = "Convert model to an image", \
                                   command = self.export_canvas_to_image)
        self.file_menu.add_command(label = "Quit!", command = self.master.destroy)
        self.edit_menu.add_command(label = "Undo", command = self.undo_operation)
        self.edit_menu.add_command(label = "Create rectangle", \
                                   command = self.create_rectangle)
        self.edit_menu.add_command(label = "Create cylinder", \
                                   command = self.create_cylin)
        self.edit_menu.add_command(label = "Create cylindrical sector", \
                                   command = self.create_cylin_sector)
        self.edit_menu.add_command(label = "Create polygon", command = self.create_polygon)
        self.edit_menu.add_command(label = "Recolour randomly", command = self.recolour_randomly)
        self.edit_menu.add_command(label = "Delete all", command = self.remove_all_shapes)
        self.view_menu.add_command(label = "Display", command = self.display_settings)
        self.view_menu.add_command(label = "Toggle grid", command = self.toggle_grid)
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
        """
        Create a right-click popup menu.
        """
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
        """
        Create main toolbar and its buttons.
        """
        self.main_toolbar = Frame(self.master, bd = 1, relief = RAISED)
        self.rectangleButton = Button(self.main_toolbar, text = "R", relief=SUNKEN, \
                                      command = self.set_mode_rectangle)
        self.rectangleButton.grid(row = 0, column = 0, padx=2, pady=2)
        self.cylinderButton = Button(self.main_toolbar, text = "C", relief=FLAT, \
                                     command = self.set_mode_cylinder)
        self.cylinderButton.grid(row = 0, column = 1, padx=2, pady=2)
        self.cylinSectorButton = Button(self.main_toolbar, text = "S", relief=FLAT, \
                                        command = self.set_mode_cylin_sector)
        self.cylinSectorButton.grid(row = 0, column = 2, padx=2, pady=2)
        self.polygonButton = Button(self.main_toolbar, text = "P", relief = FLAT, \
                                    command = self.set_mode_polygon)
        self.polygonButton.grid(row = 0, column = 4, padx=2, pady=2)
        Label(self.main_toolbar, text = "|").grid(row = 0, column = 5, padx=2, pady=2)
        self.draw_button = Button(self.main_toolbar, text = "D", relief = SUNKEN, \
                                  command = self.set_mouse_mode_draw)
        self.draw_button.grid(row = 0, column = 6, padx = 2, pady = 2)
        self.move_button = Button(self.main_toolbar, text = "M", relief = FLAT, \
                                  command = self.set_mouse_mode_move)
        self.move_button.grid(row = 0, column = 7, padx = 2, pady = 2)
        self.resize_button = Button(self.main_toolbar, text = "R", relief = FLAT, \
                                    command = self.set_mouse_mode_resize)
        self.resize_button.grid(row = 0, column = 8, padx = 2, pady = 2)
        Label(self.main_toolbar, text = "|").grid(row = 0, column = 9, padx = 2, pady = 2)
        self.zoom_in_button = Button(self.main_toolbar, text = "+", relief = FLAT, \
                                     command = self.view_zoom_in)
        self.zoom_in_button.grid(row = 0, column = 10, padx = 2, pady = 2)
        self.zoom_out_button = Button(self.main_toolbar, text = "-", relief = FLAT, \
                                      command = self.view_zoom_out)
        self.zoom_out_button.grid(row = 0, column = 11, padx = 2, pady = 2)
        Label(self.main_toolbar, text = "|").grid(row = 0, column = 12, padx=2, pady=2)
        self.model_settings_button = Button(self.main_toolbar, text = "model", relief = FLAT,\
                                            command = self.change_model_size)
        self.model_settings_button.grid(row = 0, column = 13, padx=2, pady=2)
        self.survey_settings_button = Button(self.main_toolbar, text = "survey", relief = FLAT,\
                                            command = self.survey_settings)
        self.survey_settings_button.grid(row = 0, column = 14, padx=2, pady=2)
        self.display_settings_button = Button(self.main_toolbar, text = "display", relief = FLAT,\
                                            command = self.display_settings)
        self.display_settings_button.grid(row = 0, column = 15, padx=2, pady=2)
        Label(self.main_toolbar, text = "|").grid(row = 0, column = 16, padx=2, pady=2)
        self.parseToGprMaxButton = Button(self.main_toolbar, text = "Parse to gprMax", \
                                          relief = FLAT, command = self.parse_to_gprmax)
        self.parseToGprMaxButton.grid(row = 0, column = 17, padx = 2, pady = 2)
        Label(self.main_toolbar, text = "|").grid(row = 0, column = 18, padx=2, pady=2)
        self.exitButton = Button(self.main_toolbar, text = "Q", relief=FLAT, \
                                 command = self.master.destroy)
        self.exitButton.grid(row = 0, column = 19, padx=2, pady=2)
        self.main_toolbar.grid(row = 0, column = 0, sticky = EW)

    def init_status_bar(self):
        """
        Init status bar.
        """
        fwidth = 8
        self.status_bar = Frame(self.master, bd = 1)
        self.pos_x_label = Label(self.status_bar, text = "X: -", width = fwidth, \
                                 anchor = W)
        self.pos_x_label.grid(row = 0, column = 0)
        self.pos_y_label = Label(self.status_bar, text = "Y: -", width = fwidth, \
                                 anchor = W)
        self.pos_y_label.grid(row = 0, column = 1)
        self.status_bar.grid(row = 3, column = 0, sticky = EW)

    def bind_canvas_events(self):
        """
        Bind canvas events to handling methods.
        """
        self.main_canvas.bind("<Button-1>", self.canvas_click)
        self.main_canvas.bind("<Button-3>", self.display_right_button_popup)
        self.main_canvas.bind("<Motion>", self.canvas_mouse_move)
        self.main_canvas.bind("<Button-2>", self.init_model_move)
        self.main_canvas.bind("<B2-Motion>", self.move_visible_model)
        self.main_canvas.bind("<ButtonRelease-2>", self.dispatch_model_move)
        self.main_canvas.bind("<Double-Button-1>", self.canvas_double_click)
        self.main_canvas.bind("<Configure>", self.canvas_resize)
        self.main_canvas.bind("<MouseWheel>", self.mouse_wheel)
        self.main_canvas.bind("<Button-4>", self.mouse_wheel)
        self.main_canvas.bind("<Button-5>", self.mouse_wheel)
    
    def bind_application_events(self):
        """
        Bind application events to handling methods.
        """
        self.master.bind("<Up>", self.move_cursor_up)
        self.master.bind("<Down>", self.move_cursor_down)
        self.master.bind("<Left>", self.move_cursor_left)
        self.master.bind("<Right>", self.move_cursor_right)
        self.master.bind("<Control-Key-z>", self.undo_operation)
        self.master.bind("<Control-Key-c>", self.copy_ctrl_c)
        self.master.bind("<Control-Key-v>", self.paste_ctrl_v)
        self.master.bind("<Key-d>", self.set_mouse_mode_draw)
        self.master.bind("<Key-m>", self.set_mouse_mode_move)
        self.master.bind("<Key-r>", self.set_mouse_mode_resize)
        self.master.bind("<Key-b>", self.set_mode_rectangle)
        self.master.bind("<Key-c>", self.set_mode_cylinder)
        self.master.bind("<Key-s>", self.set_mode_cylin_sector)
        self.master.bind("<Key-p>", self.set_mode_polygon)
        self.master.bind("<Escape>", self.canvas_interrupt)
        # self.master.bind("<Delete>", self.remove_shape)
        self.master.bind("<Key-plus>", self.view_zoom_in)
        self.master.bind("<Key-minus>", self.view_zoom_out)        

    def load_toolbar_icons(self):
        """
        Try to load toolbar buttons icons. At failing, display appropriate message.
        """
        try:
            self.rectangleIcon = PhotoImage(file = "./icons/icon_rectangle.gif")
            self.cylinderIcon = PhotoImage(file = "./icons/icon_cylinder.gif")
            self.cylinSectorIcon = PhotoImage(file = "./icons/icon_cylinder_sector.gif")
            self.polygonIcon = PhotoImage(file = "./icons/icon_polygon.gif")
            self.exitIcon = PhotoImage(file = "./icons/icon_exit.gif")
            self.plusIcon = PhotoImage(file = "./icons/icon_plus.gif")
            self.minusIcon = PhotoImage(file = "./icons/icon_minus.gif")
            self.playIcon = PhotoImage(file = "./icons/icon_play.gif")
            self.drawIcon = PhotoImage(file = "./icons/icon_draw.gif")
            self.moveIcon = PhotoImage(file = "./icons/icon_move.gif")
            self.resizeIcon = PhotoImage(file = "./icons/icon_resize.gif")
            self.modelIcon = PhotoImage(file = "./icons/icon_model.gif")
            self.surveyIcon = PhotoImage(file = "./icons/icon_survey.gif")
            self.displayIcon = PhotoImage(file = "./icons/icon_display.gif")
            self.rectangleButton.config(image = self.rectangleIcon)
            self.cylinderButton.config(image = self.cylinderIcon)
            self.cylinSectorButton.config(image = self.cylinSectorIcon)
            self.polygonButton.config(image = self.polygonIcon)
            self.exitButton.config(image = self.exitIcon)
            self.zoom_in_button.config(image = self.plusIcon)
            self.zoom_out_button.config(image = self.minusIcon)
            self.parseToGprMaxButton.config(image = self.playIcon)
            self.draw_button.config(image = self.drawIcon)
            self.move_button.config(image = self.moveIcon)
            self.resize_button.config(image = self.resizeIcon)
            self.model_settings_button.config(image = self.modelIcon)
            self.survey_settings_button.config(image = self.surveyIcon)
            self.display_settings_button.config(image = self.displayIcon)
        except Exception as message:
            messagebox.showerror("Error while loading icons", message)
        
    def canvas_refresh(self, *, swap = False):
        """
        Redraw all shapes on canvas.

        :param swap: shapes list selection swap toggle.
        :type swap: boolean
        """
        if(self.coordsys.grid):
            self.coordsys.draw_ticks(self.main_canvas, grid = True)
        for single_shape in self.shapes:
            single_shape.draw(self.main_canvas)
        if(not self.move and not self.resize):
            self.shapes_frame.update_list(self.shapes, swap = swap)
        self.coordsys.obscure_protruding_edges(self.main_canvas)
        self.coordsys.draw_ticks(self.main_canvas)
        self.coordsys.draw(self.main_canvas)
                         
    def canvas_click(self, event):
        """
        Handle a left mouse click event.
        
        :param event: tk mouse click event object.
        :type event: tkinter.Event
        """
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
        """
        Handle a mouse move event.
        
        :param event: tk mouse move event object.
        :type event: tkinter.Event
        """
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
        """
        Display current mouse position in m on the status bar.

        :param event: tk mouse move event object.
        :type event: Tk.Event
        """
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
        """
        Remove all shapes.
        """
        # Register every single deletion operation in stack
        for i, single_shape in enumerate(self.shapes):
            self.operations.append(TOperation("remove_all", shape = deepcopy(single_shape), \
                                              num = i))
        self.shapes = []
        self.main_canvas.delete("all")
        self.canvas_refresh()

    def remove_top_shape(self):
        """
        Remove shape at the top of the list.
        """
        try:
            self.shapes.pop()
        except IndexError:
            messagebox.showerror("Error!", "There are no shapes!")
        self.main_canvas.delete("all")
        self.canvas_refresh()
    
    def remove_shape(self, event):
        """
        Remove a shape if mouse overlapses it.

        :param event: event evoking this method (Del keystroke, RMB click)
        :type event: tkinter.Event
        """
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

    def toggle_grid(self):
        """
        Toggle displaying grid lines.
        """
        if(self.coordsys.grid):
            self.coordsys.toggle_grid("Off")
        else:
            self.coordsys.toggle_grid("On")
        self.main_canvas.delete("all")
        self.canvas_refresh()

    def increase_shapes_width(self, event):
        """
        Increase width of all shapes in the list.

        :param event: tk up arrow press event object.
        :type event: tkinter.Event
        """
        self.shapes_width += 1
        for single_rectangle in self.shapes:
            single_rectangle.width = self.shapes_width

        self.main_canvas.delete("all")
        self.canvas_refresh()
            
    def decrease_shapes_width(self, event):
        """
        Decrease width of all shapes in the list.

        :param event: tk up arrow press event object.
        :type event: tkinter.Event
        """
        self.shapes_width -= 1
        for single_rectangle in self.shapes:
            single_rectangle.width = self.shapes_width

        self.main_canvas.delete("all")
        self.canvas_refresh()

    @property
    def shapes_width(self):
        """
        Property for self.shapes_width.

        :return: shape width.
        :rtype: integer.
        """
        return self.__rectangles_width

    @shapes_width.setter
    def shapes_width(self, shapes_width):
        """
        Setter for self.rectangles_width.

        :param shapes_width: new shapes line width in pixels.
        :type shapes: integer
        """
        if(shapes_width <= 5 and shapes_width >= 1):
            self.__rectangles_width = shapes_width
        else:
            self.__rectangles_width = self.__rectangles_width
    
    def mouse_overlaps_shape(self, x, y, radius):
        """
        Check whether the mouse pointer overlaps a shape. If so, return its list index;
        otherwise return -1.

        :param x: mouse pointer position x coordinate in pixels.
        :typex: integer
        :param y: mouse pointer position y coordinate in pixels.
        :type y: integer
        :param radius: radius of the area around a point, trigerring an overlap.
        :type radius: integer

        :return: overlapped shape list index.
        :rtype: integer
        """
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
            elif(single_shape.type == "Polygon"):
                if(self.mouse_overlaps_polygon(self.shapes[shape_num], \
                                               x, y, radius)): 
                    return shape_num
        return -1

    def mouse_overlaps_rectangle(self, shape, x, y, radius):
        """
        Check whether the mouse pointer overlaps a rectangle.

        :param shape: examined shape object.
        :type shape: TRect
        :param x: mouse pointer position x coordinate in pixels.
        :type x: integer
        :param y: mouse pointer position y coordinate in pixels.
        :type y: integer
        :param radius: radius of the area around a point, trigerring an overlap.
        :type radius: integer

        :return: overlapped rectangle list index.
        :rtype: boolean
        """
        if((x >= shape.point1.x - radius and x <= shape.point1.x + radius \
            and y >= shape.point1.y - radius and y <= shape.point1.y + radius) or \
           (x >= shape.point2.x - radius and x <= shape.point2.x + radius \
            and y >= shape.point2.y - radius and y <= shape.point2.y + radius)):
            return True
        elif((x >= shape.point3.x - radius and x <= shape.point3.x + radius \
              and y >= shape.point3.y - radius and y <= shape.point3.y + radius) or \
             (x >= shape.point4.x - radius and x <= shape.point4.x + radius \
              and y >= shape.point4.y - radius and y <= shape.point4.y + radius)):
            return True
        return False
    
    def mouse_overlaps_cylinder(self, shape, x, y, radius):
        """
        Check whether the mouse pointer overlaps a cylinder.

        :param shape: examined shape object.
        :type shape: TCylin
        :param x: mouse pointer position x coordinate in pixels.
        :type x: integer
        :param y: mouse pointer position y coordinate in pixels.
        :type y: integer
        :param radius: radius of the area around a point, trigerring an overlap.
        :type radius: integer

        :return: overlapped cylinder list index.
        :rtype: boolean
        """
        if(((x - shape.centre.x)**2 + (y - shape.centre.y)**2 >= (shape.radius - radius)**2 and \
            (x - shape.centre.x)**2 + (y - shape.centre.y)**2 <= (shape.radius + radius)**2  ) or\
            (x >= shape.centre.x - radius and x <= shape.centre.x + radius \
            and y >= shape.centre.y - radius and y <= shape.centre.y + radius)):
            return True
        return False
    
    # Check whether mouse overlaps cylinder sector
    def mouse_overlaps_cylinder_sector(self, shape, x, y, radius):
        """
        Check whether the mouse pointer overlaps a cylinder sector.

        :param shape: examined shape object.
        :type shape: TCylinSector
        :param x: mouse pointer position x coordinate in pixels.
        :type x: integer
        :param y: mouse pointer position y coordinate in pixels.
        :type y: integer
        :param radius: radius of the area around a point, trigerring an overlap.
        :type radius: integer

        :return: overlapped cylinder sector list index.
        :rtype: boolean
        """
        if((x <= shape.centre.x + radius and x >= shape.centre.x - radius \
            and y <= shape.centre.y + radius and y >= shape.centre.y - radius) or\
            (x <= shape.boundary_pt1.x + radius and x >= shape.boundary_pt1.x - radius \
            and y <= shape.boundary_pt1.y + radius and y >= shape.boundary_pt1.y - radius) or\
            (x <= shape.boundary_pt2.x + radius and x >= shape.boundary_pt2.x - radius \
            and y <= shape.boundary_pt2.y + radius and y >= shape.boundary_pt2.y - radius)):
            return True
        return False
    
    # Check whether mouse overlaps polygon
    def mouse_overlaps_polygon(self, shape, x, y, radius):
        """
        Check whether the mouse pointer overlaps a polygib.

        :param shape: examined shape object.
        :type shape: TPolygon
        :param x: mouse pointer position x coordinate in pixels.
        :type x: integer
        :param y: mouse pointer position y coordinate in pixels.
        :type y: integer
        :param radius: radius of the area around a point, trigerring an overlap.
        :type radius: integer

        :return: overlapped polygon list index.
        :rtype: boolean
        """
        for pt in shape.points:
            if (x <= pt.x + radius and x >= pt.x - radius \
                and y <= pt.y + radius and y >= pt.y - radius):
                return True
        return False

    def display_right_button_popup(self, event):
        """
        Display right mouse button popup (context) menu.

        :param event: RMB press event object.
        :type event: tkinter.Event
        """
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

    def set_mode_rectangle(self, event = None):
        """
        Set drawn shape to a rectangle.
        
        :param event: button click event object.
        :type event: tkinter.Event
        """
        self.mode = "Rectangle"
        self.mode_rectangle.set(True)
        self.mode_cylinder.set(False)
        self.mode_cylin_sector.set(False)
        self.mode_polygon.set(False)
        self.rectangleButton.config(relief = SUNKEN)
        self.cylinderButton.config(relief = FLAT)
        self.cylinSectorButton.config(relief = FLAT)
        self.polygonButton.config(relief = FLAT)
    
    def set_mode_cylinder(self, event = None):
        """
        Set drawn shape to a cylinder.

        :param event: button click event object.
        :type event: tkinter.Event
        """
        self.mode = "Cylinder"
        self.mode_rectangle.set(False)
        self.mode_cylinder.set(True)
        self.mode_cylin_sector.set(False)
        self.mode_polygon.set(False)
        self.rectangleButton.config(relief = FLAT)
        self.cylinderButton.config(relief = SUNKEN)
        self.cylinSectorButton.config(relief = FLAT)
        self.polygonButton.config(relief = FLAT)

    def set_mode_cylin_sector(self, event = None):
        """
        Set drawn shape to a cylinder sector.

        :param event: button click event object.
        :type event: tkinter.Event
        """
        self.mode = "CylinSector"
        self.mode_rectangle.set(False)
        self.mode_cylinder.set(False)
        self.mode_cylin_sector.set(True)
        self.mode_polygon.set(False)
        self.rectangleButton.config(relief = FLAT)
        self.cylinderButton.config(relief = FLAT)
        self.cylinSectorButton.config(relief = SUNKEN)
        self.polygonButton.config (relief = FLAT)

    def set_mode_polygon(self, event = None):
        """
        Set drawn shape to a polygon.

        :param event: button click event object.
        :type event: tkinter.Event
        """
        self.mode = "Polygon"
        self.mode_rectangle.set(False)
        self.mode_cylinder.set(False)
        self.mode_cylin_sector.set(False)
        self.mode_polygon.set(True)
        self.rectangleButton.config(relief = FLAT)
        self.cylinderButton.config(relief = FLAT)
        self.cylinSectorButton.config(relief = FLAT)
        self.polygonButton.config(relief = SUNKEN)

    def set_mouse_mode_draw(self, event = None):
        """
        Set mouse mode to "draw".

        :param event: button click event object.
        :type event: tkinter.Event
        """
        self.mouse_mode = "draw"
        self.draw_button.config(relief = SUNKEN)
        self.move_button.config(relief = FLAT)
        self.resize_button.config(relief = FLAT)
        self.main_canvas.config(cursor = "pencil")

    def set_mouse_mode_move(self, event = None):
        """
        Set mouse mode to "move".

        :param event: button click event object.
        :param type: tkinter.Event
        """
        self.mouse_mode = "move"
        self.draw_button.config(relief = FLAT)
        self.move_button.config(relief = SUNKEN)
        self.resize_button.config(relief = FLAT)
        self.main_canvas.config(cursor = "fleur")

    def set_mouse_mode_resize(self, event = None):
        """
        Set mouse mode to "resize".

        :param event: button click event object.
        :type event: tkinter.Event
        """
        self.mouse_mode = "resize"
        self.draw_button.config(relief = FLAT)
        self.move_button.config(relief = FLAT)
        self.resize_button.config(relief = SUNKEN)
        self.main_canvas.config(cursor = "sizing")

    def canvas_double_click(self, event):
        """
        Handle a canvas double click, which ends drawing a polygon.

        :param event: canvas double LMB click event object.
        :type event: tkinter.Event
        """
        if(self.mouse_mode == "draw" and self.mode == "Polygon"):
            self.polygon_double_click_draw(event)

    def assign_material_to_shape(self, shape_num, material):
        """
        Assign material to a chosen shape.

        :param shape_num: shape list index.
        :type shape_num: integer
        :param material: material name.
        :type material: string
        """
        self.shapes[shape_num].material = str(material)
    
    def parse_to_gprmax(self):
        """
        Parse model created in program to a gprMax compliant text file.
        """
        parser_string = TParser.parse_shapes(self.materials, self.shapes, self.title)
        preview_window = TOutputPreviewWindow(self.master, parser_string)
        output_file_name = preview_window.result
        if(output_file_name is not None):
            self.run_gprmax(filename = output_file_name)
    
    def change_model_size(self):
        """
        Change model maximal x and y coordinates.
        """
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
                self.view_zoom_reset()
            except Exception as message:
                messagebox.showerror("Error while changing model size!", message)
    
    def canvas_resize(self, event):
        """
        Handle a canvas dimensions alteration event.

        :param event: canvas configure event object.
        :type event: tkinter.Event
        """
        # Resize canvas, should the window resize occur
        try:
            TWindow_Size.MAX_X = event.width
            TWindow_Size.MAX_Y = event.height
            self.coordsys.window_size_update()
            for single_shape in self.shapes:
                single_shape.update_window_positions()
            self.view_zoom_reset()
            self.main_canvas.delete("all")
            self.canvas_refresh()
        except Exception as message:
            messagebox.showerror("Error while changing canvas size!", message)
    
    def display_settings(self):
        """
        Show display settings dialog window.
        """
        input_dialog = TDisplaySettingsWindow(self.master, TTicksSettings.INT_X, \
                                              TTicksSettings.INT_Y, \
                                              TTicksSettings.ROUND_DIGITS, \
                                              TModel_Size.MIN_X, TModel_Size.MIN_Y, \
                                              TModel_Size.MAX_X, TModel_Size.MAX_Y,
                                              TModel_Size.FIT, TTicksSettings.LABEL_INT)
        result = input_dialog.result
        if(result != None):
            try:
                TTicksSettings.INT_X = result[0]
                TTicksSettings.INT_Y = result[1]
                TTicksSettings.ROUND_DIGITS = result[2]
                if(result[3] == "colour"):
                    TColours.FILL = True
                elif(result[3] == "none"):
                    TColours.FILL = False
                TTicksSettings.LABEL_INT = result[4]
                self.view_zoom_reset()
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
        """
        Remove polygon vertex.
        
        :param event: canvas RMB click event object.
        :type event: tkinter.Event
        """
        shape_num = self.mouse_overlaps_shape(event.x, event.y, self.radius)
        if (shape_num > -1):
            if(self.shapes [shape_num].type == "Polygon"):
                self.operations.append(TOperation("edit", shape = deepcopy(self.shapes[shape_num]), \
                                                  num = shape_num))
                for i, pt in enumerate(self.shapes[shape_num].points):
                    if(event.x <= pt.x + self.radius and event.x >= pt.x - self.radius \
                       and event.y <= pt.y + self.radius and event.y >= pt.y - self.radius):
                        break
                self.shapes[shape_num].remove_vertex(i)
                self.main_canvas.delete("all")
                self.canvas_refresh()
    
    #---------------------------------------------------------------------------

    def canvas_interrupt(self, event = None):
        """
        Cease pending mouse operation (draw, move, resize).

        :param event: canvas RMB click event object.
        :type event: tkinter.Event
        """
        self.first_click = False
        self.second_click = False
        self.resize = False
        self.move = False
        self.double_click = False
        self.polygon_points = []
        self.manipulated_shape_num = -1
        self.main_canvas.delete("all")
        self.copy_pos = None
        if(self.mouse_mode == "move" or self.mouse_mode == "resize"):
            if(self.shape_buffer is not None):
                self.shapes.append(self.shape_buffer)
                self.shape_buffer = None
                self.main_canvas.delete("all")
        self.canvas_refresh()

    def create_rectangle(self):
        """
        Create a rectangle from keyboard input.
        """
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
        """
        Create a cylinder from keyboard input.
        """
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
        """
        Create a cylinder sector from keyboard input.
        """
        input_str = simpledialog.askstring ("Input coordinates", "Give cylinder \
                                             sector's centre coordinates,\nradius, \
                                             start and extent angles")
        try:
            tokens = input_str.split ()
            centre = TPoint (float (tokens [0] ), float(tokens [1] ) )
            radius = float(tokens[2])
            start =  float(tokens[3])
            extent = float(tokens[4])
            self.shapes.append(TCylinSector(centre_mod = centre, radius_mod = radius, \
                                            start = start, extent = extent, \
                                            colour = self.shapes_colour, \
                                            width = self.shapes_width))
            self.main_canvas.delete ("all")
            self.canvas_refresh()
        except Exception as message:
            messagebox.showerror("Error while creating polygon!", message)
        else:
            self.operations.append(TOperation("draw", shape = deepcopy(self.shapes[-1]), \
                                              num = len(self.shapes) - 1))

    def create_polygon(self):
        """
        Create a cpolygon from keyboard input.
        """
        input_str = simpledialog.askstring("Input coordinates", \
                                           "Give polygon's coordinates")
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
        """
        Edit model title.
        """
        self.title = simpledialog.askstring("Title", "Give model's title")
        if(self.title):
            self.master.title("gprMax Designer: " + self.title)

    def recolour_randomly(self):
        """
        Assign random colours from AVAILABLE_COLOURS list to all shapes.
        """
        num_of_colours = len(self.AVAILABLE_COLOURS)
        for single_shape in self.shapes:
            random_index = randrange(0, num_of_colours)
            single_shape.fill = self.AVAILABLE_COLOURS[random_index]
        self.main_canvas.delete("all")
        self.canvas_refresh()

    def select_shape(self, event):
        """
        Select a single shape.

        :param event: canvas RMB click event object.
        :type event: tkinter.Event
        """
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
        """
        Distinguish the selected shape on the list in the shapes frame.

        :param shape_num: selected shape list index.
        :type shape_num: integer
        """
        self.shapes_frame.material_box.set(str(self.shapes[shape_num].material))
        self.shapes_frame.shapes_list.select_clear(0, END)
        self.shapes_frame.shapes_list.selection_set(shape_num)
        self.shapes_frame.shapes_list.activate(shape_num)

    def survey_settings(self):
        """
        Show survey settings dialog window and change their values.
        """
        input_dialog = TSurveySettingsWindow(self.master, self)
        result = input_dialog.result
        if(result):
            TSurveySettings.TYPE = result[0]
            TSurveySettings.TSF = result[1]
            TSurveySettings.TIME_WINDOW = result[2]
            TSurveySettings.WAVE_TYPE = result[3]
            TSurveySettings.AMPLITUDE = result[4]
            TSurveySettings.FREQUENCY = result[5]
            TSurveySettings.SRC_TYPE = result[6]
            TSurveySettings.SRC_X = result[7]
            TSurveySettings.SRC_Y = result[8]
            TSurveySettings.RX_X = result[9]
            TSurveySettings.RX_Y = result[10]
            TSurveySettings.MESSAGES = result[11]
            TSurveySettings.GEOM_VIEW = result[12]
            TSurveySettings.GEOM_FILE = result[13]
            TSurveySettings.SNAPSHOT = result[14]
            TSurveySettings.SNAP_TIME = result[15]
            TSurveySettings.SNAP_FILE = result[16]
            if(result[0] == "rx_array"):
                TSurveySettings.RX_STEP_X = result[17]
                TSurveySettings.RX_STEP_Y = result[18]
                TSurveySettings.RX_MAX_X = result[19]
                TSurveySettings.RX_MAX_Y = result[20]
            elif(result[0] == "bscan"):
                TSurveySettings.SRC_STEP_X = result[17]
                TSurveySettings.SRC_STEP_Y = result[18]
                TSurveySettings.RX_STEP_X = result[19]
                TSurveySettings.RX_STEP_Y = result[20]
    
    def edit_shape(self, event):
        """
        Change shape dimensions from keyboard input.

        :param event: canvas RMB click event object.
        :type event: tkinter.Event
        """
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
        """
        Change rectangle dimensions from keyboard input.

        :param shape_num: selected shape list index.
        :type shape_num: integer
        """
        initialvalue = str(self.shapes[shape_num].point1_mod.x) + " " + \
                       str(self.shapes[shape_num].point1_mod.y) + " " + \
                       str(self.shapes[shape_num].point2_mod.x) + " " + \
                       str(self.shapes[shape_num].point2_mod.y)
        input_str = simpledialog.askstring("Input coordinates", "Give rectangles's coordinates", \
                                           initialvalue = initialvalue)
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
            messagebox.showerror("Error while editing a rectangle!", message)
    
    def edit_cylin(self, shape_num):
        """
        Change cylinder dimensions from keyboard input.

        :param shape_num: selected shape list index.
        :type shape_num: integer
        """
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
            messagebox.showerror("Error while editing a cylinder!", message)
    
    def edit_cylin_sector(self, shape_num):
        """
        Change cylinder sector dimensions from keyboard input.

        :param shape_num: selected shape list index.
        :type shape_num: integer
        """
        initialvalue = str(self.shapes[shape_num].centre_mod.x) + " " + \
                       str(self.shapes[shape_num].centre_mod.y) + " " + \
                       str(self.shapes[shape_num].radius_mod) + " " + \
                       str(self.shapes[shape_num].start) + " " + \
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
            messagebox.showerror("Error while editing a cylinder sector!", message)

    def edit_polygon(self, shape_num):
        """
        Display polygon vertices coordinates and enable to change them manually.

        :param shape_num: selected shape list index.
        :type shape_num: integer
        """
        vertices_dialog = TPolygonWindow(self.master, self, self.shapes[shape_num])
        self.select_shape_on_list(shape_num)
        del vertices_dialog
    
    def change_shape_colour(self, event = None, shape_num = None):
        """
        Change selected shape colour using tkInter colorchooser dialog.

        :param event: canvas RMB click event object.
        :type event: tkinter.Event
        :param shape_num: selected shape list index.
        :type shape_num: integer
        """
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
        """
        Ask for new coordinates of a selected polygon vertex.
        
        :param event: canvas RMB click event object.
        :type event: tkinter.Event
        """
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
                initialvalue = str(self.shapes[shape_num].points_mod[i].x) + " " + \
                               str(self.shapes[shape_num].points_mod[i].y)
                input_str = simpledialog.askstring("Input coordinates", "Give polygons vertex's coordinates", \
                                                   initialvalue = initialvalue)
                try:
                    x, y = [float(x) for x in input_str.split()]
                    self.shapes[shape_num].edit_vertex(vertex_num = i, x = x, y = y)
                except Exception as message:
                    messagebox.showerror("Error while manipulating vertex", message)
                self.main_canvas.delete ("all")
                self.canvas_refresh ()
                self.select_shape_on_list(shape_num)
    
    def add_vertex_to_polygon(self, event):
        """
        Add signle vertex to polygon based on current mouse position.
        
        :param event: canvas RMB click event object.
        :type event: tkinter.Event
        """
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
        """
        Return coordinates of a shape characteristic point or a vertex overlapped by the mouse.
        
        :param shape: examined shape object.
        :type shape: TRect, TCylin, TCylinSector, TPolygon
        :param x: mouse pointer position x coordinate in pixels.
        :type x: integer
        :param y: mouse pointer position y coordinate in pixels.
        :type y: integer
        :param radius: radius of the area around a point, trigerring an overlap.
        :type radius: integer

        :return: overlapped point coordinates in pixels.
        :rtype: TPoint
        """
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
        """
        Return coordinates of a rectangle vertex overlapped by the mouse.
        
        :param shape: examined rectangle object.
        :type shape: TRect
        :param x: mouse pointer position x coordinate in pixels.
        :type x: integer
        :param y: mouse pointer position y coordinate in pixels.
        :type y: integer
        :param radius: radius of the area around a point, trigerring an overlap.
        :type radius: integer

        :return: overlapped rectangle point coordinates in pixels.
        :rtype: TPoint
        """
        if(x >= shape.point1.x - radius and x <= shape.point1.x + radius \
           and y >= shape.point1.y - radius and y <= shape.point1.y + radius):
            return deepcopy(shape.point1)
        elif(x >= shape.point2.x - radius and x <= shape.point2.x + radius \
             and y >= shape.point2.y - radius and y <= shape.point2.y + radius):
            return deepcopy(shape.point2)
        elif(x >= shape.point3.x - radius and x <= shape.point3.x + radius \
             and y >= shape.point3.y - radius and y <= shape.point3.y + radius):
            return deepcopy(shape.point3)
        elif(x >= shape.point4.x - radius and x <= shape.point4.x + radius \
             and y >= shape.point4.y - radius and y <= shape.point4.y + radius):
            return deepcopy(shape.point4)

    def cylinder_overlap_coord(self, shape, x, y, radius):
        """
        Return coordinates of a cylinder characteristic point overlapped by the mouse.
        
        :param shape: examined cylinder object.
        :type shape: TCylin
        :param x: mouse pointer position x coordinate in pixels.
        :type x: integer
        :param y: mouse pointer position y coordinate in pixels.
        :type y: integer
        :param radius: radius of the area around a point, trigerring an overlap.
        :type radius: integer

        :return: overlapped cylinder point coordinates in pixels.
        :rtype: TPoint
        """
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
            raise Exception("Can't stick to cylinder edge.")
    
    def cylin_sector_overlap_coord(self, shape, x, y, radius):
        """"
        Return coordinates of a cylinder sector characteristic point overlapped by the mouse.
        
        :param shape: examined cylinder sector object.
        :param type: TCylinSector
        :param x: mouse pointer position x coordinate in pixels.
        :param type: integer
        :param y: mouse pointer position y coordinate in pixels.
        :param type: integer
        :param radius: radius of the area around a point, trigerring an overlap.
        :param type: integer

        :return: overlapped sylinder sector point coordinates in pixels.
        :rtype: TPoint
        """
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
        """
        Return coordinates of a polygon vertex overlapped by the mouse.
        
        :param shape: examined polygon object.
        :type shape: TPolygon
        :param x: mouse pointer position x coordinate in pixels.
        :type x: integer
        :param y: mouse pointer position y coordinate in pixels.
        :type y: integer
        :param radius: radius of the area around a point, trigerring an overlap.
        :type radius: integer

        :return: overlapped polygon point coordinates in pixels.
        :rtype: TPoint
        """
        for pt in shape.points:
            if(x >= pt.x - radius and x <= pt.x + radius \
               and y >= pt.y - radius and y <= pt.y + radius):
                return deepcopy(pt)
        
    def overlap_coord_mod(self, shape, x, y, radius):
        """
        Return model coordinates of a shape characteristic point or a vertex overlapped by the mouse.
        
        :param shape: examined shape object.
        :type shape: TRect, TCylin, TCylinSector, TPolygon
        :param x: mouse pointer position x coordinate in metres.
        :type x: float
        :param y: mouse pointer position y coordinate in metres.
        :type y: float
        :param radius: radius of the area around a point, trigerring an overlap.
        :type radius: float

        :return: overlapped point coordinates in metres.
        :rtype: TPoint
        """
        if(shape.type == "Rectangle"):
            return self.rectangle_overlap_coord_mod(shape, x, y, radius)
        elif(shape.type == "Cylinder"):
            try:
                return self.cylinder_overlap_coord_mod(shape, x, y, radius)
            except:
                return self.winmod(TPoint(x, y))
        elif(shape.type == "CylinSector"):
            return self.cylin_sector_overlap_coord_mod(shape, x, y, radius)
        elif(shape.type == "Polygon"):
            return self.polygon_overlap_coord_mod(shape, x, y, radius)
    
    def rectangle_overlap_coord_mod(self, shape, x, y, radius):
        """
        Return model coordinates of a rectangle vertex overlapped by the mouse.
        
        :param shape: examined rectangle object.
        :type shape: TRect
        :param x: mouse pointer position x coordinate in metres.
        :type x: float
        :param y: mouse pointer position y coordinate in metres.
        :type y: float
        :param radius: radius of the area around a point, trigerring an overlap.
        :type radius: float

        :return: overlapped rectangle point coordinates in metres.
        :rtype: TPoint
        """
        if(x >= shape.point1.x - radius and x <= shape.point1.x + radius \
           and y >= shape.point1.y - radius and y <= shape.point1.y + radius):
            return deepcopy(shape.point1_mod)
        elif(x >= shape.point2.x - radius and x <= shape.point2.x + radius \
             and y >= shape.point2.y - radius and y <= shape.point2.y + radius):
            return deepcopy(shape.point2_mod)
        elif(x >= shape.point3.x - radius and x <= shape.point3.x + radius \
             and y >= shape.point3.y - radius and y <= shape.point3.y + radius):
            return deepcopy(shape.point3_mod)
        elif(x >= shape.point4.x - radius and x <= shape.point4.x + radius \
             and y >= shape.point4.y - radius and y <= shape.point4.y + radius):
            return deepcopy(shape.point4_mod)

    def cylinder_overlap_coord_mod(self, shape, x, y, radius):
        """
        Return model coordinates of a cylinder characteristic point overlapped by the mouse.
        
        :param shape: examined cylinder object.
        :type shape: TCylin
        :param x: mouse pointer position x coordinate in metres.
        :type x: float
        :param y: mouse pointer position y coordinate in metres.
        :type y: float
        :param radius: radius of the area around a point, trigerring an overlap.
        :type radius: float

        :return: overlapped cylinder point coordinates in metres.
        :rtype: TPoint
        """
        if(x >= shape.centre.x - radius and x <= shape.centre.x + radius \
           and y >= shape.centre.y - radius and y <= shape.centre.y + radius):
            return deepcopy(shape.centre_mod)
        elif(x >= shape.centre.x + shape.radius - radius and \
             x <= shape.centre.x + shape.radius + radius and \
             y >= shape.centre.y - radius and y <= shape.centre.y + radius):
             return TPoint(shape.centre_mod.x + shape.radius_mod, shape.centre_mod.y)
        elif(x >= shape.centre.x - shape.radius - radius and \
             x <= shape.centre.x - shape.radius + radius and \
             y >= shape.centre_mod.y - radius and y <= shape.centre_mod.y + radius):
             return TPoint(shape.centre_mod.x - shape.radius_mod, shape.centre_mod.y)
        elif(x >= shape.centre.x - radius and x <= shape.centre.x  + radius and \
             y >= shape.centre.y + shape.radius - radius and \
             y <= shape.centre.y + shape.radius + radius):
             return TPoint(shape.centre_mod.x, shape.centre_mod.y - shape.radius_mod)
        elif(x >= shape.centre.x - radius and x <= shape.centre.x  + radius and \
             y >= shape.centre.y - shape.radius - radius and \
             y <= shape.centre.y - shape.radius + radius):
             return TPoint(shape.centre_mod.x, shape.centre_mod.y + shape.radius_mod)
        else:
            raise Exception("Can't stick to cylinder edge")
    
    def cylin_sector_overlap_coord_mod(self, shape, x, y, radius):
        """
        Return model coordinates of a cylinder sector characteristic point overlapped by the mouse.
        
        :param shape: examined cylinder sector object.
        :type shape: TCylinSector
        :param x: mouse pointer position x coordinate in metres.
        :type x: float
        :param y: mouse pointer position y coordinate in metres.
        :type y: float
        :param radius: radius of the area around a point, trigerring an overlap.
        :type radius: float

        :return: overlapped cylinder sector point coordinates in metres.
        :rtype: TPoint
        """
        if(x >= shape.centre.x - radius and x <= shape.centre.x + radius \
           and y >= shape.centre.y - radius and y <= shape.centre.y + radius):
            return deepcopy(shape.centre_mod)
        elif(x >= shape.boundary_pt1.x - radius and x <= shape.boundary_pt1.x + radius \
             and y >= shape.boundary_pt1.y - radius and y <= shape.boundary_pt1.y + radius):
            return deepcopy(shape.boundary_pt1_mod)
        elif(x >= shape.boundary_pt2.x - radius and x <= shape.boundary_pt2.x + radius \
             and y >= shape.boundary_pt2.y - radius and y <= shape.boundary_pt2.y + radius):
            return deepcopy(shape.boundary_pt2_mod)
    
    def polygon_overlap_coord_mod(self, shape, x, y, radius):
        """
        Return model coordinates of a polygon vertex overlapped by the mouse.
        
        :param shape: examined cylinder sector object.
        :type shape: TCylinSector
        :param x: mouse pointer position x coordinate in metres.
        :type x: float
        :param y: mouse pointer position y coordinate in metres.
        :type y: float
        :param radius: radius of the area around a point, trigerring an overlap.
        :type radius: float

        :return: overlapped polygon point coordinates in metres.
        :rtype: TPoint
        """
        for i, pt in enumerate(shape.points):
            if(x >= pt.x - radius and x <= pt.x + radius \
               and y >= pt.y - radius and y <= pt.y + radius):
                return deepcopy(shape.points_mod[i])
    
    # --------------------------------------------------------------------------

    def draw_click(self, event):
        """
        Handle a click event while the active mouse working mode is set to 'draw'.
        
        :param event: canvas LMB click event object.
        :type event: tkinter.Event
        """
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
        """
        Handle a click event while the active mouse working mode is set to 'draw'
        and shape mode is set to 'Rectangle'.
        
        :param event: canvas LMB click event object.
        :type event: tkinter.Event
        :param overlap_num: list index of a shape overlapped by the mouse.
        :type overlap_num: integer
        """
        if(not self.first_click):
            if(overlap_num > -1):
                click_pt = self.overlap_coord(self.shapes[overlap_num], \
                                              event.x, event.y, self.radius)
            else:
                click_pt = TPoint(event.x, event.y)
            self.first_click_pos = self.winmod(click_pt)
            self.first_click = True
        else:
            self.main_canvas.delete("all")
            if(overlap_num > -1):
                pt = self.overlap_coord(self.shapes[overlap_num], event.x, \
                                        event.y, self.radius)
            else:
                pt = TPoint(event.x, event.y)
            pt_mod = self.winmod(pt)
            self.shapes.append(TRect(point1_mod = self.first_click_pos, \
                                     point2_mod = pt_mod, \
                                     colour = self.shapes_colour, \
                                     width = self.shapes_width))
            self.operations.append(TOperation("draw", shape = deepcopy(self.shapes[-1]), \
                                              num = len(self.shapes)-1))
            self.first_click = False
            self.first_click_pos = None
            self.canvas_refresh()
    
    def cylinder_click_draw(self, event, overlap_num = -1):
        """
        Handle a click event while the active mouse working mode is set to 'draw'
        and shape mode is set to 'Cylinder'.
        
        :param event: canvas LMB click event object.
        :type event: tkinter.Event
        :param overlap_num: list index of a shape overlapped by the mouse.
        :type overlap_num: integer
        """
        if(not self.first_click):
            if(overlap_num > -1):
                click_pt = self.overlap_coord(self.shapes[overlap_num], \
                                              event.x, event.y, self.radius)
            else:
                click_pt = TPoint(event.x, event.y)
            self.first_click_pos = self.winmod(click_pt)
            self.first_click = True
        else:
            self.main_canvas.delete("all")
            if(overlap_num > -1):
                pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
            else:
                pt = TPoint(event.x, event.y)
            pt_mod = self.winmod(pt)
            radius = ((pt_mod.x - self.first_click_pos.x)**2 + (pt_mod.y - self.first_click_pos.y)**2)**0.5
            self.shapes.append(TCylin(centre_mod = self.first_click_pos, \
                                      radius_mod = radius, colour = self.shapes_colour, \
                                      width = self.shapes_width))
            self.operations.append(TOperation("draw", shape = deepcopy(self.shapes[-1]), \
                                              num = len(self.shapes)-1))
            self.first_click = False
            self.file_click_pos = None
            self.canvas_refresh()
    
    def cylin_sector_click_draw(self, event, overlap_num = -1):
        """
        Handle a click event while the active mouse working mode is set to 'draw'
        and shape mode is set to 'CylinSector'.
        
        :param event: canvas LMB click event object.
        :type event: tkinter.Event
        :param overlap_num: list index of a shape overlapped by the mouse.
        :type overlap_num: integer
        """
        if(not self.first_click and not self.second_click):
            if(overlap_num > -1):
                click_pt = self.overlap_coord(self.shapes[overlap_num], \
                                                          event.x, event.y, self.radius)
            else:
                click_pt = TPoint(event.x, event.y)
            self.first_click_pos = self.winmod(click_pt)
            self.first_click = True
            self.second_click = False
        elif(self.first_click and not self.second_click):
            if(overlap_num > -1):
                click_pt = self.overlap_coord(self.shapes[overlap_num], \
                                                           event.x, event.y, self.radius)
            else:
                click_pt = TPoint(event.x, event.y)
            self.second_click_pos = self.winmod(click_pt)
            self.first_click = False
            self.second_click = True
        elif(not self.first_click and self.second_click):
            self.main_canvas.delete("all")
            if(overlap_num > -1):
                bpt2_mon = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
            else:
                bpt2_mon = TPoint(event.x, event.y)
            centre_mon = self.modwin(self.first_click_pos)
            bpt1_mon = self.modwin(self.second_click_pos)
            radius_mon = ((bpt1_mon.x - centre_mon.x)**2 + (bpt1_mon.y - centre_mon.y)**2)**(0.5)
            self.shapes.append(TCylinSector(centre = centre_mon, \
                                            radius = radius_mon, \
                                            colour = self.shapes_colour, \
                                            width = self.shapes_width, \
                                            boundary_pt1 = bpt1_mon, \
                                            boundary_pt2 = bpt2_mon))
            self.operations.append(TOperation("draw", shape = deepcopy(self.shapes[-1]), \
                                              num = len(self.shapes)-1))
            self.first_click = False
            self.first_click_pos = None
            self.second_click = False
            self.second_click_pos = None
            self.canvas_refresh()
    
    def polygon_click_draw(self, event, overlap_num = -1):
        """
        Handle a click event while the active mouse working mode is set to 'draw'
        and shape mode is set to 'Polygon'.
        
        :param event: canvas LMB click event object.
        :type event: tkinter.Event
        :param overlap_num: list index of a shape overlapped by the mouse.
        :type overlap_num: integer
        """
        self.main_canvas.delete("all")
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
        else:
            pt = TPoint(event.x, event.y)
        pt_mod = self.winmod(pt)
        self.polygon_points.append(pt_mod)
        for i, _ in enumerate(self.polygon_points[1:], 1):
            pt_prev = self.modwin(self.polygon_points[i-1])
            pt_curr = self.modwin(self.polygon_points[i])
            self.main_canvas.create_line(pt_prev.x, pt_prev.y, \
                                         pt_curr.x, pt_curr.y, \
                                         fill = self.shapes_colour, \
                                         width = self.shapes_width)
        pt_prev = self.modwin(self.polygon_points[-1])
        self.main_canvas.create_line(pt_prev.x, pt_prev.y, \
                                     event.x, event.y, \
                                     fill = self.shapes_colour, \
                                     width = self.shapes_width)
        self.canvas_refresh()

    def polygon_double_click_draw(self, event):
        """
        Handle a double click event while the active mouse working mode is set to 'draw'
        and shape mode is set to 'Polygon'.
        
        :param event: canvas LMB double click event object.
        :type event: tkinter.Event
        :param overlap_num: list index of a shape overlapped by the mouse.
        :type overlap_num: integer
        """
        overlap_num = self.mouse_overlaps_shape(event.x, event.y, self.radius)
        if(overlap_num > -1 and self.shapes[overlap_num].type == "Polygon"):
            pt_mon = self.modwin(self.polygon_points[0])
            if(overlap_num == self.mouse_overlaps_shape(pt_mon.x, pt_mon.y, \
                                                        self.radius)):
                self.adjacent_polygon(event, overlap_num)
        try:
            self.shapes.append(TPolygon(points_mod = self.polygon_points, \
                                        colour = self.shapes_colour, \
                                        width = self.shapes_width))
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
        """
        Complete a single polygon using points from an adjacent one.
        
        :param event: canvas LMB double click event object.
        :type event: tkinter.Event
        :param overlap_num: list index of a shape overlapped by the mouse.
        :type overlap_num: integer
        """
        pt_beg_mon = self.modwin(self.polygon_points[0])
        pt_beg = self.overlap_coord(self.shapes[overlap_num], pt_beg_mon.x, \
                                    pt_beg_mon.y, self.radius)
        pt_end = self.overlap_coord(self.shapes[overlap_num], event.x, \
                                    event.y, self.radius)
        i_beg, i_end, reverse = self.detect_shared_points_begin_end(self.shapes[overlap_num], pt_beg, pt_end)
        if(not(i_beg + 1 == i_end)):
            if(not reverse):
                # TODO: Calculating areas to one versatile and easy to read function
                area1 = TG.polygon_area(self.polygon_points + \
                                        self.shapes[overlap_num].points_mod[i_end:i_beg:-1])  
                area2 = TG.polygon_area(self.polygon_points + \
                                        self.shapes[overlap_num].points_mod[i_end + 1:] +
                                        self.shapes[overlap_num].points_mod[:i_beg + 1])
                if(area1 < area2):
                    self.polygon_points += self.shapes[overlap_num].points_mod[i_end:i_beg:-1]
                else:
                    self.polygon_points += self.shapes[overlap_num].points_mod[i_end + 1:] + \
                                           self.shapes[overlap_num].points_mod[:i_beg + 1]                 
            else:
                area1 = TG.polygon_area(self.polygon_points + \
                                        self.shapes[overlap_num].points_mod[i_end:i_beg:-1])  
                area2 = TG.polygon_area(self.polygon_points + \
                                        self.shapes[overlap_num].points_mod[i_beg + 1:] +
                                        self.shapes[overlap_num].points_mod[:i_end + 1])
                if(area1 < area2):
                    self.polygon_points += self.shapes[overlap_num].points_mod[i_beg::-1] + \
                                           self.shapes[overlap_num].points_mod[:i_end:-1]
                else:
                    self.polygon_points += self.shapes[overlap_num].points_mod[i_beg+1:i_end]

    def detect_shared_points_begin_end(self, polygon = None, pt_beg = None, pt_end = None):
        """
        Detect first and last of the vertices shared by two polygons.
        
        :param polygon: examined polygon object.
        :type polygon: TPolygon
        :param pt_beg: point from which to start the search.
        :type pt_beg: TPoint
        :param pt_end: point on which to end the search.
        :type pt_end: TPoint
        """
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
        """
        Handle a mouse move event while the active mouse working mode is set to 'draw'.
        
        :param event: canvas mouse move event object.
        :type event: tkinter.Event
        """
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
        """
        Handle a mouse move event while the active mouse working mode is set to 'draw'
        and shape mode is set to 'Rectangle'.
        
        :param event: canvas mouse move event object.
        :type event: tkinter.Event
        :param overlap_num: list index of a shape overlapped by the mouse.
        :type overlap_num: integer
        """
        if(self.first_click == True):
            self.main_canvas.delete("all")
            self.canvas_refresh()
            first_click_mon = self.modwin(self.first_click_pos)
            if(overlap_num > -1):
                pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, \
                                        self.radius)
                self.main_canvas.create_rectangle(first_click_mon.x, \
                                                  first_click_mon.y, pt.x, \
                                                  pt.y, outline = self.shapes_colour, \
                                                  width = self.shapes_width)
            else:
                self.main_canvas.create_rectangle(first_click_mon.x, \
                                                  first_click_mon.y, \
                                                  event.x, event.y, \
                                                  outline = self.shapes_colour, \
                                                  width = self.shapes_width)
    
    def cylinder_mouse_move_draw(self, event, overlap_num = -1):
        """
        Handle a mouse move event while the active mouse working mode is set to 'draw'
        and shape mode is set to 'Cylinder'.
        
        :param event: canvas mouse move event object.
        :type event: tkinter.Event
        :param overlap_num: list index of a shape overlapped by the mouse.
        :type overlap_num: integer
        """
        if (self.first_click == True):
            self.main_canvas.delete("all")
            self.canvas_refresh()
            if(overlap_num > -1):
                first_click_mon = self.overlap_coord(self.shapes[overlap_num], \
                                                     event.x, event.y, self.radius)
            else:
                first_click_mon = self.modwin(self.first_click_pos)
            radius = ((event.x - first_click_mon.x)**2 + (event.y - first_click_mon.y)**2)**0.5                      
            self.main_canvas.create_oval(first_click_mon.x - radius, \
                                         first_click_mon.y - radius, \
                                         first_click_mon.x + radius, \
                                         first_click_mon.y + radius, \
                                         outline = self.shapes_colour, \
                                         width = self.shapes_width)

    def cylin_sector_mouse_move_draw(self, event, overlap_num = -1):
        """
        Handle a mouse move event while the active mouse working mode is set to 'draw'
        and shape mode is set to 'CylindSector'.
        
        :param event: canvas mouse move event object.
        :type event: tkinter.Event
        :param overlap_num: list index of a shape overlapped by the mouse.
        :type overlap_num: integer
        """
        self.main_canvas.delete("all")
        self.canvas_refresh()
        if (self.first_click):
            if(overlap_num > -1):
                pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
            else:
                pt = TPoint(event.x, event.y)
            first_click_mon = self.modwin(self.first_click_pos)
            self.main_canvas.create_line(first_click_mon.x, first_click_mon.y, \
                                         pt.x, pt.y, fill = self.shapes_colour, \
                                         width = self.shapes_width)
        if(self.second_click):
            if(overlap_num > -1):
                pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
            else:
                pt = TPoint(event.x, event.y)
            first_click_mon = self.modwin(self.first_click_pos)
            second_click_mon = self.modwin(self.second_click_pos)
            radius_mon = ((second_click_mon.x - first_click_mon.x)**2 + (second_click_mon.y - first_click_mon.y)**2)**(0.5)
            start, extent = self.calculate_cylin_sector_start_extent(first_click_mon, \
                                                                     second_click_mon, \
                                                                     pt, radius_mon)
            self.main_canvas.create_arc(first_click_mon.x - radius_mon, \
                                        first_click_mon.y - radius_mon, \
                                        first_click_mon.x + radius_mon, \
                                        first_click_mon.y + radius_mon, \
                                        outline = self.shapes_colour, \
                                        width = self.shapes_width, \
                                        style = PIESLICE, start = start, \
                                        extent = extent)

    def polygon_mouse_move_draw(self, event, overlap_num = -1):
        """
        Handle a mouse move event while the active mouse working mode is set to 'draw'
        and shape mode is set to 'Polygon'.
        
        :param event: canvas mouse move event object.
        :type event: tkinter.Event
        :param overlap_num: list index of a shape overlapped by the mouse.
        :type overlap_num: integer
        """
        if(self.polygon_points):
            self.main_canvas.delete("all")
            self.canvas_refresh()
            for i, _ in enumerate(self.polygon_points[1:], 1):
                pt_prev = self.modwin(self.polygon_points[i-1])
                pt_curr = self.modwin(self.polygon_points[i])
                self.main_canvas.create_line(pt_prev.x, pt_prev.y, \
                                             pt_curr.x, pt_curr.y, \
                                             fill = self.shapes_colour, \
                                             width = self.shapes_width)
            if(overlap_num > -1):
                pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
            else:
                pt = TPoint(event.x, event.y)
            pt_prev = self.modwin(self.polygon_points[-1])
            self.main_canvas.create_line(pt_prev.x, pt_prev.y, pt.x, pt.y, \
                                         fill = self.shapes_colour, \
                                         width = self.shapes_width)

    # --------------------------------------------------------------------------

    def move_click(self, event):
        """
        Handle a mouse move event while the active mouse working mode is set to 'move'.
        
        :param event: canvas LMB click event object.
        :type event: tkinter.Event
        """
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
        """
        Make a copy of the shape to be moved.
        
        :param event: canvas LMB click event object.
        :type event: tkinter.Event
        :param overlap_num: list index of a shape overlapped by the mouse.
        :type overlap_num: integer
        """
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
            self.move_const_point = self.overlap_coord_mod(self.shape_buffer, \
                                                           event.x, event.y, \
                                                           self.radius)
    
    def rectangle_click_move_insert(self, event, overlap_num = -1):
        """
        Handle a click event while the active mouse working mode is set to 'move',
        there is a shape being moved and shape mode is set to 'Rectangle'.
        
        :type event: canvas LMB click event object.
        :param type: tkinter.Event
        :param overlap_num: list index of a shape overlapped by the mouse.
        :type overlap_num: integer
        """
        self.main_canvas.delete("all")
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, \
                                    self.radius)
        else:
            pt = TPoint(event.x, event.y)
        pt = self.winmod(pt)
        offset_x = pt.x - self.move_const_point.x
        offset_y = pt.y - self.move_const_point.y
        self.shape_buffer.point1_mod.x += offset_x
        self.shape_buffer.point1_mod.y += offset_y
        self.shape_buffer.point2_mod.x += offset_x
        self.shape_buffer.point2_mod.y += offset_y
        self.shape_buffer.point3_mod.x += offset_x
        self.shape_buffer.point3_mod.y += offset_y
        self.shape_buffer.point4_mod.x += offset_x
        self.shape_buffer.point4_mod.y += offset_y
        self.shape_buffer.update_window_positions()
        self.shapes.insert(self.manipulated_shape_num, self.shape_buffer)
        self.shape_buffer = None
        self.move_const_point = None
        self.manipulated_shape_num = -1
        self.move = False
        self.canvas_refresh()

    def cylinder_click_move_insert(self, event, overlap_num = -1):
        """Handle a click event while the active mouse working mode is set to 'move',
        there is a shape being moved and shape mode is set to 'Cylinder'.
        
        :param event: canvas LMB click event object.
        :type event: tkinter.Event
        :param overlap_num: list index of a shape overlapped by the mouse.
        :type overlap_num: integer
        """
        self.main_canvas.delete("all")
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
        else:
            pt = TPoint(event.x, event.y)
        pt = self.winmod(pt)
        offset_x = pt.x - self.move_const_point.x
        offset_y = pt.y - self.move_const_point.y
        self.shape_buffer.centre_mod.x += offset_x
        self.shape_buffer.centre_mod.y += offset_y
        self.shape_buffer.update_window_positions()
        self.shapes.insert(self.manipulated_shape_num, self.shape_buffer)
        self.shape_buffer = None
        self.move_const_point = None
        self.manipulated_shape_num = -1
        self.move = False
        self.canvas_refresh()

    def cylin_sector_click_move_insert(self, event, overlap_num = -1):
        """
        Handle a click event while the active mouse working mode is set to 'move',
        there is a shape being moved and shape mode is set to 'CylinSector'.
        
        :param event: canvas LMB click event object.
        :type event: tkinter.Event
        :param overlap_num: list index of a shape overlapped by the mouse.
        :type overlap_num: integer
        """
        self.main_canvas.delete("all")
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
        else:
            pt = TPoint(event.x, event.y)
        pt = self.winmod(pt)
        offset_x = pt.x - self.move_const_point.x
        offset_y = pt.y - self.move_const_point.y
        self.shape_buffer.centre_mod.x += offset_x
        self.shape_buffer.centre_mod.y += offset_y
        centre_win = self.modwin(self.shape_buffer.centre_mod)
        radius_win = self.distmodwin(self.shape_buffer.radius_mod)
        bp1, bp2 = self.calculate_cylin_sector_boundary_pts_window(centre_win,\
                                                                   radius_win, \
                                                                   self.shape_buffer.start, \
                                                                   self.shape_buffer.extent)
        self.shape_buffer.boundary_pt1_mod = self.winmod(bp1)
        self.shape_buffer.boundary_pt2_mod = self.winmod(bp2)
        self.shape_buffer.update_window_positions()
        self.shapes.insert(self.manipulated_shape_num, self.shape_buffer)
        self.shape_buffer = None
        self.move_const_point = None
        self.manipulated_shape_num = -1
        self.move = False
        self.canvas_refresh()
    
    def polygon_click_move_insert(self, event, overlap_num = -1):
        """
        Handle a click event while the active mouse working mode is set to 'move',
        there is a shape being moved and shape mode is set to 'Polygon'.
        
        :param event: canvas LMB click event object.
        :type event: tkinter.Event
        :param overlap_num: list index of a shape overlapped by the mouse.
        :type overlap_num: integer
        """
        self.main_canvas.delete("all")
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
        else:
            pt = TPoint(event.x, event.y)
        pt = self.winmod(pt)
        offset_x = pt.x - self.move_const_point.x
        offset_y = pt.y - self.move_const_point.y
        for pt in self.shape_buffer.points_mod:
            pt.x += offset_x
            pt.y += offset_y
        self.shape_buffer.update_window_positions()
        self.shapes.insert(self.manipulated_shape_num, self.shape_buffer)
        self.shape_buffer = None
        self.move_const_point = None
        self.manipulated_shape_num = -1
        self.move = False
        self.canvas_refresh()

    # --------------------------------------------------------------------------

    def move_mouse_move(self, event):
        """
        Handle a mouse move event while the active mouse working mode is set to 'draw'.
        
        :param event: canvas LMB click event object.
        :type event: tkinter.Event
        """
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

    def rectangle_mouse_move_move(self, event, overlap_num = -1):
        """
        Handle a mouse move event while the active mouse working mode is set to 'move'
        and moved shape type is 'Rectangle'.

        :type event: canvas LMB click event object.
        :param type: tkinter.Event
        :param overlap_num: list index of a shape overlapped by the mouse.
        :type overlap_num: integer
        """
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
        else:
            pt = TPoint(event.x, event.y)
        pt = self.winmod(pt)
        offset_x = pt.x - self.move_const_point.x
        offset_y = pt.y - self.move_const_point.y
        offset_x_win = self.distmodwin(offset_x)
        offset_y_win = -self.distmodwin(offset_y)
        self.main_canvas.delete("all")
        self.canvas_refresh()
        pt1_win = self.modwin(self.shape_buffer.point1_mod)
        pt2_win = self.modwin(self.shape_buffer.point2_mod)
        self.main_canvas.create_rectangle(pt1_win.x + offset_x_win, \
                                          pt1_win.y + offset_y_win, \
                                          pt2_win.x + offset_x_win, \
                                          pt2_win.y + offset_y_win, \
                                          outline = self.shape_buffer.colour, \
                                          width = self.shape_buffer.width)
    
    def cylinder_mouse_move_move(self, event, overlap_num = -1):
        """
        Handle a mouse move event while the active mouse working mode is set to 'move'
        and moved shape type is 'Cylinder'.
        
        :param event: canvas LMB click event object.
        :type event: tkinter.Event
        :param overlap_num: list index of a shape overlapped by the mouse.
        :type overlap_num: integer
        """
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, \
                                    self.radius)
        else:
            pt = TPoint(event.x, event.y)
        pt = self.winmod(pt)
        offset_x = pt.x - self.move_const_point.x
        offset_y = pt.y - self.move_const_point.y
        offset_x_win = self.distmodwin(offset_x)
        offset_y_win = -self.distmodwin(offset_y)
        centre_win = self.modwin(self.shape_buffer.centre_mod)
        radius_win = self.distmodwin(self.shape_buffer.radius_mod)
        self.main_canvas.delete("all")
        self.canvas_refresh()
        self.main_canvas.create_oval(centre_win.x + offset_x_win + \
                                     radius_win, \
                                     centre_win.y + offset_y_win + \
                                     radius_win, \
                                     centre_win.x + offset_x_win - \
                                     radius_win, \
                                     centre_win.y + offset_y_win - \
                                     radius_win, \
                                     outline = self.shape_buffer.colour, width = self.shape_buffer.width)
    
    def cylin_sector_mouse_move_move(self, event, overlap_num = -1):
        """
        Handle a mouse move event while the active mouse working mode is set to 'move'
        and moved shape type is 'CylinSector'.
        
        :param event: canvas LMB click event object.
        :type event: tkinter.Event
        :param overlap_num: list index of a shape overlapped by the mouse.
        :type overlap_num: integer
        """
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
        else:
            pt = TPoint(event.x, event.y)
        pt = self.winmod(pt)
        offset_x = pt.x - self.move_const_point.x
        offset_y = pt.y - self.move_const_point.y
        offset_x_win = self.distmodwin(offset_x)
        offset_y_win = -self.distmodwin(offset_y)
        centre_win = self.modwin(self.shape_buffer.centre_mod)
        radius_win = self.distmodwin(self.shape_buffer.radius_mod)
        self.main_canvas.delete("all")
        self.canvas_refresh()
        self.main_canvas.create_arc(centre_win.x + offset_x_win + radius_win, \
                                    centre_win.y + offset_y_win + radius_win, \
                                    centre_win.x + offset_x_win - radius_win, \
                                    centre_win.y + offset_y_win - radius_win, \
                                    start = self.shape_buffer.start, extent = self.shape_buffer.extent, \
                                    outline = self.shape_buffer.colour, width = self.shape_buffer.width)

    def polygon_mouse_move_move(self, event, overlap_num = -1):
        """
        Handle a mouse move event while the active mouse working mode is set to 'move'
        and moved shape type is 'Polygon'.
        
        :param event: canvas LMB click event object.
        :type event: tkinter.Event
        :param overlap_num: list index of a shape overlapped by the mouse.
        :type overlap_num: integer
        """
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
        else:
            pt = TPoint(event.x, event.y)
        pt = self.winmod(pt)
        offset_x = pt.x - self.move_const_point.x
        offset_y = pt.y - self.move_const_point.y
        self.main_canvas.delete("all")
        self.canvas_refresh()
        points_unwrapped = []
        for pt in self.shape_buffer.points_mod:
            tmp = self.modwin(TPoint(pt.x + offset_x, pt.y + offset_y))
            points_unwrapped.append(tmp.x)
            points_unwrapped.append(tmp.y)
        self.main_canvas.create_polygon(points_unwrapped, outline = self.shape_buffer.colour, \
                                        width = self.shape_buffer.width, fill = "")

    # --------------------------------------------------------------------------

    def resize_click(self, event):
        """
        Handle a click event while the active mouse working mode is set to 'resize'.
        
        :param event: canvas LMB click event object.
        :type event: tkinter.Event
        """
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
    
    def click_resize_shape_select(self, event, overlap_num = -1):
        """
        Make a copy of the shape to be resized.
        
        :param event: canvas LMB click event object.
        :type event: tkinter.Event
        :param overlap_num: list index of a shape overlapped by the mouse.
        :type overlap_num: integer
        """
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
            self.resized_point = self.overlap_coord_mod(self.shape_buffer, \
                                                        event.x, event.y, \
                                                        self.radius)

    def rectangle_click_resize_insert(self, event, overlap_num = -1):
        """
        Handle a click event while the active mouse working mode is set to 'resize',
        there is a shape being moved and shape mode is set to 'Rectangle'.

        :param event: canvas LMB click event object.
        :type event: tkinter.Event
        :param overlap_num: list index of a shape overlapped by the mouse.
        :type overlap_num: integer
        """
        self.main_canvas.delete("all")
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
        else:
            pt = TPoint(event.x, event.y)
        pt = self.winmod(pt)
        offset_x = pt.x - self.resized_point.x
        offset_y = pt.y - self.resized_point.y
        if(self.resized_point.x == self.shape_buffer.point1_mod.x and \
           self.resized_point.y == self.shape_buffer.point1_mod.y):
            self.shape_buffer.point1_mod.x += offset_x
            self.shape_buffer.point1_mod.y += offset_y
            self.shape_buffer.point3_mod.x += offset_x
            self.shape_buffer.point4_mod.y += offset_y
        elif(self.resized_point.x == self.shape_buffer.point2_mod.x and \
             self.resized_point.y == self.shape_buffer.point2_mod.y):
            self.shape_buffer.point2_mod.x += offset_x
            self.shape_buffer.point2_mod.y += offset_y
            self.shape_buffer.point3_mod.y += offset_y
            self.shape_buffer.point4_mod.x += offset_x
        elif(self.resized_point.x == self.shape_buffer.point3_mod.x and \
             self.resized_point.y == self.shape_buffer.point3_mod.y):
            self.shape_buffer.point1_mod.x += offset_x
            self.shape_buffer.point2_mod.y += offset_y
            self.shape_buffer.point3_mod.x += offset_x
            self.shape_buffer.point3_mod.y += offset_y
        elif(self.resized_point.x == self.shape_buffer.point4_mod.x and \
             self.resized_point.y == self.shape_buffer.point4_mod.y):
            self.shape_buffer.point1_mod.y += offset_y
            self.shape_buffer.point2_mod.x += offset_x
            self.shape_buffer.point4_mod.x += offset_x
            self.shape_buffer.point4_mod.y += offset_y
        self.shape_buffer.point1_mod.x = TG.round_to_multiple(self.shape_buffer.point1_mod.x, TModel_Size.DX)
        self.shape_buffer.point1_mod.y = TG.round_to_multiple(self.shape_buffer.point1_mod.y, TModel_Size.DY)
        self.shape_buffer.point2_mod.x = TG.round_to_multiple(self.shape_buffer.point2_mod.x, TModel_Size.DX)
        self.shape_buffer.point2_mod.y = TG.round_to_multiple(self.shape_buffer.point2_mod.y, TModel_Size.DY)
        self.shape_buffer.point3_mod.x = TG.round_to_multiple(self.shape_buffer.point3_mod.x, TModel_Size.DX)
        self.shape_buffer.point3_mod.y = TG.round_to_multiple(self.shape_buffer.point3_mod.y, TModel_Size.DY)
        self.shape_buffer.point4_mod.x = TG.round_to_multiple(self.shape_buffer.point4_mod.x, TModel_Size.DX)
        self.shape_buffer.point4_mod.y = TG.round_to_multiple(self.shape_buffer.point4_mod.y, TModel_Size.DY)
        self.shape_buffer.update_window_positions()
        self.shapes.insert(self.manipulated_shape_num, self.shape_buffer)
        self.shape_buffer = None
        self.resized_point = None
        self.manipulated_shape_num = -1
        self.resize = False
        self.canvas_refresh()

    def cylinder_click_resize_insert(self, event, overlap_num = -1):
        """
        Hande a click event while the active mouse working mode is set to 'resize',
        there is a shape being moved and shape mode is set to 'Cylinder'.

        :param event: canvas LMB click event object.
        :type event: tkinter.Event
        :param overlap_num: list index of a shape overlapped by the mouse.
        :type overlap_num: integer
        """
        self.main_canvas.delete("all")
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
        else:
            pt = TPoint(event.x, event.y)
        pt = self.winmod(pt)
        offset_x = pt.x - self.resized_point.x
        offset_y = pt.y - self.resized_point.y
        radius = ((self.resized_point.x + offset_x - self.shape_buffer.centre_mod.x)**2 + \
                  (self.resized_point.y + offset_y - self.shape_buffer.centre_mod.y)**2)**0.5
        self.shape_buffer.radius_mod = radius
        self.shape_buffer.update_window_positions()
        self.shapes.insert(self.manipulated_shape_num, self.shape_buffer)
        self.shape_buffer = None
        self.resized_point = None
        self.manipulated_shape_num = -1
        self.resize = False
        self.canvas_refresh()

    def cylin_sector_click_resize_insert(self, event, overlap_num = -1):
        """
        Handle a click event while the active mouse working mode is set to 'resize',
        there is a shape being moved and shape mode is set to 'CylinSector'.

        :param event: canvas LMB click event object.
        :type event: tkinter.Event
        :param overlap_num: list index of a shape overlapped by the mouse.
        :type overlap_num: integer
        """
        self.main_canvas.delete("all")
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
        else:
            pt = TPoint(event.x, event.y)
        pt_mon = deepcopy(pt)
        pt = self.winmod(pt)
        radius = ((pt.x - self.shape_buffer.centre_mod.x)**2 + \
                  (pt.y - self.shape_buffer.centre_mod.y)**2)**0.5
        radius_mon = self.distmodwin(radius)
        centre_mon = self.modwin(self.shape_buffer.centre_mod)
        bpt1_mon = self.modwin(self.shape_buffer.boundary_pt1_mod)
        bpt2_mon = self.modwin(self.shape_buffer.boundary_pt2_mod)
        if(self.resized_point.x == self.shape_buffer.boundary_pt1_mod.x and \
           self.resized_point.y == self.shape_buffer.boundary_pt1_mod.y):
            start, extent = self.calculate_cylin_sector_start_extent(centre_mon, \
                                                                     pt_mon, \
                                                                     bpt2_mon, \
                                                                     radius_mon)
            start = TG.round_to_multiple(start, min(TModel_Size.DX, TModel_Size.DY))
            extent = TG.round_to_multiple(extent, min(TModel_Size.DX, TModel_Size.DY))
            self.shape_buffer.radius_mod = radius
            self.shape_buffer.start = start
            self.shape_buffer.extent = extent
            bp1, bp2 = self.calculate_cylin_sector_boundary_pts_window(centre_mon, \
                                                                       radius_mon, start, extent)
            self.shape_buffer.boundary_pt1_mod = self.winmod(bp1)
            self.shape_buffer.boundary_pt2_mod = self.winmod(bp2)
        elif(self.resized_point.x == self.shape_buffer.boundary_pt2_mod.x and \
             self.resized_point.y == self.shape_buffer.boundary_pt2_mod.y):
            radius_mon = ((bpt1_mon.x - centre_mon.x)**2 + (bpt1_mon.y - centre_mon.y)**2)**(0.5)
            start, extent = self.calculate_cylin_sector_start_extent(centre_mon, \
                                                                     bpt1_mon, pt_mon, \
                                                                     radius_mon)
            start = TG.round_to_multiple(start, min(TModel_Size.DX, TModel_Size.DY))
            extent = TG.round_to_multiple(extent, min(TModel_Size.DX, TModel_Size.DY))
            self.shape_buffer.extent = extent
            _, bp2 = self.calculate_cylin_sector_boundary_pts_window(centre_mon, \
                                                                     radius_mon, start, extent)
            self.shape_buffer.boundary_pt2_mod = self.winmod(bp2)
        else:
            self.shape_buffer.radius_mod = radius
            bp1, bp2 = self.calculate_cylin_sector_boundary_pts_window(centre_mon, \
                                                                       radius_mon, \
                                                                       self.shape_buffer.start, \
                                                                       self.shape_buffer.extent)
            self.shape_buffer.boundary_pt1_mod = self.winmod(bp1)
            self.shape_buffer.boundary_pt2_mod = self.winmod(bp2)
        self.shape_buffer.update_window_positions()
        self.shapes.insert(self.manipulated_shape_num, self.shape_buffer)
        self.shape_buffer = None
        self.resized_point = None
        self.manipulated_shape_num = -1
        self.resize = False
        self.canvas_refresh()

    def polygon_click_resize_insert(self, event, overlap_num = -1):
        """
        Handle a click event while the  active mouse working mode is set to 'resize',
        there is a shape being moved and shape mode is set to 'Polygon'.

        :param event: canvas LMB click event object.
        :type event: tkinter.Event
        :param overlap_num: list index of a shape overlapped by the mouse.
        :type overlap_num: integer
        """
        self.main_canvas.delete("all")
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
        else:
            pt = TPoint(event.x, event.y)
        pt = self.winmod(pt)
        offset_x = pt.x - self.resized_point.x
        offset_y = pt.y - self.resized_point.y
        for num, pt in enumerate(self.shape_buffer.points_mod):
            if(pt.x == self.resized_point.x and pt.y == self.resized_point.y):
                break
        self.shape_buffer.points_mod[num] = TPoint(self.resized_point.x + offset_x, \
                                                   self.resized_point.y + offset_y)
        # self.shape_buffer.update_model_positions()
        self.shape_buffer.update_window_positions()
        self.shapes.insert(self.manipulated_shape_num, self.shape_buffer)
        self.shape_buffer = None
        self.resized_point = None
        self.manipulated_shape_num = -1
        self.resize = False
        self.canvas_refresh()

    # --------------------------------------------------------------------------

    def resize_mouse_move(self, event):
        """
        Handle a mouse move event while the active mouse working mode is set to 'resize'.
        
        :param event: canvas LMB click event object.
        :type event: tkinter.Event.
        """
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
    
    def rectangle_mouse_move_resize(self, event, overlap_num = -1):
        """
        Handle a mouse move event while the active mouse working mode is set to 'resize'
        and resized shape type is 'Rectangle'.
        
        :param event: canvas LMB click event object.
        :type event: tkinter.Event
        :param overlap_num: list index of a shape overlapped by the mouse.
        :type overlap_num: integer
        """
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
        else:
            pt = TPoint(event.x, event.y)
        pt = self.winmod(pt)
        offset_x = pt.x - self.resized_point.x
        offset_y = pt.y - self.resized_point.y
        self.main_canvas.delete("all")
        self.canvas_refresh()
        if(self.resized_point.x == self.shape_buffer.point1_mod.x and \
           self.resized_point.y == self.shape_buffer.point1_mod.y):
            pt1_x = self.shape_buffer.point1_mod.x + offset_x
            pt1_y = self.shape_buffer.point1_mod.y + offset_y
            pt2_x = self.shape_buffer.point2_mod.x
            pt2_y = self.shape_buffer.point2_mod.y
        elif(self.resized_point.x == self.shape_buffer.point2_mod.x and \
             self.resized_point.y == self.shape_buffer.point2_mod.y):
            pt1_x = self.shape_buffer.point1_mod.x
            pt1_y = self.shape_buffer.point1_mod.y
            pt2_x = self.shape_buffer.point2_mod.x + offset_x
            pt2_y = self.shape_buffer.point2_mod.y + offset_y
        elif(self.resized_point.x == self.shape_buffer.point3_mod.x and \
             self.resized_point.y == self.shape_buffer.point3_mod.y):
            pt1_x = self.shape_buffer.point1_mod.x + offset_x
            pt1_y = self.shape_buffer.point4_mod.y
            pt2_x = self.shape_buffer.point4_mod.x
            pt2_y = self.shape_buffer.point2_mod.y + offset_y
        elif(self.resized_point.x == self.shape_buffer.point4_mod.x and \
             self.resized_point.y == self.shape_buffer.point4_mod.y):
            pt1_x = self.shape_buffer.point1_mod.x
            pt1_y = self.shape_buffer.point1_mod.y + offset_y
            pt2_x = self.shape_buffer.point2_mod.x + offset_x
            pt2_y = self.shape_buffer.point2_mod.y
        pt1 = TPoint(pt1_x, pt1_y)
        pt2 = TPoint(pt2_x, pt2_y)
        pt1 = self.modwin(pt1)
        pt2 = self.modwin(pt2)
        self.main_canvas.create_rectangle(pt1.x, pt1.y, pt2.x, pt2.y, \
                                          outline = self.shape_buffer.colour, \
                                          width = self.shape_buffer.width)

    def cylinder_mouse_move_resize(self, event, overlap_num = -1):
        """
        Handle a mouse move event while the active mouse working mode is set to 'resize'
        and resized shape type is 'Cylinder'.
        
        :param event: canvas LMB click event object.
        :type event: tkinter.Event
        :param overlap_num: list index of a shape overlapped by the mouse.
        :type overlap_num: integer
        """
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
        else:
            pt = TPoint(event.x, event.y)
        pt = self.winmod(pt)
        offset_x = pt.x - self.resized_point.x
        offset_y = pt.y - self.resized_point.y
        self.main_canvas.delete("all")
        self.canvas_refresh()
        radius = ((self.resized_point.x + offset_x - self.shape_buffer.centre_mod.x)**2 + \
                  (self.resized_point.y + offset_y - self.shape_buffer.centre_mod.y)**2)**0.5
        radius_mon = self.distmodwin(radius)
        centre_mon = self.modwin(self.shape_buffer.centre_mod)
        self.main_canvas.create_oval(centre_mon.x + radius_mon, \
                                     centre_mon.y + radius_mon, \
                                     centre_mon.x - radius_mon, \
                                     centre_mon.y - radius_mon, \
                                     outline = self.shape_buffer.colour, width = self.shape_buffer.width)

    def cylin_sector_mouse_move_resize(self, event, overlap_num = -1):
        """
        Handle a mouse move event while the active mouse working mode is set to 'resize'
        and resized shape type is 'CylinSector'.
        
        :param event: canvas LMB click event object.
        :type event: tkinter.Event
        :param overlap_num: list index of a shape overlapped by the mouse.
        :type overlap_num: integer
        """
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
        else:
            pt = TPoint(event.x, event.y)
        pt_mon = deepcopy(pt)
        pt = self.winmod(pt)
        centre_mon = self.modwin(self.shape_buffer.centre_mod)
        bpt1_mon = self.modwin(self.shape_buffer.boundary_pt1_mod)
        bpt2_mon = self.modwin(self.shape_buffer.boundary_pt2_mod)
        if(self.resized_point.x == self.shape_buffer.boundary_pt1_mod.x and \
           self.resized_point.y == self.shape_buffer.boundary_pt1_mod.y):
            radius_mon = ((pt_mon.x - centre_mon.x)**2 + \
                          (pt_mon.y - centre_mon.y)**2)**(0.5)
            start, extent = self.calculate_cylin_sector_start_extent(centre_mon, \
                                                                     pt_mon, bpt2_mon, \
                                                                     radius_mon)
        elif(self.resized_point.x == self.shape_buffer.boundary_pt2_mod.x and \
             self.resized_point.y == self.shape_buffer.boundary_pt2_mod.y):
            radius_mon = ((bpt1_mon.x - centre_mon.x)**2 + \
                          (bpt1_mon.y - centre_mon.y)**2)**(0.5)
            start, extent = self.calculate_cylin_sector_start_extent(centre_mon, \
                                                                     bpt1_mon, pt_mon, 
                                                                     radius_mon)
        else:
            start = self.shape_buffer.start
            extent = self.shape_buffer.extent
        self.main_canvas.delete("all")
        self.canvas_refresh()
        self.main_canvas.create_arc(centre_mon.x + radius_mon, \
                                    centre_mon.y + radius_mon, \
                                    centre_mon.x - radius_mon, \
                                    centre_mon.y - radius_mon, \
                                    start = start, extent = extent, \
                                    outline = self.shape_buffer.colour, \
                                    width = self.shape_buffer.width)

    def polygon_mouse_move_resize(self, event, overlap_num = -1):
        """
        Handle a mouse move event while the active mouse working mode is set to 'resize'
        and moved shape type is 'Polygon'.

        :param event: canvas LMB click event object.
        :type event: tkinter.Event
        :param overlap_num: list index of a shape overlapped by the mouse.
        :type overlap_num: integer
        """
        if(overlap_num > -1):
            pt = self.overlap_coord(self.shapes[overlap_num], event.x, event.y, self.radius)
        else:
            pt = TPoint(event.x, event.y)
        pt = self.winmod(pt)
        offset_x = pt.x - self.resized_point.x
        offset_y = pt.y - self.resized_point.y
        pts_mod = deepcopy(self.shape_buffer.points_mod)
        pts_mon = []
        for pt in pts_mod:
            if(pt.x == self.resized_point.x and pt.y == self.resized_point.y):
                pt.x += offset_x
                pt.y += offset_y
            tmp = self.modwin(pt)
            pts_mon.append(tmp.x)
            pts_mon.append(tmp.y)
        self.main_canvas.delete("all")
        self.canvas_refresh()
        self.main_canvas.create_polygon(pts_mon, outline = self.shape_buffer.colour, \
                                        width = self.shape_buffer.width, fill = "")
    
    # --------------------------------------------------------------------------

    def calculate_cylin_sector_start_extent(self, centre, bp1, bp2, radius):
        """
        Calculate the cylinder sector start and extent angles given 3 points
        constituing it.

        :param centre: cylinder sector centre coordinates.
        :type centre: TPoint
        :param bp1: first boundary point, establishing radius starting the slice.
        :type bp1: TPoint
        :param bp2: second boundary point, establishing radius ending the slice.
        :type bp2: TPoint
        :param radius: cylinder sector radius.
        :type radius: float

        :return: cylinder sector start and extent angles in degrees.
        :rtype: float, float
        """
        if(bp1.x >= centre.x):
            start = degrees(asin((centre.y - bp1.y)/radius))
        else:
            start = 180 - degrees(asin((centre.y - bp1.y)/radius))
        if(start < 0):
            start += 360
        b1 = ((bp1.x - bp2.x)**2 + (bp1.y - bp2.y)**2)**(0.5)
        b2 = ((bp2.x - centre.x)**2 + (bp2.y - centre.y)**2)**(0.5)
        # Check whether boundry points and centre are colinear
        try:
            factor = -((b1**2 - b2**2 - radius**2)/(2*b2*radius))
        except ValueError:
            extent = 180
        else:
            try:
                extent = degrees(acos(factor))
            except ValueError:
                extent = 180
        # Check whether second boundary point is located to the right of the centre -- first boundary point line
        if(((bp2.x - centre.x)*sin(radians(start)) + \
            (bp2.y - centre.y)*cos(radians(start))) > 0 and extent != 180):
            extent = 360 - extent
        # Round extent to 90, 180 or 270 degree if it differs no more than 0.5 degree from those values
        tresh = 0.5
        if(abs(extent - 90) <= tresh):
            extent = 90
        elif(abs(extent - 180) <= tresh):
            extent = 180
        elif(abs(extent - 270) <= tresh):
            extent = 270
        return start, extent
    
    def calculate_cylin_sector_boundary_pts_window(self, centre, radius, start, extent):
        """
        Calculate the cylinder sector boundary points given its centre, radius,
        start and extent angles.

        :param centre: cylinder sector centre coordinates.
        :type centre: TPoint
        :param radius: cylinder sector radius.
        :type radius: float
        :param start: angle (in degrees) between positive OX halfaxis and centre-bp1 radius.
        :type start: float
        :param extent: angle (in degrees) between centre-bp1 radius and centree-bp2 radius.
        :type extent: float

        :return: cylinder sector boundary points.
        :rtype: TPoint, TPoint
        """
        bp1 = TPoint(int(centre.x + cos(radians(start))*radius), \
                     int(centre.y - sin(radians(start))*radius))
        bp2 = TPoint(int(centre.x + cos(radians(start + extent))*radius), \
                     int(centre.y - sin(radians(start + extent))*radius))
        return bp1, bp2
    
    # --------------------------------------------------------------------------

    def move_cursor_up(self, event):
        """
        Manually move the mouse cursor one pixel up with a keystroke.
        
        :param event: window up arrow press event object.
        :type event: tkinter.Event
        """
        x = self.master.winfo_pointerx()
        y = self.master.winfo_pointery()
        abs_coord_x = x - self.master.winfo_rootx()
        abs_coord_y = y - self.master.winfo_rooty()
        self.master.event_generate('<Motion>', warp = True, x = abs_coord_x, y = abs_coord_y - 1)
    
    def move_cursor_down(self, event):
        """
        Manually move the mouse cursor one pixel down with a keystroke.
        
        :param event: window down arrow press event object.
        :type event: tkinter.Event
        """
        x = self.master.winfo_pointerx()
        y = self.master.winfo_pointery()
        abs_coord_x = x - self.master.winfo_rootx()
        abs_coord_y = y - self.master.winfo_rooty()
        self.master.event_generate('<Motion>', warp = True, x = abs_coord_x, y = abs_coord_y + 1)

    def move_cursor_left(self, event):
        """
        Manually move the mouse cursor one pixel left with a keystroke.
        
        :param event: window left arrow press event object.
        :type event: tkinter.Event
        """
        x = self.master.winfo_pointerx()
        y = self.master.winfo_pointery()
        abs_coord_x = x - self.master.winfo_rootx()
        abs_coord_y = y - self.master.winfo_rooty()
        self.master.event_generate('<Motion>', warp = True, x = abs_coord_x - 1, y = abs_coord_y)

    def move_cursor_right(self, event):
        """
        Manually move the mouse cursor one pixel right with a keystroke.
        
        :param event: window right arrow press event object.
        :type event: tkinter.Event
        """
        x = self.master.winfo_pointerx()
        y = self.master.winfo_pointery()
        abs_coord_x = x - self.master.winfo_rootx()
        abs_coord_y = y - self.master.winfo_rooty()
        self.master.event_generate('<Motion>', warp = True, x = abs_coord_x + 1, y = abs_coord_y)

    # --------------------------------------------------------------------------

    def undo_operation(self, event = None):
        """
        Undo last operation.
        
        :param event: object of the event evoking this method (keyboard shortcut,
                      mouse menu position).
        :type event: tkinter.Event
        """
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
            elif(operation.o_type == "paste"):
                del self.shapes[operation.num]
            else:
                self.operations.append(operation)
            self.main_canvas.delete("all")
            self.canvas_refresh()
    
    def run_gprmax(self, filename = None):
        """
        Run gprMax on specified input file.

        :param filename: input file name.
        :type filename: string
        """
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
            if(sys.platform == "win32"):
                command = "start cmd /K run_gprmax.bat compute " + "\"" + filename + "\"" + \
                        " -n " + str(n_iter) + " --geometry-fixed"
            elif(sys.platform == "linux" or sys.platform == "linux2" or\
                 sys.platform == "darwin"):
                raise NotImplementedError("First create the shell script!")
            sts = subprocess.call(command, shell = True)
            del sts
    
    def view_zoom_in(self, event = None):
        """
        Zoom in the model view.

        :param event: object of the event evoking this method (keyboard shortcut, 
                      mouse menu position, toolbar button).
        :type event: tkinter.Event
        """
        if(TModel_Size.FIT):
            TModel_Size.FIT = False
            TModel_Size.MIN_X = 0.0
            TModel_Size.MIN_Y = 0.0
            len_x_mon = TWindow_Size.MAX_X - TWindow_Size.MIN_X - \
                            2*TWindow_Size.MARG_X
            len_y_mon = TWindow_Size.MAX_Y - TWindow_Size.MIN_Y - \
                            2*TWindow_Size.MARG_Y
            if(self.len_tot_x < self.len_tot_y):
                TModel_Size.MAX_X = self.len_tot_x
                TModel_Size.MAX_Y = round(self.len_tot_x/len_x_mon*len_y_mon, \
                                          TTicksSettings.ROUND_DIGITS)
            elif(self.len_tot_x > self.len_tot_y):
                TModel_Size.MAX_X = round(self.len_tot_y/len_y_mon*len_x_mon, \
                                          TTicksSettings.ROUND_DIGITS)
                TModel_Size.MAX_Y = self.len_tot_y
            else:
                if(len_x_mon > len_y_mon):
                    TModel_Size.MAX_X = self.len_tot_x
                    TModel_Size.MAX_Y = round(self.len_tot_x/len_x_mon*len_y_mon, \
                                            TTicksSettings.ROUND_DIGITS)
                elif(len_x_mon < len_y_mon):
                    TModel_Size.MAX_X = round(self.len_tot_y/len_y_mon*len_x_mon, \
                                            TTicksSettings.ROUND_DIGITS)
                    TModel_Size.MAX_Y = self.len_tot_y
                else:
                    TModel_Size.MAX_X = self.len_tot_x
                    TModel_Size.MAX_Y = self.len_tot_y
            self.scrollbars_zoom_in()
        else:
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
        if(event is None):
            x = self.main_canvas.winfo_pointerx()
            y = self.main_canvas.winfo_pointery()
            abs_coord_x = x - self.main_canvas.winfo_rootx()
            abs_coord_y = y - self.main_canvas.winfo_rooty()
            event = Event()
            event.x = abs_coord_x
            event.y = abs_coord_y
        self.canvas_mouse_move(event)

    def view_zoom_out(self, event = None):
        """
        Zoom out the model view.

        :param event: object of the event evoking this method (keyboard shortcut, 
                      mouse menu position, toolbar button).
        :type event: tkinter.Event
        """
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
            TModel_Size.MIN_Y = 0.0
            len_x_mon = TWindow_Size.MAX_X - TWindow_Size.MIN_X - \
                            2*TWindow_Size.MARG_X
            len_y_mon = TWindow_Size.MAX_Y - TWindow_Size.MIN_Y - \
                            2*TWindow_Size.MARG_Y
            if(self.len_tot_x < self.len_tot_y):
                TModel_Size.MAX_X = self.len_tot_x
                TModel_Size.MAX_Y = round(self.len_tot_x/len_x_mon*len_y_mon, \
                                          TTicksSettings.ROUND_DIGITS)
            elif(self.len_tot_x > self.len_tot_y):
                TModel_Size.MAX_X = round(self.len_tot_y/len_y_mon*len_x_mon, \
                                          TTicksSettings.ROUND_DIGITS)
                TModel_Size.MAX_Y = self.len_tot_y
            else:
                if(len_x_mon > len_y_mon):
                    TModel_Size.MAX_X = self.len_tot_x
                    TModel_Size.MAX_Y = round(self.len_tot_x/len_x_mon*len_y_mon, \
                                            TTicksSettings.ROUND_DIGITS)
                elif(len_x_mon < len_y_mon):
                    TModel_Size.MAX_X = round(self.len_tot_y/len_y_mon*len_x_mon, \
                                            TTicksSettings.ROUND_DIGITS)
                    TModel_Size.MAX_Y = self.len_tot_y
                else:
                    TModel_Size.MAX_X = self.len_tot_x
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
        if(event is None):
            x = self.main_canvas.winfo_pointerx()
            y = self.main_canvas.winfo_pointery()
            abs_coord_x = x - self.main_canvas.winfo_rootx()
            abs_coord_y = y - self.main_canvas.winfo_rooty()
            event = Event()
            event.x = abs_coord_x
            event.y = abs_coord_y
        self.canvas_mouse_move(event)
    
    def view_zoom_reset(self):
        """
        Restore default model view.
        """
        TModel_Size.FIT = True
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
        x = self.main_canvas.winfo_pointerx()
        y = self.main_canvas.winfo_pointery()
        abs_coord_x = x - self.main_canvas.winfo_rootx()
        abs_coord_y = y - self.main_canvas.winfo_rooty()
        event = Event()
        event.x = abs_coord_x
        event.y = abs_coord_y
        self.canvas_mouse_move(event)
    
    def scrollbars_zoom_in(self):
        """
        Scale scrollbars after zooming in the model view.
        """
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
        elif(self.scale == 100.0 and TModel_Size.FIT):
            self.main_horizontal_scrollbar.set(0, 1)
            self.main_vertical_scrollbar.set(0, 1)
        elif(self.scale == 100.0 and not TModel_Size.FIT):
            ratio = self.len_tot_x/self.len_tot_y
            len_x_mon = TWindow_Size.MAX_X - TWindow_Size.MIN_X - \
                        2*TWindow_Size.MARG_X
            len_y_mon = TWindow_Size.MAX_Y - TWindow_Size.MIN_Y - \
                        2*TWindow_Size.MARG_Y
            if(ratio > 1.0):
                self.main_horizontal_scrollbar.set(0, len_x_mon/(ratio*len_y_mon))
                self.main_vertical_scrollbar.set(0, 1)
            elif(ratio < 1.0):
                self.main_horizontal_scrollbar.set(0, 1)
                self.main_vertical_scrollbar.set(1 - (ratio*len_y_mon/len_x_mon), 1)
            else:
                if(len_x_mon > len_y_mon):
                    self.main_horizontal_scrollbar.set(0, 1)
                    self.main_vertical_scrollbar.set(1-len_y_mon/len_x_mon, 1)
                elif(len_x_mon < len_y_mon):
                    self.main_horizontal_scrollbar.set(0, len_x_mon/len_y_mon)
                    self.main_vertical_scrollbar.set(0, 1)
                else:
                    self.main_horizontal_scrollbar.set(0, 1)
                    self.main_vertical_scrollbar.set(0, 1)
    
    def scrollbars_zoom_out(self):
        """
        Scale scrollbars after zooming out the model view.
        """
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
        elif(self.scale == 100.0 and TModel_Size.FIT):
            self.main_horizontal_scrollbar.set(0, 1)
            self.main_vertical_scrollbar.set(0, 1)
        elif(self.scale == 100.0 and not TModel_Size.FIT):
            ratio = self.len_tot_x/self.len_tot_y
            if(ratio > 1.0):
                self.main_horizontal_scrollbar.set(0, 1/ratio)
                self.main_vertical_scrollbar.set(0, 1)
            elif(ratio < 1.0):
                self.main_horizontal_scrollbar.set(0, 1)
                self.main_vertical_scrollbar.set(1 - ratio, 1)
            else:
                len_x_mon = TWindow_Size.MAX_X - TWindow_Size.MIN_X - \
                            2*TWindow_Size.MARG_X
                len_y_mon = TWindow_Size.MAX_Y - TWindow_Size.MIN_Y - \
                                2*TWindow_Size.MARG_Y
                if(len_x_mon > len_y_mon):
                    self.main_horizontal_scrollbar.set(0, 1)
                    self.main_vertical_scrollbar.set(1-len_y_mon/len_x_mon, 1)
                elif(len_x_mon < len_y_mon):
                    self.main_horizontal_scrollbar.set(0, len_x_mon/len_y_mon)
                    self.main_vertical_scrollbar.set(0, 1)
                else:
                    self.main_horizontal_scrollbar.set(0, 1)
                    self.main_vertical_scrollbar.set(0, 1)
    
    def model_horizontal_scroll(self, action, number, units = ""):
        """
        Handle the visible model area move in the x direction.
        
        :param action: type of action performed on the scrollbar.
        :type action: string
        :param number: displacement of the scrollbar.
        :type number: float
        :param units: units of the displacement.
        :type units: string
        """
        hbar_pos = self.main_horizontal_scrollbar.get()
        hbar_pos = (Decimal(str(hbar_pos[0])), Decimal(str(hbar_pos[1])))
        hbar_len = Decimal(str(1/(self.scale/100)))
        x_y_ratio = Decimal(str(min(self.len_tot_x, self.len_tot_y)/ \
                                    max(self.len_tot_x, self.len_tot_y)))
        len_x_mon = TWindow_Size.MAX_X - TWindow_Size.MIN_X - \
                            2*TWindow_Size.MARG_X
        len_y_mon = TWindow_Size.MAX_Y - TWindow_Size.MIN_Y - \
                            2*TWindow_Size.MARG_Y
        if(not TModel_Size.FIT and (self.len_tot_x > self.len_tot_y)):
            hbar_len *= x_y_ratio*Decimal(str(len_x_mon/len_y_mon))
        elif(not TModel_Size.FIT and (self.len_tot_x == self.len_tot_y) and \
             (len_x_mon < len_y_mon)):
            hbar_len *= Decimal(str(len_x_mon/len_y_mon))
        try:
            dx_float = self.main_horizontal_scrollbar.delta(int(number), 0)
            dx = Decimal(str(dx_float))
        except:
            # Dragging the scrollbar
            new_pos_lower = Decimal(number)
            new_pos_upper = new_pos_lower + Decimal(str(hbar_len))
        else:
            if(hbar_pos[0] + dx < 0):
                dx = -hbar_pos[0]
            elif(hbar_pos[1] + dx > 1):
                dx = (1 - hbar_pos[1])
            new_pos_lower = hbar_pos[0] + dx
            new_pos_upper = hbar_pos[1] + dx
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
        """
        Handle the visible model area move in the y direction.
        
        :param action: type of action performed on the scrollbar.
        :type action: string
        :param number: displacement of the scrollbar.
        :type number: float
        :param units: units of the displacement.
        :type units: string
        """
        # Convert used quantities to decimal in order to obtain higher
        # floating point accuracy
        vbar_pos = self.main_vertical_scrollbar.get()
        vbar_pos = (Decimal(str(vbar_pos[0])), Decimal(str(vbar_pos[1])))
        vbar_len = Decimal(str(1/(self.scale/100)))
        x_y_ratio = Decimal(str(min(self.len_tot_x, self.len_tot_y)/ \
                                    max(self.len_tot_x, self.len_tot_y)))
        len_x_mon = TWindow_Size.MAX_X - TWindow_Size.MIN_X - \
                            2*TWindow_Size.MARG_X
        len_y_mon = TWindow_Size.MAX_Y - TWindow_Size.MIN_Y - \
                            2*TWindow_Size.MARG_Y
        if(not TModel_Size.FIT and (self.len_tot_x < self.len_tot_y)):
            vbar_len *= x_y_ratio*Decimal(str(len_y_mon/len_x_mon))
        elif(not TModel_Size.FIT and (self.len_tot_x == self.len_tot_y) and \
             (len_y_mon < len_x_mon)):
            vbar_len *= Decimal(str(len_y_mon/len_x_mon))
        try:
            dy_float = self.main_horizontal_scrollbar.delta(int(number), 0)
            dy = Decimal(str(dy_float))
        except:
            new_pos_lower = Decimal(number)
            new_pos_upper = new_pos_lower + Decimal(str(vbar_len))
        else:
            if(vbar_pos[0] + dy < 0.0):
                dy = -vbar_pos[0]
            elif(vbar_pos[1] + dy > 1.0):
                dy = (1 - vbar_pos[1])
            new_pos_lower = vbar_pos[0] + dy
            new_pos_upper = vbar_pos[1] + dy
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

    # --------------------------------------------------------------------------

    def read_model_file(self):
        """
        Read and load a GprMax compliant input file.
        """
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

    def handle_input_command(self, line, line_num):
        """
        Recognise and handle a command given in a line.
        
        :param line: line to be parsed.
        :type line: string
        :param line_num: parsed line number.
        :type line_num: integer
        """
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
        """
        Export a gprMax output file in HDF5 format to ASCII.
        """
        filename = filedialog.askopenfilename(initialdir = '.', title = "Select file", \
                                              filetypes = [("gprMax output files", "*.out"), \
                                              ("All files", "*.*")])
        h5file = h5py.File(filename)
        iterations = h5file.attrs["Iterations"]
        title = h5file.attrs["Title"]
        dt = h5file.attrs["dt"]
        ver = h5file.attrs["gprMax"]
        nrx = h5file.attrs["nrx"]
        try:
            traces = h5file["rxs"]["rx1"]["Ez"].shape[1]
        except:
            traces = 1
        dims = 2
        if(traces == 1):
            dims = 1
        metafilename = (filename.split("."))[0] + "_meta.txt"
        with open(metafilename, "w") as metafile:
            metafile.write("title: {}\n".format(title))
            metafile.write("gprMax version: {}\n".format(ver))
            metafile.write("no of iterations: {}\n".format(iterations))
            metafile.write("time increment [s]: {}\n".format(dt))
            metafile.write("total time [s]: {}\n".format(dt*iterations))
            metafile.write("no of traces: {}\n".format(traces))
            metafile.write("no of rxs per src: {}\n".format(nrx))
        components_window = TTraceWindow(self.master, show_fft = False)
        components = components_window.result
        if("Ex" in components):
            exfilename = (filename.split("."))[0] + "_ex.txt"
            exdata = h5file["rxs"]["rx1"]["Ex"]
            exdata = exdata[()].transpose()
            with open(exfilename, "w") as exfile:
                self.write_array_to_file(exfile, exdata, dims)
        if("Ey" in components):
            eyfilename = (filename.split("."))[0] + "_ey.txt"
            eydata = h5file["rxs"]["rx1"]["Ey"]
            eydata = eydata[()].transpose()
            with open(eyfilename, "w") as eyfile:
                self.write_array_to_file(eyfile, eydata, dims)
        if("Ez" in components):
            ezfilename = (filename.split("."))[0] + "_ez.txt"
            ezdata = h5file["rxs"]["rx1"]["Ez"]
            ezdata = ezdata[()].transpose()
            with open(ezfilename, "w") as ezfile:
                self.write_array_to_file(ezfile, ezdata, dims)
        if("Hx" in components):
            hxfilename = (filename.split("."))[0] + "_hx.txt"
            hxdata = h5file["rxs"]["rx1"]["Hx"]
            hxdata = hxdata[()].transpose()
            with open(hxfilename, "w") as hxfile:
                self.write_array_to_file(hxfile, hxdata, dims)
        if("Hy" in components):
            hyfilename = (filename.split("."))[0] + "_hy.txt"
            hydata = h5file["rxs"]["rx1"]["Hy"]
            hydata = hydata[()].transpose()
            with open(hyfilename, "w") as hyfile:
                self.write_array_to_file(hyfile, hydata, dims)
        if("Hz" in components):
            hzfilename = (filename.split("."))[0] + "_hz.txt"
            hzdata = h5file["rxs"]["rx1"]["Hz"]
            hzdata = hzdata[()].transpose()
            with open(hzfilename, "w") as hzfile:
                self.write_array_to_file(hzfile, hzdata, dims)
        
    def write_array_to_file(self, fileh, array, dims = 2):
        """
        Write a two-dimensional array into a ASCII file row by row.

        :param fileh: file handler.
        :type fileh: _io.TextIOWrapper
        :param array: array to be saved.
        :type array: list
        :param dims: number of dimensions.
        :type dims: integer
        """
        length = len(array)
        if(dims > 1):
            for i, row in enumerate(array):
                for elem in row[:-1]:
                    fileh.write(str(elem) + ", ")
                fileh.write(str(row[-1]))
                if(i != (length - 1)):
                    fileh.write("\n")
        else:
            for elem in array[:-1]:
                fileh.write(str(elem) + ", ")
            fileh.write(str(array[-1]))
    
    def merge_traces(self):
        """
        Invoke a gprMax tool to merge output files containing traces.
        """
        filename = filedialog.askopenfilename(initialdir = '.', title = "Select file", \
                    filetypes = [("gprMax output files", "*.out"), ("All files", "*.*")])
        basename = (filename.split("."))[0]
        remove_files = messagebox.askyesno("Merge files", "Do you wish to remove merged files?")
        if(basename != ""):
            command = "start cmd /K run_gprmax.bat merge " + "\"" + basename[:-1] + "\""
            if(remove_files == True):
                command += " --remove-files"
            sts = subprocess.call(command, shell = True)
            del sts
    
    def display_trace(self):
        """
        Invoke a gprMax tool to display a single trace.
        """
        filename = filedialog.askopenfilename(initialdir = '.', title = "Select file", \
                    filetypes = [("gprMax output files", "*.out"), ("All files", "*.*")])
        if(filename != ""):
            components_dialog = TTraceWindow(self.master)
            components = components_dialog.result
            command = "start cmd /K run_gprmax.bat ascan " + "\"" + filename + "\"" + \
                      " " + components
            sts = subprocess.call(command, shell = True)
            del sts
    
    def display_echogram(self):
        """
        Invoke a gprMax tool to display an entire echogram.
        """
        filename = filedialog.askopenfilename(initialdir = '.', title = "Select file", \
                    filetypes = [("gprMax output files", "*.out"), ("All files", "*.*")])
        if(filename != ""):
            component_dialog = TEchogramWindow(self.master)
            component = component_dialog.result
            command = "start cmd /K run_gprmax.bat bscan " + "\"" + filename + "\"" + \
                      " " + component
            sts = subprocess.call(command, shell = True)
            del sts
    
    def copy_shape(self, event = None, *, shape_num = -1):
        """
        Make a copy of a shape overlapped by the mouse pointer or specified by
        given number.
        
        :param event: object of the event evoking this method (keyboard shortcut, 
                      mouse menu position).
        :type event: tkinter.Event
        :param shape_num: list index of the shape being copied.
        :type shape_num: integer
        """
        self.canvas_interrupt()
        if(shape_num == -1 and event is not None):
            shape_num = self.mouse_overlaps_shape(event.x, event.y, self.radius)
        if(shape_num > -1):
            if(event is not None):
                self.move_const_point = self.winmod(TPoint(event.x, event.y))
            else:
                if(self.shapes[shape_num].type == "Rectangle"):
                    self.move_const_point = self.shapes[shape_num].point1_mod
                elif(self.shapes[shape_num].type == "Cylinder" or \
                     self.shapes[shape_num].type == "CylinSector"):
                    self.move_const_point = self.shapes[shape_num].centre_mod
                elif(self.shapes[shape_num].type == "Polygon"):
                    self.move_const_point = self.shapes[shape_num].points_mod[0]
                else:
                    raise NotImplementedError("Invalid shape type")
            self.shape_buffer = deepcopy(self.shapes[shape_num])
            self.shape_buffer.width = 1
    
    def paste_shape(self, event = None, deltax = 15, deltay = 15):
        """
        Paste shape into model.
        
        :param event: object of the event evoking this method (keyboard shortcut, 
                      mouse menu position).
        :type event: tkinter.Event
        :param deltax: offset of the pasted shape in the x direction in pixels.
        :type deltax: integer
        :param deltay: offset of the pasted shape in the y direction in pixels.
        :type deltay: integer
        """
        self.manipulated_shape_num = len(self.shapes)
        if(event is not None):
            shape_num = self.mouse_overlaps_shape(event.x, event.y, self.radius)
        if(self.shape_buffer is not None):
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
            # self.operations.append(TOperation("paste", num = self.move_shape_num))
            self.operations.append(TOperation("paste", num = self.manipulated_shape_num))
    
    def copy_ctrl_c(self, event):
        """
        Handle a ctrl+c keystroke event.
        
        :param event: ctrl+c keystroke event object.
        :type event: tkinter.Event
        """
        try:
            shape_num = (self.shapes_frame.shapes_list.curselection())[0]
        except IndexError:
            return
        self.copy_shape(shape_num = shape_num)

    def paste_ctrl_v(self, event, *, deltax = 15, deltay = 15):
        """
        Handle a ctrl+v keystroke event
        
        :param event: ctrl+v keystroke event object.
        :type event: tkinter.Event
        :param deltax: pasted shape offset in x direction in pixels.
        :type deltax: integer
        :param deltay: pasted shape offset in y direction in pixels.
        :type deltay: integer
        """
        event.x = self.move_const_point.x + deltax
        event.y = self.move_const_point.y + deltay
        self.paste_shape(event)
    
    def mouse_wheel(self, event):
        """
        Handle a mouse wheel rotation event.

        :param event: window mouse wheel rotation event object.
        :type event: tkinter.Event
        """
        # Respond to Linux or Windows wheel event accordingly
        if event.num == 5 or event.delta == -120:
            self.view_zoom_out()
        if event.num == 4 or event.delta == 120:
            self.view_zoom_in()
    
    def export_canvas_to_image(self):
        """
        Export the model to a PNG image.
        """
        white = (255, 255, 255)
        width = int(TModel_Size.DOM_X/TModel_Size.DX)
        height = int(TModel_Size.DOM_Y/TModel_Size.DY)
        model_image = Image.new("RGB", (width, height), white)
        gray_scale = []
        scale_step = 256/(len(self.materials) + 1)
        if(len(self.materials) <= 256):
            scale_step = round(scale_step)
        for i, _ in enumerate(self.materials):
            shade = (255 - (i+1)*scale_step, 255 - (i+1)*scale_step, \
                     255 - (i+1)*scale_step)
            gray_scale.append(shade)
        gray_scale += [(0, 0, 0), (255, 255, 255)]
        material_names = []
        for material in self.materials:
            material_names.append(material.name)
        for shape in self.shapes:
            if(shape.material in material_names):
                ind = material_names.index(shape.material)
                draw_colour = gray_scale[ind]
            elif(shape.material == "pec"):
                draw_colour = gray_scale[-2]
            else:
                draw_colour = gray_scale[-1]
            shape.draw_to_image(model_image, draw_colour)
        filename = filedialog.asksaveasfilename(initialdir = '.', title = "Select file", \
                                                filetypes = [("Portable Network Graphics", "*.png"), \
                                                             ("All files", "*.*")])
        if(filename != ""):
            model_image.save(filename)

    def init_model_move(self, event):
        """
        Save the initial mouse position while holding its wheel down.
        """
        self.prev_mouse_pos = TPoint(event.x, event.y)

    def move_visible_model(self, event):
        """
        Handle a mouse move while its wheel is pressed move event.

        :param event: canvas mouse move while wheel is down event object.
        :type event: tkinter.Event
        """
        dr = TPoint(self.prev_mouse_pos.x - event.x, \
                    event.y - self.prev_mouse_pos.y)
        len_x_mon = TWindow_Size.MAX_X - TWindow_Size.MIN_X - \
                            2*TWindow_Size.MARG_X
        len_y_mon = TWindow_Size.MAX_Y - TWindow_Size.MIN_Y - \
                            2*TWindow_Size.MARG_Y
        len_x_mod = TModel_Size.MAX_X - TModel_Size.MIN_X
        len_y_mod = TModel_Size.MAX_Y - TModel_Size.MIN_Y
        dr.x = dr.x * len_x_mod/len_x_mon
        dr.y = dr.y * len_y_mod/len_y_mon
        if(TModel_Size.MIN_X + dr.x <= 0.0):
            dr.x = -TModel_Size.MIN_X
        if(TModel_Size.MIN_Y + dr.y <= 0.0):
            dr.y = -TModel_Size.MIN_Y
        if(TModel_Size.MAX_X + dr.x >= TModel_Size.DOM_X):
            dr.x = TModel_Size.DOM_X - TModel_Size.MAX_X
        if(TModel_Size.MAX_Y + dr.y >= TModel_Size.DOM_Y):
            dr.y = TModel_Size.DOM_Y - TModel_Size.MAX_Y
        TModel_Size.MIN_X += dr.x
        TModel_Size.MIN_Y += dr.y
        TModel_Size.MAX_X += dr.x
        TModel_Size.MAX_Y += dr.y
        self.coordsys.model_size_update()
        self.coordsys.window_size_update()
        for single_shape in self.shapes:
            single_shape.update_window_positions()
        self.coordsys.display_settings_update()
        self.main_horizontal_scrollbar.set(TModel_Size.MIN_X/TModel_Size.DOM_X, \
                                           TModel_Size.MAX_X/TModel_Size.DOM_X)
        self.main_vertical_scrollbar.set(1 - TModel_Size.MAX_Y/TModel_Size.DOM_Y, \
                                         1 - TModel_Size.MIN_Y/TModel_Size.DOM_Y)
        self.main_canvas.delete("all")
        self.canvas_refresh()
        self.canvas_mouse_move(event)
        self.prev_mouse_pos = TPoint(event.x, event.y)

    def dispatch_model_move(self, event):
        """
        Set the initial mouse position while holding its wheel down to None.
        """
        self.prev_mouse_pos = None
    
    def modwin(self, pt):
        """
        Convert a point in model coordinates to window coordinates.

        :param pt: point to be converted.
        :type pt: TPoint

        :return: point in window coordinates.
        :rtype: TPoint
        """
        return TG.model_to_window(pt, \
                                  TPoint(TModel_Size.MIN_X, TModel_Size.MIN_Y), \
                                  TPoint(TModel_Size.MAX_X, TModel_Size.MAX_Y), \
                                  TPoint(TWindow_Size.BOX_MIN_X, \
                                         TWindow_Size.BOX_MIN_Y), \
                                  TPoint(TWindow_Size.BOX_MAX_X, \
                                         TWindow_Size.BOX_MAX_Y))
    
    def winmod(self, pt):
        """
        Convert a point in window coordinates to model coordinates.

        :param pt: point to be converted.
        :type pt: TPoint

        :return: point in model coordinates.
        :rtype: TPoint
        """
        return TG.window_to_model(pt, \
                                  TPoint(TModel_Size.MIN_X, TModel_Size.MIN_Y), \
                                  TPoint(TModel_Size.MAX_X, TModel_Size.MAX_Y), \
                                  TPoint(TWindow_Size.BOX_MIN_X, \
                                         TWindow_Size.BOX_MIN_Y), \
                                  TPoint(TWindow_Size.BOX_MAX_X, \
                                         TWindow_Size.BOX_MAX_Y), \
                                  TModel_Size.DX, TModel_Size.DY)
    
    def distmodwin(self, dist):
        """
        Convert a distance in model coordinates to window coordinates.

        :param dist: distance to be converted.
        :type dist: float

        :return: distance in pixels.
        :rtype: integer
        """
        return TG.dist_model_to_window(dist,  \
                                       TPoint(TModel_Size.MIN_X, \
                                              TModel_Size.MIN_Y), \
                                       TPoint(TModel_Size.MAX_X, \
                                              TModel_Size.MAX_Y), \
                                       TPoint(TWindow_Size.BOX_MIN_X, \
                                              TWindow_Size.BOX_MIN_Y), \
                                       TPoint(TWindow_Size.BOX_MAX_X, \
                                              TWindow_Size.BOX_MAX_Y))
    
    def distwinmod(self, dist):
        """
        Convert a distance in window coordinates to model coordinates.

        :param dist: distance to be converted.
        :type dist: integer

        :return: distance in metres.
        :rtype: float
        """
        return TG.dist_window_to_model(dist,  \
                                       TPoint(TModel_Size.MIN_X, \
                                              TModel_Size.MIN_Y), \
                                       TPoint(TModel_Size.MAX_X, \
                                              TModel_Size.MAX_Y), \
                                       TPoint(TWindow_Size.BOX_MIN_X, \
                                              TWindow_Size.BOX_MIN_Y), \
                                       TPoint(TWindow_Size.BOX_MAX_X, \
                                              TWindow_Size.BOX_MAX_Y), \
                                       TModel_Size.DX, TModel_Size.DY)


def centre_window(window):
    """
    Put the main application window in the middle of the screen.

    :param window: main windows object.
    :type window: tkinter.Tk
    """
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
    """
    Initialise and start the application.
    """
    root = Tk()
    myApp = TApp(root)
    centre_window(root)
    # Mainloop
    root.mainloop()
    del myApp


if __name__ == "__main__":
    main()
