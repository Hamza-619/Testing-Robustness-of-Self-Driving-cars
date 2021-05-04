import ctypes
import os

if os.name == 'nt':
    _LIBRARY_FILE = "dd-situation-view.dll"
else:
    _LIBRARY_FILE = "libdd-situation-view.so"

try:
    _CURRENT_SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
    _DEFAULT_LIBRARY_PATH = os.path.join(_CURRENT_SCRIPT_PATH, "..", "..", "bin")
    os.environ["PATH"] += os.pathsep + _DEFAULT_LIBRARY_PATH
except:
    pass

_LIBRARY = ctypes.cdll.LoadLibrary(_LIBRARY_FILE)

ARE_INDICATORS_VALID = False
INVALID_INDICATORS = None
MAX_INDICATORS = None
MIN_INDICATORS = None

class Indicators_t(ctypes.Structure):
    _fields_ = [
        ('Speed',  ctypes.c_double),
        ('Fast',   ctypes.c_double),
        ('Angle',  ctypes.c_double),
        ('LL',     ctypes.c_double),
        ('ML',     ctypes.c_double),
        ('MR',     ctypes.c_double),
        ('RR',     ctypes.c_double),
        ('DistLL', ctypes.c_double),
        ('DistMM', ctypes.c_double),
        ('DistRR', ctypes.c_double),
        ('L',      ctypes.c_double),
        ('M',      ctypes.c_double),
        ('R',      ctypes.c_double),
        ('DistL',  ctypes.c_double),
        ('DistR',  ctypes.c_double),
    ]


    def __init__(self):
        self.reset()

    def __str__(self):
        String = ""
        String += "Speed={}\n".format(self.Speed)
        String += "Fast={}\n".format(self.Fast)
        String += "Angle={}\n".format(self.Angle)
        String += "LL={}\n".format(self.LL)
        String += "ML={}\n".format(self.ML)
        String += "MR={}\n".format(self.MR)
        String += "RR={}\n".format(self.RR)
        String += "DistLL={}\n".format(self.DistLL)
        String += "DistMM={}\n".format(self.DistMM)
        String += "DistRR={}\n".format(self.DistRR)
        String += "L={}\n".format(self.L)
        String += "M={}\n".format(self.M)
        String += "R={}\n".format(self.R)
        String += "DistL={}\n".format(self.DistL)
        String += "DistR={}\n".format(self.DistR)
        return String


    def reset(self):
        if ARE_INDICATORS_VALID:
            self.Speed  = 35
            self.Fast   = 0
            self.Angle  = 0
            self.LL     = INVALID_INDICATORS.LL
            self.ML     = -2
            self.MR     = 2
            self.RR     = INVALID_INDICATORS.RR
            self.DistLL = INVALID_INDICATORS.DistLL
            self.DistMM = INVALID_INDICATORS.DistMM
            self.DistRR = INVALID_INDICATORS.DistRR
            self.L      = INVALID_INDICATORS.L
            self.M      = -2
            self.R      = 2
            self.DistL  = INVALID_INDICATORS.L
            self.DistR  = INVALID_INDICATORS.R


    def copyTo(self, Indicators):
        Indicators.Speed  = self.Speed
        Indicators.Fast   = self.Fast
        Indicators.Angle  = self.Angle
        Indicators.LL     = self.LL
        Indicators.ML     = self.ML
        Indicators.MR     = self.MR
        Indicators.RR     = self.RR
        Indicators.DistLL = self.DistLL
        Indicators.DistMM = self.DistMM
        Indicators.DistRR = self.DistRR
        Indicators.L      = self.L
        Indicators.M      = self.M
        Indicators.R      = self.R
        Indicators.DistL  = self.DistL
        Indicators.DistR  = self.DistR

    def copyFrom(self, Indicators):
        self.Speed = Indicators.Speed
        self.Fast = Indicators.Fast
        self.Angle = Indicators.Angle
        self.LL = Indicators.LL
        self.ML = Indicators.ML
        self.MR = Indicators.MR
        self.RR = Indicators.RR
        self.DistLL = Indicators.DistLL
        self.DistMM = Indicators.DistMM
        self.DistRR =Indicators.DistRR
        self.L = Indicators.L
        self.M = Indicators.M
        self.R = Indicators.R
        self.DistL = Indicators.DistL
        self.DistR = Indicators.DistR

    def toDict(self):
        indicators_dict = dict()
        indicators_dict['Speed']  = self.Speed
        indicators_dict['Fast']   = self.Fast
        indicators_dict['Angle']  = self.Angle
        indicators_dict['LL']     = self.LL
        indicators_dict['ML']     = self.ML
        indicators_dict['MR']     = self.MR
        indicators_dict['RR']     = self.RR
        indicators_dict['DistLL'] = self.DistLL
        indicators_dict['DistMM'] = self.DistMM
        indicators_dict['DistRR'] = self.DistRR
        indicators_dict['L']      = self.L
        indicators_dict['M']      = self.M
        indicators_dict['R']      = self.R
        indicators_dict['DistL']  = self.DistL
        indicators_dict['DistR']  = self.DistR
        return indicators_dict

    @staticmethod
    def fromDict(indicators_dict):
        indicators = Indicators_t()
        indicators.Speed = 60
        indicators.Fast = 0
        indicators.Angle = float(indicators_dict['Angle'])
        indicators.LL = float(indicators_dict['LL'])
        indicators.ML = float(indicators_dict['ML'])
        indicators.MR = 0
        indicators.RR = float(indicators_dict['RR'])
        indicators.DistLL = float(indicators_dict['DistLL'])
        indicators.DistMM = float(indicators_dict['DistMM'])
        indicators.DistRR = 0
        indicators.L = float(indicators_dict['L'])
        indicators.M = 0
        indicators.R = float(indicators_dict['R'])
        indicators.DistL = 0
        indicators.DistR = 0
        return indicators

    def isCarInLane(self):
        return (self.ML >= MIN_INDICATORS.ML) and (self.ML <= MAX_INDICATORS.ML) and (self.MR >= MIN_INDICATORS.MR) and (self.MR <= MAX_INDICATORS.MR)

    def isCarOnLane(self):
        return (self.M >= MIN_INDICATORS.M) and (self.M <= MAX_INDICATORS.M)

    def isLeftLane(self):
        if (self.isCarInLane()):
            return (self.LL >= MIN_INDICATORS.LL) and (self.LL <= MAX_INDICATORS.LL)
        elif (self.isCarOnLane()):
            return (self.L >= MIN_INDICATORS.L) and (self.L <= MAX_INDICATORS.L)
        else:
            return False

    def isRightLane(self):
        if (self.isCarInLane()):
            return (self.RR >= MIN_INDICATORS.RR) and (self.RR <= MAX_INDICATORS.RR)
        elif (self.isCarOnLane()):
            return (self.R >= MIN_INDICATORS.R) and (self.R <= MAX_INDICATORS.R)
        else :
            return False

    def getNumberOfLanes(self):
        if (self.isCarInLane()):
            NumberOfLanes = 1
        else:
            NumberOfLanes = 0

        if (self.isLeftLane()):
            NumberOfLanes = NumberOfLanes+ 1

        if (self.isRightLane()):
            NumberOfLanes = NumberOfLanes + 1

        return NumberOfLanes

def setupIndicators():
    global INVALID_INDICATORS
    getInvalidIndicators = _LIBRARY.getInvalidIndicators
    getInvalidIndicators.restype = ctypes.POINTER(Indicators_t)
    INVALID_INDICATORS = getInvalidIndicators().contents

    global MAX_INDICATORS
    getMaxIndicators = _LIBRARY.getMaxIndicators
    getMaxIndicators.restype = ctypes.POINTER(Indicators_t)
    MAX_INDICATORS = getMaxIndicators().contents

    global MIN_INDICATORS
    getMinIndicators = _LIBRARY.getMinIndicators
    getMinIndicators.restype = ctypes.POINTER(Indicators_t)
    MIN_INDICATORS = getMinIndicators().contents

    global ARE_INDICATORS_VALID
    ARE_INDICATORS_VALID = True

setupIndicators()
