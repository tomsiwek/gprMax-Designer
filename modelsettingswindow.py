from tkinter import simpledialog, Label, Entry, W, EW

class TModelSettingsWindow (simpledialog.Dialog):
    """
    Class represents popup window used for entering model size (domain)
    """
    def __init__ (self, master, maxx = 0.0, maxy = 0.0, dx = 0.01, dy = 0.01):
        self.maxx = maxx
        self.maxy = maxy
        self.dx = dx
        self.dy = dy
        super (TModelSettingsWindow, self).__init__ (master)

    def body (self, master):
        Label (master, text = "x [m]:", anchor = W).grid (row = 0, sticky = EW)
        Label (master, text = "y [m]:", anchor = W).grid (row = 1, sticky = EW)
        Label (master, text = "\u2206x [m]:", anchor = W).grid (row = 2, sticky = EW)
        Label (master, text = "\u2206y [m]:", anchor = W).grid (row = 3, sticky = EW)

        self.e1 = Entry (master)
        self.e1.insert (0, str (self.maxx) )
        self.e2 = Entry (master)
        self.e2.insert (0, str (self.maxy) )
        self.e3 = Entry (master)
        self.e3.insert (0, str (self.dx) )
        self.e4 = Entry (master)
        self.e4.insert (0, str (self.dy) )

        self.e1.grid (row = 0, column = 1)
        self.e2.grid (row = 1, column = 1)
        self.e3.grid (row = 2, column = 1)
        self.e4.grid (row = 3, column = 1)

        return self.e1

    def apply (self):
        modelsizex = float (self.e1.get () )
        modelsizey = float (self.e2.get () )
        dx = float (self.e3.get () )
        dy = float (self.e4.get () )
        self.result = modelsizex, modelsizey, dx, dy
    
    # def cancel (self):
    #     self.result = self.maxx, self.maxy, self.dx, self.dy
    #     self.destroy ()

