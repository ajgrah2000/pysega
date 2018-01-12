#from . import addressing
from . import instructions
from . import instruction_store
from . import pc_state
from . import flagtables
from .. import errors

class Core(object):
    """
        CPU Core - Contains op code mappings.
    """
    IRQIM1ADDR = 0x38;

    def __init__(self, clocks, memory, pc_state, ports, interuptor):

        self.clocks     = clocks
        self.memory     = memory
        self.pc_state   = pc_state
        self.ports      = ports
        self.interuptor = interuptor

        self.instruction_exe = instructions.InstructionExec(self.pc_state)

        self.instruction_lookup = instruction_store.InstructionStore(self.clocks, self.pc_state, self.ports, self.instruction_exe)

        self._nextPossibleInterupt = 0

        flagtables.FlagTables.init()

    def get_save_state(self):
        # TODO
        state = {}
        return state

    def set_save_state(self, state):
        # TODO
        pass

    def reset(self):
        # TODO
        pass

    def initialise(self):
        self.instruction_lookup.populate_instruction_map(self.clocks, self.pc_state, self.memory)

    def interupt(self):
        if (self.pc_state.IFF1 == 1):
            if (self.pc_state.IM == 1):
                self.pc_state.SP -= 1;
                self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                self.pc_state.SP -= 1;
                self.memory.write(self.pc_state.SP, self.pc_state.PCLow);
                self.pc_state.PC = self.IRQIM1ADDR;

                # Disable maskable interupts
                self.pc_state.IFF1 = 0;
            else:
                errors.unsupported("interupt mode not supported");

    def step(self, loop=True, debug=False):
     op_code = self.memory.read(self.pc_state.PC)
    
#    static uint16 tmp16;
#    static uint8 tmp8, t8;
#    static const Byte *atPC;

#     while True:
     if True:

          # Check for any possible interupts
      if debug:
          print ("%d %d"%(self.clocks.cycles, self._nextPossibleInterupt))

      if (self.clocks.cycles >= self._nextPossibleInterupt):
          self.interuptor.setCycle(self.clocks.cycles);
          self._nextPossibleInterupt = self.interuptor.getNextInterupt(self.clocks.cycles);

      atPC = self.memory.readMulti(self.pc_state.PC);
#      std::cout << std::hex << (int) atPC[0] << " " << (int) self.pc_state.PC << std::endl;
      op_code = atPC[0]
      if debug:
          print("%d %x %x (%x) %s"%(self.clocks.cycles, op_code, self.pc_state.PC, atPC[0], self.pc_state))

      # This will raise an exception for unsupported op_code
      instruction = self.instruction_lookup.getInstruction(op_code)
      if instruction:
        self.clocks.cycles += instruction.execute(self.memory)
      else:
                # EX self.pc_state.AF, self.pc_state.AF'
            if (op_code == 0x08):
                tmpa = self.pc_state.A;
                tmpf = self.pc_state.F;
                self.pc_state.A = self.pc_state.A_;
                self.pc_state.F = self.pc_state.F_;
                self.pc_state.A_ = tmpa;
                self.pc_state.F_ = tmpf;

                self.pc_state.PC += 1
                self.clocks.cycles+=4;

                # LD (self.pc_state.DE), self.pc_state.A
            elif (op_code == 0x12):
                self.memory.write(self.pc_state.DE, self.pc_state.A);
                self.pc_state.PC += 1
                self.clocks.cycles += 7;

                # RLA
            elif (op_code == 0x17):
                tmp8 = self.pc_state.A;
                self.pc_state.A = (self.pc_state.A << 1) | (self.pc_state.Fstatus.C);
                self.pc_state.Fstatus.C = (tmp8 & 0x80) >> 7;
                self.pc_state.Fstatus.H = 0;
                self.pc_state.Fstatus.N = 0;
                self.pc_state.PC += 1
                self.clocks.cycles+=4;

                # Relative jump
                # JR e
            elif (op_code == 0x18):
                self.pc_state.PC += self._int_signed_char(atPC[1])
                self.pc_state.PC += 2;

                self.clocks.cycles += 12;

                # RRA
            elif (op_code == 0x1F):
                tmp8 = self.pc_state.A;
                self.pc_state.A = (self.pc_state.A >> 1) | (self.pc_state.Fstatus.C << 7);
                self.pc_state.Fstatus.C = tmp8 & 0x1;
                self.pc_state.Fstatus.H = 0;
                self.pc_state.Fstatus.N = 0;
                self.pc_state.PC += 1
                self.clocks.cycles+=4;

                # LD (nn), self.pc_state.HL
            elif (op_code == 0x22):
                self.memory.write(self.memory.read16(self.pc_state.PC+1), self.pc_state.L);
                self.memory.write(self.memory.read16(self.pc_state.PC+1)+1, self.pc_state.H);
                self.pc_state.PC += 3;

                self.clocks.cycles += 16;

                # Really need to put this into a table
            elif (op_code == 0x27):
                if (self.pc_state.Fstatus.N == 0): # self.pc_state.Addition instruction
                    self.calculateDAAAdd();
                else: # Subtraction instruction
                    self.calculateDAASub();
                self.pc_state.PC += 1
                self.clocks.cycles+=4;

                # CPL
            elif (op_code == 0x2F):
                self.pc_state.Fstatus.H = 1;
                self.pc_state.Fstatus.N = 1;
                self.pc_state.A ^= 0xFF;
                self.pc_state.PC += 1

                self.clocks.cycles+=4;

                # JR NC, e
            elif (op_code == 0x30):
                if (self.pc_state.Fstatus.C == 0):
