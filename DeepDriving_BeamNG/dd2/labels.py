import ctypes

class Labels_t(ctypes.Structure):
    _fields_ = [
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


    def __str__(self):
        String = ""
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
