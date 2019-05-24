from tkinter import simpledialog, Label, Entry, W, EW, messagebox, Radiobutton, IntVar, DISABLED, NORMAL
from tkinter.ttk import Combobox

from settings import TModel_Size, TTicksSettings, TSurveySettings

class TSurveySettingsWindow(simpledialog.Dialog):
    """
    Class represents popup window used for introducing survey parameters.
    """

    def __init__(self, master, TApp):
        self.TApp = TApp
        super().__init__(master)

    def body(self, master):
        dx = TModel_Size.DX
        dy = TModel_Size.DY
        # dz = min(dx, dy)
        # dt = self.calculate_cfl_dt(dx = dx, dy = dy, dz = dz)
        tsf = 1.0
        maxy = TModel_Size.DOM_Y
        twt = self.calculate_two_way_time(maxy = maxy)

        width = 20
        Label(master, text = "time stablity factor:", anchor = W, width = width).grid(row = 0, sticky = EW)
        Label(master, text = "time window [s]:", anchor = W, width = width).grid(row = 0, column = 2, sticky = EW, padx = (5,0))
        Label(master, text = "waveform:", anchor = W, width = width).grid(row = 1, sticky = EW)
        Label(master, text = "amplitude:", anchor = W, width = width).grid(row = 2, column = 0, sticky = EW)
        Label(master, text = "frequency [Hz]:", anchor = W, width = width).grid(row = 2, column = 2, sticky = EW, padx = (5,0))
        Label(master, text = "source:", anchor = W, width = width).grid(row = 3, column = 0, sticky = EW)
        Label(master, text = "x [m]:", anchor = W, width = width).grid(row = 4, column = 0, sticky = EW)
        Label(master, text = "y [m]:", anchor = W, width = width).grid(row = 4, column = 2, sticky = EW, padx = (5,0))
        Label(master, text = "receiver", anchor = W, width = width).grid(row = 5, sticky = EW)
        Label(master, text = "x [m]:", anchor = W, width = width).grid(row = 6, column = 0, sticky = EW)
        Label(master, text = "y [m]:", anchor = W, width = width).grid(row = 6, column = 2, sticky = EW, padx = (5,0))
        Label(master, text = "survey type:", anchor = W, width = width).grid(row = 7, column = 0, sticky = EW)
        Label(master, text = "src step", anchor = W, width = width).grid(row = 8, column = 0, sticky = EW)
        Label(master, text = "\u2206x [m]:", anchor = W, width = width).grid(row = 9, column = 0, sticky = EW)
        Label(master, text = "\u2206y [m]:", anchor = W, width = width).grid(row = 9, column = 2, sticky = EW, padx = (5,0))
        Label(master, text = "rx step", anchor = W, width = width).grid(row = 10, column = 0, sticky = EW)
        Label(master, text = "\u2206x [m]:", anchor = W, width = width).grid(row = 11, column = 0, sticky = EW)
        Label(master, text = "\u2206y [m]:", anchor = W, width = width).grid(row = 11, column = 2, sticky = EW, padx = (5,0))
        Label(master, text = "rx array", anchor = W, width = width).grid(row = 12, column = 0, sticky = EW)
        Label(master, text = "max x [m]:", anchor = W, width = width).grid(row = 13, column = 0, sticky = EW)
        Label(master, text = "max y [m]:", anchor = W, width = width).grid(row = 13, column = 2, sticky = EW, padx = (5,0))

        self.tsf = Entry(master, width = width)
        format_str = "." + str(TTicksSettings.ROUND_DIGITS + 1) + "g"
        self.tsf.insert(0, format(tsf, format_str))
        self.tsf.grid(row = 0, column = 1, sticky = EW)

        self.time_window = Entry(master, width = width)
        self.time_window.insert(0, format(twt, format_str))
        self.time_window.grid(row = 0, column = 3, sticky = EW)

        wave_type_vals = ["gaussian", "gaussiandot", "gaussiandotnorm", \
                          "gaussiandotdot", "gaussiandotdotnorm", "ricker", \
                          "gaussianprime", "gaussiandoubleprime", "sine", \
                          "contsine"]
        self.wavetype = Combobox(master, values = wave_type_vals, width = width)
        self.wavetype.set(TSurveySettings.WAVE_TYPE)
        self.wavetype.grid(row = 1, column = 1, sticky = EW)

        self.amplitude = Entry(master, width = width)
        self.amplitude.insert(0, str(TSurveySettings.AMPLITUDE))
        self.amplitude.grid(row = 2, column = 1, sticky = EW)

        self.frequency = Entry(master, width = width)
        self.frequency.insert(0, str(TSurveySettings.FREQUENCY))
        self.frequency.grid(row = 2, column = 3, sticky = EW)

        self.sourcetype = Combobox(master, values = ["hertzian_dipole", "magnetic_dipole"], width = width)
        self.sourcetype.set(TSurveySettings.SRC_TYPE)
        self.sourcetype.grid(row = 3, column = 1, sticky = EW)

        self.src_x = Entry(master, width = width)
        self.src_x.insert(0, str(TSurveySettings.SRC_X))
        self.src_x.grid(row = 4, column = 1, sticky = EW)

        self.src_y = Entry(master, width = width)
        self.src_y.insert(0, str(TSurveySettings.SRC_Y))
        self.src_y.grid(row = 4, column = 3, sticky = EW)

        self.rx_x = Entry(master, width = width)
        self.rx_x.insert(0, str(TSurveySettings.RX_X))
        self.rx_x.grid(row = 6, column = 1, sticky = EW)

        self.rx_y = Entry(master, width = width)
        self.rx_y.insert(0, str(TSurveySettings.RX_Y))
        self.rx_y.grid(row = 6, column = 3, sticky = EW)

        self.scan_type = IntVar()
        self.radio_ascan = Radiobutton(master, text = "Ascan", variable = self.scan_type, value = 0, anchor = W, width = width, command = self.change_survey_type)
        self.radio_ascan.grid(row = 7, column = 1, sticky = EW)

        self.radio_bscan = Radiobutton(master, text = "rx array", variable = self.scan_type, value = 1, anchor = W, width = width, command = self.change_survey_type)
        self.radio_bscan.grid(row = 7, column = 2, sticky = EW, padx = (5, 0))

        self.radio_rxarray = Radiobutton(master, text = "Bscan", variable = self.scan_type, value = 2, anchor = W, width = width, command = self.change_survey_type)
        self.radio_rxarray.grid(row = 7, column = 3, sticky = EW)

        self.src_step_x = Entry(master, width = width)
        self.src_step_x.insert(0, str(TSurveySettings.SRC_STEP_X))
        self.src_step_x.grid(row = 9, column = 1, sticky = EW)

        self.src_step_y = Entry(master, width = width)
        self.src_step_y.insert(0, str(TSurveySettings.SRC_STEP_Y))
        self.src_step_y.grid(row = 9, column = 3, sticky = EW)

        self.rx_step_x = Entry(master, width = width)
        self.rx_step_x.insert(0, str(TSurveySettings.RX_STEP_X))
        self.rx_step_x.config(state = DISABLED)
        self.rx_step_x.grid(row = 11, column = 1, sticky = EW)

        self.rx_step_y = Entry(master, width = width)
        self.rx_step_y.insert(0, str(TSurveySettings.RX_STEP_Y))
        self.rx_step_y.grid(row = 11, column = 3, sticky = EW)

        self.rx_max_x = Entry(master, width = width)
        self.rx_max_x.insert(0, str(TSurveySettings.RX_MAX_X))
        self.rx_max_x.grid(row = 13, column = 1, sticky = EW)

        self.rx_max_y = Entry(master, width = width)
        self.rx_max_y.insert(0, str(TSurveySettings.RX_MAX_Y))
        self.rx_max_y.grid(row = 13, column = 3, sticky = EW)

        if(TSurveySettings.TYPE == "ascan"):
            self.scan_type.set(0)
            self.src_step_x.config(state = DISABLED)
            self.src_step_y.config(state = DISABLED)
            self.rx_step_x.config(state = DISABLED)
            self.rx_step_y.config(state = DISABLED)
            self.rx_max_x.config(state = DISABLED)
            self.rx_max_y.config(state = DISABLED)
        elif(TSurveySettings.TYPE == "rx_array"):
            self.scan_type.set(1)
            self.src_step_x.config(state = DISABLED)
            self.src_step_y.config(state = DISABLED)
            self.rx_step_x.config(state = NORMAL)
            self.rx_step_y.config(state = NORMAL)
            self.rx_max_x.config(state = NORMAL)
            self.rx_max_y.config(state = NORMAL)
        elif(TSurveySettings.TYPE == "bscan"):
            self.scan_type.set(2)
            self.src_step_x.config(state = NORMAL)
            self.src_step_y.config(state = NORMAL)
            self.rx_step_x.config(state = NORMAL)
            self.rx_step_y.config(state = NORMAL)
            self.rx_max_x.config(state = DISABLED)
            self.rx_max_y.config(state = DISABLED)

        return self.tsf

    def change_survey_type(self):
        num = self.scan_type.get()
        if (num == 0):
            self.src_step_x.configure(state = DISABLED)
            self.src_step_y.configure(state = DISABLED)
            self.rx_step_x.configure(state = DISABLED)
            self.rx_step_y.configure(state = DISABLED)
            self.rx_max_x.config(state = DISABLED)
            self.rx_max_y.config(state = DISABLED)
        elif (num == 1):
            self.src_step_x.configure(state = DISABLED)
            self.src_step_y.configure(state = DISABLED)
            self.rx_step_x.configure(state = NORMAL)
            self.rx_step_y.configure(state = NORMAL)
            self.rx_max_x.config(state = NORMAL)
            self.rx_max_y.config(state = NORMAL)
        elif (num == 2):
            self.src_step_x.configure(state = NORMAL)
            self.src_step_y.configure(state = NORMAL)
            self.rx_step_x.configure(state = NORMAL)
            self.rx_step_y.configure(state = NORMAL)
            self.rx_max_x.config(state = DISABLED)
            self.rx_max_y.config(state = DISABLED)
    
    def calculate_cfl_dt(self, *, v = 299792458, dx, dy, dz):
        return 1/(v*(1/(dx**2) + 1/(dy**2) + 1/(dz**2))**(0.5))
    
    def calculate_two_way_time(self, *, c = 299792458.0, maxy):
        sum_prod = 0.0
        sum_area = 0.0
        v = 0.0
        a = 0.0
        names = [mat.name for mat in self.TApp.materials]
        for shape in self.TApp.shapes:
            if(shape.material == "pec"):
                v = 0.0
            elif(shape.material == "free_space"):
                v = c
            else:
                ind = names.index(shape.material)
                v = self.TApp.materials[ind].velocity()
            a = shape.area()
            sum_prod += a*v
            sum_area += a
        mod_area = TModel_Size.DOM_X*TModel_Size.DOM_Y
        sum_prod += mod_area*c
        sum_area = mod_area
        return 2*maxy*sum_area/sum_prod

    def apply(self):
        try:
            num = self.scan_type.get()
            dt = float(self.dt.get())
            tw = float(self.time_window.get())
            wavetype = self.wavetype.get()
            amp = float(self.amplitude.get())
            freq = float(self.frequency.get())
            srctype = self.sourcetype.get()
            src_x = float(self.src_x.get())
            src_y = float(self.src_y.get())
            rx_x = float(self.rx_x.get())
            rx_y = float(self.rx_y.get())
            if (num == 0):
                result = "ascan", dt, tw, wavetype, amp, freq, srctype, src_x, src_y, rx_x, rx_y
            elif (num == 1):
                rx_step_x = float(self.rx_step_x.get())
                rx_step_y = float(self.rx_step_y.get())
                rx_max_x = float(self.rx_max_x.get())
                rx_max_y = float(self.rx_max_y.get())
                result = "rx_array", dt, tw, wavetype, amp, freq, srctype, src_x, src_y, rx_x, rx_y, rx_step_x, rx_step_y, rx_max_x, rx_max_y
            elif (num == 2):
                src_step_x = float(self.src_step_x.get())
                src_step_y = float(self.src_step_y.get())
                rx_step_x = float(self.src_step_x.get())
                rx_step_y = float(self.src_step_y.get())
                result = "bscan", dt, tw, wavetype, amp, freq, srctype, src_x, src_y, rx_x, rx_y, src_step_x, src_step_y, rx_step_x, rx_step_y
            self.result = result
        except Exception as message:
            messagebox.showerror ("Error while changing settings!", message)