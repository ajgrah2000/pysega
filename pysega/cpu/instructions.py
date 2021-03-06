import ctypes
from . import flagtables
from . import addressing
from .. import errors

def signed_char_to_int(value):
    result = value
    if (value & 0x80):
        result = value + 0xFF00
    return result

# self.pc_state.Add two 8 bit ints plus the carry bit, and set flags accordingly
def add8c(pc_state, a, b, c):
    r = a + b + c;
    rs = (a + b + c) & 0xFF;
    if (rs & 0x80): # Negative
        pc_state.F.Fstatus.S = 1
    else:
        pc_state.F.Fstatus.S = 0

    if (rs == 0): # Zero
        pc_state.F.Fstatus.Z = 1
    else:
        pc_state.F.Fstatus.Z = 0

    if (((r & 0xF00) != 0) and 
         (r & 0xF00) != 0xF00):
        pc_state.F.Fstatus.PV = 1
    else:
        pc_state.F.Fstatus.PV = 0

    r = (a & 0xF) + (b & 0xF) + c;
    if (r & 0x10): # Half carry
        pc_state.F.Fstatus.H = 1
    else:
        pc_state.F.Fstatus.H = 0

    pc_state.F.Fstatus.N = 0;

    r = (a & 0xFF) + (b & 0xFF) + c;
    if (r & 0x100): # Carry
        pc_state.F.Fstatus.C = 1
    else:
        pc_state.F.Fstatus.C = 0

    return (a + b + c) & 0xFF

# Subtract two 8 bit ints and the carry bit, set flags accordingly
def sub8c(pc_state, a, b, c):
    r = a - b - c;
    rs = a - b - c;
    if (rs & 0x80): # Negative
        pc_state.F.Fstatus.S = 1
    else:
        pc_state.F.Fstatus.S = 0

    if (rs == 0): # Zero
        pc_state.F.Fstatus.Z = 1
    else:
        pc_state.F.Fstatus.Z = 0

    if (((r & 0x180) != 0) and 
         (r & 0x180) != 0x180): # Overflow
        pc_state.F.Fstatus.PV = 1
    else:
        pc_state.F.Fstatus.PV = 0

    r = (a & 0xF) - (b & 0xF) - c;
    if (r & 0x10): # Half carry
        pc_state.F.Fstatus.H = 1
    else:
        pc_state.F.Fstatus.H = 0
    pc_state.F.Fstatus.N = 1;

    r = (a & 0xFF) - (b & 0xFF) - c;
    if (r & 0x100): # Carry
        pc_state.F.Fstatus.C = 1
    else:
        pc_state.F.Fstatus.C = 0
    return (a - b - c) & 0xFF
    
# self.pc_state.Add two 16 bit ints and set flags accordingly
def add16c(pc_state, a, b, c):
    r = a + b + c;
    rs = r & 0xFFFF;
    if (rs & 0x8000): # Negative
        pc_state.F.Fstatus.S = 1
    else:
        pc_state.F.Fstatus.S = 0

    if (rs == 0): # Zero
        pc_state.F.Fstatus.Z = 1
    else:
        pc_state.F.Fstatus.Z = 0

    # Overflow
    if (((r & 0x18000) != 0) and 
         (r & 0x18000) != 0x18000): # Overflow
        pc_state.F.Fstatus.PV = 1
    else:
        pc_state.F.Fstatus.PV = 0

    r = (a & 0xFFF) + (b & 0xFFF) + c;
    if (r & 0x1000): # Half carry
        pc_state.F.Fstatus.H = 1
    else:
        pc_state.F.Fstatus.H = 0

    pc_state.F.Fstatus.N = 0;

    r = (a & 0xFFFF) + (b & 0xFFFF) + c;
    if (r & 0x10000): # Carry
        pc_state.F.Fstatus.C = 1
    else:
        pc_state.F.Fstatus.C = 0
    return a + b + c;
    
    
def sub16c(pc_state, a, b, c):

    r = a - b - c;
    if (r & 0x8000): # Negative
        pc_state.F.Fstatus.S = 1
    else:
        pc_state.F.Fstatus.S = 0

    if(r == 0): # Zero
        pc_state.F.Fstatus.Z = 1
    else:
        pc_state.F.Fstatus.Z = 0

    if (((r & 0x18000) != 0) and 
         (r & 0x18000) != 0x18000): # Overflow
        pc_state.F.Fstatus.PV = 1
    else:
        pc_state.F.Fstatus.PV = 0

    r = (a & 0xFFF) - (b & 0xFFF) - c;
    if(r & 0x1000): #Half carry
        pc_state.F.Fstatus.H = 1
    else:
        pc_state.F.Fstatus.H = 0

    pc_state.F.Fstatus.N = 1;

    r = (a & 0xFFFF) - (b & 0xFFFF) - c;
    if(r & 0x10000): # Carry
        pc_state.F.Fstatus.C = 1
    else:
        pc_state.F.Fstatus.C = 0

    return a - b - c;

# Calculate the result of the DAA functio
def calculateDAAAdd(pc_state):
    upper = (pc_state.A >> 4) & 0xF;
    lower = pc_state.A & 0xF;
    
    if (pc_state.F.Fstatus.C == 0):
        if ((upper <= 9) and (pc_state.F.Fstatus.H == 0) and (lower <= 9)):
            pass
        elif ((upper <= 8) and (pc_state.F.Fstatus.H == 0) and ((lower >= 0xA) and (lower <= 0xF))):
            pc_state.A += 0x06;
        elif ((upper <= 9) and (pc_state.F.Fstatus.H == 1) and (lower <= 0x3)):
            pc_state.A += 0x06;
        elif (((upper >= 0xA) and (upper <= 0xF)) and (pc_state.F.Fstatus.H == 0) and (lower <= 0x9)):
            pc_state.A += 0x60;
            pc_state.F.Fstatus.C = 1;
        elif (((upper >= 0x9) and (upper <= 0xF)) and (pc_state.F.Fstatus.H == 0) and ((lower >= 0xA) and (lower <= 0xF))):
            pc_state.A += 0x66;
            pc_state.F.Fstatus.C = 1;
        elif (((upper >= 0xA) and (upper <= 0xF)) and (pc_state.F.Fstatus.H == 1) and (lower <= 0x3)):
            pc_state.A += 0x66;
            pc_state.F.Fstatus.C = 1;
    else:
        if ((upper <= 0x2) and (pc_state.F.Fstatus.H == 0) and (lower <= 0x9)):
            pc_state.A += 0x60;
        elif ((upper <= 0x2) and (pc_state.F.Fstatus.H == 0) and ((lower >= 0xA) and (lower <= 0xF))):
            pc_state.A += 0x66;
        elif ((upper <= 0x3) and (pc_state.F.Fstatus.H == 1) and (lower <= 0x3)):
            pc_state.A += 0x66;

    pc_state.F.Fstatus.PV = flagtables.FlagTables.calculateParity(pc_state.A);
    if (pc_state.A & 0x80): # Is negative
        pc_state.F.Fstatus.S  = 1
    else:
        pc_state.F.Fstatus.S  = 0

    if (pc_state.A==0): # Is zero
        pc_state.F.Fstatus.Z = 1
    else:
        pc_state.F.Fstatus.Z = 0

# Fcpu_state->IXME, table in z80 guide is wrong, need to check values by hand
def calculateDAASub(pc_state):
    upper = (pc_state.A >> 4) & 0xF;
    lower = pc_state.A & 0xF;

    if (pc_state.F.Fstatus.C == 0):
        if ((upper <= 0x9) and (pc_state.F.Fstatus.H == 0) and (lower <= 0x9)):
            pass
        elif ((upper <= 0x8) and (pc_state.F.Fstatus.H == 1) and ((lower >= 0x6) and (lower <= 0xF))):
            pc_state.A += 0xFA;
    else:
        if (((upper >= 0x7) and (upper <= 0xF)) and (pc_state.F.Fstatus.H == 0) and (lower <= 0x9)):
            pc_state.A += 0xA0;
        elif (((upper >= 0x6) and (upper <= 0xF)) and (pc_state.F.Fstatus.H == 1) and ((lower >= 0x6) and (lower <= 0xF))):
            pc_state.F.Fstatus.H = 0;
            pc_state.A += 0x9A;
    pc_state.F.Fstatus.PV = flagtables.FlagTables.calculateParity(pc_state.A);
    if (pc_state.A & 0x80): #Is negative
        pc_state.F.Fstatus.S = 1
    else:
        pc_state.F.Fstatus.S = 0
    if (pc_state.A==0): # Is zero
        pc_state.F.Fstatus.Z = 1
    else:
        pc_state.F.Fstatus.Z = 0
    


class Instruction(object):
    FLAG_MASK_INC8 = 0x01; # Bits to leave unchanged
    FLAG_MASK_DEC8 = 0x01; # Bits to leave unchanged

    def __init__(self, pc_state, instruction_exec):
        self.pc_state = pc_state
        self.instruction_exec = instruction_exec

    def execute(self):
        pass

    def _exec(self, data):
        return self.instruction_exec(data)


class JumpInstruction(Instruction):
     
    def __init__(self, memory, pc_state):
        self.memory = memory
        super(JumpInstruction, self).__init__(pc_state, None)

    def execute(self):
        self.pc_state.PC = self.memory.read16(self.pc_state.PC + 1)
        return 10

#class MemoryReadInstruction(Instruction):
#     
#    def __init__(self, memory, clocks, pc_state, instruction_exec, self.memory):
#        super(MemoryReadInstruction, self).__init__(clocks, pc_state, instruction_exec)
#        self.self.memory = self.memory
#        self.instruction_exec = instruction_exec
#
#    def execute(self):
#        return self.instruction_exec(self.self.memory)

class ExtendedInstruction(Instruction):
    def __init__(self, memory, pc_state, get_function):
        self.memory = memory
        self.pc_state = pc_state
        self.instruction_get_function = get_function

    def execute(self):
        # Ignore unsupported instructions (will result in a dereference of 'None')
        return self.instruction_get_function(self.memory.read(self.pc_state.PC + 1)).execute()

    def get_extended_instruction(self):
        return self.instruction_get_function(self.memory.read(self.pc_state.PC + 1))

class Instruction_r(Instruction):
    # TODO
    pass

