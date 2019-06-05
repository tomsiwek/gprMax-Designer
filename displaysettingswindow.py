from tkinter import simpledialog, Label, Entry, messagebox, W, EW, Frame
from tkinter.ttk import Combobox

from settings import TColours

class TDisplaySettingsWindow(simpledialog.Dialog):
    """
    Class represents pop up window used to tweak display options.
    """
    def __init__(self, master, tickintx = 1.0, tickinty = 1.0, round_digits = 2, \
                 min_model_x = 0.0, min_model_y = 0.0, max_model_x = 10.0, \
                 max_model_y = 10.0, fit_to_window = True, label_int = 1.0):
        "Init object variables and call parent class constructor"
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
        "Initialize widgets"
        self.body_frame = Frame(self)

        Label(self.body_frame, text = "x tick interval:", \
              anchor = W).grid(row = 0, sticky = EW)
        Label(self.body_frame, text = "y tick interval:", \
              anchor = W).grid(row = 1, sticky = EW)
        Label(self.body_frame, text = "Label decimal precision:", \
              anchor = W).grid(row = 2, sticky = EW)
        # Label(self.body_frame, text = "Minimal visible x:", anchor = W).grid(row = 3, sticky = EW)
        # Label(self.body_frame, text = "Minimal visible y:", anchor = W).grid(row = 4, sticky = EW)
        # Label(self.body_frame, text = "Maximal visible x:", anchor = W).grid(row = 5, sticky = EW)
        # Label(self.body_frame, text = "Maximal visible y:", anchor = W).grid(row = 6, sticky = EW)
        # Label(self.body_frame, text = "Scaling mode:", anchor = W).grid(row = 7, sticky = EW)
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
        # self.e4 = Entry(self.body_frame)
        # self.e4.insert(0, str(self.min_model_x))
        # self.e5 = Entry(self.body_frame)
        # self.e5.insert(0, str(self.min_model_y))
        # self.e6 = Entry(self.body_frame)
        # self.e6.insert(0, str(self.max_model_x))
        # self.e7 = Entry(self.body_frame)
        # self.e7.insert(0, str(self.max_model_y))
        # fit_values = ["fit to window", "stretch"]
        # self.scale_mode = Combobox(self.body_frame, values = fit_values)
        # if(self.fit_to_window == True):
        #     self.scale_mode.set(fit_values[0])
        # else:
        #     self.scale_mode.set(fit_values[1])
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
        # self.e4.grid(row = 3, column = 1, sticky = EW, padx = 5)
        # self.e5.grid(row = 4, column = 1, sticky = EW, padx = 5)
        # self.e6.grid(row = 5, column = 1, sticky = EW, padx = 5)
        # self.e7.grid(row = 6, column = 1, sticky = EW, padx = 5)
        # self.scale_mode.grid(row = 7, column = 1, sticky = EW, padx = 5)
        self.toggle_fill.grid(row = 3, column = 1, sticky = EW, padx = 5)
        self.label_int_e.grid(row = 4, column = 1, sticky = EW, padx = 5)

        self.body_frame.pack()

        return self.e1
    
    def apply (self):
        "Return requested inputs"
        try:
            tickintx = float(self.e1.get())
            tickinty = float(self.e2.get())
            round_digits = int(self.e3.get())
            # min_model_x = float(self.e4.get())
            # min_model_y = float(self.e5.get())
            # max_model_x = float(self.e6.get())
            # max_model_y = float(self.e7.get())
            # scale_mode = self.scale_mode.get()
            fill = self.toggle_fill.get()
            label_int = float(self.label_int_e.get())
            self.result = tickintx, tickinty, round_digits, fill, label_int#, min_model_x, \
                        #   min_model_y, max_model_x, max_model_y, scale_mode
        except Exception as message:
            messagebox.showerror("Error while changing settings!", message)
