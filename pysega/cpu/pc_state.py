#
# 8-bit registers, combine 8-bit to generate 16-bit
#

class PC_Register(object):
    def __init__(self, num_bits):
        self._value = 0
        self._mask = (2 ** num_bits) - 1

    def get_save_state(self):
        return self.value

    def set_save_state(self, state):
        self.value = state

    def __add__(self, x):
        if isinstance(x, PC_Register):
          self.value = (self.value + x.value) & self._mask
        else:
          self.value = (self.value + x) & self._mask
        return self

    def __sub__(self, x):
        if isinstance(x, PC_Register):
          self.value = (self.value - x.value) & self._mask
        else:
          self.value = (self.value - x) & self._mask
        return self

    def __int__(self):
        return self.value


    def __setattribute__(self, name, x):
        print "setattribute"
        self.value = x & self._mask

    def set_value(self, value):
        if isinstance(value, PC_Register):
            self.value = value.get_value()
        else:
            self.value = value & self._mask

    def get_value(self):
        return self.value

    def __str__(self):
        return "%X"%(self.value)

class PC_StatusFlags(object):
    def __init__(self):
        self.value = 0

    def get_save_state(self):
        return self.value

    def set_save_state(self, state):
        self.value = state

    def set_S(self, value):
        self.value = (self.value & ~(1 << 7)) | ((value & 1) << 7)

    def set_Z(self, value):
        self.value = (self.value & ~(1 << 6)) | ((value & 1) << 6)

    def set_X2(self, value):
        self.value = (self.value & ~(1 << 5)) | ((value & 1) << 5)

    def set_H(self, value):
        self.value = (self.value & ~(1 << 4)) | ((value & 1) << 4)

    def set_X1(self, value):
        self.value = (self.value & ~(1 << 3)) | ((value & 1) << 3)

    def set_PV(self, value):
        self.value = (self.value & ~(1 << 2)) | ((value & 1) << 2)

    def set_N(self, value):
        self.value = (self.value & ~(1 << 1)) | ((value & 1) << 1)

    def set_C(self, value):
        self.value = (self.value & ~(1 << 0)) | ((value & 1) << 0)

    def get_S(self):
        return (self.value >> 7) & 1

    def get_Z(self):
        return (self.value >> 6) & 1

    def get_X2(self):
        return (self.value >> 5) & 1

    def get_H(self):
        return (self.value >> 4) & 1

    def get_X1(self):
        return (self.value >> 3) & 1

    def get_PV(self):
        return (self.value >> 2) & 1

    def get_N(self):
        return (self.value >> 1) & 1

    def get_C(self):
        return (self.value >> 0) & 1

    def __str__(self):
        return "(C:%s N:%s PV:%s X1:%s H:%s X2:%s Z:%s S:%s)"%(
                self.get_C(), self.get_N(),  self.get_PV(), self.get_X1(), 
                self.get_H(), self.get_X2(), self.get_Z(), self.get_S())

class PC_State(object):
    """ Initially, an ineficient but convinient representation of PC State.
    """
    eight_bit_registers = ['A', 'B', 'C', 'D', 'E', 'HLHigh', 'HLLow', 'F', 'PCHigh', 'PCLow', 'SPHigh', 'SPLow', 'IXHigh', 'IXLow', 'IYHigh', 'IYLow']

    sixteen_bit_registers = ['PC', 'SP', 'IX', 'IY', 'HL']
    def __init__(self):
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
        return "TODO"
