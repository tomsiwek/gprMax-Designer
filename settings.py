"""
.. module:: settings module.
:synopsis: Module contains a few classes that encapsulate various application
           settings, eg. window and model size, label ticks settings etc...
           The settings are organised into following classes: TWindow_Size,
           TModel_Size, TTicksSettings, TSurveySettings, and TColours.

.. moduleauthor:: Tomasz Siwek <tsiwek@g.pl>
"""


class TWindow_Size():
    """
    Class contains main window parameters.
    """
    MIN_X       = 0     #: minimal x coordinate in pixels.
    MIN_Y       = 0     #: minimal y coordinate in pixels.
    MAX_X       = 620   #: maximal x coordinate in pixels.
    MAX_Y       = 620   #: maximal y coordinate in pixels.
    MARG_X      = 20    #: x margin width in pixels.
    MARG_Y      = 20    #: y margin width in pixels.
    # Position of model box's corners
    BOX_MIN_X   = 20    #: minimal x coordinate of the drawing box in pixels.
    BOX_MIN_Y   = 600   #: minimal y coordinate of the drawing box in pixels.
    BOX_MAX_X   = 600   #: maximal x coordinate of the drawing box in pixels.
    BOX_MAX_Y   = 20    #: maximal y coordinate of the drawing box in pixels.


class TModel_Size():
    """
    Class contains model parameters.
    """
    MIN_X   =  0.00     #: minimal x coordinate of the visible model area in metres.
    MIN_Y   =  0.00     #: minimal y coordinate of the visible model area in metres.
    MAX_X   = 10.00     #: maximal x coordinate of the visible model area in metres.
    MAX_Y   = 10.00     #: maximal x coordinate of the visible model area in metres.
    DOM_X   = 10.00     #: minimal x coordinate of the model in metres.
    DOM_Y   = 10.00     #: minimal x coordinate of the model in metres.
    DX      =  0.01     #: discretisation step in the x direction of the model in metres.
    DY      =  0.01     #: discretisation step in the y direction of the model in metres.
    FIT     = True      #: model-to-window view fitting toggle.


class TTicksSettings():
    """
    Class contains axis ticks parameters.
    """
    # Ticks intervals in metres
    INT_X           = 1.0   #: tick interval in the x direction in metres.
    INT_Y           = 1.0   #: tick interval in the y direction in metres.
    # Label round digits
    ROUND_DIGITS    = 2     #: label decimal precision.
    LABEL_INT       = 1.0   #: label interval in both directions.


class TSurveySettings():
    """
    Class contains survey parameters.
    """
    TYPE        = "ascan"           #: type of the scan (ascan, bscan, rx_array).
    TSF         = 1.0               #: time stability factor.
    TIME_WINDOW = 0.0               #: time window in seconds.
    WAVE_TYPE   = "gaussian"        #: shape of the emitted wave.
    AMPLITUDE   = 1.0               #: amplitude of the wave.
    FREQUENCY   = 0.0               #: frequency of the wave in hertz.
    SRC_TYPE    = "hertzian_dipole" #: source type.
    SRC_X       = 0.0               #: source position in the x direction.
    SRC_Y       = 0.0               #: source position in the y direction.
    RX_X        = 0.0               #: receiver position in the x direction.
    RX_Y        = 0.0               #: receiver position in the y direction.
    SRC_STEP_X  = 0.0               #: source step in the x direction.
    SRC_STEP_Y  = 0.0               #: source step in the y direction.
    RX_STEP_X   = 0.0               #: receiver step in the x direction.
    RX_STEP_Y   = 0.0               #: receiver step in the y direction.
    RX_MAX_X    = 0.0               #: x coordinate of the last receiver in an array.
    RX_MAX_Y    = 0.0               #: y coordinate of the last receiver in an array.
    MESSAGES    = "yes"             #: toggle displaying messages during simulation.
    GEOM_VIEW   = "no"              #: toggle creating a geometry view file.
    GEOM_FILE   = ""                #: geometry file name.
    SNAPSHOT    = "no"              #: toggle creating a snapshot.
    SNAP_TIME   = 0.0               #: time of the snapshot.
    SNAP_FILE   = ""                #: snapshot file name.

class TColours():
    """
    Class contains colours diplay settings.
    """
    FILL = False    #: toggle filling shapes with an uniform colour.