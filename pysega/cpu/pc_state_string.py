class PC_StatusFlagFields(object):
    __slots__ = ('value')
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
      if name in PC_StatusFlagFields.flags:
        return (self.value >> PC_StatusFlagFields.flags[name]) & 1
      else:
        return super(PC_StatusFlagFields, self).__getattribute__(name)

    def __setattr__(self, name, value):
      if name in PC_StatusFlagFields.flags:
        shift = PC_StatusFlagFields.flags[name]
        self.value = (self.value & ~(1 << shift)) | ((value & 1) << shift)
      else:
        return super(PC_StatusFlagFields, self).__setattr__(name, value)

    def get_save_state(self):
        return self.value

    def set_save_state(self, state):
        self.value = state

    def __str__(self):
        return "(C:%s N:%s PV:%s X1:%s H:%s X2:%s Z:%s S:%s)"%(
                self.C, self.N,  self.PV, self.X1, 
                self.H, self.X2, self.Z, self.S)

class PC_StatusFlags(object):
    __slots__ = ('Fstatus')

    def __init__(self):
        self.Fstatus = PC_StatusFlagFields()
        self.value = 0

    def __getattribute__(self, name):
      if name in 'value':
        return self.Fstatus.value
      else:
        return super(PC_StatusFlags, self).__getattribute__(name)

    def __setattr__(self, name, value):
      if name == 'Fstatus':
        super(PC_StatusFlags, self).__setattr__(name, value)
      elif name == 'value':
        self.Fstatus.value = value
      else:
        super(PC_StatusFlags, self).__setattr__(name, value)

    def __str__(self):
        return str(self.Fstatus)

class PC_State(object):
    """ Initially, an ineficient but convinient representation of PC State.
    """
    __slots__ = ('A', 'B', 'C', 'D', 'E', 'H', 'L', 'PCHigh', 'PCLow', 'SPHigh', 'SPLow', 'IXHigh', 'IXLow', 'IYHigh', 'IYLow','BC_', 'DE_', 'HL_', 'A_', 'F_', 'PC', 'SP', 'IX', 'IY', 'Fstatus', '_PC', 'BC', 'DE', 'HL', 'AF', 'I', 'R', 'IM', 'IFF1', 'IFF2', '_F', 'CYCLES_TO_CLOCK')


    eight_bit_registers = ['A', 'B', 'C', 'D', 'E', 'H', 'L', 'PCHigh', 'PCLow', 'SPHigh', 'SPLow', 'IXHigh', 'IXLow', 'IYHigh', 'IYLow']

    sixteen_bit_shadow_registers = ['BC_', 'DE_', 'HL_']

    eight_bit_shadow_registers = ['A_', 'F_']

    sixteen_bit_registers = ['PC', 'SP', 'IX', 'IY']

    sixteen_bit_split_registers = ['BC', 'DE', 'AF', 'HL']

    sixteen = sixteen_bit_shadow_registers + sixteen_bit_registers + sixteen_bit_split_registers 

    def __init__(self):

        self.Fstatus =  PC_StatusFlags()

        self._PC = 0
        for name in PC_State.eight_bit_registers:
            super(PC_State, self).__setattr__(name, 0)

        for name in PC_State.sixteen_bit_registers:
            super(PC_State, self).__setattr__(name, 0)

        for name in PC_State.sixteen_bit_split_registers:
            super(PC_State, self).__setattr__(name, 0)

        for name in PC_State.sixteen_bit_shadow_registers:
            super(PC_State, self).__setattr__(name, 0)

        for name in PC_State.eight_bit_shadow_registers:
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
        if name == 'F':
            return self.Fstatus
        elif name in PC_State.eight_bit_registers:
            return super(PC_State, self).__getattribute__(name) & 0xFF
        if name in PC_State.sixteen:
            if name in PC_State.sixteen_bit_registers:
                return super(PC_State, self).__getattribute__("%sHigh"%(name)) * 256 + super(PC_State, self).__getattribute__("%sLow"%(name))
            elif name in PC_State.sixteen_bit_split_registers:
                return super(PC_State, self).__getattribute__(name[0]) * 256 + super(PC_State, self).__getattribute__(name[1])
            elif name in PC_State.sixteen_bit_shadow_registers:
                return super(PC_State, self).__getattribute__(name)
        else:
            return super(PC_State, self).__getattribute__(name)

    def __setattr__(self, name, value):
        if name == 'F':
            self.Fstatus.value = value & 0xFF
        elif name in self.eight_bit_registers:
            super(PC_State, self).__setattr__(name, value & 0xFF)
        elif name in PC_State.sixteen_bit_registers:
            super(PC_State, self).__setattr__("%sHigh"%(name), value/256 & 0xFF)
            super(PC_State, self).__setattr__("%sLow"%(name),  value % 256)
        elif name in PC_State.sixteen_bit_split_registers:
            super(PC_State, self).__setattr__(name[0], value/256 & 0xFF)
            super(PC_State, self).__setattr__(name[1],  value % 256)
        elif name in PC_State.sixteen_bit_shadow_registers:
            super(PC_State, self).__setattr__(name, value)
        else:
            super(PC_State, self).__setattr__(name, value)

    def __str__(self):
        return "A:%x SP:%x B:%x C:%x D:%x E:%x H:%x L:%x F:%x PCHigh:%x PCLow:%x SPHigh:%x SPLow:%x IXHigh:%x IXLow:%x IYHigh:%x IYLow:%x %s"%(self.A, self.SP, self.B,self.C,self.D,self.E,self.H,self.L,self.Fstatus.value,self.PCHigh,self.PCLow,self.SPHigh,self.SPLow,self.IXHigh,self.IXLow,self.IYHigh,self.IYLow, self.Fstatus)

