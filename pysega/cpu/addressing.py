
class RegWrapper(object):
    def __init__(self, pc_state):
        self.pc_state = pc_state

class RegWrapperGeneric(RegWrapper):
    def __init__(self, pc_state):
        super(RegWrapperGeneric, self).__init__(pc_state)

    def __int__(self):
        return self.get()

    def __add__(self, value):
        self.set(self.get() + value)
        return self

    def __sub__(self, value):
        self.set(self.get() - value)
        return self

    def get_low(self):
        value = self.get()
        return value & 0xFF

    def get_high(self):
        value = self.get()
        return (value >> 8) & 0xFF

    def set_high(self, value):
        new = self.get_low() + (value << 8)
        self.set(new)

    def set_low(self, value):
        new = value + (self.get_high() << 8)
        self.set(new)

class RegWrapper_A(RegWrapperGeneric):
    def __init__(self, pc_state):
        super(RegWrapper_A, self).__init__(pc_state)

    def __int__(self):
        return self.pc_state.A

    def __and__(self, value):
        return self.pc_state.A & value

    def __add__(self, value):
        self.pc_state.A += value
        return self

    def __sub__(self, value):
        self.pc_state.A -= value
        return self

    def get(self):
        return self.pc_state.A

    def set(self, data):
        self.pc_state.A = data

class RegWrapper_B(RegWrapperGeneric):
    def __init__(self, pc_state):
        super(RegWrapper_B, self).__init__(pc_state)

    def __int__(self):
        return self.pc_state.B

    def __and__(self, value):
        return self.pc_state.B & value

    def __add__(self, value):
        self.pc_state.B += value
        return self

    def __sub__(self, value):
        self.pc_state.B -= value
        return self

    def get(self):
        return self.pc_state.B

    def set(self, data):
        self.pc_state.B = data

class RegWrapper_C(RegWrapperGeneric):
    def __init__(self, pc_state):
        super(RegWrapper_C, self).__init__(pc_state)

    def __int__(self):
        return self.pc_state.C

    def __and__(self, value):
        return self.pc_state.C & value

    def __add__(self, value):
        self.pc_state.C += value
        return self

    def __sub__(self, value):
        self.pc_state.C -= value
        return self

    def get(self):
        return self.pc_state.C

    def set(self, data):
        self.pc_state.C = data

class RegWrapper_D(RegWrapperGeneric):
    def __init__(self, pc_state):
        super(RegWrapper_D, self).__init__(pc_state)

    def __int__(self):
        return self.pc_state.D

    def __and__(self, value):
        return self.pc_state.D & value

    def __add__(self, value):
        self.pc_state.D += value
        return self

    def __sub__(self, value):
        self.pc_state.D -= value
        return self

    def get(self):
        return self.pc_state.D

    def set(self, data):
        self.pc_state.D = data

class RegWrapper_E(RegWrapperGeneric):
    def __init__(self, pc_state):
        super(RegWrapper_E, self).__init__(pc_state)

    def __int__(self):
        return self.pc_state.E

    def __and__(self, value):
        return self.pc_state.E & value

    def __add__(self, value):
        self.pc_state.E += value
        return self

    def __sub__(self, value):
        self.pc_state.E -= value
        return self

    def get(self):
        return self.pc_state.E

    def set(self, data):
        self.pc_state.E = data

class RegWrapper_H(RegWrapperGeneric):
    def __init__(self, pc_state):
        super(RegWrapper_H, self).__init__(pc_state)

    def __int__(self):
        return self.pc_state.H

    def __and__(self, value):
        return self.pc_state.H & value

    def __add__(self, value):
        self.pc_state.H += value
        return self

    def __sub__(self, value):
        self.pc_state.H -= value
        return self

    def get(self):
        return self.pc_state.H

    def set(self, data):
        self.pc_state.H = data

class RegWrapper_L(RegWrapperGeneric):
    def __init__(self, pc_state):
        super(RegWrapper_L, self).__init__(pc_state)

    def __int__(self):
        return self.pc_state.L

    def __and__(self, value):
        return self.pc_state.L & value

    def __add__(self, value):
        self.pc_state.L += value
        return self

    def __sub__(self, value):
        self.pc_state.L -= value
        return self

    def get(self):
        return self.pc_state.L

    def set(self, data):
        self.pc_state.L = data

class RegWrapper_BC(RegWrapperGeneric):
    def __init__(self, pc_state):
        super(RegWrapper_BC, self).__init__(pc_state)

    def __int__(self):
        return self.pc_state.BC

    def __and__(self, value):
        return self.pc_state.BC & value

    def __add__(self, value):
        self.pc_state.BC += value
        return self

    def __sub__(self, value):
        self.pc_state.BC -= value
        return self

    def get(self):
        return self.pc_state.BC

    def set(self, data):
        self.pc_state.BC = data

class RegWrapper_DE(RegWrapperGeneric):
    def __init__(self, pc_state):
        super(RegWrapper_DE, self).__init__(pc_state)

    def __int__(self):
        return self.pc_state.DE

    def __and__(self, value):
        return self.pc_state.DE & value

    def __add__(self, value):
        self.pc_state.DE += value
        return self

    def __sub__(self, value):
        self.pc_state.DE -= value
        return self

    def get(self):
        return self.pc_state.DE

    def set(self, data):
        self.pc_state.DE = data

class RegWrapper_HL(RegWrapperGeneric):
    def __init__(self, pc_state):
        super(RegWrapper_HL, self).__init__(pc_state)

    def __int__(self):
        return self.pc_state.HL

    def __and__(self, value):
        return self.pc_state.HL & value

    def __add__(self, value):
        self.pc_state.HL += value
        return self

    def __sub__(self, value):
        self.pc_state.HL -= value
        return self

    def get(self):
        return self.pc_state.HL

    def set(self, data):
        self.pc_state.HL = data

class RegWrapper_IX(RegWrapperGeneric):
    def __init__(self, pc_state):
        super(RegWrapper_IX, self).__init__(pc_state)

    def __int__(self):
        return self.pc_state.IX

    def __and__(self, value):
        return self.pc_state.IX & value

    def __add__(self, value):
        self.pc_state.IX += value
        return self

    def __sub__(self, value):
        self.pc_state.IX -= value
        return self

    def get(self):
        return self.pc_state.IX

    def set(self, data):
        self.pc_state.IX = data

class RegWrapper_IY(RegWrapperGeneric):
    def __init__(self, pc_state):
        super(RegWrapper_IY, self).__init__(pc_state)

    def __int__(self):
        return self.pc_state.IY

    def __and__(self, value):
        return self.pc_state.IY & value

    def __add__(self, value):
        self.pc_state.IY += value
        return self

    def __sub__(self, value):
        self.pc_state.IY -= value
        return self

    def get(self):
        return self.pc_state.IY

    def set(self, data):
        self.pc_state.IY = data

class RegWrapper_SP(RegWrapperGeneric):
    def __init__(self, pc_state):
        super(RegWrapper_SP, self).__init__(pc_state)

    def __int__(self):
        return self.pc_state.SP

    def __and__(self, value):
        return self.pc_state.SP & value

    def __add__(self, value):
        self.pc_state.SP += value
        return self

    def __sub__(self, value):
        self.pc_state.SP -= value
        return self

    def get(self):
        return self.pc_state.SP

    def set(self, data):
        self.pc_state.SP = data
