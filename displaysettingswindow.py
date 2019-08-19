from tkinter import simpledialog, Label, Entry, messagebox, W, EW, Frame
from tkinter.ttk import Combobox

from settings import TColours


class TDisplaySettingsWindow(simpledialog.Dialog):
    """
    Class represents pop up window used to tweak display options.

    :param master: master window object.
    :param type: tkinter.Tk.
    :param tickintx: x axis tick interval in m.
    :param type: float.
    :param tickinty: y axis tick interval in m.
    :param type: float.
    :param round_digits: axis label rounding precision.
    :param type: integer.
    :param min_model_x: visible model area lower left x coorfinate.
    :param type: float.
    :param min_model_y: visible model area lower left y coordinate.
    :param type: float.
    :param max_model_x: visible model area upper right x coordinate.
    :param type: float.
    :param max_model_y: visible model area upper right y coordinate.
    :param type: float.
    :param fit_to_model: toogle fitting visible model area to the window.
    :param type: float.
    :param label_int: axes label interval in m.
    :param type: float.
    """
    def __init__(self, master, tickintx = 1.0, tickinty = 1.0, round_digits = 2, \
                 min_model_x = 0.0, min_model_y = 0.0, max_model_x = 10.0, \
                 max_model_y = 10.0, fit_to_window = True, label_int = 1.0):
        """
        Initialise object variables and call the parent class constructor.
        """
        self.tickintx = tickintx
        self.tickinty = tickinty
        self.round_digits = round_digits
        self.min_model_x = min_model_x
        self.min_model_y = min_model_y
        self.max_model_x = max_model_x
        self.max_model_y = max_model_y
        self.fit_to_window = fit_to_window
        self.label_int = label_int
        super().__init__(master)

    def body(self, master):
        """
        Initialise widgets.

        :param master: master window object.
        :param type: tkinter.Tk.
        """
        self.body_frame = Frame(self)

        Label(self.body_frame, text = "x tick interval:", \
              anchor = W).grid(row = 0, sticky = EW)
        Label(self.body_frame, text = "y tick interval:", \
              anchor = W).grid(row = 1, sticky = EW)
        Label(self.body_frame, text = "Label decimal precision:", \
              anchor = W).grid(row = 2, sticky = EW)
        Label(self.body_frame, text = "Shapes fill", \
              anchor = W).grid(row = 3, column = 0, sticky = EW)
        Label(self.body_frame, text = "Tick labels interval", \
              anchor = W).grid(row = 4, column = 0, sticky = EW)

        self.e1 = Entry(self.body_frame)
        self.e1.insert(0, str(self.tickintx))
        self.e2 = Entry(self.body_frame)
        self.e2.insert(0, str(self.tickinty))
        self.e3 = Entry(self.body_frame)
        self.e3.insert(0, str(self.round_digits))
        fill_values = ["colour", "none"]
        self.toggle_fill = Combobox(self.body_frame, values = fill_values)
        if(TColours.FILL):
            self.toggle_fill.set("colour")
        else:
            self.toggle_fill.set("none")
        self.label_int_e = Entry(self.body_frame)
        self.label_int_e.insert(0, str(self.label_int))

        self.e1.grid(row = 0, column = 1, sticky = EW, padx = 5)
        self.e2.grid(row = 1, column = 1, sticky = EW, padx = 5)
        self.e3.grid(row = 2, column = 1, sticky = EW, padx = 5)
        self.toggle_fill.grid(row = 3, column = 1, sticky = EW, padx = 5)
        self.label_int_e.grid(row = 4, column = 1, sticky = EW, padx = 5)

        self.body_frame.pack()

        return self.e1
    
    def apply(self):
        """
        Return requested inputs.
        """
        try:
            tickintx = float(self.e1.get())
            tickinty = float(self.e2.get())
            round_digits = int(self.e3.get())
            fill = self.toggle_fill.get()
            label_int = float(self.label_int_e.get())
            self.result = tickintx, tickinty, round_digits, fill, label_int
        except Exception as message:
            messagebox.showerror("Error while changing settings!", message)