class Noop(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        """NOP"""
        self.pc_state.PC = self.pc_state.PC + 1
        return 4;

class OUT_n_A(Instruction):
    def __init__(self, memory, pc_state, ports):
        self.memory = memory
        self.pc_state = pc_state
        self.ports    = ports

# OUT (n), self.pc_state.A
# Write register A, to port n
    def execute(self):
     self.ports.portWrite(self.memory.read(self.pc_state.PC + 1), self.pc_state.A)
     self.pc_state.PC+=2;

     return 11;


class RRCA(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.F.Fstatus.C = self.pc_state.A & 0x1;
        self.pc_state.F.Fstatus.H = 0;
        self.pc_state.F.Fstatus.N = 0;
        self.pc_state.A = (self.pc_state.A >> 1) | ((self.pc_state.A & 0x1) << 7);
        self.pc_state.PC += 1

        return 4;


class AND_r(Instruction):
    def __init__(self, memory, pc_state, src):
        self.memory = memory
        self.pc_state = pc_state
        self.src = src

    def execute(self):
        self.pc_state.A = self.pc_state.A & self.src.get();
        self.pc_state.PC += 1
    
        self.pc_state.F.value = flagtables.FlagTables.getStatusAnd(self.pc_state.A);
    
        return 4;

class AND_a(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.PC += 1
        self.pc_state.F.value = flagtables.FlagTables.getStatusAnd(self.pc_state.A);
        return 4;

class AND_n(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
    
        self.pc_state.A = self.pc_state.A & self.memory.read(self.pc_state.PC +1);
        self.pc_state.PC += 2;
        self.pc_state.F.value = flagtables.FlagTables.getStatusAnd(self.pc_state.A);
    
        return 7;

class OR_r(Instruction):
    def __init__(self, memory, pc_state, src):
        self.memory = memory
        self.pc_state = pc_state
        self.src = src

    def execute(self):
        self.pc_state.A = self.pc_state.A | self.src.get();
        self.pc_state.PC += 1
    
        self.pc_state.F.value = flagtables.FlagTables.getStatusOr(self.pc_state.A);
    
        return 4;

class OR_a(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.PC += 1
        self.pc_state.F.value = flagtables.FlagTables.getStatusOr(self.pc_state.A);
        return 4;

class OR_e(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.A = self.pc_state.A | self.pc_state.E
        self.pc_state.PC += 1
    
        self.pc_state.F.value = flagtables.FlagTables.getStatusOr(self.pc_state.A);
    
        return 4;

class XOR_r(Instruction):
    def __init__(self, memory, pc_state, src):
        self.memory = memory
        self.pc_state = pc_state
        self.src = src

    def execute(self):
        self.pc_state.A = self.pc_state.A ^ self.src.get();
        self.pc_state.PC += 1
    
        self.pc_state.F.value = flagtables.FlagTables.getStatusOr(self.pc_state.A);
    
        return 4;

class XOR_a(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state
        self.status = flagtables.FlagTables.getStatusOr(0);

    def execute(self):
        self.pc_state.A = 0
        self.pc_state.PC += 1
        self.pc_state.F.value = self.status
    
        return 4;

class EXX(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        tmp16 = self.pc_state.BC;
        self.pc_state.BC = self.pc_state.BC_;
        self.pc_state.BC_ = tmp16;
    
        tmp16 = self.pc_state.DE;
        self.pc_state.DE = self.pc_state.DE_;
        self.pc_state.DE_ = tmp16;
    
        tmp16 = self.pc_state.HL;
        self.pc_state.HL = self.pc_state.HL_;
        self.pc_state.HL_ = tmp16;
    
        self.pc_state.PC += 1
    
        return 4;

class CP_n(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state
        self._last_pc = 0

    def execute(self):
        self.pc_state.F.value = flagtables.FlagTables.getStatusSub(self.pc_state.A, self.memory.read(self.pc_state.PC +1))

        self.pc_state.PC += 2;
    
        return 7;

    def get_cached_execute(self):
        r =  self.memory.read(self.pc_state.PC +1)
        pc = self.pc_state.PC + 2;

        def _get_cached_execute(self):
            self.pc_state.F.value = flagtables.FlagTables.getStatusSub(self.pc_state.A, r)
            self.pc_state.PC = pc;
        
            return 7;

        return _get_cached_execute

class CP_r(Instruction_r):
    def __init__(self, memory, pc_state, r):
        self.memory = memory
        self.pc_state = pc_state
        self.r = r

    def execute(self):
        self.pc_state.F.value = flagtables.FlagTables.getStatusSub(self.pc_state.A,self.r);
        self.pc_state.PC += 1
    
        return 4;

class JRZe(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    # JR Z, e
    def execute(self):
        if (self.pc_state.F.Fstatus.Z == 1):
            self.pc_state.PC += signed_char_to_int(self.memory.read(self.pc_state.PC+1))
            cycles = 12
        else:
            cycles = 7

        self.pc_state.PC += 2;
    
        return cycles;

    # JR Z, e
    def get_cached_execute(self):
        jump_pc = self.pc_state.PC + signed_char_to_int(self.memory.read(self.pc_state.PC+1)) + 2
        no_jump_pc = self.pc_state.PC + 2;
        ps = self.pc_state

        def _get_cached_execute(self):
            if (ps.F.Fstatus.Z == 1):
                ps.PC = jump_pc
                cycles = 12
            else:
                ps.PC = no_jump_pc
                cycles = 7

            return cycles;

        return _get_cached_execute

class JPNC(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    # JP NC, e
    def execute(self):
         if (self.pc_state.F.Fstatus.C == 0):
             self.pc_state.PC = self.memory.read16(self.pc_state.PC+1);
         else:
             self.pc_state.PC += 3;
    
         return 10;

    def get_cached_execute(self):
        jump_pc = self.memory.read16(self.pc_state.PC+1);
        no_jump_pc = self.pc_state.PC + 3

        def _get_cached_execute(self):
            if (self.pc_state.F.Fstatus.C == 0):
                self.pc_state.PC = jump_pc
            else:
                self.pc_state.PC = no_jump_pc
    
            return 10;

        return _get_cached_execute
    

class JPCnn(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    # JP C, nn
    def execute(self):
         if (self.pc_state.F.Fstatus.C == 1):
             self.pc_state.PC = self.memory.read16(self.pc_state.PC+1);
         else:
             self.pc_state.PC += 3;
    
         return 10;

class JRNZe(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state
        self._last_pc = 0
        self._next_pc = 0

    # JR NZ, e
    def execute(self):
        cycles = 7;
    
        if (self.pc_state.F.Fstatus.Z == 0):
            if (self._last_pc == self.pc_state.PC):
                self.pc_state.PC = self._next_pc
            else:
                self._last_pc = self.pc_state.PC
                self.pc_state.PC += signed_char_to_int(self.memory.read(self.pc_state.PC+1))
                self._next_pc = self.pc_state.PC
            cycles+=5;
    
        self.pc_state.PC += 2;
    
        return cycles;

    def get_cached_execute(self):
        jump_pc = self.pc_state.PC + signed_char_to_int(self.memory.read(self.pc_state.PC+1)) + 2
        no_jump_pc = self.pc_state.PC + 2
    
        def _get_cached_execute(self):
            if (self.pc_state.F.Fstatus.Z == 0):
                self.pc_state.PC = jump_pc
                cycles = 12;
            else:
                self.pc_state.PC = no_jump_pc
                cycles = 7;
        
            return cycles;

        return _get_cached_execute

class INC_r(Instruction_r):
    def __init__(self, memory, pc_state, r):
        self.memory = memory
        self.pc_state = pc_state
        self.r = r

    def execute(self):
        self.r += 1
        self.pc_state.F.value = (self.pc_state.F.value & Instruction.FLAG_MASK_INC8) | flagtables.FlagTables.getStatusInc8(self.r.get() & 0xFF);
        self.pc_state.PC += 1
    
        return 4;

class INC_16(Instruction):
    def __init__(self, memory, pc_state, r, cycles, pcInc = 1):
        self.memory = memory
        self.pc_state = pc_state
        self.r = r
        self.cycles = cycles
        self.pcInc = pcInc

    def execute(self):
      self.r += 1
      self.pc_state.PC += self.pcInc;
  
      return self.cycles;

class DEC_16(Instruction):
    def __init__(self, memory, pc_state, r, cycles, pcInc = 1):
        self.memory = memory
        self.pc_state = pc_state
        self.r = r
        self.cycles = cycles
        self.pcInc = pcInc

    def execute(self):
        self.r -= 1;
        self.pc_state.PC += self.pcInc;
    
        return self.cycles;
    

class DEC_r(Instruction_r):
    def __init__(self, memory, pc_state, r):
        self.memory = memory
        self.pc_state = pc_state
        self.r = r

    def execute(self):
        self.r -= 1;
        self.pc_state.F.value = (self.pc_state.F.value & Instruction.FLAG_MASK_DEC8) | flagtables.FlagTables.getStatusDec8(self.r.get());
        self.pc_state.PC += 1
    
        return 4;
    

class INC_BC(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.BC += 1
        self.pc_state.PC += 1
    
        return 6;

class INC_HL(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    # INC (self.pc_state.HL)
    def execute(self):
        self.memory.write(self.pc_state.HL, self.memory.read(self.pc_state.HL) + 1);
        self.pc_state.F.value = (self.pc_state.F.value & Instruction.FLAG_MASK_INC8) | flagtables.FlagTables.getStatusInc8(self.memory.read(self.pc_state.HL));
        self.pc_state.PC  += 1
        return 11;

class DEC_HL(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.memory.write(self.pc_state.HL, self.memory.read(self.pc_state.HL) - 1)
        self.pc_state.F.value = (self.pc_state.F.value & Instruction.FLAG_MASK_DEC8) | flagtables.FlagTables.getStatusDec8(self.memory.read(self.pc_state.HL));
        self.pc_state.PC  += 1
        return 11;

class DJNZ(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    # DJNZ n
    def execute(self):
        cycles = 8;
    
        self.pc_state.B -= 1;
        if (self.pc_state.B != 0):

            self.pc_state.PC += signed_char_to_int(self.memory.read(self.pc_state.PC + 1))
            cycles += 5
    
        self.pc_state.PC += 2
    
        return cycles
    

class RET(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.PCLow  = self.memory.read(self.pc_state.SP)
        self.pc_state.SP += 1
        self.pc_state.PCHigh = self.memory.read(self.pc_state.SP)
        self.pc_state.SP += 1
    
        return 10;

# Addition instructions

class ADD16(Instruction):
    def __init__(self, memory, pc_state, dst, add, cycles, pcInc = 1):
        self.memory = memory
        self.pc_state = pc_state
        self.dst = dst
        self.add = add
        self.cycles = cycles
        self.pcInc = pcInc

    def execute(self):
        a = self.dst.get()
        b = self.add.get()

        r = (a & 0xFFF) + (b & 0xFFF);
        if (r & 0x1000): # Half carry
          self.pc_state.F.Fstatus.H = 1 # Half carry
        else:
          self.pc_state.F.Fstatus.H = 0 # Half carry
        self.pc_state.F.Fstatus.N = 0;
    
        r = (a & 0xFFFF) + (b & 0xFFFF);
        if (r & 0x10000): # Carry
          self.pc_state.F.Fstatus.C = 1 # Carry
        else:
          self.pc_state.F.Fstatus.C = 0 # Carry
    
        self.dst.set(r)
    
        self.pc_state.PC += self.pcInc;
    
        return self.cycles;

class ADD_r(Instruction):
    def __init__(self, memory, pc_state, src):
        self.memory = memory
        self.pc_state = pc_state
        self.src = src

    def execute(self):
            self.pc_state.F.value = flagtables.FlagTables.getStatusAdd(self.pc_state.A,self.src.get());
            self.pc_state.A = self.pc_state.A + self.src.get();
            self.pc_state.PC += 1
            return 4;

class SUB_r(Instruction):
    def __init__(self, memory, pc_state, src):
        self.memory = memory
        self.pc_state = pc_state
        self.src = src

    def execute(self):
            self.pc_state.F.value = flagtables.FlagTables.getStatusSub(self.pc_state.A,self.src.get());
            self.pc_state.A = self.pc_state.A - self.src.get();
            self.pc_state.PC += 1
            return 4;

class SUB_a(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
            self.pc_state.F.value = flagtables.FlagTables.getStatusSub(self.pc_state.A,self.pc_state.A);
            self.pc_state.A = 0
            self.pc_state.PC += 1
            return 4;

class BIT_r(Instruction):
    def __init__(self, memory, pc_state, src):
        self.memory = memory
        self.pc_state = pc_state
        self.src = src

    def execute(self):
        tmp8 = self.memory.read(self.pc_state.PC+1)

        self.pc_state.F.Fstatus.Z = (self.src.get() >> ((tmp8 >> 3) & 7)) ^ 0x1;
        self.pc_state.F.Fstatus.PV = flagtables.FlagTables.calculateParity(self.src.get());
        self.pc_state.F.Fstatus.H = 1;
        self.pc_state.F.Fstatus.N = 0;
        self.pc_state.F.Fstatus.S = 0;
        self.pc_state.PC += 2;
        return 8;

# self.pc_state.Bit b, (self.pc_state.HL) 
class BIT_HL(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        tmp8 = self.memory.read(self.pc_state.PC+1)
        self.pc_state.F.Fstatus.Z = (self.memory.read(self.pc_state.HL) >> 
                            ((tmp8 >> 3) & 7)) ^ 0x1;
        self.pc_state.F.Fstatus.H = 1;
        self.pc_state.F.Fstatus.N = 0;
        self.pc_state.F.Fstatus.S = 0;
        self.pc_state.PC += 2;

        return 12;

# RES b, r
class RES_b_r(Instruction):
    def __init__(self, memory, pc_state, dst):
        self.memory = memory
        self.pc_state = pc_state
        self.dst = dst

    def execute(self):
        tmp8 = self.memory.read(self.pc_state.PC+1)
        self.dst.set(int(self.dst) & ~(0x1 << ((tmp8 >> 3) & 7)));
        self.pc_state.PC += 2;
        return 8;

# RES b, HL
class RES_b_HL(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        tmp8 = self.memory.read(self.pc_state.PC+1)
        self.memory.write(self.pc_state.HL, self.memory.read(self.pc_state.HL) & ~(0x1 << ((tmp8 >> 3) & 7)));
        self.pc_state.PC += 2;
        return 12;

# SET b, r
class SET_b_r(Instruction):
    def __init__(self, memory, pc_state, dst):
        self.memory = memory
        self.pc_state = pc_state
        self.dst = dst

    def execute(self):
        tmp8 = self.memory.read(self.pc_state.PC+1)
        self.dst.set(int(self.dst) | (0x1 << ((tmp8 >> 3) & 7)));
        self.pc_state.PC += 2;
        return 8;

# SET b, HL
class SET_b_HL(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        tmp8 = self.memory.read(self.pc_state.PC+1)
        self.memory.write(self.pc_state.HL, self.memory.read(self.pc_state.HL) | (0x1 << ((tmp8 >> 3) & 7)));
        self.pc_state.PC += 2;
        return 12;


class RLCA(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.A = (self.pc_state.A << 1) | ((self.pc_state.A >> 7) & 0x1);
        self.pc_state.F.Fstatus.C = self.pc_state.A & 0x1;
        self.pc_state.F.Fstatus.N = 0;
        self.pc_state.F.Fstatus.H = 0;
        self.pc_state.PC += 1
        return 4;

# RLC r
class RLC_r(Instruction):
    def __init__(self, memory, pc_state, dst):
        self.memory = memory
        self.pc_state = pc_state
        self.dst = dst

    def execute(self):
        self.dst.set((int(self.dst) << 1) | ((int(self.dst) >> 7) & 0x1));
        self.pc_state.F.value = flagtables.FlagTables.getStatusOr(int(self.dst));
        self.pc_state.F.Fstatus.C = int(self.dst) & 0x1; # bit-7 of src = bit-0
        self.pc_state.PC+=2;
        return 8;

# RLC (HL)
class RLC_HL(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        tmp8 = self.memory.read(self.pc_state.HL);
        self.memory.write(self.pc_state.HL, (tmp8 << 1) | ((tmp8 >> 7) & 0x1));
        self.pc_state.F.value = flagtables.FlagTables.getStatusOr(self.memory.read(self.pc_state.HL));
        self.pc_state.F.Fstatus.C = (tmp8 >> 7) & 0x1; # bit-7 of src
        self.pc_state.PC+=2;
        return 15;

# RRC r
class RRC_r(Instruction):
    def __init__(self, memory, pc_state, dst):
        self.memory = memory
        self.pc_state = pc_state
        self.dst = dst

    def execute(self):
        self.dst.set((int(self.dst) >> 1) | ((int(self.dst) & 0x1) << 7));
        self.pc_state.F.value = flagtables.FlagTables.getStatusOr(self.dst);
        self.pc_state.F.Fstatus.C = (int(self.dst) >> 7) & 0x1; # bit-0 of src
        self.pc_state.PC+=2;
        return 8

# RRC (HL)
class RRC_HL(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        tmp8 = self.memory.read(self.pc_state.HL);
        self.memory.write(self.pc_state.HL,(tmp8 >> 1) | ((tmp8 & 0x1) << 7));
        self.pc_state.F.value = flagtables.FlagTables.getStatusOr(self.memory.read(self.pc_state.HL));
        self.pc_state.F.Fstatus.C = tmp8 & 0x1; # bit-0 of src
        self.pc_state.PC+=2;
        return 8;

# RL r
class RL_r(Instruction):
    def __init__(self, memory, pc_state, dst):
        self.memory = memory
        self.pc_state = pc_state
        self.dst = dst

    def execute(self):
        tmp8 = int(self.dst);
        self.dst.set((int(self.dst) << 1) | (self.pc_state.F.Fstatus.C));
        self.pc_state.F.value = flagtables.FlagTables.getStatusOr(int(self.dst));
        self.pc_state.F.Fstatus.C = (tmp8 >> 7) & 0x1;
        self.pc_state.PC+=2;
        return 8

# RR r
class RR_r(Instruction):
    def __init__(self, memory, pc_state, dst):
        self.memory = memory
        self.pc_state = pc_state
        self.dst = dst

    def execute(self):
        tmp8 = int(self.dst);
        self.dst.set((int(self.dst) >> 1) | (self.pc_state.F.Fstatus.C << 7));
        self.pc_state.F.value = flagtables.FlagTables.getStatusOr(int(self.dst));
        self.pc_state.F.Fstatus.C = tmp8 & 0x1;
        self.pc_state.PC+=2;
        return 8;

# SLA r
class SLA_r(Instruction):
    def __init__(self, memory, pc_state, dst):
        self.memory = memory
        self.pc_state = pc_state
        self.dst = dst

    def execute(self):
        tmp8 = (int(self.dst) >> 7) & 0x1;
        self.dst.set(int(self.dst) << 1)
        self.pc_state.F.value = flagtables.FlagTables.getStatusOr(int(self.dst))
        self.pc_state.F.Fstatus.C = tmp8;

        self.pc_state.PC += 2;
        return 8

# SLA (HL)
class SLA_HL(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        tmp8 = (self.memory.read(self.pc_state.HL) >> 7) & 0x1;
        self.memory.write(self.pc_state.HL, self.memory.read(self.pc_state.HL) << 1);
        self.pc_state.F.value = flagtables.FlagTables.getStatusOr(self.memory.read(self.pc_state.HL));
        self.pc_state.F.Fstatus.C = tmp8;

        self.pc_state.PC += 2;
        return 15

# SRA r
class SRA_r(Instruction):
    def __init__(self, memory, pc_state, dst):
        self.memory = memory
        self.pc_state = pc_state
        self.dst = dst

    def execute(self):
        tmp8 = int(self.dst);
        self.dst.set((int(self.dst) & 0x80) | ((int(self.dst) >> 1) & 0x7F));

        self.pc_state.F.value = flagtables.FlagTables.getStatusOr(self.dst);
        self.pc_state.F.Fstatus.C = tmp8 & 0x1;

        self.pc_state.PC += 2;
        return 8

# SRA (HL)
class SRA_HL(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        tmp8 = self.memory.read(self.pc_state.HL);
        self.memory.write(self.pc_state.HL, (tmp8 & 0x80) | ((tmp8 >> 1) & 0x7F));

        self.pc_state.F.value = flagtables.FlagTables.getStatusOr(self.memory.read(self.pc_state.HL));
        self.pc_state.F.Fstatus.C = tmp8 & 0x1;

        self.pc_state.PC += 2;
        return 15;

# SLL r
class SLL_r(Instruction):
    def __init__(self, memory, pc_state, dst):
        self.memory = memory
        self.pc_state = pc_state
        self.dst = dst

    def execute(self):
        tmp8 = (int(self.dst) >> 7) & 0x1;
        self.dst.set(int(self.dst) << 1 | 0x1);
        self.pc_state.F.value = flagtables.FlagTables.getStatusOr(int(self.dst));
        self.pc_state.F.Fstatus.C = tmp8;

        self.pc_state.PC += 2;
        return 8

# SLL (HL)
class SLL_HL(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        tmp8 = (self.memory.read(self.pc_state.HL) >> 7) & 0x1;
        self.memory.write(self.pc_state.HL, self.memory.read(self.pc_state.HL) << 1 | 0x1);
        self.pc_state.F.value = flagtables.FlagTables.getStatusOr(self.memory.read(self.pc_state.HL));
        self.pc_state.F.Fstatus.C = tmp8;

        self.pc_state.PC += 2;
        return 15

# SRL r
class SRL_r(Instruction):
    def __init__(self, memory, pc_state, dst):
        self.memory = memory
        self.pc_state = pc_state
        self.dst = dst

    def execute(self):
        tmp8 = int(self.dst);
        self.dst.set((int(self.dst) >> 1) & 0x7F);

        self.pc_state.F.value = flagtables.FlagTables.getStatusOr(int(self.dst));
        self.pc_state.F.Fstatus.C = tmp8 & 0x1;

        self.pc_state.PC += 2;
        return 8;

# SRL (HL)
class SRL_HL(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        tmp8 = self.memory.read(self.pc_state.HL);
        self.memory.write(self.pc_state.HL, (tmp8 >> 1) & 0x7F);

        self.pc_state.F.value = flagtables.FlagTables.getStatusOr(self.memory.read(self.pc_state.HL));
        self.pc_state.F.Fstatus.C = tmp8 & 0x1;

        self.pc_state.PC += 2;
        return 15;

class InstructionExec(object):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    
class Load16BC(Instruction):

    def __init__(self, memory, pc_state, r16):
        self.memory = memory
        self.pc_state = pc_state
        self.r16 = r16

    def execute(self):
      # Load 16-bit cpu_state->BC register
      # LD cpu_state->BC, 0x
    
      self.r16.set(self.memory.read16(self.pc_state.PC+1))
      self.pc_state.PC += 3;

      return 10;

# Load a 16-bit register with the value 'nn'
class LD_16_nn(Instruction):
    def __init__(self, memory, pc_state, r16):
        self.memory = memory
        self.pc_state = pc_state
        self.r16 = r16

    def execute(self):
      self.r16.set(self.memory.read16(self.pc_state.PC+1)); 
      self.pc_state.PC += 3;
      return 10;

class LD_r_r(Instruction):
    def __init__(self, memory, pc_state, dst, src):
        self.memory = memory
        self.pc_state = pc_state
        self.dst = dst
        self.src = src

    # Load any register to any other register.
    def execute(self):
      self.dst.set(self.src.get());
      self.pc_state.PC += 1;

      return 4;

# LD (16 REG), n
# Load the value 'n' into the 16-bit address
class LD_mem_n(Instruction):
    def __init__(self, memory, pc_state, addr):
        self.memory = memory
        self.pc_state = pc_state
        self.addr = addr

    # Load the 8 bit value 'n' into self.memory.
    def execute(self):
      self.memory.write(self.addr, self.memory.read(self.pc_state.PC +1));
      self.pc_state.PC += 2;

      return 10;

# LD (self.pc_state.IY+d), r
class LD_IY_d_r(Instruction):
    def __init__(self, memory, pc_state, src):
        self.memory = memory
        self.pc_state = pc_state
        self.src = src

    def execute(self):
        self.memory.write(self.pc_state.IY + signed_char_to_int(self.memory.read(self.pc_state.PC+2)), self.src.get()); 
        self.pc_state.PC += 3;
        return 19

# LD (16 REG), r
# The register r into the 16-bit address
class LD_mem_r(Instruction_r):
    # r - 8-bit
    def __init__(self, memory, pc_state, addr, r):
        self.memory = memory
        self.pc_state = pc_state
        self.addr = addr
        self.r = r

    # Load the register into self.memory.
    def execute(self):
        self.memory.write(self.addr, self.r);
        self.pc_state.PC += 1;

        return 7;

# LD r, (16 REG)
# Load the value from the 16-bit address into the register
class LD_r_mem (Instruction):
    # r - 8-bit
    def __init__(self, memory, pc_state, r, addr):
        self.memory = memory
        self.pc_state = pc_state
        self.addr = addr
        self.r = r

    # Load the value at the address into a register.
    def execute(self):
        self.r.set(self.memory.read(int(self.addr)));
        self.pc_state.PC += 1;
        return 7;

# LD r, (nn)
# Load the value from the 16-bit address into the 16-bit register
class LD_r16_mem(Instruction):
    # r - 16-bit
    def __init__(self, memory, pc_state, r):
        self.memory = memory
        self.pc_state = pc_state
        self.r = r

    # Load the value at the address into a register.
    def execute(self):
        self.r.set(self.memory.read16(self.memory.read16(self.pc_state.PC+1)));
        self.pc_state.PC += 3;

        return 20;

# LD r, (nn)
# Load the value from the 16-bit address into the 8-bit register
class LD_r8_mem(Instruction):
    # r - 8-bit
    def __init__(self, memory, pc_state, r):
        self.memory = memory
        self.pc_state = pc_state
        self.r = r

    # Load the value at the address into a register.
    def execute(self):
        self.r.set(self.memory.read(self.memory.read16(self.pc_state.PC+1)));
        self.pc_state.PC += 3;

        return 13;

    def get_cached_execute(self):
        r = self.memory.read16(self.pc_state.PC+1)
        s = self.r.set
        pc = self.pc_state.PC + 3;

        def _get_cached_execute(self):
            s(self.memory.read(r));
            self.pc_state.PC = pc
            return 13;

        return _get_cached_execute

class LD_r(Instruction_r):
    # r - 8-bit
    def __init__(self, memory, pc_state, r):
        self.memory = memory
        self.pc_state = pc_state
        self.r = r

    def execute(self):
        # This can be optimised.
        self.r.set(self.memory.read(self.pc_state.PC + 1));
        self.pc_state.PC += 2;
        return 7;

# LD self.I_reg, nn
class LD_I_nn(Instruction):
    def __init__(self, memory, pc_state, I_reg):
        self.memory = memory
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self):
        self.I_reg.set(self.memory.read16(self.pc_state.PC+2))
        self.pc_state.PC += 4
        return 20
    
# LD (nn), self.I_reg
class LD_nn_I(Instruction):
    def __init__(self, memory, pc_state, I_reg):
        self.memory = memory
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self):
        self.memory.write(self.memory.read16(self.pc_state.PC+2), self.I_reg.get_low())
        self.memory.write(self.memory.read16(self.pc_state.PC+2)+1, self.I_reg.get_high())
        self.pc_state.PC += 4
    
        return 20
    
# LD self.I_reg, (nn)
class LD_I__nn_(Instruction):
    def __init__(self, memory, pc_state, I_reg):
        self.memory = memory
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self):
        self.I_reg.set(self.memory.read16(self.memory.read16(self.pc_state.PC+2)))
        self.pc_state.PC += 4
    
        return 20
    
# INC (self.I_reg+d)
class INC_I_d(Instruction):
    def __init__(self, memory, pc_state, I_reg):
        self.memory = memory
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self):
        tmp16 = self.I_reg.get() + signed_char_to_int(self.memory.read(self.pc_state.PC+2))
        self.memory.write(tmp16, self.memory.read(tmp16) + 1)
        self.pc_state.F.value = (self.pc_state.F.value & Instruction.FLAG_MASK_INC8) | flagtables.FlagTables.getStatusInc8(self.memory.read(tmp16))
        self.pc_state.PC+=3
        return 23
    
# self.pc_state.DEC (self.I_reg+d)
class DEC_I_d(Instruction):
    def __init__(self, memory, pc_state, I_reg):
        self.memory = memory
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self):
        tmp16 = self.I_reg.get() + signed_char_to_int(self.memory.read(self.pc_state.PC+2))
        self.memory.write(tmp16, self.memory.read(tmp16) - 1)
        self.pc_state.F.value = (self.pc_state.F.value & Instruction.FLAG_MASK_DEC8) | flagtables.FlagTables.getStatusDec8(self.memory.read(tmp16))
        self.pc_state.PC+=3
        return 23
    
# LD (self.I_reg + d), n
class LD_I_d_n(Instruction):
    def __init__(self, memory, pc_state, I_reg):
        self.memory = memory
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self):
        tmp16 = self.I_reg.get() + signed_char_to_int(self.memory.read(self.pc_state.PC+2))
        self.memory.write(tmp16, self.memory.read(self.pc_state.PC+3))
        self.pc_state.PC += 4
        return  19
    
# LD r, (self.I_reg+e)
class LD_r_I_e(Instruction):
    def __init__(self, memory, pc_state, I_reg, dst):
        self.memory = memory
        self.pc_state = pc_state
        self.I_reg = I_reg
        self.dst = dst

    def execute(self):
        self.dst.set(self.memory.read(self.I_reg.get() + signed_char_to_int(self.memory.read(self.pc_state.PC+2))))
                                        
        self.pc_state.PC = self.pc_state.PC + 3
        return  19
    
# LD (self.I_reg+d), r
class LD_I_d_r(Instruction):
    def __init__(self, memory, pc_state, I_reg, src):
        self.memory = memory
        self.pc_state = pc_state
        self.I_reg = I_reg
        self.src = src

    def execute(self):
                          
        self.memory.write(self.I_reg.get() + signed_char_to_int(self.memory.read(self.pc_state.PC+2)), self.src.get()) 
        self.pc_state.PC += 3
        return  19
    
# self.pc_state.ADD self.pc_state.A,(self.I_reg+d)
class ADDA_I_d(Instruction):
    def __init__(self, memory, pc_state, I_reg):
        self.memory = memory
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self):
        tmp8 = self.memory.read(self.I_reg.get() + 
                         signed_char_to_int(self.memory.read(self.pc_state.PC+2)))
        self.pc_state.F.value = flagtables.FlagTables.getStatusAdd(self.pc_state.A,tmp8)
        self.pc_state.A = self.pc_state.A + tmp8
        self.pc_state.PC += 3
        return  19
    
# self.pc_state.ADC (self.I_reg + d)
class ADC_I_d(Instruction):
    def __init__(self, memory, pc_state, I_reg):
        self.memory = memory
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self):
        self.pc_state.A = add8c(self.pc_state, self.pc_state.A, self.memory.read(self.I_reg.get() + signed_char_to_int(self.memory.read(self.pc_state.PC+2))), self.pc_state.F.Fstatus.C)
        self.pc_state.PC+=3
        return 19
    
# SUB (self.I_reg + d)
class SUB_I_d(Instruction):
    def __init__(self, memory, pc_state, I_reg):
        self.memory = memory
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self):
        tmp8 = self.memory.read(self.I_reg.get() + 
                         signed_char_to_int(self.memory.read(self.pc_state.PC+2)))
        self.pc_state.F.value = flagtables.FlagTables.getStatusSub(self.pc_state.A,tmp8)
        self.pc_state.A = self.pc_state.A - tmp8
        self.pc_state.PC += 3
        return  19
    
# self.pc_state.AND (self.I_reg + d)
class AND_I_d(Instruction):
    def __init__(self, memory, pc_state, I_reg):
        self.memory = memory
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self):
        self.pc_state.A = self.pc_state.A & self.memory.read(self.I_reg.get() +
                         signed_char_to_int(self.memory.read(self.pc_state.PC+2)))
        self.pc_state.PC+=3
        self.pc_state.F.value = flagtables.FlagTables.getStatusAnd(self.pc_state.A)
    
        return 19
    
# XOR (self.I_reg + d)
class XOR_I_d(Instruction):
    def __init__(self, memory, pc_state, I_reg):
        self.memory = memory
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self):
        self.pc_state.A = self.pc_state.A ^ self.memory.read(self.I_reg.get() +
                         signed_char_to_int(self.memory.read(self.pc_state.PC+2)))
        self.pc_state.PC+=3
        self.pc_state.F.value = flagtables.FlagTables.getStatusOr(self.pc_state.A)
    
        return  19
    
# OR (self.I_reg + d)
class OR_I_d(Instruction):
    def __init__(self, memory, pc_state, I_reg):
        self.memory = memory
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self):
        tmp8 = self.memory.read(self.I_reg.get() + 
                         signed_char_to_int(self.memory.read(self.pc_state.PC+2)))
        self.pc_state.A = self.pc_state.A | tmp8
        self.pc_state.F.value = flagtables.FlagTables.getStatusOr(self.pc_state.A)
        self.pc_state.PC += 3
        return  19
    
# CP (self.I_reg + d)
class CP_I_d(Instruction):
    def __init__(self, memory, pc_state, I_reg):
        self.memory = memory
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self):
        tmp8 = self.memory.read(self.I_reg.get() + 
                         signed_char_to_int(self.memory.read(self.pc_state.PC+2)))
        self.pc_state.F.value = flagtables.FlagTables.getStatusSub(self.pc_state.A,tmp8)
        self.pc_state.PC+=3
        return 19
    
# Probably should turn this into a lookup table
class BIT_I_d(Instruction):
    def __init__(self, memory, pc_state, I_reg):
        self.memory = memory
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self):
        tmp16 = self.I_reg.get() + signed_char_to_int(self.memory.read(self.pc_state.PC+2))
        tmp8  = self.memory.read(tmp16)
        t8    = self.memory.read(self.pc_state.PC+3)

        if ((t8 & 0xC7) == 0x46): # self.pc_state.BIT b, (self.I_reg.get() + d)
            tmp8 = (tmp8 >> ((t8 & 0x38) >> 3)) & 0x1
            f = self.pc_state.F.Fstatus
            f.Z = tmp8 ^ 0x1
            f.PV = flagtables.FlagTables.calculateParity(tmp8)
            f.H = 1
            f.N = 0
            f.S = 0
        elif ((t8 & 0xC7) == 0x86): # RES b, (self.I_reg + d)
            tmp8 = tmp8 & ~(0x1 << ((t8 >> 3) & 0x7))
            self.memory.write(tmp16,tmp8)
        elif ((t8 & 0xC7) == 0xC6): # SET b, (self.I_reg + d)
            tmp8 = tmp8 | (0x1 << ((t8 >> 3) & 0x7))
            self.memory.write(tmp16,tmp8)
        else:
            errors.error("Instruction arg for 0xFD 0xCB")
    
        self.pc_state.PC += 4
    
        return  23

    def get_cached_execute(self):
        offset = signed_char_to_int(self.memory.read(self.pc_state.PC+2))
        t8    = self.memory.read(self.pc_state.PC+3)

        if ((t8 & 0xC7) == 0x46): # self.pc_state.BIT b, (self.I_reg.get() + d)
         t8_2 = (t8 & 0x38) >> 3
         def _get_cached_execute(self):
            tmp16 = self.I_reg.get() + offset
            tmp8  = self.memory.read(tmp16)

            tmp8 = (tmp8 >> t8_2) & 0x1

            f = self.pc_state.F.Fstatus
            f.Z = tmp8 ^ 0x1
            f.PV = flagtables.FlagTables.calculateParity(tmp8)
            f.H = 1
            f.N = 0
            f.S = 0
    
            self.pc_state.PC += 4
    
            return  23
        elif ((t8 & 0xC7) == 0x86): # RES b, (self.I_reg + d)
          t8_2 = ~(0x1 << ((t8 >> 3) & 0x7))
          def _get_cached_execute(self):
            tmp16 = self.I_reg.get() + offset
            tmp8  = self.memory.read(tmp16) & t8_2
            self.memory.write(tmp16,tmp8)
    
            self.pc_state.PC += 4
    
            return  23

        elif ((t8 & 0xC7) == 0xC6): # SET b, (self.I_reg + d)
          t8_2 =(0x1 << ((t8 >> 3) & 0x7))
          def _get_cached_execute(self):
            tmp16 = self.I_reg.get() + offset
            tmp8  = self.memory.read(tmp16) | t8_2
            self.memory.write(tmp16,tmp8)
    
            self.pc_state.PC += 4
    
            return  23

        return _get_cached_execute
    
# POP self.I_reg
class POP_I(Instruction):
    def __init__(self, memory, pc_state, I_reg):
        self.memory = memory
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self):
        self.I_reg.set_low(self.memory.read(self.pc_state.SP))
        self.pc_state.SP += 1
        self.I_reg.set_high(self.memory.read(self.pc_state.SP))
        self.pc_state.SP += 1
        self.pc_state.PC += 2
        return  14
    
# EX (self.pc_state.SP), self.I_reg
class EX_SP_I(Instruction):
    def __init__(self, memory, pc_state, I_reg):
        self.memory = memory
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self):
        tmp8 = self.memory.read(self.pc_state.SP)
        self.memory.write(self.pc_state.SP, self.I_reg.get_low())
        self.I_reg.set_low(tmp8)
        tmp8 = self.memory.read(self.pc_state.SP+1)
        self.memory.write(self.pc_state.SP+1, self.I_reg.get_high())
        self.I_reg.set_high(tmp8)
        self.pc_state.PC+=2
        return  23
    
# PUSH self.I_reg
class PUSH_I(Instruction):
    def __init__(self, memory, pc_state, I_reg):
        self.memory = memory
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self):
        self.pc_state.SP -= 1
        self.memory.write(self.pc_state.SP, self.I_reg.get_high())
        self.pc_state.SP -= 1
        self.memory.write(self.pc_state.SP, self.I_reg.get_low())
        self.pc_state.PC += 2
    
        return 15
    
# Don't know how many self.clocks.cycles
# LD self.pc_state.PC, self.I_reg
class LD_PC_I(Instruction):
    def __init__(self, memory, pc_state, I_reg):
        self.memory = memory
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self):
        self.pc_state.PC = self.I_reg.get()
        return 6

# IN r, (C)
class IN_r_C(Instruction):
    def __init__(self, memory, pc_state, ports, reg):
        self.memory = memory
        self.pc_state = pc_state
        self.reg = reg
        self.ports = ports

    def execute(self):
        self.reg.set(self.ports.portRead(self.pc_state.C))
        self.pc_state.PC += 2;
        return 12;
    
# OUT (C), r
class OUT_C_r(Instruction):
    def __init__(self, memory, pc_state, ports, reg):
        self.memory = memory
        self.pc_state = pc_state
        self.reg = reg
        self.ports = ports

    def execute(self):
        self.ports.portWrite(self.pc_state.C, self.reg.get());
        self.pc_state.PC += 2;
        return 3;
    
# SBC_HL_r16
class SBC_HL_r16(Instruction):
    def __init__(self, memory, pc_state, reg):
        self.memory = memory
        self.pc_state = pc_state
        self.reg = reg

    def execute(self):
        self.pc_state.HL = sub16c(self.pc_state, self.pc_state.HL, int(self.reg), self.pc_state.F.Fstatus.C);
    
        self.pc_state.PC += 2;
        return  15;
    
# LD (nn), self.pc_state.BC
class LD_nn_BC(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.memory.write(self.memory.read16(self.pc_state.PC+2), self.pc_state.C);
        self.memory.write(self.memory.read16(self.pc_state.PC+2)+1, self.pc_state.B);
        self.pc_state.PC += 4;
    
        return  20;
    
# NEG
class NEG(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.F.value = flagtables.FlagTables.getStatusSub(0,self.pc_state.A);
        self.pc_state.A = -self.pc_state.A;
        self.pc_state.PC += 2;
        return 8;
    
# LD I, self.pc_state.A
class LD_I_A(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.I = self.pc_state.A;
        self.pc_state.PC += 2;
        return  9;
    
# Load 16-bit self.pc_state.BC register
# LD self.pc_state.BC, (nn)
class LD_BC_nn(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.BC = self.memory.read16(self.memory.read16(self.pc_state.PC+2)); 
        self.pc_state.PC += 4;
        return  20;
    
# Fself.pc_state.IXME, should check, since there is only one
# interupting device, this is the same as normal ret
# RETI
class RETI(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.PCLow  = self.memory.read(self.pc_state.SP);
        self.pc_state.SP += 1
        self.pc_state.PCHigh = self.memory.read(self.pc_state.SP);
        self.pc_state.SP += 1
    
        return  14;
                
# LD (nn), self.pc_state.DE
class LD_nn_DE(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.memory.write(self.memory.read16(self.pc_state.PC+2), self.pc_state.E);
        self.memory.write(self.memory.read16(self.pc_state.PC+2)+1, self.pc_state.D);
        self.pc_state.PC += 4;
    
        return  20;
    
# self.pc_state.IM 1
class IM_1(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.PC+=2;
        self.pc_state.IM = 1;
    
        return  2;
    
# LD self.pc_state.A, I
class LD_A_I(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.A = self.pc_state.I;
        self.pc_state.F.Fstatus.N = 0;
        self.pc_state.F.Fstatus.H = 0;
        self.pc_state.F.Fstatus.PV = self.pc_state.IFF2;
        self.pc_state.F.Fstatus.S = (self.pc_state.A & 0x80) >> 7;
        if (self.pc_state.A == 0):
            self.pc_state.F.Fstatus.Z = 1
        else:
            self.pc_state.F.Fstatus.Z = 0
    
        self.pc_state.PC += 2;
        return  9;
    
# LD self.pc_state.DE, (nn)    
class LD_DE_nn(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.DE = self.memory.read16(self.memory.read16(self.pc_state.PC+2));
        self.pc_state.PC += 4;
        return  20;
    
# Fself.pc_state.IXME, not sure about this
# LD self.pc_state.A, R
class LD_A_R(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        # HMM??? Random???
        self.pc_state.R =  (self.pc_state.R & 0x80) | ((self.pc_state.R + 1) & 0x7F);
        self.pc_state.A = self.pc_state.R;
        self.pc_state.F.Fstatus.N = 0;
        self.pc_state.F.Fstatus.H = 0;
        self.pc_state.F.Fstatus.PV = self.pc_state.IFF2;
        self.pc_state.F.Fstatus.S = (self.pc_state.A & 0x80) >> 7;
        if (self.pc_state.A == 0):
            self.pc_state.F.Fstatus.Z = 1
        else:
            self.pc_state.F.Fstatus.Z = 0
    
        self.pc_state.PC += 2;
        return  9;
    
# Fself.pc_state.IXME, can't find existance of this instruction
# LD (nn), self.pc_state.HL
class LD_nn_HL(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.memory.write(self.memory.read16(self.pc_state.PC+2), self.pc_state.L);
        self.memory.write(self.memory.read16(self.pc_state.PC+2)+1, self.pc_state.H);
        self.pc_state.PC += 4;
    
        return  16;
    
# RRD, wacky instruction
class RRD(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        tmp8 = self.pc_state.A;
        self.pc_state.A = (self.pc_state.A & 0xF0) | (self.memory.read(self.pc_state.HL) & 0xF);
        self.memory.write(self.pc_state.HL, 
               ((self.memory.read(self.pc_state.HL) >> 4) & 0xF) | 
               ((tmp8 << 4) & 0xF0));
    
        tmp8 = self.pc_state.F.Fstatus.C;
        self.pc_state.F.value = flagtables.FlagTables.getStatusOr(self.pc_state.A);
        self.pc_state.F.Fstatus.C = tmp8;
    
        self.pc_state.PC+=2;
        return  18;
    
# self.pc_state.ADC self.pc_state.HL, self.pc_state.r16
class ADC_HL_r16(Instruction):
    def __init__(self, memory, pc_state, reg):
        self.memory = memory
        self.pc_state = pc_state
        self.reg = reg

    def execute(self):
        self.pc_state.HL = add16c(self.pc_state, self.pc_state.HL, int(self.reg), self.pc_state.F.Fstatus.C);
        self.pc_state.PC+=2;
        return 15;
    
# Fself.pc_state.IXME, not sure about the existance of this instruction
# LD self.pc_state.HL, (nn)
class LD_HL_nn(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.HL = self.memory.read16(self.memory.read16(self.pc_state.PC+2));
        self.pc_state.PC += 4;
    
        return  20;
    
# LD (nn), self.pc_state.SP
class LD_nn_SP(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.memory.write(self.memory.read16(self.pc_state.PC+2), self.pc_state.SPLow);
        self.memory.write(self.memory.read16(self.pc_state.PC+2)+1, self.pc_state.SPHigh);
        self.pc_state.PC += 4;
    
        return  6;
    
# Load 16-bit self.pc_state.BC register
# LD self.pc_state.SP, (nn)
class LD_SP_nn(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.SP = self.memory.read16(self.memory.read16(self.pc_state.PC+2)); 
        self.pc_state.PC += 4;
        return  20;
    
# LDI
class LDI(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.memory.write(self.pc_state.DE, self.memory.read(self.pc_state.HL));
        self.pc_state.DE += 1
        self.pc_state.HL += 1
        self.pc_state.BC -= 1
        if (self.pc_state.BC == 0):
            self.pc_state.F.Fstatus.PV = 1
        else:
            self.pc_state.F.Fstatus.PV = 0
        self.pc_state.F.Fstatus.H = 0;
        self.pc_state.F.Fstatus.N = 0;
        self.pc_state.PC += 2;
    
        return  16;
    
# CPI
class CPI(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.F.value = flagtables.FlagTables.getStatusSub(self.pc_state.A,self.memory.read(self.pc_state.HL));
        self.pc_state.HL += 1
        self.pc_state.BC -= 1
        if (self.pc_state.BC == 0):
            self.pc_state.F.Fstatus.PV = 1
        else:
            self.pc_state.F.Fstatus.PV = 0
        self.pc_state.PC += 2;
        return  16;
    
# INI
class INI(Instruction):
    def __init__(self, memory, pc_state, ports):
        self.memory = memory
        self.pc_state = pc_state
        self.ports = ports

    def execute(self):
        self.pc_state.B -= 1
        self.memory.write(self.pc_state.HL, self.ports.portRead(self.pc_state.C));
        self.pc_state.HL += 1
        self.pc_state.F.Fstatus.N = 1;
        if (self.pc_state.B == 0):
            self.pc_state.F.Fstatus.Z = 1;
        else:
            self.pc_state.F.Fstatus.Z = 0;
    
        self.pc_state.PC += 2;
        return  16;
    
# OUTI
class OUTI(Instruction):
    def __init__(self, memory, pc_state, ports):
        self.memory = memory
        self.pc_state = pc_state
        self.ports = ports

    def execute(self):
        self.pc_state.B -= 1
        self.ports.portWrite(self.pc_state.C, self.memory.read(self.pc_state.HL));
        self.pc_state.HL += 1
        if (self.pc_state.B == 0):
            self.pc_state.F.Fstatus.Z = 1
        else:
            self.pc_state.F.Fstatus.Z = 0
        self.pc_state.F.Fstatus.N = 1;
        self.pc_state.PC += 2;
        return  16;
    
# OUTD
class OUTD(Instruction):
    def __init__(self, memory, pc_state, ports):
        self.memory = memory
        self.pc_state = pc_state
        self.ports = ports

    def execute(self):
        self.pc_state.B -= 1
        self.ports.portWrite(self.pc_state.C, self.memory.read(self.pc_state.HL));
        self.pc_state.HL -= 1
        if (self.pc_state.B == 0):
            self.pc_state.F.Fstatus.Z = 1
        else:
            self.pc_state.F.Fstatus.Z = 0
        self.pc_state.F.Fstatus.N = 1;
        self.pc_state.PC += 2;
        return  16;
    
# LDIR
class LDIR(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        cycles = 0
        if (self.pc_state.BC >= 4):
            self.memory.writeMulti(self.pc_state.DE, self.pc_state.HL, 4);
            self.pc_state.DE += 4;
            self.pc_state.HL += 4;
            self.pc_state.BC -= 4;
            cycles += 84;
        else:
            self.pc_state.BC -= 1
            self.memory.write(self.pc_state.DE, self.memory.read(self.pc_state.HL));
            self.pc_state.DE += 1
            self.pc_state.HL += 1
            cycles += 21;
    
        self.pc_state.F.Fstatus.H = 0;
        self.pc_state.F.Fstatus.PV = 0;
        self.pc_state.F.Fstatus.N = 1; # hmmm, not sure
        if (self.pc_state.BC == 0):
            self.pc_state.F.Fstatus.N = 0;
            self.pc_state.PC += 2;
            cycles -=5;

        return cycles
    
# CPIR
class CPIR(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        cycles = 0
        self.pc_state.BC -= 1
        tmp8 = self.pc_state.F.Fstatus.C;
        self.pc_state.F.value = flagtables.FlagTables.getStatusSub(self.pc_state.A,self.memory.read(self.pc_state.HL));
        self.pc_state.HL += 1
        self.pc_state.F.Fstatus.C = tmp8; 
    
        if ((self.pc_state.BC == 0)or(self.pc_state.F.Fstatus.Z == 1)):
            self.pc_state.F.Fstatus.PV = 0; 
            self.pc_state.PC += 2;
            cycles += 16;
        else:
            self.pc_state.F.Fstatus.PV = 1; 
            cycles += 21;

        return cycles
    
# Should speed this function up a bit
# Flags match emulator, not z80 document
# OTIR (port)
class OTIR(Instruction):
    def __init__(self, memory, pc_state, ports):
        self.memory = memory
        self.pc_state = pc_state
        self.ports = ports

    def execute(self):
        cycles = 0
        if (self.pc_state.B >= 8):
            self.pc_state.B -= 8;
            self.ports.portMultiWrite(self.pc_state.C, self.memory.readArray(self.pc_state.HL,8), 8);
            self.pc_state.HL+= 8;
            cycles += 168;
        else:
            self.pc_state.B -= 1
            self.ports.portWrite(self.pc_state.C, self.memory.read(self.pc_state.HL));
            self.pc_state.HL += 1
            cycles += 21;
        self.pc_state.F.Fstatus.S = 0; # Unknown
        self.pc_state.F.Fstatus.H = 0; # Unknown
        self.pc_state.F.Fstatus.PV = 0; # Unknown
        self.pc_state.F.Fstatus.N = 1;
        self.pc_state.F.Fstatus.Z = 0;
        if (self.pc_state.B == 0):
            self.pc_state.F.Fstatus.Z = 1;
            self.pc_state.PC += 2;
            cycles -= 5;
        return cycles
    
# LDDR
class LDDR(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        cycles = 0
        self.memory.write(self.pc_state.DE, self.memory.read(self.pc_state.HL));
        self.pc_state.DE -= 1
        self.pc_state.HL -= 1
        self.pc_state.BC -= 1
        if (self.pc_state.BC == 0):
            self.pc_state.PC += 2;
            cycles += 16;
            self.pc_state.F.Fstatus.N = 0;
            self.pc_state.F.Fstatus.H = 0;
            self.pc_state.F.Fstatus.PV = 0;
        else:
            cycles += 21;

        return cycles


################ NEW INSTRUCTIONS ##################

# EX self.pc_state.AF, self.pc_state.AF'
class EX(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        tmpa = self.pc_state.A;
        tmpf = self.pc_state.F.value;
        self.pc_state.A = self.pc_state.A_;
        self.pc_state.F.value = self.pc_state.F_;
        self.pc_state.A_ = tmpa;
        self.pc_state.F_ = tmpf;

        self.pc_state.PC += 1
        return 4;

# LD (self.pc_state.DE), self.pc_state.A
class LD_DE_A(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.memory.write(self.pc_state.DE, self.pc_state.A);
        self.pc_state.PC += 1
        return  7;

# RLA
class RLA(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        tmp8 = self.pc_state.A;
        self.pc_state.A = (self.pc_state.A << 1) | (self.pc_state.F.Fstatus.C);
        self.pc_state.F.Fstatus.C = (tmp8 & 0x80) >> 7;
        self.pc_state.F.Fstatus.H = 0;
        self.pc_state.F.Fstatus.N = 0;
        self.pc_state.PC += 1
        return 4;

# Relative jump
# JR e
class JR_e(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.PC += signed_char_to_int(self.memory.read(self.pc_state.PC + 1))
        self.pc_state.PC += 2;

        return  12;

# RRA
class RRA(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        tmp8 = self.pc_state.A;
        self.pc_state.A = (self.pc_state.A >> 1) | (self.pc_state.F.Fstatus.C << 7);
        self.pc_state.F.Fstatus.C = tmp8 & 0x1;
        self.pc_state.F.Fstatus.H = 0;
        self.pc_state.F.Fstatus.N = 0;
        self.pc_state.PC += 1
        return 4;

# LD (nn), self.pc_state.HL
class LD__nn_HL(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.memory.write(self.memory.read16(self.pc_state.PC+1), self.pc_state.L);
        self.memory.write(self.memory.read16(self.pc_state.PC+1)+1, self.pc_state.H);
        self.pc_state.PC += 3;

        return  16;

# Really need to put this into a table
class DAA(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        if (self.pc_state.F.Fstatus.N == 0): # self.pc_state.Addition instruction
            calculateDAAAdd(self.pc_state);
        else: # Subtraction instruction
            calculateDAASub(self.pc_state);
        self.pc_state.PC += 1
        return 4;

# CPL
class CPL(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.F.Fstatus.H = 1;
        self.pc_state.F.Fstatus.N = 1;
        self.pc_state.A ^= 0xFF;
        self.pc_state.PC += 1

        return 4;

# JR NC, e
class JRNC_e(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        cycles = 0
        if (self.pc_state.F.Fstatus.C == 0):
            self.pc_state.PC += signed_char_to_int(self.memory.read(self.pc_state.PC+1))
            cycles +=5;

        self.pc_state.PC += 2;
        cycles += 7;

        return cycles


# LD (nn), self.pc_state.A
class LD_nn_A(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.memory.write(self.memory.read16(self.pc_state.PC+1), self.pc_state.A);
        self.pc_state.PC +=3;

        return  13;

# SCF
class SCF(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
         self.pc_state.F.Fstatus.H = 0;
         self.pc_state.F.Fstatus.N = 0;
         self.pc_state.F.Fstatus.C = 1;
         self.pc_state.PC += 1
         return  4;

# JR C, e
class JRC_e(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        cycles = 0
        if (self.pc_state.F.Fstatus.C == 1):
            self.pc_state.PC += signed_char_to_int(self.memory.read(self.pc_state.PC+1))
            cycles +=5;

        self.pc_state.PC += 2;
        cycles += 7;
        return cycles

# CCF
class CCF(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.F.Fstatus.H = self.pc_state.F.Fstatus.C;
        self.pc_state.F.Fstatus.N = 0;
        self.pc_state.F.Fstatus.C = 1-self.pc_state.F.Fstatus.C; #Invert carry flag
        self.pc_state.PC += 1
        return  4;

# LD (self.pc_state.HL), (self.pc_state.HL)
class LD_HL_HL(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.PC += 1
        return  7;

# self.pc_state.ADD (self.pc_state.HL) 
class ADD_HL(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.F.value = flagtables.FlagTables.getStatusAdd(self.pc_state.A,self.memory.read(self.pc_state.HL));
        self.pc_state.A = self.pc_state.A + self.memory.read(self.pc_state.HL);
        self.pc_state.PC += 1
        return 7;

# self.pc_state.ADC r
class ADC_r(Instruction):
    def __init__(self, memory, pc_state, reg):
        self.memory = memory
        self.pc_state = pc_state
        self.reg = reg

    def execute(self):
        self.pc_state.A = add8c(self.pc_state, self.pc_state.A, self.reg.get(), self.pc_state.F.Fstatus.C);
        self.pc_state.PC += 1
        return 4;

# self.pc_state.ADC (self.pc_state.HL)
class ADC_HL(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.A = add8c(self.pc_state, self.pc_state.A, self.memory.read(self.pc_state.HL), self.pc_state.F.Fstatus.C);
        self.pc_state.PC += 1
        return 7;

# SUB (self.pc_state.HL) 
class SUB_HL(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.F.value = flagtables.FlagTables.getStatusSub(self.pc_state.A,self.memory.read(self.pc_state.HL));
        self.pc_state.A = self.pc_state.A - self.memory.read(self.pc_state.HL);
        self.pc_state.PC += 1
        return 7;

# SBC r
class SBC_A_r(Instruction):
    def __init__(self, memory, pc_state, reg):
        self.memory = memory
        self.pc_state = pc_state
        self.reg = reg

    def execute(self):
        self.pc_state.A = sub8c(self.pc_state, self.pc_state.A, self.reg.get(), self.pc_state.F.Fstatus.C);
        self.pc_state.PC += 1
        return 4;

# SBC (self.pc_state.HL)
class SBC_A_HL(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.A = sub8c(self.pc_state, self.pc_state.A, self.memory.read(self.pc_state.HL), self.pc_state.F.Fstatus.C);
        self.pc_state.PC += 1
        return 7;

# self.pc_state.AND (self.pc_state.HL)
class AND_HL(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.A = self.pc_state.A & self.memory.read(self.pc_state.HL);
        self.pc_state.PC += 1
        self.pc_state.F.value = flagtables.FlagTables.getStatusAnd(self.pc_state.A);

        return 7;

# XOR (self.pc_state.HL)
class XOR_HL(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.A = self.pc_state.A ^ self.memory.read(self.pc_state.HL);
        self.pc_state.PC += 1
        self.pc_state.F.value = flagtables.FlagTables.getStatusOr(self.pc_state.A);

        return  7;

# OR (self.pc_state.HL)
class OR_HL(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.A = self.pc_state.A | self.memory.read(self.pc_state.HL);
        self.pc_state.PC += 1
        self.pc_state.F.value = flagtables.FlagTables.getStatusOr(self.pc_state.A);

        return  7;

# CP (self.pc_state.HL) 
class CP_HL(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.F.value = flagtables.FlagTables.getStatusSub(self.pc_state.A,self.memory.read(self.pc_state.HL));
        self.pc_state.PC += 1

        return 7;

# RET NZ
class RET_NZ(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        cycles = 0
        if (self.pc_state.F.Fstatus.Z == 0):
            self.pc_state.PCLow  = self.memory.read(self.pc_state.SP);
            self.pc_state.SP += 1
            self.pc_state.PCHigh = self.memory.read(self.pc_state.SP);
            self.pc_state.SP += 1
            cycles += 11;
        else:
            self.pc_state.PC += 1
            cycles +=5;
        return cycles

# JP NZ, nn
class JPNZ_nn(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        if (self.pc_state.F.Fstatus.Z == 0):
            self.pc_state.PC = self.memory.read16(self.pc_state.PC+1);
        else:
            self.pc_state.PC += 3;

        return  10;

    def get_cached_execute(self):
        jump_pc = self.memory.read16(self.pc_state.PC+1);
        no_jump_pc = self.pc_state.PC + 3;

        def _get_cached_execute(self):
            if (self.pc_state.F.Fstatus.Z == 0):
                self.pc_state.PC = jump_pc
            else:
                self.pc_state.PC = no_jump_pc
            return  10;

        return _get_cached_execute

# JP nn
class JP_nn(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.PC = self.memory.read16(self.pc_state.PC+1);

        return 10;

# CALL NZ, nn
class CALL_NZ_nn(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        cycles = 0
        self.pc_state.PC += 3;
        if (self.pc_state.F.Fstatus.Z == 0):
            self.pc_state.SP -= 1
            self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
            self.pc_state.SP -= 1
            self.memory.write(self.pc_state.SP, self.pc_state.PCLow);
            self.pc_state.PC = self.memory.read16(self.pc_state.PC-2);
            cycles += 7;

        cycles += 10;
        return cycles

# PUSH 
class PUSH(Instruction):
    def __init__(self, memory, pc_state, reg):
        self.memory = memory
        self.pc_state = pc_state
        self.reg = reg

    def execute(self):
        self.pc_state.SP -= 1
        self.memory.write(self.pc_state.SP, self.reg.get_high());
        self.pc_state.SP -= 1
        self.memory.write(self.pc_state.SP, self.reg.get_low());
        self.pc_state.PC += 1

        return 11;

# self.pc_state.ADD n
class ADD_n(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.F.value = flagtables.FlagTables.getStatusAdd(self.pc_state.A,self.memory.read(self.pc_state.PC + 1));
        self.pc_state.A = self.pc_state.A + self.memory.read(self.pc_state.PC + 1);
        self.pc_state.PC+=2;
        return 7;

# RST
class RST(Instruction):
    def __init__(self, memory, pc_state, rst_addr):
        self.memory = memory
        self.pc_state = pc_state
        self.rst_addr = rst_addr

    def execute(self):
        self.pc_state.PC += 1
        self.pc_state.SP -= 1
        self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
        self.pc_state.SP -= 1
        self.memory.write(self.pc_state.SP, self.pc_state.PCLow);

        self.pc_state.PC = self.rst_addr

        return  11;

# RET Z
class RST_Z(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        cycles = 0
        if (self.pc_state.F.Fstatus.Z == 1):
            self.pc_state.PCLow  = self.memory.read(self.pc_state.SP);
            self.pc_state.SP += 1
            self.pc_state.PCHigh = self.memory.read(self.pc_state.SP);
            self.pc_state.SP += 1
            cycles += 11;
        else:
            self.pc_state.PC += 1
            cycles +=5;
        return cycles

# JP Z, nn
class JPZ_nn(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        if (self.pc_state.F.Fstatus.Z == 1):
            self.pc_state.PC = self.memory.read16(self.pc_state.PC+1);
        else:
            self.pc_state.PC += 3;

        return  10;

# CALL Z, nn
class CALL_Z_nn(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        cycles = 0
        self.pc_state.PC += 3;
        if (self.pc_state.F.Fstatus.Z == 1):
            self.pc_state.SP -= 1
            self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
            self.pc_state.SP -= 1
            self.memory.write(self.pc_state.SP, self.pc_state.PCLow);
            self.pc_state.PC = self.memory.read16(self.pc_state.PC-2);

            cycles += 7;
        else:
            cycles += 10;
        return cycles

# CALL nn
class CALL_nn(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.PC += 3;
        self.pc_state.SP -= 1
        self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
        self.pc_state.SP -= 1
        self.memory.write(self.pc_state.SP, self.pc_state.PCLow);
        self.pc_state.PC = self.memory.read16(self.pc_state.PC-2);

        return  17;

# self.pc_state.ADC nn
class ADC_nn(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.A = add8c(self.pc_state, self.pc_state.A, self.memory.read(self.pc_state.PC + 1), self.pc_state.F.Fstatus.C);
        self.pc_state.PC+=2;
        return 4;

# RET NC
class RET_NC(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        cycles = 0
        if (self.pc_state.F.Fstatus.C == 0):
            self.pc_state.PCLow  = self.memory.read(self.pc_state.SP);
            self.pc_state.SP += 1
            self.pc_state.PCHigh = self.memory.read(self.pc_state.SP);
            self.pc_state.SP += 1
            cycles += 11;
        else:
            self.pc_state.PC += 1
            cycles +=5;
        return cycles

# POP self.pc_state.DE
class POP(Instruction):
    def __init__(self, memory, pc_state, reg):
        self.memory = memory
        self.pc_state = pc_state
        self.reg = reg

    def execute(self):
        self.reg.set_low(self.memory.read(self.pc_state.SP))
        self.pc_state.SP += 1
        self.reg.set_high(self.memory.read(self.pc_state.SP));
        self.pc_state.SP += 1
        self.pc_state.PC += 1
        return  10;

# CALL NC, nn  
class CALL_NC_nn(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        cycles = 0
        self.pc_state.PC += 3;
        if (self.pc_state.F.Fstatus.C == 0):
            self.pc_state.SP -= 1
            self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
            self.pc_state.SP -= 1
            self.memory.write(self.pc_state.SP, self.pc_state.PCLow);
            self.pc_state.PC = self.memory.read16(self.pc_state.PC-2);

            cycles += 7;
        else:
            cycles += 10;
        return cycles

# SUB n
class SUB_n(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.F.value = flagtables.FlagTables.getStatusSub(self.pc_state.A,self.memory.read(self.pc_state.PC + 1));
        self.pc_state.A = self.pc_state.A - self.memory.read(self.pc_state.PC + 1);
        self.pc_state.PC += 2;
        return  7;

# RET C
class RET_C(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        cycles = 0
        if (self.pc_state.F.Fstatus.C == 1):
            self.pc_state.PCLow  = self.memory.read(self.pc_state.SP);
            self.pc_state.SP += 1
            self.pc_state.PCHigh = self.memory.read(self.pc_state.SP);
            self.pc_state.SP += 1
            cycles += 11;
        else:
            self.pc_state.PC += 1
            cycles+=5;
        return cycles

# IN self.pc_state.A, (N)
class IN_A_n(Instruction):
    def __init__(self, memory, pc_state, ports):
        self.memory = memory
        self.pc_state = pc_state
        self.ports = ports

    def execute(self):
        self.pc_state.A = self.ports.portRead(self.memory.read(self.pc_state.PC + 1));
        self.pc_state.PC += 2;
        return  11;

# Call C, nn
class CALL_C_nn(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        cycles = 0
        self.pc_state.PC += 3;
        if (self.pc_state.F.Fstatus.C == 1):
            self.pc_state.SP -= 1
            self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
            self.pc_state.SP -= 1
            self.memory.write(self.pc_state.SP, self.pc_state.PCLow);
            self.pc_state.PC = self.memory.read16(self.pc_state.PC-2);
            cycles += 17;
        else:
            cycles += 10;
        return cycles

# SBC n 
class SBC_n(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.A = sub8c(self.pc_state, self.pc_state.A, self.memory.read(self.pc_state.PC + 1), self.pc_state.F.Fstatus.C);
        self.pc_state.PC+=2;
        return 7;

# RET PO  
class RET_PO(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        cycles = 0
        if (self.pc_state.F.Fstatus.PV == 0):
            self.pc_state.PCLow  = self.memory.read(self.pc_state.SP);
            self.pc_state.SP += 1
            self.pc_state.PCHigh = self.memory.read(self.pc_state.SP);
            self.pc_state.SP += 1
            cycles += 11;
        else:
            self.pc_state.PC += 1
            cycles +=5;
        return cycles

# JP PO, nn   Parity Odd 
class JP_PO_nn(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        if (self.pc_state.F.Fstatus.PV == 0):
            self.pc_state.PC = self.memory.read16(self.pc_state.PC+1);
        else:
            self.pc_state.PC += 3;

        return 10;

# EX (self.pc_state.SP), self.pc_state.HL
class EX_SP_HL(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        tmp8 = self.memory.read(self.pc_state.SP);
        self.memory.write(self.pc_state.SP, self.pc_state.L);
        self.pc_state.L = tmp8;
        tmp8 = self.memory.read(self.pc_state.SP+1);
        self.memory.write(self.pc_state.SP+1, self.pc_state.H);
        self.pc_state.H = tmp8;
        self.pc_state.PC += 1
        return  19;

# CALL PO, nn 
class CALL_PO_nn(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        cycles = 0
        self.pc_state.PC += 3;
        if (self.pc_state.F.Fstatus.PV == 0):
            self.pc_state.SP -= 1
            self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
            self.pc_state.SP -= 1
            self.memory.write(self.pc_state.SP, self.pc_state.PCLow);
            self.pc_state.PC = self.memory.read16(self.pc_state.PC-2);
            cycles += 7;

        cycles += 10;
        return cycles

# RET PE  
class RET_PE(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        cycles = 0
        if (self.pc_state.F.Fstatus.PV == 1):
            self.pc_state.PCLow  = self.memory.read(self.pc_state.SP);
            self.pc_state.SP += 1
            self.pc_state.PCHigh = self.memory.read(self.pc_state.SP);
            self.pc_state.SP += 1
            cycles += 11;
        else:
            self.pc_state.PC += 1
            cycles +=5;
        return cycles

# Don't know how many self.clocks.cycles
# LD self.pc_state.PC, self.pc_state.HL
class LD_PC_HL(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.PC = self.pc_state.HL;
        return 6;

# JP PE, nn   Parity Even 
class JP_PE_nn(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        if (self.pc_state.F.Fstatus.PV == 1):
            self.pc_state.PC = self.memory.read16(self.pc_state.PC+1);
        else:
            self.pc_state.PC += 3;

        return 10;

# EX self.pc_state.DE, self.pc_state.HL
class EX_DE_HL(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        tmp16 = self.pc_state.DE;
        self.pc_state.DE = self.pc_state.HL;
        self.pc_state.HL = tmp16;
        self.pc_state.PC += 1
        return 4;

# CALL PE, nn
class CALL_PE_nn(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        cycles = 0
        self.pc_state.PC += 3;
        if (self.pc_state.F.Fstatus.PV == 1):
            self.pc_state.SP -= 1
            self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
            self.pc_state.SP -= 1
            self.memory.write(self.pc_state.SP, self.pc_state.PCLow);
            self.pc_state.PC = self.memory.read16(self.pc_state.PC-2);
            cycles += 7;

        cycles += 10;
        return cycles

# XOR n
class XOR_n(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.A = self.pc_state.A ^ self.memory.read(self.pc_state.PC + 1);
        self.pc_state.F.value = flagtables.FlagTables.getStatusOr(self.pc_state.A);
        self.pc_state.PC+=2;
        return 7;

# RET P, if Positive
class RET_P(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        cycles = 0
        if (self.pc_state.F.Fstatus.S == 0):
            self.pc_state.PCLow  = self.memory.read(self.pc_state.SP);
            self.pc_state.SP += 1
            self.pc_state.PCHigh = self.memory.read(self.pc_state.SP);
            self.pc_state.SP += 1
            cycles += 11;
        else:
            self.pc_state.PC += 1
            cycles +=5;
        return cycles

# POP self.pc_state.AF
class POP_AF(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.F.value = self.memory.read(self.pc_state.SP);
        self.pc_state.SP += 1
        self.pc_state.A = self.memory.read(self.pc_state.SP);
        self.pc_state.SP += 1

        self.pc_state.PC += 1

        return 10;

# JP P, nn    if Positive
class JP_P_nn(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        if (self.pc_state.F.Fstatus.S == 0):
            self.pc_state.PC = self.memory.read16(self.pc_state.PC+1);
        else:
            self.pc_state.PC += 3;

        return 10;

# Disable interupts
# DI
class DI(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.IFF1 = 0;
        self.pc_state.IFF2 = 0;
        self.pc_state.PC += 1

        return 4;

# CALL P, nn  if Positive
class CALL_P_nn(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        cycles = 0
        self.pc_state.PC += 3;
        if (self.pc_state.F.Fstatus.S == 0):
            self.pc_state.SP -= 1
            self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
            self.pc_state.SP -= 1
            self.memory.write(self.pc_state.SP, self.pc_state.PCLow);
            self.pc_state.PC = self.memory.read16(self.pc_state.PC-2);
            cycles += 7;

        cycles += 10;
        return cycles

# PUSH self.pc_state.AF
class PUSH_AF(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.SP -= 1
        self.memory.write(self.pc_state.SP, self.pc_state.A);
        self.pc_state.SP -= 1
        self.memory.write(self.pc_state.SP, self.pc_state.F.value);
        self.pc_state.PC += 1

        return 11;

    def get_cached_execute(self):
        ps = self.pc_state
        w = self.memory.write
        def _get_cached_execute(self):
            ps.SP -= 1
            w(ps.SP, ps.A);
            ps.SP -= 1
            w(ps.SP, ps.F.value);
            ps.PC += 1

            return 11;
        return _get_cached_execute

# OR n
class OR_n(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.A = self.pc_state.A | self.memory.read(self.pc_state.PC + 1);
        self.pc_state.F.value = flagtables.FlagTables.getStatusOr(self.pc_state.A);
        self.pc_state.PC += 2;
        return 7;

# RET M  if Negative
class RET_M(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        cycles = 0
        if (self.pc_state.F.Fstatus.S == 1):
            self.pc_state.PCLow  = self.memory.read(self.pc_state.SP);
            self.pc_state.SP += 1
            self.pc_state.PCHigh = self.memory.read(self.pc_state.SP);
            self.pc_state.SP += 1
            cycles += 11;
        else:
            self.pc_state.PC += 1
            cycles +=5;
        return cycles

# LD self.pc_state.SP, self.pc_state.HL
class LD_SP_HL(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        self.pc_state.SP = self.pc_state.HL;
        self.pc_state.PC += 1
        return 6;

# JP M, nn    if Negative
class JP_M_nn(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        if (self.pc_state.F.Fstatus.S == 1):
            self.pc_state.PC = self.memory.read16(self.pc_state.PC+1);
        else:
            self.pc_state.PC += 3;

        return 10;

# Enable interupts
# EI
class EI(Instruction):
    def __init__(self, memory, clocks, pc_state, interupt, poll_interupts, step):
        self.memory = memory
        self.pc_state = pc_state
        self.interupt = interupt
        self.poll_interupts = poll_interupts
        self.step = step
        self.clocks = clocks

    def execute(self):
        self.pc_state.PC += 1

        # Process next instruction before enabling interupts
        self.step(); # Single step

        self.pc_state.IFF1 = 1;
        self.pc_state.IFF2 = 1;

          # Check for any pending interupts
        if (self.poll_interupts(self.clocks.cycles) == True):
            self.interupt()

        return 4

# CALL M, nn  if Negative
class CALL_M_nn(Instruction):
    def __init__(self, memory, pc_state):
        self.memory = memory
        self.pc_state = pc_state

    def execute(self):
        cycles = 0
        self.pc_state.PC += 3;
        if (self.pc_state.F.Fstatus.S == 1):
            self.pc_state.SP -= 1
            self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
            self.pc_state.SP -= 1
            self.memory.write(self.pc_state.SP, self.pc_state.PCLow);
            self.pc_state.PC = self.memory.read16(self.pc_state.PC-2);

            cycles += 7;
        else:
            cycles += 10;
        return cycles