#                    self.pc_state.PC += (int) (signed char) atPC[1];
                    self.pc_state.PC += self._int_signed_char(atPC[1])
                    self.clocks.cycles+=5;

                self.pc_state.PC += 2;
                self.clocks.cycles += 7;


                # LD (nn), self.pc_state.A
            elif (op_code == 0x32):
                self.memory.write(self.memory.read16(self.pc_state.PC+1), self.pc_state.A);
                self.pc_state.PC +=3;

                self.clocks.cycles += 13;

                # SCF
            elif (op_code == 0x37):
                 self.pc_state.Fstatus.H = 0;
                 self.pc_state.Fstatus.N = 0;
                 self.pc_state.Fstatus.C = 1;
                 self.pc_state.PC += 1
                 self.clocks.cycles += 4;

                # JR C, e
            elif (op_code == 0x38):
                if (self.pc_state.Fstatus.C == 1):
#                    self.pc_state.PC += (int) (signed char) atPC[1];
                    self.pc_state.PC += self._int_signed_char(atPC[1])
                    self.clocks.cycles+=5;

                self.pc_state.PC += 2;
                self.clocks.cycles += 7;

                # CCF
            elif (op_code == 0x3F):
                self.pc_state.Fstatus.H = self.pc_state.Fstatus.C;
                self.pc_state.Fstatus.N = 0;
                self.pc_state.Fstatus.C = 1-self.pc_state.Fstatus.C; #Invert carry flag
                self.pc_state.PC += 1
                self.clocks.cycles += 4;

            elif (op_code == 0x76): # LD (self.pc_state.HL), (self.pc_state.HL)
                self.pc_state.PC += 1
                self.clocks.cycles += 7;

            elif (op_code == 0x86): # self.pc_state.ADD (self.pc_state.HL) 
                self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusAdd(self.pc_state.A,self.memory.read(self.pc_state.HL));
                self.pc_state.A = self.pc_state.A + self.memory.read(self.pc_state.HL);
                self.pc_state.PC += 1
                self.clocks.cycles+=7;

                # self.pc_state.ADC r
            elif ((op_code == 0x88) or # self.pc_state.ADC self.pc_state.B
                  (op_code == 0x89) or # self.pc_state.ADC C
                  (op_code == 0x8A) or # self.pc_state.ADC D
                  (op_code == 0x8B) or # self.pc_state.ADC E
                  (op_code == 0x8C) or # self.pc_state.ADC H
                  (op_code == 0x8D) or # self.pc_state.ADC L
                  (op_code == 0x8F)): # self.pc_state.ADC self.pc_state.A
                self.pc_state.A = self.add8c(self.pc_state.A, self.pc_state[atPC[0]&0x7], self.pc_state.Fstatus.C);
                self.pc_state.PC += 1
                self.clocks.cycles+=4;

                # self.pc_state.ADC (self.pc_state.HL)
            elif (op_code == 0x8E):
                self.pc_state.A = self.add8c(self.pc_state.A, self.memory.read(self.pc_state.HL), self.pc_state.Fstatus.C);
                self.pc_state.PC += 1
                self.clocks.cycles+=7;

                # SUB (self.pc_state.HL) 
            elif (op_code == 0x96):
                self.pc_state.F = flagtables.FlagTables.getStatusSub(self.pc_state.A,self.memory.read(self.pc_state.HL));
                self.pc_state.A = self.pc_state.A - self.memory.read(self.pc_state.HL);
                self.pc_state.PC += 1
                self.clocks.cycles+=7;

                # Sself.pc_state.BC r
            elif ((op_code == 0x98) or # Sself.pc_state.BC self.pc_state.B
                  (op_code == 0x99) or # Sself.pc_state.BC C
                  (op_code == 0x9A) or # Sself.pc_state.BC D
                  (op_code == 0x9B) or # Sself.pc_state.BC E
                  (op_code == 0x9C) or # Sself.pc_state.BC H
                  (op_code == 0x9D) or # Sself.pc_state.BC L
                  (op_code == 0x9F)): # Sself.pc_state.BC self.pc_state.A
                self.pc_state.A = self.sub8c(self.pc_state.A, self.pc_state[atPC[0]&0x7], self.pc_state.Fstatus.C);
                self.pc_state.PC += 1
                self.clocks.cycles+=4;

                # Sself.pc_state.BC (self.pc_state.HL)
            elif (op_code == 0x9E):
                self.pc_state.A = self.sub8c(self.pc_state.A, self.memory.read(self.pc_state.HL), self.pc_state.Fstatus.C);
                self.pc_state.PC += 1
                self.clocks.cycles+=7;

                # self.pc_state.AND r
            elif ((op_code == 0xA0) or # self.pc_state.AND self.pc_state.B
                  (op_code == 0xA1) or # self.pc_state.AND C
                  (op_code == 0xA2) or # self.pc_state.AND D
                  (op_code == 0xA3) or # self.pc_state.AND E
                  (op_code == 0xA4) or # self.pc_state.AND H
                  (op_code == 0xA5)): # self.pc_state.AND L
                self.pc_state.A = self.pc_state.A & self.pc_state[atPC[0]&0x7];
                self.pc_state.PC += 1
                self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusAnd(self.pc_state.A);

                self.clocks.cycles+=4;

                # self.pc_state.AND (self.pc_state.HL)
            elif (op_code == 0xA6):
                self.pc_state.A = self.pc_state.A & self.memory.read(self.pc_state.HL);
                self.pc_state.PC += 1
                self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusAnd(self.pc_state.A);

                self.clocks.cycles+=7;

            elif (op_code == 0xA7): # self.pc_state.AND self.pc_state.A
                self.pc_state.PC += 1
                self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusAnd(self.pc_state.A);
                self.clocks.cycles+=4;

                # XOR (self.pc_state.HL)
            elif (op_code == 0xAE):
                self.pc_state.A = self.pc_state.A ^ self.memory.read(self.pc_state.HL);
                self.pc_state.PC += 1
                self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusOr(self.pc_state.A);

                self.clocks.cycles += 7;

                # OR (self.pc_state.HL)
            elif (op_code == 0xB6):
                self.pc_state.A = self.pc_state.A | self.memory.read(self.pc_state.HL);
                self.pc_state.PC += 1
                self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusOr(self.pc_state.A);

                self.clocks.cycles += 7;

                # CP (self.pc_state.HL) 
            elif (op_code == 0xBE):
                self.pc_state.F = flagtables.FlagTables.getStatusSub(self.pc_state.A,self.memory.read(self.pc_state.HL));
                self.pc_state.PC += 1

                self.clocks.cycles+=7;

                # RET NZ
            elif (op_code == 0xC0):
                if (self.pc_state.Fstatus.Z == 0):
                    self.pc_state.PCLow  = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    self.pc_state.PCHigh = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    self.clocks.cycles += 11;
                else:
                    self.pc_state.PC += 1
                    self.clocks.cycles+=5;

                # POP self.pc_state.BC
            elif (op_code == 0xC1):
                self.pc_state.C = self.memory.read(self.pc_state.SP);
                self.pc_state.SP += 1
                self.pc_state.B = self.memory.read(self.pc_state.SP);
                self.pc_state.SP += 1

                self.pc_state.PC += 1

                self.clocks.cycles += 10;

                # JP NZ, nn
            elif (op_code == 0xC2):
                if (self.pc_state.Fstatus.Z == 0):
                    self.pc_state.PC = self.memory.read16(self.pc_state.PC+1);
                else:
                    self.pc_state.PC += 3;

                self.clocks.cycles += 10;

                # JP nn
            elif (op_code == 0xC3):
                self.pc_state.PC = self.memory.read16(self.pc_state.PC+1);

                self.clocks.cycles+=10;

                # CALL NZ, nn
            elif (op_code == 0xC4):
                self.pc_state.PC += 3;
                if (self.pc_state.Fstatus.Z == 0):
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCLow);
                    self.pc_state.PC = self.memory.read16(self.pc_state.PC-2);
                    self.clocks.cycles += 7;

                self.clocks.cycles += 10;

                # PUSH self.pc_state.BC
            elif (op_code == 0xC5):
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.B);
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.C);
                self.pc_state.PC += 1

                self.clocks.cycles +=11;

                # self.pc_state.ADD n
            elif (op_code == 0xC6):
                self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusAdd(self.pc_state.A,atPC[1]);
                self.pc_state.A = self.pc_state.A + atPC[1];
                self.pc_state.PC+=2;
                self.clocks.cycles+=7;

                # RST 00h
            elif (op_code == 0xC7):
                self.pc_state.PC += 1
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCLow);

                self.pc_state.PC = 0x00;

                self.clocks.cycles += 11;

                # RET Z
            elif (op_code == 0xC8):
                if (self.pc_state.Fstatus.Z == 1):
                    self.pc_state.PCLow  = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    self.pc_state.PCHigh = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    self.clocks.cycles += 11;
                else:
                    self.pc_state.PC += 1
                    self.clocks.cycles+=5;

                # JP Z, nn
            elif (op_code == 0xCA):
                if (self.pc_state.Fstatus.Z == 1):
                    self.pc_state.PC = self.memory.read16(self.pc_state.PC+1);
                else:
                    self.pc_state.PC += 3;

                self.clocks.cycles += 10;

            elif (op_code == 0xCB):
                # Temporary, until `all instructions are covered'
                instruction = self.instruction_lookup.getExtendedCB(atPC[1]);# &atPC[1]);
                if (instruction != None):
                    self.clocks.cycles += instruction.execute(self.memory);
                else:
                    extended_op_code = atPC[1]

                    errors.warning("OP 0xCB n, value %x unsupported"%(extended_op_code));
                    return -1;

                # CALL Z, nn
            elif (op_code == 0xCC):
                self.pc_state.PC += 3;
                if (self.pc_state.Fstatus.Z == 1):
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCLow);
                    self.pc_state.PC = self.memory.read16(self.pc_state.PC-2);

                    self.clocks.cycles += 7;
                else:
                    self.clocks.cycles += 10;

                # CALL nn
            elif (op_code == 0xCD):
                self.pc_state.PC += 3;
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCLow);
                self.pc_state.PC = self.memory.read16(self.pc_state.PC-2);

                self.clocks.cycles += 17;

                # self.pc_state.ADC nn
            elif (op_code == 0xCE):
                self.pc_state.A = self.add8c(self.pc_state.A, atPC[1], self.pc_state.Fstatus.C);
                self.pc_state.PC+=2;
                self.clocks.cycles+=4;

                # RST 08h
            elif (op_code == 0xCF):
                self.pc_state.PC += 1
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCLow);

                self.pc_state.PC = 0x08;

                self.clocks.cycles += 11;

                # RET NC
            elif (op_code == 0xD0):
                if (self.pc_state.Fstatus.C == 0):
                    self.pc_state.PCLow  = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    self.pc_state.PCHigh = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    self.clocks.cycles += 11;
                else:
                    self.pc_state.PC += 1
                    self.clocks.cycles+=5;

                  # POP self.pc_state.DE
            elif (op_code == 0xD1):
                self.pc_state.E = self.memory.read(self.pc_state.SP);
                self.pc_state.SP += 1
                self.pc_state.D = self.memory.read(self.pc_state.SP);
                self.pc_state.SP += 1
                self.pc_state.PC += 1
                self.clocks.cycles += 10;

                # CALL NC, nn  
            elif (op_code == 0xD4):
                self.pc_state.PC += 3;
                if (self.pc_state.Fstatus.C == 0):
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCLow);
                    self.pc_state.PC = self.memory.read16(self.pc_state.PC-2);

                    self.clocks.cycles += 7;
                else:
                    self.clocks.cycles += 10;

                # PUSH self.pc_state.DE
            elif (op_code == 0xD5):
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.D);
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.E);
                self.pc_state.PC += 1

                self.clocks.cycles +=11;

                # SUB n
            elif (op_code == 0xD6):
                self.pc_state.F = flagtables.FlagTables.getStatusSub(self.pc_state.A,atPC[1]);
                self.pc_state.A = self.pc_state.A - atPC[1];
                self.pc_state.PC += 2;
                self.clocks.cycles += 7;

                # RST 10h
            elif (op_code == 0xD7):
                self.pc_state.PC += 1
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCLow);

                self.pc_state.PC = 0x10;

                self.clocks.cycles += 11;
                
                # RET C
            elif (op_code == 0xD8):
                if (self.pc_state.Fstatus.C == 1):
                    self.pc_state.PCLow  = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    self.pc_state.PCHigh = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    self.clocks.cycles += 11;
                else:
                    self.pc_state.PC += 1
                    self.clocks.cycles+=5;

                # IN self.pc_state.A, (N)
            elif (op_code == 0xDB):
                self.pc_state.A = self.ports.portRead(atPC[1]);
                self.pc_state.PC += 2;
                self.clocks.cycles += 11;

                # Call C, nn
            elif (op_code == 0xDC):
                self.pc_state.PC += 3;
                if (self.pc_state.Fstatus.C == 1):
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCLow);
                    self.pc_state.PC = self.memory.read16(self.pc_state.PC-2);
                    self.clocks.cycles += 17;
                else:
                    self.clocks.cycles += 10;

                # Sself.pc_state.BC n 
            elif (op_code == 0xDE):
                self.pc_state.A = self.sub8c(self.pc_state.A, atPC[1], self.pc_state.Fstatus.C);
                self.pc_state.PC+=2;
                self.clocks.cycles+=7;

                # RST 18h
            elif (op_code == 0xDF):
                self.pc_state.PC += 1
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCLow);

                self.pc_state.PC = 0x18;

                self.clocks.cycles += 11;

                # RET PO  
            elif (op_code == 0xE0):
                if (self.pc_state.Fstatus.PV == 0):
                    self.pc_state.PCLow  = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    self.pc_state.PCHigh = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    self.clocks.cycles += 11;
                else:
                    self.pc_state.PC += 1
                    self.clocks.cycles+=5;

                # POP self.pc_state.HL
            elif (op_code == 0xE1):
                self.pc_state.L = self.memory.read(self.pc_state.SP);
                self.pc_state.SP += 1
                self.pc_state.H = self.memory.read(self.pc_state.SP);
                self.pc_state.SP += 1

                self.pc_state.PC += 1

                self.clocks.cycles += 10;

                # JP PO, nn   Parity Odd 
            elif (op_code == 0xE2):
                if (self.pc_state.Fstatus.PV == 0):
                    self.pc_state.PC = self.memory.read16(self.pc_state.PC+1);
                else:
                    self.pc_state.PC += 3;

                self.clocks.cycles +=10;

                # EX (self.pc_state.SP), self.pc_state.HL
            elif (op_code == 0xE3):
                tmp8 = self.memory.read(self.pc_state.SP);
                self.memory.write(self.pc_state.SP, self.pc_state.L);
                self.pc_state.L = tmp8;
                tmp8 = self.memory.read(self.pc_state.SP+1);
                self.memory.write(self.pc_state.SP+1, self.pc_state.H);
                self.pc_state.H = tmp8;
                self.pc_state.PC += 1
                self.clocks.cycles += 19;

                # CALL PO, nn 
            elif (op_code == 0xE4):
                self.pc_state.PC += 3;
                if (self.pc_state.Fstatus.PV == 0):
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCLow);
                    self.pc_state.PC = self.memory.read16(self.pc_state.PC-2);
                    self.clocks.cycles += 7;

                self.clocks.cycles += 10;


                # PUSH self.pc_state.HL
            elif (op_code == 0xE5):
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.H);
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.L);
                self.pc_state.PC += 1

                self.clocks.cycles +=11;

                # RST 20h
            elif (op_code == 0xE7):
                self.pc_state.PC += 1
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCLow);

                self.pc_state.PC = 0x20;

                self.clocks.cycles += 11;

                # RET PE  
            elif (op_code == 0xE8):
                if (self.pc_state.Fstatus.PV == 1):
                    self.pc_state.PCLow  = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    self.pc_state.PCHigh = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    self.clocks.cycles += 11;
                else:
                    self.pc_state.PC += 1
                    self.clocks.cycles+=5;

                # Don't know how many self.clocks.cycles
                # LD self.pc_state.PC, self.pc_state.HL
            elif (op_code == 0xE9):
                self.pc_state.PC = self.pc_state.HL;
                self.clocks.cycles+=6;

                # JP PE, nn   Parity Even 
            elif (op_code == 0xEA):
                if (self.pc_state.Fstatus.PV == 1):
                    self.pc_state.PC = self.memory.read16(self.pc_state.PC+1);
                else:
                    self.pc_state.PC += 3;

                self.clocks.cycles +=10;

                # EX self.pc_state.DE, self.pc_state.HL
            elif (op_code == 0xEB):
                tmp16 = self.pc_state.DE;
                self.pc_state.DE = self.pc_state.HL;
                self.pc_state.HL = tmp16;
                self.pc_state.PC += 1
                self.clocks.cycles+=4;

                # CALL PE, nn
            elif (op_code == 0xEC):
                self.pc_state.PC += 3;
                if (self.pc_state.Fstatus.PV == 1):
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCLow);
                    self.pc_state.PC = self.memory.read16(self.pc_state.PC-2);
                    self.clocks.cycles += 7;

                self.clocks.cycles += 10;

                # XOR n
            elif (op_code == 0xEE): 
                self.pc_state.A = self.pc_state.A ^ atPC[1];
                self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusOr(self.pc_state.A);
                self.pc_state.PC+=2;
                self.clocks.cycles+=7;

                # RST 28h
            elif (op_code == 0xEF):
                self.pc_state.PC += 1
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCLow);

                self.pc_state.PC = 0x28;

                self.clocks.cycles += 11;

                # RET P, if Positive
            elif (op_code == 0xF0):
                if (self.pc_state.Fstatus.S == 0):
                    self.pc_state.PCLow  = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    self.pc_state.PCHigh = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    self.clocks.cycles += 11;
                else:
                    self.pc_state.PC += 1
                    self.clocks.cycles+=5;

                # POP self.pc_state.AF
            elif (op_code == 0xF1):
                self.pc_state.F = self.memory.read(self.pc_state.SP);
                self.pc_state.SP += 1
                self.pc_state.A = self.memory.read(self.pc_state.SP);
                self.pc_state.SP += 1

                self.pc_state.PC += 1

                self.clocks.cycles+=10;

                # JP P, nn    if Positive
            elif (op_code == 0xF2):
                if (self.pc_state.Fstatus.S == 0):
                    self.pc_state.PC = self.memory.read16(self.pc_state.PC+1);
                else:
                    self.pc_state.PC += 3;

                self.clocks.cycles +=10;

              # Disable interupts
              # DI
            elif (op_code == 0xF3):
                self.pc_state.IFF1 = 0;
                self.pc_state.IFF2 = 0;
                self.pc_state.PC += 1

                self.clocks.cycles+=4;

                # CALL P, nn  if Positive
            elif (op_code == 0xF4):
                self.pc_state.PC += 3;
                if (self.pc_state.Fstatus.S == 0):
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCLow);
                    self.pc_state.PC = self.memory.read16(self.pc_state.PC-2);
                    self.clocks.cycles += 7;

                self.clocks.cycles += 10;

                # PUSH self.pc_state.AF
            elif (op_code == 0xF5):
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.A);
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.F);
                self.pc_state.PC += 1

                self.clocks.cycles+=11;

                # OR n
            elif (op_code == 0xF6):
                self.pc_state.A = self.pc_state.A | atPC[1];
                self.pc_state.Fstatus.value = flagtables.FlagTables.getStatusOr(self.pc_state.A);
                self.pc_state.PC += 2;
                self.clocks.cycles+=7;

                # RST 30h
            elif (op_code == 0xF7):
                self.pc_state.PC += 1
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCLow);

                self.pc_state.PC = 0x30;

                self.clocks.cycles += 11;

                # RET M  if Negative
            elif (op_code == 0xF8):
                if (self.pc_state.Fstatus.S == 1):
                    self.pc_state.PCLow  = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    self.pc_state.PCHigh = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    self.clocks.cycles += 11;
                else:
                    self.pc_state.PC += 1
                    self.clocks.cycles+=5;

                # LD self.pc_state.SP, self.pc_state.HL
            elif (op_code == 0xF9):
                self.pc_state.SP = self.pc_state.HL;
                self.pc_state.PC += 1
                self.clocks.cycles+=6;

                # JP M, nn    if Negative
            elif (op_code == 0xFA):
                if (self.pc_state.Fstatus.S == 1):
                    self.pc_state.PC = self.memory.read16(self.pc_state.PC+1);
                else:
                    self.pc_state.PC += 3;

                self.clocks.cycles +=10;

                # Enable interupts
                # EI
            elif (op_code == 0xFB):
                self.pc_state.PC += 1

                # Process next instruction before enabling interupts
                self.step(False); # Single step, no loop

                self.pc_state.IFF1 = 1;
                self.pc_state.IFF2 = 1;
                self.clocks.cycles+=4;

                  # Check for any pending interupts
                if (self.interuptor.pollInterupts(self.clocks.cycles) == True):
                    self.interupt()


                # CALL M, nn  if Negative
            elif (op_code == 0xFC):
                self.pc_state.PC += 3;
                if (self.pc_state.Fstatus.S == 1):
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCLow);
                    self.pc_state.PC = self.memory.read16(self.pc_state.PC-2);

                    self.clocks.cycles += 7;
                else:
                    self.clocks.cycles += 10;

                # RST 38h
            elif (op_code == 0xFF):
                self.pc_state.PC += 1
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCLow);

                self.pc_state.PC = 0x38;

                self.clocks.cycles += 11;

            elif (op_code == 0xDD):
                # Temporary, until `all instructions are covered'
                instruction = self.instruction_lookup.getExtendedDD(atPC[1]);# &atPC[1]);
                if (instruction):
                    self.clocks.cycles += instruction.execute(self.memory);
                else:
                    print("Unsupported op code DD %x"%(atPC[1]))
                    return -1;

            elif (op_code == 0xFD):
                # Temporary, until `all instructions are covered'
                instruction = self.instruction_lookup.getExtendedFD(atPC[1]);# &atPC[1]);
                if (instruction):
                    self.clocks.cycles += instruction.execute(self.memory);
                else:
                    print("Unsupported op code FD %x"%(atPC[1]))
                    return -1;

              # Extended op_code
            elif (op_code == 0xED):
                # Temporary, until `all instructions are covered'
                instruction = self.instruction_lookup.getExtendedED(atPC[1]);# &atPC[1]);
                if (instruction):
                    self.clocks.cycles += instruction.execute(self.memory);
                else:
                    print("Unsupported op code ED %x"%(atPC[1]))
                    return -1;

            else:
#        std::cout << "Unsupported op_code 0x" << 
#                        std::hex << (int) atPC[0] << std::endl;
                print("Unsupported op code %x"%(atPC[0]))
                return -1;

#      if (False == loop):
#          break
     return 0

    def _int_signed_char(self, value):
        result = value
        if (value & 0x80):
            result = value + 0xFF00
        return result

    # Calculate the result of the DAA functio
    def calculateDAAAdd(self):
        print "calculateDAAAdd"

        upper = (self.pc_state.A >> 4) & 0xF;
        lower = self.pc_state.A & 0xF;
        
        if (self.pc_state.Fstatus.C == 0):
            if ((upper <= 9) and (self.pc_state.Fstatus.H == 0) and (lower <= 9)):
                pass
            elif ((upper <= 8) and (self.pc_state.Fstatus.H == 0) and ((lower >= 0xA) and (lower <= 0xF))):
                self.pc_state.A += 0x06;
            elif ((upper <= 9) and (self.pc_state.Fstatus.H == 1) and (lower <= 0x3)):
                self.pc_state.A += 0x06;
            elif (((upper >= 0xA) and (upper <= 0xF)) and (self.pc_state.Fstatus.H == 0) and (lower <= 0x9)):
                self.pc_state.A += 0x60;
                self.pc_state.Fstatus.C = 1;
            elif (((upper >= 0x9) and (upper <= 0xF)) and (self.pc_state.Fstatus.H == 0) and ((lower >= 0xA) and (lower <= 0xF))):
                self.pc_state.A += 0x66;
                self.pc_state.Fstatus.C = 1;
            elif (((upper >= 0xA) and (upper <= 0xF)) and (self.pc_state.Fstatus.H == 1) and (lower <= 0x3)):
                self.pc_state.A += 0x66;
                self.pc_state.Fstatus.C = 1;
        else:
            if ((upper <= 0x2) and (self.pc_state.Fstatus.H == 0) and (lower <= 0x9)):
                self.pc_state.A += 0x60;
            elif ((upper <= 0x2) and (self.pc_state.Fstatus.H == 0) and ((lower >= 0xA) and (lower <= 0xF))):
                self.pc_state.A += 0x66;
            elif ((upper <= 0x3) and (self.pc_state.Fstatus.H == 1) and (lower <= 0x3)):
                self.pc_state.A += 0x66;

        self.pc_state.Fstatus.PV = flagtables.FlagTables.calculateParity(self.pc_state.A);
        if (self.pc_state.A & 0x80): # Is negative
            self.pc_state.Fstatus.S  = 1
        else:
            self.pc_state.Fstatus.S  = 0

        if (self.pc_state.A==0): # Is zero
            self.pc_state.Fstatus.Z = 1
        else:
            self.pc_state.Fstatus.Z = 0
    
    # Fcpu_state->IXME, table in z80 guide is wrong, need to check values by hand
    def calculateDAASub(self):
        upper = (self.pc_state.A >> 4) & 0xF;
        lower = self.pc_state.A & 0xF;
    
        if (self.pc_state.Fstatus.C == 0):
            if ((upper <= 0x9) and (self.pc_state.Fstatus.H == 0) and (lower <= 0x9)):
                pass
            elif ((upper <= 0x8) and (self.pc_state.Fstatus.H == 1) and ((lower >= 0x6) and (lower <= 0xF))):
                self.pc_state.A += 0xFA;
        else:
            if (((upper >= 0x7) and (upper <= 0xF)) and (self.pc_state.Fstatus.H == 0) and (lower <= 0x9)):
                self.pc_state.A += 0xA0;
            elif (((upper >= 0x6) and (upper <= 0xF)) and (self.pc_state.Fstatus.H == 1) and ((lower >= 0x6) and (lower <= 0xF))):
                self.pc_state.Fstatus.H = 0;
                self.pc_state.A += 0x9A;
        self.pc_state.Fstatus.PV = flagtables.FlagTables.calculateParity(self.pc_state.A);
        if (self.pc_state.A & 0x80): #Is negative
            self.pc_state.Fstatus.S = 1
        else:
            self.pc_state.Fstatus.S = 0
        if (self.pc_state.A==0): # Is zero
            self.pc_state.Fstatus.Z = 1
        else:
            self.pc_state.Fstatus.Z = 0
    
    # self.pc_state.Add two 8 bit ints plus the carry bit, and set flags accordingly
    def add8c(self, a, b, c):
        r = a + b + c;
        rs = (a + b + c) & 0xFF;
        if (rs & 0x80): # Negative
            self.pc_state.Fstatus.S = 1
        else:
            self.pc_state.Fstatus.S = 0

        if (rs == 0): # Zero
            self.pc_state.Fstatus.Z = 1
        else:
            self.pc_state.Fstatus.Z = 0

        if (((r & 0xF00) != 0) and 
             (r & 0xF00) != 0xF00):
            self.pc_state.Fstatus.PV = 1
        else:
            self.pc_state.Fstatus.PV = 0
    
        r = (a & 0xF) + (b & 0xF) + c;
        if (r & 0x10): # Half carry
            self.pc_state.Fstatus.H = 1
        else:
            self.pc_state.Fstatus.H = 0

        self.pc_state.Fstatus.N = 0;
    
        r = (a & 0xFF) + (b & 0xFF) + c;
        if (r & 0x100): # Carry
            self.pc_state.Fstatus.C = 1
        else:
            self.pc_state.Fstatus.C = 0

        return (a + b + c) & 0xFF
    
    # Subtract two 8 bit ints and the carry bit, set flags accordingly
    def sub8c(self, a, b, c):
        #static int16 r;
        #static int8 rs;
    
        r = a - b - c;
        rs = a - b - c;
        if (rs & 0x80): # Negative
            self.pc_state.Fstatus.S = 1
        else:
            self.pc_state.Fstatus.S = 0

        if (rs == 0): # Zero
            self.pc_state.Fstatus.Z = 1
        else:
            self.pc_state.Fstatus.Z = 0

        if (((r & 0x180) != 0) and 
             (r & 0x180) != 0x180): # Overflow
            self.pc_state.Fstatus.PV = 1
        else:
            self.pc_state.Fstatus.PV = 0
    
        r = (a & 0xF) - (b & 0xF) - c;
        if (r & 0x10): # Half carry
            self.pc_state.Fstatus.H = 1
        else:
            self.pc_state.Fstatus.H = 0
        self.pc_state.Fstatus.N = 1;
    
        r = (a & 0xFF) - (b & 0xFF) - c;
        if (r & 0x100): # Carry
            self.pc_state.Fstatus.C = 1
        else:
            self.pc_state.Fstatus.C = 0
        return (a - b - c) & 0xFF
