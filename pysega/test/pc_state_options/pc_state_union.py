import ctypes

class Register(type(ctypes.Union)):
    def __new__(mcs, name, bases, dict):
        # make the bitfield class
        class regBitfield(ctypes.LittleEndianStructure):
            _fields_ = dict['_fields_']

        # set up the Union
        class regUnion(ctypes.Union):
            _fields_ = [('base', dict['_basetype_']), ('_b', regBitfield)]
            _anonymous_ = ('_b', )
#            __iter__ = _register_iter
#            keys = _register_keys
#            items = _register_items
#            update = _register_update
    
        # retun a subclass of the temporary regUnion class
        return type(ctypes.Union).__new__(mcs, name, (regUnion,), dict)

class MyRegister:
    __metaclass__ = Register
    _fields_ = [('S' , ctypes.c_ubyte, 1),
                ('Z' , ctypes.c_ubyte, 1),
                ('X2', ctypes.c_ubyte, 1),
                ('H' , ctypes.c_ubyte, 1),
                ('X1', ctypes.c_ubyte, 1),
                ('PV', ctypes.c_ubyte, 1),
                ('N' , ctypes.c_ubyte, 1),
                ('C' , ctypes.c_ubyte, 1)]

    _basetype_ = ctypes.c_ubyte


class PC_StatusFlagFields(ctypes.Structure):
    _fields_ = [
                ('C' , ctypes.c_ubyte, 1),
                ('N' , ctypes.c_ubyte, 1),
                ('PV', ctypes.c_ubyte, 1),
                ('X1', ctypes.c_ubyte, 1),
                ('H' , ctypes.c_ubyte, 1),
                ('X2', ctypes.c_ubyte, 1),
                ('Z' , ctypes.c_ubyte, 1),
                ('S' , ctypes.c_ubyte, 1)]

class PC_StatusFlags(ctypes.Union):
    _fields_ = [('status', PC_StatusFlagFields),
                ('value' , ctypes.c_ubyte)]

    _anonymous_ = ('status',)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "(C:%s N:%s PV:%s X1:%s H:%s X2:%s Z:%s S:%s)"%(
                self.C, self.N,  self.PV, self.X1, 
                self.H, self.X2, self.Z, self.S)

class Bytes(ctypes.Structure):
    _fields_ = [('low', ctypes.c_ubyte),
                ('high', ctypes.c_ubyte),
                ]

class Register(ctypes.Union):
    _fields_ = [('bytes', Bytes),
                ('value', ctypes.c_ushort)]


class PC_State_8BitStructure(ctypes.Structure):

    _fields_ =[
               # Register overlays
               ('B', ctypes.c_ubyte),
               ('C', ctypes.c_ubyte),
               ('D', ctypes.c_ubyte),
               ('E', ctypes.c_ubyte),
               ('A', ctypes.c_ubyte),
               ('F', PC_StatusFlags),
               ('H', ctypes.c_ubyte),
               ('L', ctypes.c_ubyte),

               ('PCHigh', ctypes.c_ubyte),
               ('PCLow' , ctypes.c_ubyte),
               ('SPHigh', ctypes.c_ubyte),
               ('SPLow' , ctypes.c_ubyte),
               ('IXHigh', ctypes.c_ubyte),
               ('IXLow' , ctypes.c_ubyte),
               ('IYHigh', ctypes.c_ubyte),
               ('IYLow' , ctypes.c_ubyte),

               # Shadow registers
               ('B_',  ctypes.c_ubyte),
               ('C_',  ctypes.c_ubyte),
               ('D_',  ctypes.c_ubyte),
               ('E_',  ctypes.c_ubyte),
               ('H_',  ctypes.c_ubyte),
               ('L_',  ctypes.c_ubyte),
               ('BC_', ctypes.c_ushort),
               ('DE_', ctypes.c_ushort),
               ('HL_', ctypes.c_ushort),
               ('A_',  ctypes.c_ushort),
               ('F_',  ctypes.c_ushort)]

#    _anonymous_ = ('F',)

class PC_State_16BitStructure(ctypes.BigEndianStructure):

    _fields_ =[
               # Register overlays
               ('BC', ctypes.c_ushort),
               ('DE', ctypes.c_ushort),
               ('AF', ctypes.c_ushort),
               ('HL', ctypes.c_ushort),
               ('PC', ctypes.c_ushort),
               ('SP', ctypes.c_ushort),
               ('IX', ctypes.c_ushort),
               ('IY', ctypes.c_ushort)
               ]

class PC_State(ctypes.Union):
    """ Initially, an ineficient but convinient representation of PC State.
    """
    _fields_ = [('_registers_8bit',  PC_State_8BitStructure),
                ('_registers_16bit', PC_State_16BitStructure)]

    _anonymous_ = ('_registers_8bit', '_registers_16bit')

    def __str__(self):
        return "A:%x SP:%x B:%x C:%x D:%x E:%x H:%x L:%x F:%x PCHigh:%x PCLow:%x SPHigh:%x SPLow:%x IXHigh:%x IXLow:%x IYHigh:%x IYLow:%x %s"%(self.A, self.SP, self.B,self.C,self.D,self.E,self.H,self.L,self.Fstatus.value,self.PCHigh,self.PCLow,self.SPHigh,self.SPLow,self.IXHigh,self.IXLow,self.IYHigh,self.IYLow, self.Fstatus)


