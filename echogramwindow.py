from tkinter import simpledialog, Label
from tkinter.ttk import Combobox


class TEchogramWindow(simpledialog.Dialog):
    """
    Class represents popup used to choose echogram component
    """

    def body(self, master):
        Label(self, text = "Choose component to plot:").pack()
        components = ["Ex", "Ey", "Ez", "Hx", "Hy", "Hz", "Ix", "Iy", "Iz"]
        self.component_list = Combobox(self, values = components)
        self.component_list.set(components[0])
        self.component_list.pack()

    def apply(self):
        self.result = self.component_list.get()