from tkinter import simpledialog, Listbox, Scrollbar, Frame, Button, messagebox
from tkinter import NSEW, EW, NS, W, E, VERTICAL, BOTH, END, X, Y, LEFT, RIGHT

from point import TPoint


class TPolygonWindow(simpledialog.Dialog):
    """
    Class represents a polygon vertices edit window.

    :param master: master window object.
    :param type: tkinter.Tk.
    :param app: main app object.
    :param type: TApp.
    :param polygon: edited polygon object.
    :param type: TPolygon.
    """
    def __init__(self, master, app, polygon):
        """
        Initialise object variables and call the parent class constructor.
        """
        self._app = app
        self._polygon = polygon
        super().__init__(master)
    
    def body(self, master):
        """
        Initialise widgets.

        :param master: master window object.
        :param type: tkinter.Tk.
        """
        # Frame for widgets
        self.main_frame = Frame(self)
        # Listbox
        self.vertices_list = Listbox(self.main_frame, exportselection = False, \
                                     width = 40)
        self.vertices_list.config(exportselection=0)
        self.vertices_list.pack(expand = True, fill = BOTH, side = LEFT)
        self.vertices_list.bind("<Double-Button-1>", self.vertices_list_selected_item)
        # Listbox's yscrollbar
        self.vertices_list_scrollbar = Scrollbar(self.main_frame, orient = VERTICAL, \
                                                 command = self.vertices_list.yview)
        self.vertices_list_scrollbar.pack(expand = True, fill = Y, side = LEFT)
        self.vertices_list.config(yscrollcommand = self.vertices_list_scrollbar.set)
        self.main_frame.pack(expand = True, fill = BOTH)
        # Fill list with vertices data
        self.update_vertices_list()
    
    def buttonbox(self):
        """
        Redefine default Ok/Cancel buttons in the bottom of the window with
        Apply/Add/Delete.
        """
        self.bbox = Frame(self)
        self.apply_button = Button(self.bbox, text = "Apply", width = 10, \
                                   command = self.apply)
        self.apply_button.pack(side = LEFT, padx = 5, pady = 5)
        self.add_button = Button(self.bbox, text = "Add", width = 10, \
                                 command = self.add_vertex)
        self.add_button.pack(side = LEFT, padx = 5, pady = 5)
        self.delete_button = Button(self.bbox, text = "Delete", width = 10, \
                                    command = self.delete_vertex)
        self.delete_button.pack(side = LEFT, padx = 5, pady = 5)
        self.bbox.pack()

    def get_current_selection(self):
        """
        Retrieve the selected vertex index. 

        :rtype: integer.
        """
        try:
            cursel = self.vertices_list.curselection()[0]
        except:
            cursel = 0
        return cursel

    def vertices_list_selected_item(self, event):
        """
        Display and edit selected vertex parameters.

        :param event: listbox LMB click event.
        :param type: tkinter.Event.
        """
        try:
            vertex_num = (self.vertices_list.curselection())[0]
        except IndexError:
            return
        except Exception as message:
            messagebox.showerror("Error while picking shape!", message)
        if (vertex_num < 0):
            return
        else:
            try:
                vertex = self._polygon.points_mod[vertex_num]
            except Exception as message:
                messagebox.showerror("Materials list error", message)
                return
        initialvalue = str(vertex.x) + " " + str(vertex.y)
        input_str = simpledialog.askstring("Input coordinates", "Give vertex coordinates", \
                                           initialvalue = initialvalue)
        try:
            new_x, new_y = input_str.split()
        except AttributeError:
            pass
        except ValueError as e:
            messagebox.showerror("Wrong input!", e)
        else:
            edited_point = self._polygon.points_mod[vertex_num]
            edited_point.x, edited_point.y = float(new_x), float(new_y)
            self._polygon.update_window_positions()
            self._app.main_canvas.delete("all")
            self._app.canvas_refresh()
        finally:
            self.update_vertices_list()
            self.vertices_list.select_clear(0, END)
            self.vertices_list.selection_set(vertex_num)
            self.vertices_list.activate(vertex_num)
            self.vertices_list.focus_set()

    def update_vertices_list(self):
        """
        Update entries in the vertices listbox.
        """
        cursel = self.get_current_selection()
        self.vertices_list.delete(0, END)
        for i, v in enumerate(self._polygon.points_mod):
            self.vertices_list.insert(i, str(i + 1) + ". (" + str(v.x) + ", " + \
                                      str(v.y) + ")")      
        self.vertices_list.select_clear(0, END)
        if(cursel >= self.vertices_list.size()):
            self.vertices_list.selection_set(cursel - 1)
            self.vertices_list.activate(cursel)
        else:
            self.vertices_list.selection_set(cursel)
            self.vertices_list.activate(cursel)

    
    def add_vertex(self):
        """
        Add a vertex to the polygon.
        """
        cursel = self.get_current_selection()
        input_str = simpledialog.askstring("Input coordinates", "Give vertex coordinates")
        try:
            new_x, new_y = input_str.split()
        except AttributeError:
            pass
        except ValueError as e:
            messagebox.showerror("Wrong input", e)
        else:
            self._polygon.add_vertex(x_mod = float(new_x), y_mod = float(new_y))
            self._app.main_canvas.delete("all")
            self._app.canvas_refresh()
        finally:
            self.update_vertices_list()
            self.vertices_list.select_clear(0, END)
            self.vertices_list.selection_set(cursel)
            self.vertices_list.activate(cursel)
            self.vertices_list.focus_set()

    def delete_vertex(self):
        """
        Delete a vertex from the polygon.
        """
        cursel = self.get_current_selection()
        self._polygon.remove_vertex(cursel)
        self._app.main_canvas.delete("all")
        self._app.canvas_refresh()
        self.update_vertices_list()
        self.vertices_list.select_clear(0, END)
        self.vertices_list.selection_set(cursel)
        self.vertices_list.activate(cursel)
        self.vertices_list.focus_set()
    
    def apply(self):
        """
        Destroy window upon clicking Apply button.
        """
        self.destroy()