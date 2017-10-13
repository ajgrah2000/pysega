
class PC_Register(object):
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

    def set_value(self, value):
        if isinstance(value, PC_Register):
            self.value = value.get_value()
        else:
            self.value = value & 0xFF

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
    def __init__(self):
        self.PC = 0

        self.A  = PC_Register()
        self.B  = PC_Register()
        self.C  = PC_Register()
        self.D  = PC_Register()
        self.E  = PC_Register()
        self.H  = PC_Register()
        self.L  = PC_Register()
        self.F  = PC_Register()
        self.SPHigh = PC_Register()
        self.SPLow  = PC_Register()
        self.PCHigh = PC_Register()
        self.PCLow  = PC_Register()
        self.IXHigh = PC_Register()
        self.IXLow  = PC_Register()
        self.IYHigh = PC_Register()
        self.IYLow  = PC_Register()
        self.I      = PC_Register()
        self.R      = PC_Register()
        self.IM     = PC_Register()
        self.IFF1   = PC_Register()
        self.IFF2   = PC_Register()

        self.F = PC_StatusFlags()

        self.CYCLES_TO_CLOCK = 3

    def get_save_state(self):
        # TODO
        state = {}
        return state

    def set_save_state(self, state):
        # TODO
        pass

    def __str__(self):
        return "TODO"
