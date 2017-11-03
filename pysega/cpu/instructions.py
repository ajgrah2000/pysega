import ctypes
import flagtables

class Instruction(object):

    def __init__(self, clocks, pc_state, instruction_exec):
        self.clocks = clocks
        self.pc_state = pc_state
        self.instruction_exec = instruction_exec

    def execute(self):
        pass

    def _exec(self, data):
        return self.instruction_exec(data)

class JumpInstruction(Instruction):
     
    def __init__(self, clocks, pc_state, memory):
        super(JumpInstruction, self).__init__(clocks, pc_state, None)
        self.memory = memory

    def execute(self):
        self.pc_state.PC = self.memory.read16(self.pc_state.PC + 1)
        self.clocks.system_clock += 10

class InstructionExec(object):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    def NOP_exec(self, data):
        """NOP"""
        self.pc_state.PC = self.pc_state.PC + 1
        self.clocks.system_clock += 4
#        return int(data)

    def RRCA_exec():
        self.pc_state.Fstatus.status.C = self.pc_state.A & 0x1;
        self.pc_state.Fstatus.status.HLHigh = 0;
        self.pc_state.Fstatus.status.N = 0;
        self.pc_state.A = (self.pc_state.A >> 1) | ((self.pc_state.A & 0x1) << 7);
        self.pc_state.PC += 1

        return 4;

    def INC_BC_exec():
        self.pc_state.BC += 1
        self.pc_state.PC += 1
    
        return 6;
    
# OUT (n), self.pc_state.A
# Write register A, to port n
    def OUT_n_A_exec():
# Need to sort out port write.
     # TODO
     print("TODO")
     print("Ports::instance()->portWrite(self.memory.read(self.pc_state.PC + 1), self.pc_state.A);")

     self.pc_state.PC+=2;

     return 11;

  # DJNZ n
    def DJNZ_exec():
        cycles = 8;
    
        self.pc_state.B -= 1;
        if (self.pc_state.B != 0):
            self.pc_state.PC += self.memory.read(self.pc_state.PC + 1) #(int) (signed char) self.memory.read(self.pc_state.PC + 1);
            cycles += 5
    
        self.pc_state.PC += 2
    
        return cycles
    
  # JR Z, e
    def JRZe_exec():
        cycles = 7
    
        if (self.pc_state.Fstatus.status.Z == 1):
            atPC = self.memory.readMulti(self.pc_state.PC);
            self.pc_state.PC += atPC[1] & 0xFF #(int) (signed char) atPC[1]; 
            cycles+=5;

        self.pc_state.PC += 2;
    
        return cycles;
    
  # JR NZ, e
    def JRNZe_exec():
        cycles = 7;
    
        if (self.pc_state.Fstatus.status.Z == 0):
            atPC = self.memory.readMulti(self.pc_state.PC);
            self.pc_state.PC += atPC[1] & 0xFF # (int) (signed char) atPC[1]; 
            cycles+=5;
    
        self.pc_state.PC += 2;
    
        return cycles;
      # JP NC, e
    def JPNC_exec():
         if (self.pc_state.Fstatus.status.C == 0):
             self.pc_state.PC = self.memory.read16(self.pc_state.PC+1);
         else:
             self.pc_state.PC += 3;
    
         return 10;
    
  # JP C, nn
    def JPCnn_exec():
         if (self.pc_state.Fstatus.status.C == 1):
             self.pc_state.PC = self.memory.read16(self.pc_state.PC+1);
         else:
             self.pc_state.PC += 3;
    
         return 10;
    
    def INC_16_exec():
      r += 1
      self.pc_state.PC += pcInc;
  
      return cycles;

    def DEC_16_exec():
        r -= 1;
        self.pc_state.PC += pcInc;
    
        return cycles;
    
    def INC_r_exec():
        r += 1
        self.pc_state.F = (self.pc_state.F & FLAG_MASK_INC8) | flagtables.FlagTables.getStatusInc8(r);
        self.pc_state.PC += 1
    
        return 4;
    
    def DEC_r_exec():
        r -= 1;
        self.pc_state.F = (self.pc_state.F & FLAG_MASK_DEC8) | flagtables.FlagTables.getStatusDec8(r);
        self.pc_state.PC += 1
    
        return 4;
    

            # INC (self.pc_state.HL)
    def INC_HL_exec():
        self.memory.write(self.pc_state.HL, self.memory.read(self.pc_state.HL) + 1);
        self.pc_state.F = (self.pc_state.F & FLAG_MASK_INC8) | flagtables.FlagTables.getStatusInc8(self.memory.read(self.pc_state.HL));
        self.pc_state.PC  += 1
        return 11;
    
    def DEC_HL_exec():
        self.memory.write(self.pc_state.HL, self.memory.read(self.pc_state.HL) - 1)
        self.pc_state.F = (self.pc_state.F & FLAG_MASK_DEC8) | flagtables.FlagTables.getStatusDec8(self.memory.read(self.pc_state.HL));
        self.pc_state.PC  += 1
        return 11;
    
    def RET_exec():
        self.pc_state.PCLow  = self.memory.read(self.pc_state.SP)
        self.pc_state.SP += 1
        self.pc_state.PCHigh = self.memory.read(self.pc_state.SP)
        self.pc_state.SP += 1
    
        return 10;
    
# Addition instructions
#ADD16::ADD16(uint16 &dst, uint16 &add, int cycles, int pcInc)
        #:dst(dst),add(add),cycles(cycles),pcInc(pcInc)
#{
#}

    def ADD16_exec():
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
    
    def ADD_r_exec():
	    self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusAdd(self.pc_state.A,src);
	    self.pc_state.A = self.pc_state.A + src;
	    self.pc_state.PC += 1
	    return 4;
    
    def AND_r_exec():
        self.pc_state.A = self.pc_state.A & src;
        self.pc_state.PC += 1
    
        self.pc_state.F = flagtables.FlagTables.getStatusAnd(self.pc_state.A);
    
        return 4;
    
    def AND_n_exec():
    
        self.pc_state.A = self.pc_state.A & self.memory.read(self.pc_state.PC +1);
        self.pc_state.PC += 2;
        self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusAnd(self.pc_state.A);
    
        return 7;
    
    def OR_r_exec():
        self.pc_state.A = self.pc_state.A | src;
        self.pc_state.PC += 1
    
        self.pc_state.F = flagtables.FlagTables.getStatusOr(self.pc_state.A);
    
        return 4;
    
    def XOR_r_exec():
        self.pc_state.A = self.pc_state.A ^ src;
        self.pc_state.PC += 1
    
        self.pc_state.F = flagtables.FlagTables.getStatusOr(self.pc_state.A);
    
        return 4;
    
    def EXX_exec():
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
    
    def RLCA_exec():
        self.pc_state.A = (self.pc_state.A << 1) | ((self.pc_state.A >> 7) & 0x1);
        self.pc_state.Fstatus.status.C = self.pc_state.A & 0x1;
        self.pc_state.Fstatus.status.N = 0;
        self.pc_state.Fstatus.status.HLHigh = 0;
        self.pc_state.PC += 1
        return 4;
    
    def CP_n_exec():
    
        self.pc_state.F = flagtables.FlagTables.getStatusSub(self.pc_state.A, self.memory.read(self.pc_state.PC +1));
        self.pc_state.PC += 2;
    
        return 7;
    
    def CP_r_exec():
        self.pc_state.F = flagtables.FlagTables.getStatusSub(self.pc_state.A,r);
        self.pc_state.PC += 1
    
        return 4;
