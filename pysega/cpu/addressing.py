
class RegWrapper(object):
    def __init__(self, pc_state):
        self.pc_state = pc_state

class RegWrapperGeneric(RegWrapper):
    def __init__(self, pc_state, reg_string):
        super(RegWrapperGeneric, self).__init__(pc_state)
        self._reg_string = reg_string

    def set(self, value):
        self.pc_state.__setattr__(self._reg_string, value)

    def get(self, value):
        return self.pc_state.__getattribute__(self._reg_string)

class RegWrapper_A(RegWrapperGeneric):
    def __init__(self, pc_state):
        super(RegWrapper_A, self).__init__(pc_state, "A")

class RegWrapper_B(RegWrapperGeneric):
    def __init__(self, pc_state):
        super(RegWrapper_B, self).__init__(pc_state, "B")

class RegWrapper_C(RegWrapperGeneric):
    def __init__(self, pc_state):
        super(RegWrapper_C, self).__init__(pc_state, "C")

class RegWrapper_D(RegWrapperGeneric):
    def __init__(self, pc_state):
        super(RegWrapper_D, self).__init__(pc_state, "D")

class RegWrapper_E(RegWrapperGeneric):
    def __init__(self, pc_state):
        super(RegWrapper_E, self).__init__(pc_state, "E")

class RegWrapper_H(RegWrapperGeneric):
    def __init__(self, pc_state):
        super(RegWrapper_H, self).__init__(pc_state, "H")

class RegWrapper_L(RegWrapperGeneric):
    def __init__(self, pc_state):
        super(RegWrapper_L, self).__init__(pc_state, "L")

class RegWrapper_SP(RegWrapperGeneric):
    def __init__(self, pc_state):
        super(RegWrapper_SP, self).__init__(pc_state, "SP")

class RegWrapper_BC(RegWrapperGeneric):
    def __init__(self, pc_state):
        super(RegWrapper_BC, self).__init__(pc_state, "BC")

class RegWrapper_DE(RegWrapperGeneric):
    def __init__(self, pc_state):
        super(RegWrapper_DE, self).__init__(pc_state, "DE")

class RegWrapper_HL(RegWrapperGeneric):
    def __init__(self, pc_state):
        super(RegWrapper_HL, self).__init__(pc_state, "HL")
