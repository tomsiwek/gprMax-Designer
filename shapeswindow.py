from copy import deepcopy
from tkinter import Listbox, Frame, Scrollbar, messagebox, Menu, simpledialog
from tkinter import NSEW, EW, NS, W, E, VERTICAL, BOTH, END
from tkinter.ttk import Combobox

from operation import TOperation
from settings import TTicksSettings

class TShapesWindow(Frame):
    """
    Class representing auxiliary window containg shapes information.
    """
    def __init__(self, master, TApp):
        super().__init__()
        self.TApp = TApp
        self.round_digits = TTicksSettings.ROUND_DIGITS
        self.init_widgets()

    def init_widgets(self):
        # Listbox
        self.shapes_list = Listbox(self, exportselection = False)
        # self.shapes_list.config(exportselection = 0)
        self.grid_columnconfigure(0, weight = 1, minsize = 300)
        self.grid_rowconfigure(0, weight = 1)
        self.shapes_list.grid(row = 0, column = 0, sticky = NSEW, padx = (5, 25), pady = 5)
        self.shapes_list.bind("<<ListboxSelect>>", self.shapes_list_selected_item)

        # Listbox's yscrollbar
        self.shapes_list_scrollbar = Scrollbar(self, orient = VERTICAL, \
                                               command = self.shapes_list.yview)
        self.shapes_list_scrollbar.grid(row = 0, column = 0, sticky = NS + E, padx = (0, 5), pady = 5)
        self.shapes_list.config(yscrollcommand = self.shapes_list_scrollbar.set)
        # self.shapes_list.bind("<Up>", lambda x: "break")
        # self.shapes_list.bind("<Down>", lambda x: "break")

        # Drop down menu with materials
        self.material_box = Combobox(self, values = ["pec", "free_space"] )
        # self.material_box.current (0)
        self.material_box.grid(row = 1, column = 0, sticky = EW, padx = 5, pady = 5)
        self.material_box.bind("<<ComboboxSelected>>", self.assign_material_to_shape)

        # Right click popup menu
        self.init_popup_menu()
        self.shapes_list.bind("<Button-3>", self.show_popoup_menu)
   
    def update_list(self, shapes, *, swap = False):
        try:
            cursel = self.shapes_list.curselection()[0]
        except:
            cursel = 0
        self.shapes_list.delete(0, END)
        coord_string = ""
        for i, single_shape in enumerate(shapes):
            if(single_shape.type == "Rectangle"):
                coord_string = "(" + str(round(single_shape.point1_mod.x, self.round_digits)) + ", " + str(round(single_shape.point1_mod.y, self.round_digits)) + "), (" + \
                    str(round (single_shape.point2_mod.x, self.round_digits)) + ", " + str(round(single_shape.point2_mod.y, self.round_digits)) + ")"
            elif(single_shape.type == "Cylinder"):
                coord_string = "(" + str(round(single_shape.centre_mod.x, self.round_digits)) + ", " + str(round(single_shape.centre_mod.y, self.round_digits)) + "), " + \
                    str(round(single_shape.radius_mod, self.round_digits))
            elif(single_shape.type == "CylinSector"):
                coord_string = "(" + str(round(single_shape.centre_mod.x, self.round_digits)) + ", " + str(round(single_shape.centre_mod.y, self.round_digits)) + "), " + \
                    str(round(single_shape.radius_mod, self.round_digits)) + ", " + str(round(single_shape.start, self.round_digits)) + ", " + str(round(single_shape.extent, self.round_digits))
            # elif(single_shape.type == "Triangle"):
            #     coord_string = "(" + str (round (single_shape.point1_mod.x, self.round_digits) ) + ", " + str (round (single_shape.point1_mod.y, self.round_digits) ) + "), (" + \
            #         str(round(single_shape.point2_mod.x, self.round_digits)) + ", " + str(round (single_shape.point2_mod.y, self.round_digits)) + "), (" + \
            #         str(round(single_shape.point3_mod.x, self.round_digits)) + ", " + str(round (single_shape.point3_mod.y, self.round_digits)) + ")"
            elif(single_shape.type == "Polygon"):
                coord_string = str(len(single_shape.points))
            self.shapes_list.insert(i, str(i + 1) + ". " + single_shape.type + ": " + coord_string)
            coord_string = ""
        if(not swap):
            self.shapes_list.select_clear(0, END)
            if(cursel >= self.shapes_list.size()):
                self.shapes_list.selection_set(cursel - 1)
                self.shapes_list.activate(cursel)
            else:
                self.shapes_list.selection_set(cursel)
                self.shapes_list.activate(cursel)
    
    def assign_material_to_shape(self, event):
        material = self.material_box.get()
        try:
            shape_num = (self.shapes_list.curselection())[0]
        except:
            return
        else:
            if(shape_num < 0 or material == ""):
                return
            else:
                try:
                    self.TApp.shapes [shape_num].material = material
                except Exception as message:
                    messagebox.showerror("Material assignment error!", message)
                    return

    def shapes_list_selected_item(self, event):
        try:
            shape_num = (self.shapes_list.curselection())[0]
        except IndexError:
            return
        except Exception as message:
            messagebox.showerror("Error while picking shape!", message)
        if (shape_num < 0):
            return
        else:
            try:
                shape = self.TApp.shapes[shape_num]
            except Exception as message:
                messagebox.showerror("Materials list error", message)
                return
        
        self.material_box.set(str(shape.material))
        
        for single_shape in self.TApp.shapes:
            single_shape.width = 1
        
        self.TApp.shapes[shape_num].width = 2
        self.TApp.main_canvas.delete("all")
        self.TApp.canvas_refresh()
        self.shapes_list.select_clear(0, END)
        self.shapes_list.selection_set(shape_num)
        self.shapes_list.activate(shape_num)
        self.shapes_list.focus_set()

    def init_popup_menu (self):
        "Inits shapes pane pup-up menu"
        self.popup_menu = Menu (self, tearoff = 0)
        self.popup_menu.add_command(label = "Edit shape", command = self.edit_shape)
        self.popup_menu.add_command(label = "Change shape colour", command = self.change_shape_colour)
        self.popup_menu.add_command(label = "Remove shape", command = self.remove_shape)
        self.popup_menu.add_separator()
        self.popup_menu.add_command(label = "Add vertex to polygon", command = self.add_vertex_to_polygon)
        self.popup_menu.add_separator()
        self.popup_menu.add_command(label = "Copy shape", command = self.copy_shape)
        self.popup_menu.add_command(label = "Paste shape", command = self.paste_shape)
        self.popup_menu.add_separator()
        self.popup_menu.add_command(label = "Move up", command = self.move_shape_up)
        self.popup_menu.add_command(label = "Move down", command = self.move_shape_down)
        self.popup_menu.add_command(label = "Move to top", command = self.move_shape_top)
        self.popup_menu.add_command(label = "Move to bottom", command = self.move_shape_bottom)

    def show_popoup_menu (self, event):
        try:
            self.popup_menu.post (event.x_root, event.y_root)
        finally:
            self.popup_menu.grab_release ()
    
    def move_shape_up(self):
        try:
            shape_num = (self.shapes_list.curselection())[0]
        except IndexError:
            return
        if (shape_num < 0):
            return
        else:
            try:
                self.TApp.shapes.insert(shape_num - 1, self.TApp.shapes.pop (shape_num) )
                self.update_list(self.TApp.shapes)
                self.TApp.main_canvas.delete("all")
                self.TApp.canvas_refresh(swap = True)
                self.shapes_list.selection_set(shape_num - 1)
                self.shapes_list.activate(shape_num - 1)
            except Exception as message:
                messagebox.showerror ("Error while manipulating shapes list!", message)
                return
    
    def move_shape_down (self):
        try:
            shape_num = (self.shapes_list.curselection () ) [0]
        except IndexError:
            return
        if (shape_num < 0):
            return
        else:
            try:
                self.TApp.shapes.insert (shape_num + 1, self.TApp.shapes.pop (shape_num) )
                self.update_list (self.TApp.shapes)
                self.TApp.main_canvas.delete ("all")
                self.TApp.canvas_refresh(swap = True)
                self.shapes_list.selection_set (shape_num + 1)
                self.shapes_list.activate (shape_num + 1)
                # self.shapes_list.focus_set ()
            except Exception as message:
                messagebox.showerror ("Error while manipulating shapes list!", message)
                return
    
    def move_shape_top (self):
        try:
            shape_num = (self.shapes_list.curselection () ) [0]
        except IndexError:
            return
        if (shape_num < 0):
            return
        else:
            try:
                self.TApp.shapes.insert (0, self.TApp.shapes.pop (shape_num) )
                self.update_list (self.TApp.shapes)
                self.TApp.main_canvas.delete ("all")
                self.TApp.canvas_refresh(swap = True)
                self.shapes_list.selection_set (0)
                self.shapes_list.activate (0)
                # self.shapes_list.focus_set ()
            except Exception as message:
                messagebox.showerror ("Error while manipulating shapes list!", message)
                return

    def move_shape_bottom(self):
        try:
            shape_num = (self.shapes_list.curselection())[0]
        except IndexError:
            return
        if(shape_num < 0):
            return
        else:
            try:
                self.TApp.shapes.append(self.TApp.shapes.pop (shape_num) )
                self.update_list(self.TApp.shapes)
                self.TApp.main_canvas.delete("all")
                self.TApp.canvas_refresh(swap = True)
                self.shapes_list.selection_set(END)
                self.shapes_list.activate(END)
            except Exception as message:
                messagebox.showerror("Error while manipulating shapes list!", message)
                return

    def edit_shape(self):
        try:
            shape_num = (self.shapes_list.curselection())[0]
        except IndexError:
            return
        if (shape_num < 0):
            return
        else:
            self.TApp.operations.append(TOperation("edit", shape = \
                                                   deepcopy(self.TApp.shapes[shape_num]), \
                                                   num = shape_num))
            if(self.TApp.shapes[shape_num].type == "Rectangle"):
                self.TApp.edit_rectangle(shape_num)
            elif(self.TApp.shapes[shape_num].type == "Cylinder"):
                self.TApp.edit_cylin(shape_num)
            elif(self.TApp.shapes[shape_num].type == "CylinSector"):
                self.TApp.edit_cylin_sector(shape_num)
            elif(self.TApp.shapes[shape_num].type == "Polygon"):
                self.TApp.edit_polygon(shape_num)
    
    def change_shape_colour(self):
        try:
            shape_num = (self.shapes_list.curselection())[0]
        except IndexError:
            return
        if(shape_num < 0):
            return
        else:
            self.TApp.change_shape_colour(shape_num = shape_num)

    def remove_shape(self):
        try:
            shape_num = (self.shapes_list.curselection())[0]
        except IndexError:
            return
        if (shape_num < 0):
            return
        else:
            try:
                del self.TApp.shapes[shape_num]
                self.update_list (self.TApp.shapes)
                if (shape_num == len (self.TApp.shapes) ):
                    self.shapes_list.selection_set (shape_num - 1)
                    self.shapes_list.activate (shape_num - 1)
                else:
                    self.shapes_list.selection_set (shape_num)
                    self.shapes_list.activate (shape_num)
                self.TApp.main_canvas.delete ("all")
                self.TApp.canvas_refresh ()
            except Exception as message:
                messagebox.showerror ("Error while manipulating shapes list!", message)
                return

    def add_vertex_to_polygon(self):
        try:
            shape_num = (self.shapes_list.curselection())[0]
        except IndexError:
            return
        input_str = simpledialog.askstring("Input coordinates", "Give mew vertex's coordinates")
        point_mod_x, point_mod_y = [float(val) for val in input_str.split()]
        if(self.TApp.shapes[shape_num].type == "Polygon" and shape_num > -1):
            self.TApp.shapes[shape_num].add_vertex(x_mod = point_mod_x, y_mod = point_mod_y)
        self.TApp.main_canvas.delete("all")
        self.TApp.canvas_refresh()

    def copy_shape(self):
        "Copy selected shape to buffer"
        try:
            shape_num = (self.shapes_list.curselection())[0]
        except IndexError:
            return
        if (shape_num < 0):
            return
        else:
            try:
                self.TApp.copy_shape(shape_num = shape_num)
            except Exception as message:
                messagebox.showerror ("Error while manipulating shapes list!", message)
                return
    
    def paste_shape(self):
        "Paste selected shape from buffer"
        pass