import ctypes
import flagtables
import addressing

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
        pc_state.Fstatus.S = 1
    else:
        pc_state.Fstatus.S = 0

    if (rs == 0): # Zero
        pc_state.Fstatus.Z = 1
    else:
        pc_state.Fstatus.Z = 0

    if (((r & 0xF00) != 0) and 
         (r & 0xF00) != 0xF00):
        pc_state.Fstatus.PV = 1
    else:
        pc_state.Fstatus.PV = 0

    r = (a & 0xF) + (b & 0xF) + c;
    if (r & 0x10): # Half carry
        pc_state.Fstatus.H = 1
    else:
        pc_state.Fstatus.H = 0

    pc_state.Fstatus.N = 0;

    r = (a & 0xFF) + (b & 0xFF) + c;
    if (r & 0x100): # Carry
        pc_state.Fstatus.C = 1
    else:
        pc_state.Fstatus.C = 0

    return (a + b + c) & 0xFF
    


class Instruction(object):
    FLAG_MASK_INC8 = 0x01; # Bits to leave unchanged
    FLAG_MASK_DEC8 = 0x01; # Bits to leave unchanged

    def __init__(self, clocks, pc_state, instruction_exec):
        self.clocks = clocks
        self.pc_state = pc_state
        self.instruction_exec = instruction_exec

    def execute(self):
        pass

    def _exec(self, data):
        return self.instruction_exec(data)


class JumpInstruction(Instruction):
     
    def __init__(self, clocks, pc_state):
        super(JumpInstruction, self).__init__(clocks, pc_state, None)

    def execute(self, memory):
        self.pc_state.PC = memory.read16(self.pc_state.PC + 1)
        return 10

#class MemoryReadInstruction(Instruction):
#     
#    def __init__(self, clocks, pc_state, instruction_exec, memory):
#        super(MemoryReadInstruction, self).__init__(clocks, pc_state, instruction_exec)
#        self.memory = memory
#        self.instruction_exec = instruction_exec
#
#    def execute(self):
#        return self.instruction_exec(self.memory)

class Instruction_r(Instruction):
    # TODO
    pass

class Noop(Instruction):
    def __init__(self, clocks, pc_state):
        self.pc_state = pc_state
        self.clocks = clocks

    def execute(self, data):
        """NOP"""
        self.pc_state.PC = self.pc_state.PC + 1
        return 4;

class OUT_n_A(Instruction):
    def __init__(self, pc_state, ports):
        self.pc_state = pc_state
        self.ports    = ports

# OUT (n), self.pc_state.A
# Write register A, to port n
    def execute(self, memory):
     self.ports.portWrite(memory.read(self.pc_state.PC + 1), self.pc_state.A)
     self.pc_state.PC+=2;

     return 11;


