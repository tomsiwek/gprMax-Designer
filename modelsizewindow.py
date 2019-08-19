from tkinter import simpledialog, Label, Entry

class TModelSizeWindow(simpledialog.Dialog):
    """
    Class represents popup window for entering model size (domain).

    :param master: master window object.
    :param type: tkinter.Tk.
    """
    def body(self, master):
        """
        Initialise widgets.

        :param master: master window object.
        :param type: tkinter.Tk.
        """
        Label(master, text="x:").grid(row=0)
        Label(master, text="y:").grid(row=1)

        self.e1 = Entry(master)
        self.e2 = Entry(master)

        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)

    def apply(self):
        """
        Return requested inputs.
        """
        first = self.e1.get ()
        second = self.e2.get ()
        self.result = first, second
