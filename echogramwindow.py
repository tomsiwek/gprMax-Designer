from tkinter import simpledialog, Label
from tkinter.ttk import Combobox


class TEchogramWindow(simpledialog.Dialog):
    """
    Class represents popup used to choose echogram component.

    :param master: master window object.
    :param type: tkinter.Tk
    """

    def body(self, master):
        """
        Initialise widgets.

        :param master: master window object.
        :param type: tkinter.Tk
        """
        Label(self, text = "Choose component to plot:").pack()
        components = ["Ex", "Ey", "Ez", "Hx", "Hy", "Hz", "Ix", "Iy", "Iz"]
        self.component_list = Combobox(self, values = components)
        self.component_list.set(components[0])
        self.component_list.pack()

    def apply(self):
        """
        Return requested inputs.
        """
        self.result = self.component_list.get()