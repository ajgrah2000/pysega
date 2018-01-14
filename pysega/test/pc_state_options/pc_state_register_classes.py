
class PC_StatusFlags(object):
    flags = {'S' :7,
             'Z' :6,
             'X2':5,
             'H' :4,
             'X1':3,
             'PV':2,
             'N' :1,
             'C' :0}

    def __init__(self):
        self.value = 0

    def __getattribute__(self, name):
      if name in PC_StatusFlags.flags:
        return (self.value >> PC_StatusFlags.flags[name]) & 1
      else:
        return super(PC_StatusFlags, self).__getattribute__(name)

    def __setattr__(self, name, value):
      if name in PC_StatusFlags.flags:
        shift = PC_StatusFlags.flags[name]
        self.value = (self.value & ~(1 << shift)) | ((value & 1) << shift)
      else:
        return super(PC_StatusFlags, self).__setattr__(name, value)

    def get_save_state(self):
        return self.value

    def set_save_state(self, state):
        self.value = state

    def __str__(self):
        return "(C:%s N:%s PV:%s X1:%s H:%s X2:%s Z:%s S:%s)"%(
                self.C, self.N,  self.PV, self.X1, 
                self.H, self.X2, self.Z, self.S)

class PC_Register8bit(object):
    def __init__(self):
        self.value = 0

    def get_save_state(self):
        return self.value

    def set_save_state(self, state):
        self.value = state

    def __add__(self, x):
        self.value = (self.value + x) & 0xFF
        return self

    def __sub__(self, x):
        self.value = (self.value - x) & 0xFF
        return self

    def __int__(self):
        return self.value

    def __and__(self, x):
        return self.get_value() & x

    def set_value(self, value):
        if isinstance(value, PC_Register8bit):
            self.value = value.get_value()
        else:
            self.value = value & 0xFF

    def get_value(self):
        return self.value

    def __str__(self):
        return "%X"%(self.value)

class PC_Register16bit(object):
    def __init__(self, high_register, low_register):
        self.high_register = high_register
        self.low_register = low_register

    def __add__(self, x):
        self.set_value(self.get_value() + x)
        return self

    def __and__(self, x):
        return self.get_value() & x

    def __sub__(self, x):
        self.set_value(self.get_value() - x)
        return self

    def __int__(self):
        return self.get_value()

    def set_value(self, value):
        if isinstance(value, PC_Register16bit):
            self.set_value(value.get_value())
        else:
            self.low_register.set_value(value & 0xFF)
            self.high_register.set_value((value >> 8) & 0xFF)

    def get_value(self):
        value = self.high_register.get_value()
        value = (value << 8) + self.low_register.get_value()
        return value

    def __str__(self):
        return "%X"%(self.get_value())


class PC_State(object):
    """ Initially, an ineficient but convinient representation of PC State.
    """

    def __init__(self):

        self.Fstatus =  PC_StatusFlags()

        self._PC = 0

        self.I      = 0
        self.R      = 0
        self.IM     = 0
        self.IFF1   = 0
        self.IFF2   = 0

        self._F = PC_StatusFlags()

        self.A      = PC_Register8bit()
        self.B      = PC_Register8bit()
        self.C      = PC_Register8bit()
        self.D      = PC_Register8bit()
        self.E      = PC_Register8bit()
        self.H      = PC_Register8bit()
        self.L      = PC_Register8bit()
        self.F      = PC_Register8bit()

        self.PCHigh = PC_Register8bit()
        self.PCLow  = PC_Register8bit()
        self.SPHigh = PC_Register8bit()
        self.SPLow  = PC_Register8bit()
        self.IXHigh = PC_Register8bit()
        self.IXLow  = PC_Register8bit()
        self.IYHigh = PC_Register8bit()
        self.IYLow  = PC_Register8bit()

        self.PC = PC_Register16bit(self.PCHigh, self.PCLow)
        self.SP = PC_Register16bit(self.PCHigh, self.PCLow)
        self.IX = PC_Register16bit(self.IXHigh, self.IXLow)
        self.IY = PC_Register16bit(self.IYHigh, self.IYLow)

        self.BC = PC_Register16bit(self.B, self.C)
        self.DE = PC_Register16bit(self.D, self.E)
        self.AF = PC_Register16bit(self.A, self.F)
        self.HL = PC_Register16bit(self.H, self.L)

        # Shadow registers
        self.B_  = PC_Register8bit()
        self.C_  = PC_Register8bit()
        self.D_  = PC_Register8bit()
        self.E_  = PC_Register8bit()
        self.H_  = PC_Register8bit()
        self.L_  = PC_Register8bit()
        self.BC_ = PC_Register16bit(self.B_, self.C_)
        self.DE_ = PC_Register16bit(self.D_, self.E_)
        self.HL_ = PC_Register16bit(self.H_, self.L_)

        self.A_ = PC_Register8bit()
        self.F_ = PC_Register8bit()


        self.CYCLES_TO_CLOCK = 3

    def __getattribute__(self, name):
        if name == 'F':
            return self.Fstatus.value
        else:
            return super(PC_State, self).__getattribute__(name)

    def __setattr__(self, name, value):
        if name == 'F':
            self.Fstatus.value = int(value) & 0xFF
        else:
            super(PC_State, self).__setattr__(name, value)

    def __str__(self):
        return "A:%x SP:%x B:%x C:%x D:%x E:%x H:%x L:%x F:%x PCHigh:%x PCLow:%x SPHigh:%x SPLow:%x IXHigh:%x IXLow:%x IYHigh:%x IYLow:%x %s"%(self.A, self.SP, self.B,self.C,self.D,self.E,self.H,self.L,self.Fstatus.value,self.PCHigh,self.PCLow,self.SPHigh,self.SPLow,self.IXHigh,self.IXLow,self.IYHigh,self.IYLow, PC_StatusFlags.__str__(self.Fstatus))

