from tkinter import simpledialog, Label, Checkbutton, IntVar, Frame, W

class TTraceWindow(simpledialog.Dialog):
    """
    Class represents popup used to choose trace components and FFT
    """

    def __init__(self, master, *, show_fft = True):
        self.show_fft = show_fft
        super().__init__(master)

    def body(self, master):
        Label(self, text = "Choose component(s) to plot:").pack()
        bwidth = 3
        self.button_frame = Frame(self)
        # self.mag_frame = Frame(self)
        self.ex_en = IntVar()
        self.ex = Checkbutton(self.button_frame, text = "Ex", \
                              variable = self.ex_en, width = bwidth, anchor = W)
        self.ex.select()
        self.ex.grid(row = 0, column = 0)
        self.ey_en = IntVar()
        self.ey = Checkbutton(self.button_frame, text = "Ey", \
                              variable = self.ey_en, width = bwidth, anchor = W)
        self.ey.select()
        self.ey.grid(row = 0, column = 1)
        self.ez_en = IntVar()
        self.ez = Checkbutton(self.button_frame, text = "Ez", \
                              variable = self.ez_en, width = bwidth, anchor = W)
        self.ez.select()
        self.ez.grid(row = 0, column = 2)
        self.hx_en = IntVar()
        self.hx = Checkbutton(self.button_frame, text = "Hx", \
                              variable = self.hx_en, width = bwidth, anchor = W)
        self.hx.select()
        self.hx.grid(row = 1, column = 0)
        self.hy_en = IntVar()
        self.hy = Checkbutton(self.button_frame, text = "Hy", \
                              variable = self.hy_en, width = bwidth, anchor = W)
        self.hy.select()
        self.hy.grid(row = 1, column = 1)
        self.hz_en = IntVar()
        self.hz = Checkbutton(self.button_frame, text = "Hz", \
                              variable = self.hz_en, width = bwidth, anchor = W)
        self.hz.select()
        self.hz.grid(row = 1, column = 2)
        self.button_frame.pack()
        self.fft_en = IntVar()
        if(self.show_fft):
            self.fft_button = Checkbutton(self, text = "Show FFT", variable = self.fft_en)
            self.fft_button.pack()
        # self.mag_frame.pack()

    def apply(self):
        res_str = ""
        if(self.ex_en.get() == 1):
            res_str += " Ex"
        if(self.ey_en.get() == 1):
            res_str += " Ey"
        if(self.ez_en.get() == 1):
            res_str += " Ez"
        if(self.hx_en.get() == 1):
            res_str += " Hx"
        if(self.hy_en.get() == 1):
            res_str += " Hy"
        if(self.hz_en.get() == 1):
            res_str += " Hz"
        if(self.fft_en.get() == 1):
            res_str += " -fft"
        self.result = res_str[1:]