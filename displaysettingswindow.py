from tkinter import simpledialog, Label, Entry, messagebox, W, EW

class TDisplaySettingsWindow (simpledialog.Dialog):
    """
    Class represents pop up window used to tweak display options.
    """
    def __init__(self, master, tickintx = 1.0, tickinty = 1.0, round_digits = 2, \
                 min_model_x = 0.0, min_model_y = 0.0, max_model_x = 10.0, \
                 max_model_y = 10.0):
        "Init object variables and call parent class constructor"
        self.tickintx = tickintx
        self.tickinty = tickinty
        self.round_digits = round_digits
        self.min_model_x = min_model_x
        self.min_model_y = min_model_y
        self.max_model_x = max_model_x
        self.max_model_y = max_model_y
        super().__init__(master)

    def body(self, master):
        "Initialize widgets"
        Label(master, text = "x tick interval:", anchor = W).grid(row = 0, sticky = EW)
        Label(master, text = "y tick interval:", anchor = W).grid(row = 1, sticky = EW)
        Label(master, text = "Label decimal precision:", anchor = W).grid(row = 2, sticky = EW)
        Label(master, text = "Minimal visible x:", anchor = W).grid(row = 3, sticky = EW)
        Label(master, text = "Minimal visible y:", anchor = W).grid(row = 4, sticky = EW)
        Label(master, text = "Maximal visible x:", anchor = W).grid(row = 5, sticky = EW)
        Label(master, text = "Maximal visible y:", anchor = W).grid(row = 6, sticky = EW)

        self.e1 = Entry(master)
        self.e1.insert(0, str(self.tickintx))
        self.e2 = Entry(master)
        self.e2.insert(0, str(self.tickinty))
        self.e3 = Entry(master)
        self.e3.insert(0, str(self.round_digits))
        self.e4 = Entry(master)
        self.e4.insert(0, str(self.min_model_x))
        self.e5 = Entry(master)
        self.e5.insert(0, str(self.min_model_y))
        self.e6 = Entry(master)
        self.e6.insert(0, str(self.max_model_x))
        self.e7 = Entry(master)
        self.e7.insert(0, str(self.max_model_y))

        self.e1.grid(row = 0, column = 1)
        self.e2.grid(row = 1, column = 1)
        self.e3.grid(row = 2, column = 1)
        self.e4.grid(row = 3, column = 1)
        self.e5.grid(row = 4, column = 1)
        self.e6.grid(row = 5, column = 1)
        self.e7.grid(row = 6, column = 1)

        return self.e1
    
    def apply (self):
        "Return requested inputs"
        try:
            tickintx = float(self.e1.get())
            tickinty = float(self.e2.get())
            round_digits = int(self.e3.get())
            min_model_x = float(self.e4.get())
            min_model_y = float(self.e5.get())
            max_model_x = float(self.e6.get())
            max_model_y = float(self.e7.get())
            self.result = tickintx, tickinty, round_digits, min_model_x, \
                          min_model_y, max_model_x, max_model_y
        except Exception as message:
            messagebox.showerror("Error while changing settings!", message)