class RRCA(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    def execute(self, memory):
        self.pc_state.Fstatus.C = self.pc_state.A & 0x1;
        self.pc_state.Fstatus.H = 0;
        self.pc_state.Fstatus.N = 0;
        self.pc_state.A = (self.pc_state.A >> 1) | ((self.pc_state.A & 0x1) << 7);
        self.pc_state.PC += 1

        return 4;


class AND_r(Instruction):
    def __init__(self, pc_state, src):
        self.pc_state = pc_state
        self.src = src

    def execute(self, memory):
        self.pc_state.A = int(self.pc_state.A) & int(self.src);
        self.pc_state.PC += 1
    
        self.pc_state.F = flagtables.FlagTables.getStatusAnd(self.pc_state.A);
    
        return 4;

class AND_n(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    def execute(self, memory):
    
        self.pc_state.A = self.pc_state.A & memory.read(self.pc_state.PC +1);
        self.pc_state.PC += 2;
        self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusAnd(self.pc_state.A);
    
        return 7;

class OR_r(Instruction):
    def __init__(self, pc_state, src):
        self.pc_state = pc_state
        self.src = src

    def execute(self, memory):
        self.pc_state.A = self.pc_state.A | int(self.src);
        self.pc_state.PC += 1
    
        self.pc_state.F = flagtables.FlagTables.getStatusOr(self.pc_state.A);
    
        return 4;

class XOR_r(Instruction):
    def __init__(self, pc_state, src):
        self.pc_state = pc_state
        self.src = src

    def execute(self, memory):
        self.pc_state.A = int(self.pc_state.A) ^ int(self.src);
        self.pc_state.PC += 1
    
        self.pc_state.F = flagtables.FlagTables.getStatusOr(self.pc_state.A);
    
        return 4;

class EXX(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    def execute(self, memory):
        #static uint16 tmp16;
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
    def __init__(self, pc_state):
        self.pc_state = pc_state

    def execute(self, memory):
        self.pc_state.F = flagtables.FlagTables.getStatusSub(self.pc_state.A, memory.read(self.pc_state.PC +1));
        self.pc_state.PC += 2;
    
        return 7;

class CP_r(Instruction_r):
    def __init__(self, pc_state, r):
        self.pc_state = pc_state
        self.r = r

    def execute(self, memory):
        self.pc_state.F = flagtables.FlagTables.getStatusSub(self.pc_state.A,self.r);
        self.pc_state.PC += 1
    
        return 4;

class JRZe(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    # JR Z, e
    def execute(self, memory):
        cycles = 7
    
        if (self.pc_state.Fstatus.Z == 1):
            self.pc_state.PC += signed_char_to_int(memory.read(self.pc_state.PC+1) & 0xFF)
            cycles+=5;

        self.pc_state.PC += 2;
    
        return cycles;

class JPNC(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    # JP NC, e
    def execute(self, memory):
         if (self.pc_state.Fstatus.C == 0):
             self.pc_state.PC = memory.read16(self.pc_state.PC+1);
         else:
             self.pc_state.PC += 3;
    
         return 10;
    

class JPCnn(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    # JP C, nn
    def execute(self, memory):
         if (self.pc_state.Fstatus.C == 1):
             self.pc_state.PC = memory.read16(self.pc_state.PC+1);
         else:
             self.pc_state.PC += 3;
    
         return 10;

class JRNZe(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    # JR NZ, e
    def execute(self, memory):
        cycles = 7;
    
        if (self.pc_state.Fstatus.Z == 0):
            self.pc_state.PC += signed_char_to_int(memory.read(self.pc_state.PC+1) & 0xFF)
            cycles+=5;
    
        self.pc_state.PC += 2;
    
        return cycles;

class INC_r(Instruction_r):
    def __init__(self, pc_state, r):
        self.pc_state = pc_state
        self.r = r

    def execute(self, memory):
        self.r += 1
        self.pc_state.F = (self.pc_state.F & Instruction.FLAG_MASK_INC8) | flagtables.FlagTables.getStatusInc8(self.r.get());
        self.pc_state.PC += 1
    
        return 4;

class INC_16(Instruction):
    def __init__(self, pc_state, r, cycles, pcInc = 1):
        self.pc_state = pc_state
        self.r = r
        self.cycles = cycles
        self.pcInc = pcInc

    def execute(self, memory):
      self.r += 1
      self.pc_state.PC += self.pcInc;
  
      return self.cycles;

class DEC_16(Instruction):
    def __init__(self, pc_state, r, cycles, pcInc = 1):
        self.pc_state = pc_state
        self.r = r
        self.cycles = cycles
        self.pcInc = pcInc

    def execute(self, memory):
        self.r -= 1;
        self.pc_state.PC += self.pcInc;
    
        return self.cycles;
    

class DEC_r(Instruction_r):
    def __init__(self, pc_state, r):
        self.pc_state = pc_state
        self.r = r

    def execute(self, memory):
        self.r -= 1;
        self.pc_state.F = (self.pc_state.F & Instruction.FLAG_MASK_DEC8) | flagtables.FlagTables.getStatusDec8(self.r.get());
        self.pc_state.PC += 1
    
        return 4;
    

class INC_BC(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    def execute(self, memory):
        self.pc_state.BC += 1
        self.pc_state.PC += 1
    
        return 6;

class INC_HL(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    # INC (self.pc_state.HL)
    def execute(self, memory):
        memory.write(self.pc_state.HL, memory.read(self.pc_state.HL) + 1);
        self.pc_state.F = (self.pc_state.F & Instruction.FLAG_MASK_INC8) | flagtables.FlagTables.getStatusInc8(memory.read(self.pc_state.HL));
        self.pc_state.PC  += 1
        return 11;

class DEC_HL(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    def execute(self, memory):
        memory.write(self.pc_state.HL, memory.read(self.pc_state.HL) - 1)
        self.pc_state.F = (self.pc_state.F & Instruction.FLAG_MASK_DEC8) | flagtables.FlagTables.getStatusDec8(memory.read(self.pc_state.HL));
        self.pc_state.PC  += 1
        return 11;

class DJNZ(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    # DJNZ n
    def execute(self, memory):
        cycles = 8;
    
        self.pc_state.B -= 1;
        if (self.pc_state.B != 0):

            self.pc_state.PC += signed_char_to_int(memory.read(self.pc_state.PC + 1)) #(int) (signed char) memory.read(self.pc_state.PC + 1);
            cycles += 5
    
        self.pc_state.PC += 2
    
        return cycles
    

class RET(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    def execute(self, memory):
        self.pc_state.PCLow  = memory.read(self.pc_state.SP)
        self.pc_state.SP += 1
        self.pc_state.PCHigh = memory.read(self.pc_state.SP)
        self.pc_state.SP += 1
    
        return 10;

# Addition instructions

class ADD16(Instruction):
    def __init__(self, pc_state, dst, add, cycles, pcInc = 1):
        self.pc_state = pc_state
        self.dst = dst
        self.add = add
        self.cycles = cycles
        self.pcInc = pcInc

    def execute(self, memory):
        #static int32 r;
    
        r =  int(self.dst) + int(self.add);
    
        r = (self.dst & 0xFFF) + (self.add & 0xFFF);
        if (r & 0x1000): # Half carry
          self.pc_state.Fstatus.H = 1 # Half carry
        else:
          self.pc_state.Fstatus.H = 0 # Half carry
        self.pc_state.Fstatus.N = 0;
    
        r = (self.dst & 0xFFFF) + (self.add & 0xFFFF);
        if (r & 0x10000): # Carry
          self.pc_state.Fstatus.C = 1 # Carry
        else:
          self.pc_state.Fstatus.C = 0 # Carry
    
        self.dst += self.add;
    
        self.pc_state.PC += self.pcInc;
    
        return self.cycles;

class ADD_r(Instruction):
    def __init__(self, pc_state, src):
        self.pc_state = pc_state
        self.src = src

    def execute(self, memory):
	    self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusAdd(self.pc_state.A,self.src);
	    self.pc_state.A = self.pc_state.A + int(self.src);
	    self.pc_state.PC += 1
	    return 4;

class SUB_r(Instruction):
    def __init__(self, pc_state, src):
        self.pc_state = pc_state
        self.src = src

    def execute(self, memory):
	    self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusSub(self.pc_state.A,self.src);
	    self.pc_state.A = self.pc_state.A - int(self.src);
	    self.pc_state.PC += 1
	    return 4;

class BIT_r(Instruction):
    def __init__(self, pc_state, src):
        self.pc_state = pc_state
        self.src = src

    def execute(self, memory):
        tmp8 = memory.read(self.pc_state.PC+1)

        self.pc_state.Fstatus.Z = (int(self.src) >> ((tmp8 >> 3) & 7)) ^ 0x1;
        self.pc_state.Fstatus.PV = flagtables.FlagTables.calculateParity(int(self.src));
        self.pc_state.Fstatus.H = 1;
        self.pc_state.Fstatus.N = 0;
        self.pc_state.Fstatus.S = 0;
        self.pc_state.PC += 2;
        return 8;

# self.pc_state.Bit b, (self.pc_state.HL) 
class BIT_HL(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    def execute(self, memory):
        tmp8 = memory.read(self.pc_state.PC+1)
        self.pc_state.Fstatus.Z = (memory.read(self.pc_state.HL) >> 
                            ((tmp8 >> 3) & 7)) ^ 0x1;
        self.pc_state.Fstatus.H = 1;
        self.pc_state.Fstatus.N = 0;
        self.pc_state.Fstatus.S = 0;
        self.pc_state.PC += 2;

        return 12;

# RES b, r
class RES_b_r(Instruction):
    def __init__(self, pc_state, dst):
        self.pc_state = pc_state
        self.dst = dst

    def execute(self, memory):
        tmp8 = memory.read(self.pc_state.PC+1)
        self.dst.set(int(self.dst) & ~(0x1 << ((tmp8 >> 3) & 7)));
        self.pc_state.PC += 2;
        return 8;

# RES b, HL
class RES_b_HL(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    def execute(self, memory):
        tmp8 = memory.read(self.pc_state.PC+1)
        memory.write(self.pc_state.HL, memory.read(self.pc_state.HL) & ~(0x1 << ((tmp8 >> 3) & 7)));
        self.pc_state.PC += 2;
        return 12;

# SET b, r
class SET_b_r(Instruction):
    def __init__(self, pc_state, dst):
        self.pc_state = pc_state
        self.dst = dst

    def execute(self, memory):
        tmp8 = memory.read(self.pc_state.PC+1)
        self.dst.set(int(self.dst) | (0x1 << ((tmp8 >> 3) & 7)));
        self.pc_state.PC += 2;
        return 8;

# SET b, HL
class SET_b_HL(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    def execute(self, memory):
        tmp8 = memory.read(self.pc_state.PC+1)
        memory.write(self.pc_state.HL, memory.read(self.pc_state.HL) | (0x1 << ((tmp8 >> 3) & 7)));
        self.pc_state.PC += 2;
        return 12;


class RLCA(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    def execute(self, memory):
        self.pc_state.A = (self.pc_state.A << 1) | ((self.pc_state.A >> 7) & 0x1);
        self.pc_state.Fstatus.C = self.pc_state.A & 0x1;
        self.pc_state.Fstatus.N = 0;
        self.pc_state.Fstatus.H = 0;
        self.pc_state.PC += 1
        return 4;

# RLC r
class RLC_r(Instruction):
    def __init__(self, pc_state, dst):
        self.pc_state = pc_state
        self.dst = dst

    def execute(self, memory):
        self.dst.set((int(self.dst) << 1) | ((int(self.dst) >> 7) & 0x1));
        self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusOr(int(self.dst));
        self.pc_state.Fstatus.C = int(self.dst) & 0x1; # bit-7 of src = bit-0
        self.pc_state.PC+=2;
        return 8;

# RLC (HL)
class RLC_HL(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    def execute(self, memory):
        tmp8 = memory.read(self.pc_state.HL);
        memory.write(self.pc_state.HL, (tmp8 << 1) | ((tmp8 >> 7) & 0x1));
        self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusOr(memory.read(self.pc_state.HL));
        self.pc_state.Fstatus.C = (tmp8 >> 7) & 0x1; # bit-7 of src
        self.pc_state.PC+=2;
        return 15;

# RRC r
class RRC_r(Instruction):
    def __init__(self, pc_state, dst):
        self.pc_state = pc_state
        self.dst = dst

    def execute(self, memory):
        self.dst.set((int(self.dst) >> 1) | ((int(self.dst) & 0x1) << 7));
        self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusOr(self.dst);
        self.pc_state.Fstatus.C = (self.dst >> 7) & 0x1; # bit-0 of src
        self.pc_state.PC+=2;
        return 8

# RRC (HL)
class RRC_HL(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    def execute(self, memory):
        tmp8 = memory.read(self.pc_state.HL);
        memory.write(self.pc_state.HL,(tmp8 >> 1) | ((tmp8 & 0x1) << 7));
        self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusOr(memory.read(self.pc_state.HL));
        self.pc_state.Fstatus.C = tmp8 & 0x1; # bit-0 of src
        self.pc_state.PC+=2;
        return 8;

# RL r
class RL_r(Instruction):
    def __init__(self, pc_state, dst):
        self.pc_state = pc_state
        self.dst = dst

    def execute(self, memory):
        tmp8 = int(self.dst);
        self.dst.set((int(self.dst) << 1) | (self.pc_state.Fstatus.C));
        self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusOr(int(self.dst));
        self.pc_state.Fstatus.C = (tmp8 >> 7) & 0x1;
        self.pc_state.PC+=2;
        return 8

# RR r
class RR_r(Instruction):
    def __init__(self, pc_state, dst):
        self.pc_state = pc_state
        self.dst = dst

    def execute(self, memory):
        tmp8 = int(self.dst);
        self.dst.set((int(self.dst) >> 1) | (self.pc_state.Fstatus.C << 7));
        self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusOr(int(self.dst));
        self.pc_state.Fstatus.C = tmp8 & 0x1;
        self.pc_state.PC+=2;
        return 8;

# SLA r
class SLA_r(Instruction):
    def __init__(self, pc_state, dst):
        self.pc_state = pc_state
        self.dst = dst

    def execute(self, memory):
        tmp8 = (int(self.dst) >> 7) & 0x1;
        self.dst.set(int(self.dst) << 1)
        self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusOr(int(self.dst))
        self.pc_state.Fstatus.C = tmp8;

        self.pc_state.PC += 2;
        return 8

# SLA (HL)
class SLA_HL(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    def execute(self, memory):
        tmp8 = (memory.read(self.pc_state.HL) >> 7) & 0x1;
        memory.write(self.pc_state.HL, memory.read(self.pc_state.HL) << 1);
        self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusOr(memory.read(self.pc_state.HL));
        self.pc_state.Fstatus.C = tmp8;

        self.pc_state.PC += 2;
        return 15

# SRA r
class SRA_r(Instruction):
    def __init__(self, pc_state, dst):
        self.pc_state = pc_state
        self.dst = dst

    def execute(self, memory):
        tmp8 = int(self.dst);
        self.dst.set((int(self.dst) & 0x80) | ((self.dst >> 1) & 0x7F));

        self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusOr(self.dst);
        self.pc_state.Fstatus.C = tmp8 & 0x1;

        self.pc_state.PC += 2;
        return 8

# SRA (HL)
class SRA_HL(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    def execute(self, memory):
        tmp8 = memory.read(self.pc_state.HL);
        memory.write(self.pc_state.HL, (tmp8 & 0x80) | ((tmp8 >> 1) & 0x7F));

        self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusOr(memory.read(self.pc_state.HL));
        self.pc_state.Fstatus.C = tmp8 & 0x1;

        self.pc_state.PC += 2;
        self.clocks.cycles += 15;

# SLL r
class SLL_r(Instruction):
    def __init__(self, pc_state, dst):
        self.pc_state = pc_state
        self.dst = dst

    def execute(self, memory):
        tmp8 = (int(self.dst) >> 7) & 0x1;
        self.dst.set(int(self.dst) << 1 | 0x1);
        self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusOr(int(self.dst));
        self.pc_state.Fstatus.C = tmp8;

        self.pc_state.PC += 2;
        return 8

# SLL (HL)
class SLL_HL(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    def execute(self, memory):
        tmp8 = (memory.read(self.pc_state.HL) >> 7) & 0x1;
        memory.write(self.pc_state.HL, memory.read(self.pc_state.HL) << 1 | 0x1);
        self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusOr(memory.read(self.pc_state.HL));
        self.pc_state.Fstatus.C = tmp8;

        self.pc_state.PC += 2;
        return 15

# SRL r
class SRL_r(Instruction):
    def __init__(self, pc_state, dst):
        self.pc_state = pc_state
        self.dst = dst

    def execute(self, memory):
        tmp8 = int(self.dst);
        self.dst.set((int(self.dst) >> 1) & 0x7F);

        self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusOr(int(self.dst));
        self.pc_state.Fstatus.C = tmp8 & 0x1;

        self.pc_state.PC += 2;
        return 8;

# SRL (HL)
class SRL_HL(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    def execute(self, memory):
        tmp8 = memory.read(self.pc_state.HL);
        memory.write(self.pc_state.HL, (tmp8 >> 1) & 0x7F);

        self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusOr(memory.read(self.pc_state.HL));
        self.pc_state.Fstatus.C = tmp8 & 0x1;

        self.pc_state.PC += 2;
        return 15;

class InstructionExec(object):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    
class Load16BC(Instruction):

    def __init__(self, pc_state, r16):
        self.pc_state = pc_state
        self.r16 = r16

    def execute(self, memory):
      # Load 16-bit cpu_state->BC register
      # LD cpu_state->BC, 0x
    
      self.r16.set(memory.read16(self.pc_state.PC+1))
      self.pc_state.PC += 3;

      return 10;

# Load a 16-bit register with the value 'nn'
class LD_16_nn(Instruction):
    def __init__(self, pc_state, r16):
        self.pc_state = pc_state
        self.r16 = r16

    def execute(self, memory):
      self.r16.set(memory.read16(self.pc_state.PC+1)); 
      self.pc_state.PC += 3;
      return 10;

class LD_r_r(Instruction):
    def __init__(self, pc_state, dst, src):
        self.pc_state = pc_state
        self.dst = dst
        self.src = src

    # Load any register to any other register.
    def execute(self, memory):
      self.dst.set(self.src);
      self.pc_state.PC += 1;

      return 4;

# LD (16 REG), n
# Load the value 'n' into the 16-bit address
class LD_mem_n(Instruction):
    def __init__(self, pc_state, addr):
        self.pc_state = pc_state
        self.addr = addr

    # Load the 8 bit value 'n' into memory.
    def execute(self, memory):
      memory.write(self.addr, memory.read(self.pc_state.PC +1));
      self.pc_state.PC += 2;

      return 10;

# LD (self.pc_state.IY+d), r
class LD_IY_d_r(Instruction):
    def __init__(self, pc_state, src):
        self.pc_state = pc_state
        self.src = src

    def execute(self, memory):
        memory.write(self.pc_state.IY + signed_char_to_int(memory.read(self.pc_state.PC+2)), self.src); 
        self.pc_state.PC += 3;
        return 19

# LD (16 REG), r
# The register r into the 16-bit address
class LD_mem_r(Instruction_r):
    # r - 8-bit
    def __init__(self, pc_state, addr, r):
      self.pc_state = pc_state
      self.addr = addr
      self.r = r

    # Load the register into memory.
    def execute(self, memory):
      memory.write(self.addr, self.r);
      self.pc_state.PC += 1;

      return 7;

# LD r, (16 REG)
# Load the value from the 16-bit address into the register
class LD_r_mem (Instruction):
    # r - 8-bit
    def __init__(self, pc_state, r, addr):
      self.pc_state = pc_state
      self.addr = addr
      self.r = r

    # Load the value at the address into a register.
    def execute(self, memory):
      self.r.set(memory.read(self.addr));
      self.pc_state.PC += 1;
      return 7;

# LD r, (nn)
# Load the value from the 16-bit address into the 16-bit register
class LD_r16_mem(Instruction):
    # r - 16-bit
    def __init__(self, pc_state, r):
      self.pc_state = pc_state
      self.r = r

    # Load the value at the address into a register.
    def execute(self, memory):
      self.r.set(memory.read16(memory.read16(self.pc_state.PC+1)));
      self.pc_state.PC += 3;

      return 20;

# LD r, (nn)
# Load the value from the 16-bit address into the 8-bit register
class LD_r8_mem(Instruction):
    # r - 8-bit
    def __init__(self, pc_state, r):
      self.pc_state = pc_state
      self.r = r

    # Load the value at the address into a register.
    def execute(self, memory):
      self.r.set(memory.read(memory.read16(self.pc_state.PC+1)));
      self.pc_state.PC += 3;

      return 13;

class LD_r(Instruction_r):
    # r - 8-bit
    def __init__(self, pc_state, r):
      self.pc_state = pc_state
      self.r = r

    def execute(self, memory):
      # This can be optimised.
      self.r.set(memory.read(self.pc_state.PC + 1));
      self.pc_state.PC += 2;
      return 7;

# LD self.I_reg, nn
class LD_I_nn(Instruction):
    def __init__(self, pc_state, I_reg):
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self, memory):
        self.I_reg.set(memory.read16(self.pc_state.PC+2))
        self.pc_state.PC += 4
        return 20
    
# LD (nn), self.I_reg
class LD_nn_I(Instruction):
    def __init__(self, pc_state, I_reg):
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self, memory):
        memory.write(memory.read16(self.pc_state.PC+2), self.I_reg.get_low())
        memory.write(memory.read16(self.pc_state.PC+2)+1, self.I_reg.get_high())
        self.pc_state.PC += 4
    
        return 20
    
# LD self.I_reg, (nn)
class LD_I__nn_(Instruction):
    def __init__(self, pc_state, I_reg):
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self, memory):
        self.I_reg.set(memory.read16(memory.read16(self.pc_state.PC+2)))
        self.pc_state.PC += 4
    
        return 20
    
# INC (self.I_reg+d)
class INC_I_d(Instruction):
    def __init__(self, pc_state, I_reg):
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self, memory):
        tmp16 = self.I_reg.get() + signed_char_to_int(memory.read(self.pc_state.PC+2))
        memory.write(tmp16, memory.read(tmp16) + 1)
        self.pc_state.F = (self.pc_state.F & Instruction.FLAG_MASK_INC8) | flagtables.FlagTables.getStatusInc8(memory.read(tmp16))
        self.pc_state.PC+=3
        return 23
    
# self.pc_state.DEC (self.I_reg+d)
class DEC_I_d(Instruction):
    def __init__(self, pc_state, I_reg):
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self, memory):
        tmp16 = self.I_reg.get() + signed_char_to_int(memory.read(self.pc_state.PC+2))
        memory.write(tmp16, memory.read(tmp16) - 1)
        self.pc_state.F = (self.pc_state.F & Instruction.FLAG_MASK_DEC8) | flagtables.FlagTables.getStatusDec8(memory.read(tmp16))
        self.pc_state.PC+=3
        return 23
    
# LD (self.I_reg + d), n
class LD_I_d_n(Instruction):
    def __init__(self, pc_state, I_reg):
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self, memory):
        tmp16 = self.I_reg.get() + signed_char_to_int(memory.read(self.pc_state.PC+2))
        memory.write(tmp16, memory.read(self.pc_state.PC+3))
        self.pc_state.PC += 4
        return  19
    
# LD r, (self.I_reg+e)
class LD_r_I_e(Instruction):
    def __init__(self, pc_state, I_reg, dst):
        self.pc_state = pc_state
        self.I_reg = I_reg
        self.dst = dst

    def execute(self, memory):
        self.dst.set(memory.read(self.I_reg.get() + signed_char_to_int(memory.read(self.pc_state.PC+2))))
                                        
        self.pc_state.PC = self.pc_state.PC + 3
        return  19
    
# LD (self.I_reg+d), r
class LD_I_d_r(Instruction):
    def __init__(self, pc_state, I_reg, src):
        self.pc_state = pc_state
        self.I_reg = I_reg
        self.src = src

    def execute(self, memory):
                          
        memory.write(self.I_reg.get() + signed_char_to_int(memory.read(self.pc_state.PC+2)),
                      self.src) 
        self.pc_state.PC += 3
        return  19
    
# self.pc_state.ADD self.pc_state.A,(self.I_reg+d)
class ADDA_I_d(Instruction):
    def __init__(self, pc_state, I_reg):
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self, memory):
        tmp8 = memory.read(self.I_reg.get() + 
                         signed_char_to_int(memory.read(self.pc_state.PC+2)))
        self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusAdd(self.pc_state.A,tmp8)
        self.pc_state.A = self.pc_state.A + tmp8
        self.pc_state.PC += 3
        return  19
    
# self.pc_state.ADC (self.I_reg + d)
class ADC_I_d(Instruction):
    def __init__(self, pc_state, I_reg):
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self, memory):
        self.pc_state.A = add8c(self.pc_state, self.pc_state.A, memory.read(self.I_reg.get() + signed_char_to_int(memory.read(self.pc_state.PC+2))), self.pc_state.Fstatus.C)
        self.pc_state.PC+=3
        return 19
    
# SUB (self.I_reg + d)
class SUB_I_d(Instruction):
    def __init__(self, pc_state, I_reg):
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self, memory):
        tmp8 = memory.read(self.I_reg.get() + 
                         signed_char_to_int(memory.read(self.pc_state.PC+2)))
        self.pc_state.F = flagtables.FlagTables.getStatusSub(self.pc_state.A,tmp8)
        self.pc_state.A = self.pc_state.A - tmp8
        self.pc_state.PC += 3
        return  19
    
# self.pc_state.AND (self.I_reg + d)
class AND_I_d(Instruction):
    def __init__(self, pc_state, I_reg):
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self, memory):
        self.pc_state.A = self.pc_state.A & memory.read(self.I_reg.get() +
                         signed_char_to_int(memory.read(self.pc_state.PC+2)))
        self.pc_state.PC+=3
        self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusAnd(self.pc_state.A)
    
        return 19
    
# XOR (self.I_reg + d)
class XOR_I_d(Instruction):
    def __init__(self, pc_state, I_reg):
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self, memory):
        self.pc_state.A = self.pc_state.A ^ memory.read(self.I_reg.get() +
                         signed_char_to_int(memory.read(self.pc_state.PC+2)))
        self.pc_state.PC+=3
        self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusOr(self.pc_state.A)
    
        return  19
    
# OR (self.I_reg + d)
class OR_I_d(Instruction):
    def __init__(self, pc_state, I_reg):
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self, memory):
        tmp8 = memory.read(self.I_reg.get() + 
                         signed_char_to_int(memory.read(self.pc_state.PC+2)))
        self.pc_state.A = self.pc_state.A | tmp8
        self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusOr(self.pc_state.A)
        self.pc_state.PC += 3
        return  19
    
# CP (self.I_reg + d)
class CP_I_d(Instruction):
    def __init__(self, pc_state, I_reg):
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self, memory):
        tmp8 = memory.read(self.I_reg.get() + 
                         signed_char_to_int(memory.read(self.pc_state.PC+2)))
        self.pc_state.F = flagtables.FlagTables.getStatusSub(self.pc_state.A,tmp8)
        self.pc_state.PC+=3
        return 19
    
# Probably should turn this into a lookup table
class BIT_I_d(Instruction):
    def __init__(self, pc_state, I_reg):
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self, memory):
        tmp16 = self.I_reg.get() + signed_char_to_int(memory.read(self.pc_state.PC+2))
        tmp8 = memory.read(tmp16)
        t8 = memory.read(self.pc_state.PC+3)
    
        if ((t8 & 0xC7) == 0x46): # self.pc_state.BIT b, (self.I_reg.get() + d)
            tmp8 = (tmp8 >> ((t8 & 0x38) >> 3)) & 0x1
            self.pc_state.Fstatus.Z = tmp8 ^ 0x1
            self.pc_state.Fstatus.PV = flagtables.FlagTables.calculateParity(tmp8)
            self.pc_state.Fstatus.H = 1
            self.pc_state.Fstatus.N = 0
            self.pc_state.Fstatus.S = 0
        elif ((t8 & 0xC7) == 0x86): # RES b, (self.I_reg + d)
            tmp8 = tmp8 & ~(0x1 << ((t8 >> 3) & 0x7))
            memory.write(tmp16,tmp8)
        elif ((t8 & 0xC7) == 0xC6): # SET b, (self.I_reg + d)
            tmp8 = tmp8 | (0x1 << ((t8 >> 3) & 0x7))
            memory.write(tmp16,tmp8)
        else:
            error("Instruction arg for 0xFD 0xCB")
    
        self.pc_state.PC += 4
    
        return  23
    
# POP self.I_reg
class POP_I(Instruction):
    def __init__(self, pc_state, I_reg):
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self, memory):
        self.I_reg.set_low(memory.read(self.pc_state.SP))
        self.pc_state.SP += 1
        self.I_reg.set_high(memory.read(self.pc_state.SP))
        self.pc_state.SP += 1
        self.pc_state.PC += 2
        return  14
    
# EX (self.pc_state.SP), self.I_reg
class EX_SP_I(Instruction):
    def __init__(self, pc_state, I_reg):
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self, memory):
        tmp8 = memory.read(self.pc_state.SP)
        memory.write(self.pc_state.SP, self.I_reg.get_low())
        self.I_reg.set_low(tmp8)
        tmp8 = memory.read(self.pc_state.SP+1)
        memory.write(self.pc_state.SP+1, self.I_reg.get_high())
        self.I_reg.set_high(tmp8)
        self.pc_state.PC+=2
        return  23
    
# PUSH self.I_reg
class PUSH_I(Instruction):
    def __init__(self, pc_state, I_reg):
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self, memory):
        self.pc_state.SP -= 1
        memory.write(self.pc_state.SP, self.I_reg.get_high())
        self.pc_state.SP -= 1
        memory.write(self.pc_state.SP, self.I_reg.get_low())
        self.pc_state.PC += 2
    
        return 15
    
# Don't know how many self.clocks.cycles
# LD self.pc_state.PC, self.I_reg
class LD_PC_I(Instruction):
    def __init__(self, pc_state, I_reg):
        self.pc_state = pc_state
        self.I_reg = I_reg

    def execute(self, memory):
        self.pc_state.PC = self.I_reg.get()
        return 6
    
