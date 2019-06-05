class TWindow_Size():
    MIN_X       = 0
    MIN_Y       = 0
    MAX_X       = 620
    MAX_Y       = 620
    MARG_X      = 20
    MARG_Y      = 20
    # Position of model box's corners
    BOX_MIN_X   = 20
    BOX_MIN_Y   = 600
    BOX_MAX_X   = 600
    BOX_MAX_Y   = 20


class TModel_Size():
    MIN_X   =  0.00
    MIN_Y   =  0.00
    MAX_X   = 10.00
    MAX_Y   = 10.00
    DOM_X   = 10.00
    DOM_Y   = 10.00
    DX      =  0.01
    DY      =  0.01
    FIT     = True


class TTicksSettings():
    # Ticks intervals in metres
    INT_X           = 1.0
    INT_Y           = 1.0
    # Label round digits
    ROUND_DIGITS    = 2
    LABEL_INT       = 1.0


class TSurveySettings():
    "Survey settings class"
    TYPE        = "ascan"
    TSF         = 1.0
    TIME_WINDOW = 0.0
    WAVE_TYPE   = "gaussian"
    AMPLITUDE   = 1.0
    FREQUENCY   = 0.0
    SRC_TYPE    = "hertzian_dipole"
    SRC_X       = 0.0
    SRC_Y       = 0.0
    RX_X        = 0.0
    RX_Y        = 0.0
    SRC_STEP_X  = 0.0
    SRC_STEP_Y  = 0.0
    RX_STEP_X   = 0.0
    RX_STEP_Y   = 0.0
    RX_MAX_X    = 0.0
    RX_MAX_Y    = 0.0
    MESSAGES    = "yes"
    GEOM_VIEW   = "no"
    GEOM_FILE   = ""
    SNAPSHOT    = "no"
    SNAP_TIME   = 0.0
    SNAP_FILE   = ""

class TColours():
    "Colours diplay settings."
    FILL = False