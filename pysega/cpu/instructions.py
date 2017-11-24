import ctypes
import flagtables
import addressing

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
#        self.clocks.system_clock += 10
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
    def __init__(self, pc_state):
        self.pc_state = pc_state

    def NOP_exec(self, data):
        """NOP"""
        self.pc_state.PC = self.pc_state.PC + 1
        self.clocks.system_clock += 4

class OUT_n_A(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

# OUT (n), self.pc_state.A
# Write register A, to port n
    def OUT_n_A_exec(memory):
# Need to sort out port write.
     # TODO
     print("TODO")
     print("Ports::instance()->portWrite(self.memory.read(self.pc_state.PC + 1), self.pc_state.A);")

     self.pc_state.PC+=2;

     return 11;


class RRCA(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    def RRCA_exec(memory):
        self.pc_state.Fstatus.status.C = self.pc_state.A & 0x1;
        self.pc_state.Fstatus.status.HLHigh = 0;
        self.pc_state.Fstatus.status.N = 0;
        self.pc_state.A = (self.pc_state.A >> 1) | ((self.pc_state.A & 0x1) << 7);
        self.pc_state.PC += 1

        return 4;


class AND_r(Instruction):
    def __init__(self, pc_state, src):
        self.pc_state = pc_state
        self.src = src

    def AND_r_exec(memory):
        self.pc_state.A = self.pc_state.A & src;
        self.pc_state.PC += 1
    
        self.pc_state.F = flagtables.FlagTables.getStatusAnd(self.pc_state.A);
    
        return 4;

class AND_n(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    def AND_n_exec(memory):
    
        self.pc_state.A = self.pc_state.A & self.memory.read(self.pc_state.PC +1);
        self.pc_state.PC += 2;
        self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusAnd(self.pc_state.A);
    
        return 7;

class OR_r(Instruction):
    def __init__(self, pc_state, src):
        self.pc_state = pc_state
        self.src = src

    def OR_r_exec(memory):
        self.pc_state.A = self.pc_state.A | src;
        self.pc_state.PC += 1
    
        self.pc_state.F = flagtables.FlagTables.getStatusOr(self.pc_state.A);
    
        return 4;

class XOR_r(Instruction):
    def __init__(self, pc_state, src):
        self.pc_state = pc_state
        self.src = src

    def XOR_r_exec(memory):
        self.pc_state.A = self.pc_state.A ^ src;
        self.pc_state.PC += 1
    
        self.pc_state.F = flagtables.FlagTables.getStatusOr(self.pc_state.A);
    
        return 4;

class EXX(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    def EXX_exec(memory):
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

    def CP_n_exec(memory):
    
        self.pc_state.F = flagtables.FlagTables.getStatusSub(self.pc_state.A, self.memory.read(self.pc_state.PC +1));
        self.pc_state.PC += 2;
    
        return 7;

class CP_r(Instruction_r):
    def __init__(self, pc_state, r):
        self.pc_state = pc_state
        self.r = r

    def CP_r_exec(memory):
        self.pc_state.F = flagtables.FlagTables.getStatusSub(self.pc_state.A,r);
        self.pc_state.PC += 1
    
        return 4;

class JRZe(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    # JR Z, e
    def JRZe_exec(memory):
        cycles = 7
    
        if (self.pc_state.Fstatus.status.Z == 1):
            atPC = self.memory.readMulti(self.pc_state.PC);
            self.pc_state.PC += atPC[1] & 0xFF #(int) (signed char) atPC[1]; 
            cycles+=5;

        self.pc_state.PC += 2;
    
        return cycles;

class JPNC(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    # JP NC, e
    def JPNC_exec(memory):
         if (self.pc_state.Fstatus.status.C == 0):
             self.pc_state.PC = self.memory.read16(self.pc_state.PC+1);
         else:
             self.pc_state.PC += 3;
    
         return 10;
    

class JPCnn(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    # JP C, nn
    def JPCnn_exec(memory):
         if (self.pc_state.Fstatus.status.C == 1):
             self.pc_state.PC = self.memory.read16(self.pc_state.PC+1);
         else:
             self.pc_state.PC += 3;
    
         return 10;

class JRNZe(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    # JR NZ, e
    def JRNZe_execmemory():
        cycles = 7;
    
        if (self.pc_state.Fstatus.status.Z == 0):
            atPC = self.memory.readMulti(self.pc_state.PC);
            self.pc_state.PC += atPC[1] & 0xFF # (int) (signed char) atPC[1]; 
            cycles+=5;
    
        self.pc_state.PC += 2;
    
        return cycles;

class INC_r(Instruction_r):
    def __init__(self, pc_state, r):
        self.pc_state = pc_state
        self.r = r

    def INC_r_exec(memory):
        r += 1
        self.pc_state.F = (self.pc_state.F & FLAG_MASK_INC8) | flagtables.FlagTables.getStatusInc8(r);
        self.pc_state.PC += 1
    
        return 4;

class INC_16(Instruction):
    def __init__(self, pc_state, r, cycles, pcInc = 1):
        self.pc_state = pc_state
        self.r = r
        self.cycles = cycles
        self.pcInc = pcInc

    def INC_16_exec(memory):
      r += 1
      self.pc_state.PC += pcInc;
  
      return cycles;

class DEC_16(Instruction):
    def __init__(self, pc_state, r, cycles, pcInc = 1):
        self.pc_state = pc_state
        self.r = r
        self.cycles = cycles
        self.pcInc = pcInc

    def DEC_16_exec(memory):
        r -= 1;
        self.pc_state.PC += pcInc;
    
        return cycles;
    

class DEC_r(Instruction_r):
    def __init__(self, pc_state, r):
        self.pc_state = pc_state
        self.r = r

    def DEC_r_exec(memory):
        r -= 1;
        self.pc_state.F = (self.pc_state.F & FLAG_MASK_DEC8) | flagtables.FlagTables.getStatusDec8(r);
        self.pc_state.PC += 1
    
        return 4;
    

class INC_BC(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    def INC_BC_exec(memory):
        self.pc_state.BC += 1
        self.pc_state.PC += 1
    
        return 6;

class INC_HL(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    # INC (self.pc_state.HL)
    def INC_HL_exec(memory):
        self.memory.write(self.pc_state.HL, self.memory.read(self.pc_state.HL) + 1);
        self.pc_state.F = (self.pc_state.F & FLAG_MASK_INC8) | flagtables.FlagTables.getStatusInc8(self.memory.read(self.pc_state.HL));
        self.pc_state.PC  += 1
        return 11;

class DEC_HL(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    def DEC_HL_exec(memory):
        self.memory.write(self.pc_state.HL, self.memory.read(self.pc_state.HL) - 1)
        self.pc_state.F = (self.pc_state.F & FLAG_MASK_DEC8) | flagtables.FlagTables.getStatusDec8(self.memory.read(self.pc_state.HL));
        self.pc_state.PC  += 1
        return 11;

class DJNZ(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    # DJNZ n
    def DJNZ_exec(memory):
        cycles = 8;
    
        self.pc_state.B -= 1;
        if (self.pc_state.B != 0):
            self.pc_state.PC += self.memory.read(self.pc_state.PC + 1) #(int) (signed char) self.memory.read(self.pc_state.PC + 1);
            cycles += 5
    
        self.pc_state.PC += 2
    
        return cycles
    

class RET(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    def RET_exec(memory):
        self.pc_state.PCLow  = self.memory.read(self.pc_state.SP)
        self.pc_state.SP += 1
        self.pc_state.PCHigh = self.memory.read(self.pc_state.SP)
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
        self.r = r
        self.cycles = cycles
        self.pcInc = pcInc

    def ADD16_exec(memory):
        #static int32 r;
    
        r =  dst + add;
    
        r = (dst & 0xFFF) + (add & 0xFFF);
        if (r & 0x1000): # Half carry
          self.pc_state.Fstatus.status.HLHigh = 1 # Half carry
        else:
          self.pc_state.Fstatus.status.HLHigh = 0 # Half carry
        self.pc_state.Fstatus.status.N = 0;
    
        r = (dst & 0xFFFF) + (add & 0xFFFF);
        if (r & 0x10000): # Carry
          self.pc_state.Fstatus.status.C = 1 # Carry
        else:
          self.pc_state.Fstatus.status.C = 0 # Carry
    
        dst += add;
    
        self.pc_state.PC += pcInc;
    
        return cycles;

class ADD_r(Instruction):
    def __init__(self, pc_state, src):
        self.pc_state = pc_state
        self.src = src

    def ADD_r_exec(memory):
	    self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusAdd(self.pc_state.A,src);
	    self.pc_state.A = self.pc_state.A + src;
	    self.pc_state.PC += 1
	    return 4;

class RLCA(Instruction):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    def RLCA_exec(memory):
        self.pc_state.A = (self.pc_state.A << 1) | ((self.pc_state.A >> 7) & 0x1);
        self.pc_state.Fstatus.status.C = self.pc_state.A & 0x1;
        self.pc_state.Fstatus.status.N = 0;
        self.pc_state.Fstatus.status.HLHigh = 0;
        self.pc_state.PC += 1
        return 4;

class InstructionExec(object):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    
class Load16BC(Instruction):

    def Load16BC_exec(memory):
      # Load 16-bit cpu_state->BC register
      # LD cpu_state->BC, 0x
    
      self.pc_state.BC = self.memory.read16(self.pc_state.PC+1); 
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
    def LD_r_r_exec(memory):
      dst = src;
      self.pc_state.PC += 1;

      return 4;

# LD (16 REG), n
# Load the value 'n' into the 16-bit address
class LD_mem_n(Instruction):
    def __init__(self, pc_state, addr):
        sels.pc_state = pc_state
        sels.addr = addr

    # Load the 8 bit value 'n' into memory.
    def LD_mem_n_exec(memory):
      self.memory.write(addr, self.memory.read(self.pc_state.PC +1));
      self.pc_state.PC += 2;

      return 10;

# LD (16 REG), r
# The register r into the 16-bit address
class LD_mem_r(Instruction_r):
    # r - 8-bit
    def __init__(self, pc_state, addr, r):
      self.pc_state = pc_state
      self.addr = addr
      self.r = r

    # Load the register into memory.
    def LD_mem_r_exec(memory):
      self.memory.write(addr, r);
      self.pc_state.PC += 1;

      return 7;

# LD r, (16 REG)
# Load the value from the 16-bit address into the register
class LD_r_mem (Instruction):
    # r - 8-bit
    def __init__(self, pc_state, addr, r):
      self.pc_state = pc_state
      self.addr = addr
      self.r = r

    # Load the value at the address into a register.
    def LD_r_mem_exec(memory):
      r = self.memory.read(addr);
      self.pc_state.PC += 1;
      return 7;

# LD r, (nn)
# Load the value from the 16-bit address into the 16-bit register
class LD_r16_mem(Instruction):
    # r - 16-bit
    def __init__(self, pc_state, addr, r):
      self.pc_state = pc_state
      self.r = r

    # Load the value at the address into a register.
    def LD_r16_mem_exec(memory):
      r = self.memory.read16(self.memory.read16(self.pc_state.PC+1));
      self.pc_state.PC += 3;

      return 20;

# LD r, (nn)
# Load the value from the 16-bit address into the 8-bit register
class LD_r8_mem(Instruction):
    # r - 8-bit
    def __init__(self, pc_state, addr, r):
      self.pc_state = pc_state
      self.r = r

    # Load the value at the address into a register.
    def LD_r8_mem_exec(memory):
      r = self.memory.read(self.memory.read16(self.pc_state.PC+1));
      self.pc_state.PC += 3;

      return 13;

class LD_r(Instruction_r):
    # r - 8-bit
    def __init__(self, pc_state, addr, r):
      self.pc_state = pc_state
      self.r = r

    def LD_r_exec(memory):
      # This can be optimised.
      r = self.memory.read(self.pc_state.PC + 1);
      self.pc_state.PC += 2;
      return 7;
