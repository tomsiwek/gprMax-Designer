class TWindow_Size():
    MIN_X       = 0
    MIN_Y       = 0
    MAX_X       = 620
    MAX_Y       = 620
    MARG_X      = 15
    MARG_Y      = 15
    # Position of model box's corners
    BOX_MIN_X   = 15
    BOX_MIN_Y   = 605
    BOX_MAX_X   = 605
    BOX_MAX_Y   = 15


class TModel_Size():
    MIN_X   =  0.00
    MIN_Y   =  0.00
    MAX_X   = 10.00
    MAX_Y   = 10.00
    DOM_X   = 10.00
    DOM_Y   = 10.00
    DX      =  0.01
    DY      =  0.01


class TTicksSettings():
    # Ticks intervals in metres
    INT_X           = 1.0
    INT_Y           = 1.0
    # Label round digits
    ROUND_DIGITS    = 2


class TSurveySettings():
    "Survey settings class"
    TYPE        = "ascan"
    DT          = 0.0
    TIME_WINDOW = 0.0
    WAVE_TYPE   = "gaussian"
    AMPLITUDE   = 0.0
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