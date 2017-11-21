
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

class PC_State(object):
    """ Initially, an ineficient but convinient representation of PC State.
    """
    eight_bit_registers = ['A', 'B', 'C', 'D', 'E', 'HLHigh', 'HLLow', 'F', 'PCHigh', 'PCLow', 'SPHigh', 'SPLow', 'IXHigh', 'IXLow', 'IYHigh', 'IYLow']

    sixteen_bit_registers = ['PC', 'SP', 'IX', 'IY', 'HL']
    def __init__(self):

        self.Fstatus =  PC_StatusFlags()

        self._PC = 0
        for name in PC_State.eight_bit_registers:
            super(PC_State, self).__setattr__(name, 0)

        for name in PC_State.sixteen_bit_registers:
            super(PC_State, self).__setattr__(name, 0)

        self.I      = 0
        self.R      = 0
        self.IM     = 0
        self.IFF1   = 0
        self.IFF2   = 0

        self._F = PC_StatusFlags()

        self.CYCLES_TO_CLOCK = 3

    def __getitem__(self, index):
        result = None
        if (0 == index):
            result = self.B
        elif (1 == index):
            result = self.C
        elif (2 == index):
            result = self.D
        elif (3 == index):
            result = self.E
        elif (4 == index):
            result = self.H
        elif (5 == index):
            result = self.L
        elif (7 == index):
            result = self.A

        return result

    def __setitem__(self, index, value):
        if (0 == index):
             self.B = value
        elif (1 == index):
             self.C = value
        elif (2 == index):
             self.D = value
        elif (3 == index):
             self.E = value
        elif (4 == index):
             self.H = value
        elif (5 == index):
             self.L = value
        elif (7 == index):
             self.A = value

    def get_save_state(self):
        # TODO
        state = {}
        return state

    def set_save_state(self, state):
        # TODO
        pass

    def __getattribute__(self, name):
        if name in PC_State.eight_bit_registers:
            return super(PC_State, self).__getattribute__(name) & 0xFF
        elif name in PC_State.sixteen_bit_registers:
            return super(PC_State, self).__getattribute__("%sHigh"%(name)) * 256 + super(PC_State, self).__getattribute__("%sLow"%(name))
        else:
            return super(PC_State, self).__getattribute__(name)

    def __setattr__(self, name, value):
        if name in self.eight_bit_registers:
            super(PC_State, self).__setattr__(name, value & 0xFF)
        elif name in PC_State.sixteen_bit_registers:
            super(PC_State, self).__setattr__("%sHigh"%(name), value/256 & 0xFF)
            super(PC_State, self).__setattr__("%sLow"%(name),  value % 256)
        else:
            super(PC_State, self).__setattr__(name, value)

    def __str__(self):
        return "A:%x SP:%x B:%x C:%x D:%x E:%x HLHigh:%x HLLow:%x F:%x PCHigh:%x PCLow:%x SPHigh:%x SPLow:%x IXHigh:%x IXLow:%x IYHigh:%x IYLow:%x %s"%(self.A, self.SP, self.B,self.C,self.D,self.E,self.HLHigh,self.HLLow,self.F,self.PCHigh,self.PCLow,self.SPHigh,self.SPLow,self.IXHigh,self.IXLow,self.IYHigh,self.IYLow, self._F)

