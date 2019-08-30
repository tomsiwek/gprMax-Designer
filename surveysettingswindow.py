from tkinter import simpledialog, Label, Entry, W, EW, messagebox, Radiobutton, \
                    IntVar, DISABLED, NORMAL, Frame
from tkinter.ttk import Combobox

from settings import TModel_Size, TTicksSettings, TSurveySettings

class TSurveySettingsWindow(simpledialog.Dialog):
    """
    Class represents popup window used for introducing survey parameters.

    :param master: master window object.
    :type master: tkinter.Tk
    :param app: main app object.
    :type app: TApp
    """

    def __init__(self, master, TApp):
      """
      Initialise object variables and call the parent class constructor.
      """
      self.TApp = TApp
      super().__init__(master)

    def body(self, master):
      """
      Initialise widgets.

      :param master: master window object.
      :type master: tkinter.Tk
      """
      tsf = TSurveySettings.TSF
      maxy = TModel_Size.DOM_Y
      if(TSurveySettings.TIME_WINDOW == 0.0):
          twt = self.calculate_two_way_time(maxy = maxy)
      else:
          twt = TSurveySettings.TIME_WINDOW
      dl = max(TModel_Size.DX, TModel_Size.DY)
      if(TSurveySettings.FREQUENCY == 0.0):
          freq = self.calculate_frequency(dl)
      else:
          freq = TSurveySettings.FREQUENCY

      self.widgets = Frame(self)

      width = 20
      Label(self.widgets, text = "time stablity factor:", \
            anchor = W, width = width).grid(row = 0, sticky = EW)
      Label(self.widgets, text = "time window [s]:", anchor = W, \
            width = width).grid(row = 0, column = 2, sticky = EW, padx = (5,0))
      Label(self.widgets, text = "waveform:", anchor = W, \
            width = width).grid(row = 1, sticky = EW)
      Label(self.widgets, text = "amplitude:", anchor = W, \
            width = width).grid(row = 2, column = 0, sticky = EW)
      Label(self.widgets, text = "frequency [Hz]:", anchor = W, \
            width = width).grid(row = 2, column = 2, sticky = EW, padx = (5,0))
      Label(self.widgets, text = "source:", anchor = W, \
            width = width).grid(row = 3, column = 0, sticky = EW)
      Label(self.widgets, text = "x [m]:", anchor = W, \
            width = width).grid(row = 4, column = 0, sticky = EW)
      Label(self.widgets, text = "y [m]:", anchor = W, \
            width = width).grid(row = 4, column = 2, sticky = EW, padx = (5,0))
      Label(self.widgets, text = "receiver", anchor = W, \
            width = width).grid(row = 5, sticky = EW)
      Label(self.widgets, text = "x [m]:", anchor = W, \
            width = width).grid(row = 6, column = 0, sticky = EW)
      Label(self.widgets, text = "y [m]:", anchor = W, \
            width = width).grid(row = 6, column = 2, sticky = EW, padx = (5,0))
      Label(self.widgets, text = "survey type:", anchor = W, \
            width = width).grid(row = 7, column = 0, sticky = EW)
      Label(self.widgets, text = "src step", anchor = W, \
            width = width).grid(row = 8, column = 0, sticky = EW)
      Label(self.widgets, text = "\u2206x [m]:", anchor = W, \
            width = width).grid(row = 9, column = 0, sticky = EW)
      Label(self.widgets, text = "\u2206y [m]:", anchor = W, \
            width = width).grid(row = 9, column = 2, sticky = EW, padx = (5,0))
      Label(self.widgets, text = "rx step", anchor = W, \
            width = width).grid(row = 10, column = 0, sticky = EW)
      Label(self.widgets, text = "\u2206x [m]:", anchor = W, \
            width = width).grid(row = 11, column = 0, sticky = EW)
      Label(self.widgets, text = "\u2206y [m]:", anchor = W, \
            width = width).grid(row = 11, column = 2, sticky = EW, padx = (5,0))
      Label(self.widgets, text = "rx array", anchor = W, \
            width = width).grid(row = 12, column = 0, sticky = EW)
      Label(self.widgets, text = "max x [m]:", anchor = W, \
            width = width).grid(row = 13, column = 0, sticky = EW)
      Label(self.widgets, text = "max y [m]:", anchor = W, \
            width = width).grid(row = 13, column = 2, sticky = EW, padx = (5,0))
      Label(self.widgets, text = "messages:", anchor = W, \
            width = width).grid(row = 14, column = 0, sticky = EW)
      Label(self.widgets, text = "geometry view:", anchor = W, \
            width = width).grid(row = 15, column = 0, sticky = EW)
      Label(self.widgets, text = "vtk file:", anchor = W, \
            width = width).grid(row = 15, column = 2, sticky = EW)
      Label(self.widgets, text = "snapshot:", anchor = W, \
            width = width).grid(row = 16, column = 0, sticky = EW)
      Label(self.widgets, text = "snapshot time:", anchor = W, \
            width = width).grid(row = 16, column = 2, sticky = EW)
      Label(self.widgets, text = "snapshot file:", anchor = W, \
            width = width).grid(row = 17, column = 0, sticky = EW)

      self.tsf = Entry(self.widgets, width = width)
      format_str = "." + str(TTicksSettings.ROUND_DIGITS + 1) + "g"
      self.tsf.insert(0, str(tsf))
      self.tsf.grid(row = 0, column = 1, sticky = EW)

      self.time_window = Entry(self.widgets, width = width)
      self.time_window.insert(0, format(twt, format_str))
      self.time_window.grid(row = 0, column = 3, sticky = EW)

      wave_type_vals = ["gaussian", "gaussiandot", "gaussiandotnorm", \
                        "gaussiandotdot", "gaussiandotdotnorm", "ricker", \
                        "gaussianprime", "gaussiandoubleprime", "sine", \
                        "contsine"]
      self.wavetype = Combobox(self.widgets, values = wave_type_vals, width = width)
      self.wavetype.set(TSurveySettings.WAVE_TYPE)
      self.wavetype.grid(row = 1, column = 1, sticky = EW)

      self.amplitude = Entry(self.widgets, width = width)
      self.amplitude.insert(0, str(TSurveySettings.AMPLITUDE))
      self.amplitude.grid(row = 2, column = 1, sticky = EW)

      self.frequency = Entry(self.widgets, width = width)
      self.frequency.insert(0, format(freq, format_str))
      self.frequency.grid(row = 2, column = 3, sticky = EW)

      self.sourcetype = Combobox(self.widgets, values = ["hertzian_dipole", \
                                                         "magnetic_dipole"], \
                                 width = width)
      self.sourcetype.set(TSurveySettings.SRC_TYPE)
      self.sourcetype.grid(row = 3, column = 1, sticky = EW)

      self.src_x = Entry(self.widgets, width = width)
      self.src_x.insert(0, str(TSurveySettings.SRC_X))
      self.src_x.grid(row = 4, column = 1, sticky = EW)

      self.src_y = Entry(self.widgets, width = width)
      self.src_y.insert(0, str(TSurveySettings.SRC_Y))
      self.src_y.grid(row = 4, column = 3, sticky = EW)

      self.rx_x = Entry(self.widgets, width = width)
      self.rx_x.insert(0, str(TSurveySettings.RX_X))
      self.rx_x.grid(row = 6, column = 1, sticky = EW)

      self.rx_y = Entry(self.widgets, width = width)
      self.rx_y.insert(0, str(TSurveySettings.RX_Y))
      self.rx_y.grid(row = 6, column = 3, sticky = EW)

      self.scan_type = IntVar()
      self.radio_ascan = Radiobutton(self.widgets, text = "Ascan", \
                                     variable = self.scan_type, value = 0, \
                                     anchor = W, width = width, \
                                     command = self.change_survey_type)
      self.radio_ascan.grid(row = 7, column = 1, sticky = EW)

      self.radio_bscan = Radiobutton(self.widgets, text = "rx array", \
                                     variable = self.scan_type, value = 1, \
                                     anchor = W, width = width, \
                                     command = self.change_survey_type)
      self.radio_bscan.grid(row = 7, column = 2, sticky = EW, padx = (5, 0))

      self.radio_rxarray = Radiobutton(self.widgets, text = "Bscan", \
                                       variable = self.scan_type, value = 2, \
                                       anchor = W, width = width, \
                                       command = self.change_survey_type)
      self.radio_rxarray.grid(row = 7, column = 3, sticky = EW)

      self.src_step_x = Entry(self.widgets, width = width)
      self.src_step_x.insert(0, str(TSurveySettings.SRC_STEP_X))
      self.src_step_x.grid(row = 9, column = 1, sticky = EW)

      self.src_step_y = Entry(self.widgets, width = width)
      self.src_step_y.insert(0, str(TSurveySettings.SRC_STEP_Y))
      self.src_step_y.grid(row = 9, column = 3, sticky = EW)

      self.rx_step_x = Entry(self.widgets, width = width)
      self.rx_step_x.insert(0, str(TSurveySettings.RX_STEP_X))
      self.rx_step_x.config(state = DISABLED)
      self.rx_step_x.grid(row = 11, column = 1, sticky = EW)

      self.rx_step_y = Entry(self.widgets, width = width)
      self.rx_step_y.insert(0, str(TSurveySettings.RX_STEP_Y))
      self.rx_step_y.grid(row = 11, column = 3, sticky = EW)

      self.rx_max_x = Entry(self.widgets, width = width)
      self.rx_max_x.insert(0, str(TSurveySettings.RX_MAX_X))
      self.rx_max_x.grid(row = 13, column = 1, sticky = EW)

      self.rx_max_y = Entry(self.widgets, width = width)
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
      
      self.messages = Combobox(self.widgets, values = ["yes", "no"], width = width)
      self.messages.set(TSurveySettings.MESSAGES)
      self.messages.grid(row = 14, column = 1, sticky = EW)

      self.geom_view = Combobox(self.widgets, values = ["yes", "no"], width = width)
      self.geom_view.set(TSurveySettings.GEOM_VIEW)
      self.geom_view.grid(row = 15, column = 1, sticky = EW)

      self.geom_file = Entry(self.widgets)
      self.geom_file.insert(0, TSurveySettings.GEOM_FILE)
      self.geom_file.grid(row = 15, column = 3, sticky = EW)

      self.snapshot = Combobox(self.widgets, values = ["yes", "no"], width = width)
      self.snapshot.set(TSurveySettings.SNAPSHOT)
      self.snapshot.grid(row = 16, column = 1, sticky = EW)

      self.snap_time = Entry(self.widgets)
      if(TSurveySettings.SNAP_TIME != 0.0):
          self.snap_time.insert(0, format(TSurveySettings.SNAP_TIME, format_str))
      else:
          self.snap_time.insert(0, "0.0")
      self.snap_time.grid(row = 16, column = 3, sticky = EW)

      self.snap_file = Entry(self.widgets, width = width)
      self.snap_file.insert(0, TSurveySettings.SNAP_FILE)
      self.snap_file.grid(row = 17, column = 1, sticky = EW)

      self.widgets.pack()

      return self.tsf

    def change_survey_type(self):
      """
      Activate and deactivate Entry boxes accordingly to the selected 
      survey type.
      """
      num = self.scan_type.get()
      if(num == 0):
          self.src_step_x.configure(state = DISABLED)
          self.src_step_y.configure(state = DISABLED)
          self.rx_step_x.configure(state = DISABLED)
          self.rx_step_y.configure(state = DISABLED)
          self.rx_max_x.config(state = DISABLED)
          self.rx_max_y.config(state = DISABLED)
      elif(num == 1):
          self.src_step_x.configure(state = DISABLED)
          self.src_step_y.configure(state = DISABLED)
          self.rx_step_x.configure(state = NORMAL)
          self.rx_step_y.configure(state = NORMAL)
          self.rx_max_x.config(state = NORMAL)
          self.rx_max_y.config(state = NORMAL)
      elif(num == 2):
          self.src_step_x.configure(state = NORMAL)
          self.src_step_y.configure(state = NORMAL)
          self.rx_step_x.configure(state = NORMAL)
          self.rx_step_y.configure(state = NORMAL)
          self.rx_max_x.config(state = DISABLED)
          self.rx_max_y.config(state = DISABLED)
    
    def calculate_cfl_dt(self, *, v = 299792458, dx, dy, dz):
      """
      Calculate time time window from CFL criterion.

      :param v: em wave velocity in m/s.
      :type v: float
      :param dx: discretisation step in x direction in metres.
      :type dx: float
      :param dy: discretisation step in y direction in metres.
      :type dy: float
      :param dz: discretisation step in z direction in metres.
      :type dz: float
      """
      return 1/(v*(1/(dx**2) + 1/(dy**2) + 1/(dz**2))**(0.5))
    
    def calculate_two_way_time(self, *, c = 299792458.0, maxy):
      """
      Calculate em wave travel time from the top to the bottom of the model and back.

      :param c: light speed in m/s.
      :type c: float
      :param maxy: model maximal y coordinate.
      :type maxy: float

      :return: em wave two way time.
      :rtype: float
      """
      lowest = c
      for material in self.TApp.materials:
            v = material.velocity()
            if(v < lowest):
                  lowest = v
      return 2*maxy/lowest
    
    def calculate_frequency(self, dl, v = 299792458.0):
      """
      Calculate optimal antenna frequency.

      :param dl: em wavelength in metres.
      :type dl: float
      :param v: em wave velocity in m/s.
      :type v: float

      :return: optimal antenna frequency.
      :rtype: float
      """
      return v/(30*dl)

    def apply(self):
      """
      Return requested inputs.
      """
      try:
          num = self.scan_type.get()
          tsf = float(self.tsf.get())
          tw = float(self.time_window.get())
          wavetype = self.wavetype.get()
          amp = float(self.amplitude.get())
          freq = float(self.frequency.get())
          srctype = self.sourcetype.get()
          src_x = float(self.src_x.get())
          src_y = float(self.src_y.get())
          rx_x = float(self.rx_x.get())
          rx_y = float(self.rx_y.get())
          messages = self.messages.get()
          geom_view = self.geom_view.get()
          geom_file = self.geom_file.get()
          snapshot = self.snapshot.get()
          snap_time = float(self.snap_time.get())
          snap_file = self.snap_file.get()
          if(num == 0):
              result = "ascan", tsf, tw, wavetype, amp, freq, srctype, src_x, \
                       src_y, rx_x, rx_y, messages, geom_view, geom_file, \
                       snapshot, snap_time, snap_file
          elif(num == 1):
              rx_step_x = float(self.rx_step_x.get())
              rx_step_y = float(self.rx_step_y.get())
              rx_max_x = float(self.rx_max_x.get())
              rx_max_y = float(self.rx_max_y.get())
              result = "rx_array", tsf, tw, wavetype, amp, freq, srctype, src_x, \
                       src_y, rx_x, rx_y, messages, geom_view, geom_file, \
                       snapshot, snap_time, snap_file, \
                       rx_step_x, rx_step_y, rx_max_x, rx_max_y
          elif(num == 2):
              src_step_x = float(self.src_step_x.get())
              src_step_y = float(self.src_step_y.get())
              rx_step_x = float(self.src_step_x.get())
              rx_step_y = float(self.src_step_y.get())
              result = "bscan", tsf, tw, wavetype, amp, freq, srctype, src_x, \
                       src_y, rx_x, rx_y, messages, geom_view, geom_file, \
                       snapshot, snap_time, snap_file, \
                       src_step_x, src_step_y, rx_step_x, rx_step_y
          self.result = result
      except Exception as message:
          messagebox.showerror ("Error while changing settings!", message)