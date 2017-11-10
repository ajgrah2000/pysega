#from . import addressing
from . import instructions
from . import pc_state

class Core(object):
    """
        CPU Core - Contains op code mappings.
    """
    def __init__(self, clocks, memory, pc_state):
        self.clocks    = clocks
        self.memory    = memory
        self.pc_state  = pc_state

        self.instruction_exe = instructions.InstructionExec(self.pc_state)

        self.instruction_lookup = [instructions.Instruction(self.clocks, self.pc_state, self.instruction_exe)] * 256

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
        self.populate_instruction_map()

    def step(self):
        op_code = self.memory.read(self.pc_state.PC)
        print "%x"%(op_code)
    
#    static uint16 tmp16;
#    static uint8 tmp8, t8;
#    static const Byte *atPC;

    while loop:

          # Check for any possible interupts
      if (cycles >= nextPossibleInterupt):
          interuptor->setCycle(cycles);
          nextPossibleInterupt = interuptor->getNextInterupt(cycles);

      atPC = self.memory.readMulti(self.pc_state.PC);
      std::cout << std::hex << (int) atPC[0] << " " << (int) self.pc_state.PC << std::endl;

      # This will raise an exception for unsupported op_code
      if op_code in self.instruction_lookup:
        cycles += self.instruction_lookup[op_code].execute()
      else:
        op_code = atPC[0]
                # EX self.pc_state.AF, self.pc_state.AF'
            if (op_code == 0x08):
                tmp16 = self.pc_state.AF;
                self.pc_state.AF = self.pc_state.AF_;
                self.pc_state.AF_ = tmp16;

                self.pc_state.PC += 1
                cycles+=4;

                # LD (self.pc_state.DE), self.pc_state.A
            elif (op_code == 0x12):
                self.memory.write(self.pc_state.DE, self.pc_state.A);
                self.pc_state.PC += 1
                cycles += 7;

                # RLA
            elif (op_code == 0x17):
                tmp8 = self.pc_state.A;
                self.pc_state.A = (self.pc_state.A << 1) | (self.pc_state.Fstatus.status.C);
                self.pc_state.Fstatus.status.C = (tmp8 & 0x80) >> 7;
                self.pc_state.Fstatus.status.H = 0;
                self.pc_state.Fstatus.status.N = 0;
                self.pc_state.PC += 1
                cycles+=4;

                # Relative jump
                # JR e
            elif (op_code == 0x18):
                self.pc_state.PC += (int) (signed char) atPC[1];
                self.pc_state.PC += 2;

                cycles += 12;

                # RRA
            elif (op_code == 0x1F):
                tmp8 = self.pc_state.A;
                self.pc_state.A = (self.pc_state.A >> 1) | (self.pc_state.Fstatus.status.C << 7);
                self.pc_state.Fstatus.status.C = tmp8 & 0x1;
                self.pc_state.Fstatus.status.H = 0;
                self.pc_state.Fstatus.status.N = 0;
                self.pc_state.PC += 1
                cycles+=4;

                # LD (nn), self.pc_state.HL
            elif (op_code == 0x22):
                self.memory.write(self.memory.read16(self.pc_state.PC+1), self.pc_state.L);
                self.memory.write(self.memory.read16(self.pc_state.PC+1)+1, self.pc_state.H);
                self.pc_state.PC += 3;

                cycles += 16;

                # Really need to put this into a table
            elif (op_code == 0x27):
                if (self.pc_state.Fstatus.status.N == 0): # self.pc_state.Addition instruction
                    calculateDAAAdd();
                else: # Subtraction instruction
                    calculateDAASub();
                self.pc_state.PC += 1
                cycles+=4;

                # CPL
            elif (op_code == 0x2F):
                self.pc_state.Fstatus.status.H = 1;
                self.pc_state.Fstatus.status.N = 1;
                self.pc_state.A ^= 0xFF;
                self.pc_state.PC += 1

                cycles+=4;

                # JR NC, e
            elif (op_code == 0x30):
                if (self.pc_state.Fstatus.status.C == 0):
                    self.pc_state.PC += (int) (signed char) atPC[1];
                    cycles+=5;

                self.pc_state.PC += 2;
                cycles += 7;


                # LD (nn), self.pc_state.A
            elif (op_code == 0x32):
                self.memory.write(self.memory.read16(self.pc_state.PC+1), self.pc_state.A);
                self.pc_state.PC +=3;

                cycles += 13;

                # SCF
            elif (op_code == 0x37):
                 self.pc_state.Fstatus.status.H = 0;
                 self.pc_state.Fstatus.status.N = 0;
                 self.pc_state.Fstatus.status.C = 1;
                 self.pc_state.PC += 1
                 cycles += 4;

                # JR C, e
            elif (op_code == 0x38):
                if (self.pc_state.Fstatus.status.C == 1):
                    self.pc_state.PC += (int) (signed char) atPC[1];
                    cycles+=5;

                self.pc_state.PC += 2;
                cycles += 7;

                # CCF
            elif (op_code == 0x3F):
                self.pc_state.Fstatus.status.H = self.pc_state.Fstatus.status.C;
                self.pc_state.Fstatus.status.N = 0;
                self.pc_state.Fstatus.status.C = 1-self.pc_state.Fstatus.status.C; #Invert carry flag
                self.pc_state.PC += 1
                cycles += 4;

            elif (op_code == 0x76): # LD (self.pc_state.HL), (self.pc_state.HL)
                self.pc_state.PC += 1
                cycles += 7;

            elif (op_code == 0x86): # self.pc_state.ADD (self.pc_state.HL) 
                self.pc_state.Fstatus.value = FlagTables::getStatusAdd(self.pc_state.A,self.memory.read(self.pc_state.HL));
                self.pc_state.A = self.pc_state.A + self.memory.read(self.pc_state.HL);
                self.pc_state.PC += 1
                cycles+=7;

                # self.pc_state.ADC r
            elif ((op_code == 0x88) or # self.pc_state.ADC self.pc_state.B
                  (op_code == 0x89) or # self.pc_state.ADC C
                  (op_code == 0x8A) or # self.pc_state.ADC D
                  (op_code == 0x8B) or # self.pc_state.ADC E
                  (op_code == 0x8C) or # self.pc_state.ADC H
                  (op_code == 0x8D) or # self.pc_state.ADC L
                  (op_code == 0x8F)): # self.pc_state.ADC self.pc_state.A
                self.pc_state.A = add8c(self.pc_state.A, *r[atPC[0]&0x7], self.pc_state.Fstatus.status.C);
                self.pc_state.PC += 1
                cycles+=4;

                # self.pc_state.ADC (self.pc_state.HL)
            elif (op_code == 0x8E):
                self.pc_state.A = add8c(self.pc_state.A, self.memory.read(self.pc_state.HL), self.pc_state.Fstatus.status.C);
                self.pc_state.PC += 1
                cycles+=7;

                # SUB r
            elif ((op_code == 0x90) or # SUB self.pc_state.B
                  (op_code == 0x91) or # SUB C
                  (op_code == 0x92) or # SUB D
                  (op_code == 0x93) or # SUB E
                  (op_code == 0x94) or # SUB H
                  (op_code == 0x95) or # SUB L
                  (op_code == 0x97)): # SUB self.pc_state.A
                self.pc_state.F = FlagTables::getStatusSub(self.pc_state.A,*r[atPC[0] & 0x7]);
                self.pc_state.A = self.pc_state.A - *r[atPC[0] & 0x7];
                self.pc_state.PC += 1
                cycles+=4;

                # SUB (self.pc_state.HL) 
            elif (op_code == 0x96):
                self.pc_state.F = FlagTables::getStatusSub(self.pc_state.A,self.memory.read(self.pc_state.HL));
                self.pc_state.A = self.pc_state.A - self.memory.read(self.pc_state.HL);
                self.pc_state.PC += 1
                cycles+=7;

                # Sself.pc_state.BC r
            elif ((op_code == 0x98) or # Sself.pc_state.BC self.pc_state.B
                  (op_code == 0x99) or # Sself.pc_state.BC C
                  (op_code == 0x9A) or # Sself.pc_state.BC D
                  (op_code == 0x9B) or # Sself.pc_state.BC E
                  (op_code == 0x9C) or # Sself.pc_state.BC H
                  (op_code == 0x9D) or # Sself.pc_state.BC L
                  (op_code == 0x9F)): # Sself.pc_state.BC self.pc_state.A
                self.pc_state.A = sub8c(self.pc_state.A, *r[atPC[0]&0x7], self.pc_state.Fstatus.status.C);
                self.pc_state.PC += 1
                cycles+=4;

                # Sself.pc_state.BC (self.pc_state.HL)
            elif (op_code == 0x9E):
                self.pc_state.A = sub8c(self.pc_state.A, self.memory.read(self.pc_state.HL), self.pc_state.Fstatus.status.C);
                self.pc_state.PC += 1
                cycles+=7;

                # self.pc_state.AND r
            elif ((op_code == 0xA0) or # self.pc_state.AND self.pc_state.B
                  (op_code == 0xA1) or # self.pc_state.AND C
                  (op_code == 0xA2) or # self.pc_state.AND D
                  (op_code == 0xA3) or # self.pc_state.AND E
                  (op_code == 0xA4) or # self.pc_state.AND H
                  (op_code == 0xA5)): # self.pc_state.AND L
                self.pc_state.A = self.pc_state.A & *r[atPC[0]&0x7];
                self.pc_state.PC += 1
                self.pc_state.Fstatus.value = FlagTables::getStatusAnd(self.pc_state.A);

                cycles+=4;

                # self.pc_state.AND (self.pc_state.HL)
            elif (op_code == 0xA6):
                self.pc_state.A = self.pc_state.A & self.memory.read(self.pc_state.HL);
                self.pc_state.PC += 1
                self.pc_state.Fstatus.value = FlagTables::getStatusAnd(self.pc_state.A);

                cycles+=7;

            elif (op_code == 0xA7): # self.pc_state.AND self.pc_state.A
                self.pc_state.PC += 1
                self.pc_state.Fstatus.value = FlagTables::getStatusAnd(self.pc_state.A);
                cycles+=4;

                # XOR (self.pc_state.HL)
            elif (op_code == 0xAE):
                self.pc_state.A = self.pc_state.A ^ self.memory.read(self.pc_state.HL);
                self.pc_state.PC += 1
                self.pc_state.Fstatus.value = FlagTables::getStatusOr(self.pc_state.A);

                cycles += 7;

                # OR (self.pc_state.HL)
            elif (op_code == 0xB6):
                self.pc_state.A = self.pc_state.A | self.memory.read(self.pc_state.HL);
                self.pc_state.PC += 1
                self.pc_state.Fstatus.value = FlagTables::getStatusOr(self.pc_state.A);

                cycles += 7;

                # CP (self.pc_state.HL) 
            elif (op_code == 0xBE):
                self.pc_state.F = FlagTables::getStatusSub(self.pc_state.A,self.memory.read(self.pc_state.HL));
                self.pc_state.PC += 1

                cycles+=7;

                # RET NZ
            elif (op_code == 0xC0):
                if (self.pc_state.Fstatus.status.Z == 0):
                    self.pc_state.PCLow  = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    self.pc_state.PCHigh = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    cycles += 11;
                else:
                    self.pc_state.PC += 1
                    cycles+=5;

                # POP self.pc_state.BC
            elif (op_code == 0xC1):
                self.pc_state.C = self.memory.read(self.pc_state.SP);
                self.pc_state.SP += 1
                self.pc_state.B = self.memory.read(self.pc_state.SP);
                self.pc_state.SP += 1

                self.pc_state.PC += 1

                cycles += 10;

                # JP NZ, nn
            elif (op_code == 0xC2):
                if (self.pc_state.Fstatus.status.Z == 0):
                    self.pc_state.PC = self.memory.read16(self.pc_state.PC+1);
                else:
                    self.pc_state.PC += 3;

                cycles += 10;

                # JP nn
            elif (op_code == 0xC3):
                self.pc_state.PC = self.memory.read16(self.pc_state.PC+1);

                cycles+=10;

                # CALL NZ, nn
            elif (op_code == 0xC4):
                self.pc_state.PC += 3;
                if (self.pc_state.Fstatus.status.Z == 0):
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCLow);
                    self.pc_state.PC = self.memory.read16(self.pc_state.PC-2);
                    cycles += 7;

                cycles += 10;

                # PUSH self.pc_state.BC
            elif (op_code == 0xC5):
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.B);
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.C);
                self.pc_state.PC += 1

                cycles +=11;

                # self.pc_state.ADD n
            elif (op_code == 0xC6):
                self.pc_state.Fstatus.value = FlagTables::getStatusAdd(self.pc_state.A,atPC[1]);
                self.pc_state.A = self.pc_state.A + atPC[1];
                self.pc_state.PC+=2;
                cycles+=7;

                # RST 00h
            elif (op_code == 0xC7):
                self.pc_state.PC += 1
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCLow);

                self.pc_state.PC = 0x00;

                cycles += 11;

                # RET Z
            elif (op_code == 0xC8):
                if (self.pc_state.Fstatus.status.Z == 1):
                    self.pc_state.PCLow  = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    self.pc_state.PCHigh = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    cycles += 11;
                else:
                    self.pc_state.PC += 1
                    cycles+=5;

                # JP Z, nn
            elif (op_code == 0xCA):
                if (self.pc_state.Fstatus.status.Z == 1):
                    self.pc_state.PC = self.memory.read16(self.pc_state.PC+1);
                else:
                    self.pc_state.PC += 3;

                cycles += 10;

            elif (op_code == 0xCB):
                    extended_op_code = atPC[1] & 0xC7;

                    # self.pc_state.Bit b, r
                    if  ((extended_op_code == 0x40) or
                         (extended_op_code == 0x41) or
                         (extended_op_code == 0x42) or
                         (extended_op_code == 0x43) or
                         (extended_op_code == 0x44) or
                         (extended_op_code == 0x45) or
                         (extended_op_code == 0x47)):
                        self.pc_state.Fstatus.status.Z = 
                                   (*r[tmp8&0x7] >> ((tmp8 >> 3) & 7)) ^ 0x1;
                        self.pc_state.Fstatus.status.PV = FlagTables::calculateParity(*r[tmp8&0x7]);
                        self.pc_state.Fstatus.status.H = 1;
                        self.pc_state.Fstatus.status.N = 0;
                        self.pc_state.Fstatus.status.S = 0;
                        self.pc_state.PC += 2;
                        cycles += 8;
                        return 0;

                    # self.pc_state.Bit b, (self.pc_state.HL) 
                    elif (extended_op_code == 0x46):
                        self.pc_state.Fstatus.status.Z = (self.memory.read(self.pc_state.HL) >> 
                                            ((tmp8 >> 3) & 7)) ^ 0x1;
                        self.pc_state.Fstatus.status.H = 1;
                        self.pc_state.Fstatus.status.N = 0;
                        self.pc_state.Fstatus.status.S = 0;
                        self.pc_state.PC += 2;
                        cycles += 12;
                        return 0;

                    # RES b, r
                    elif ((extended_op_code == 0x80) or
                          (extended_op_code == 0x81) or
                          (extended_op_code == 0x82) or
                          (extended_op_code == 0x83) or
                          (extended_op_code == 0x84) or
                          (extended_op_code == 0x85) or
                          (extended_op_code == 0x87)):
                        *r[tmp8&0x7] = *r[tmp8&0x7] & ~(0x1 << ((tmp8 >> 3) & 7));
                        self.pc_state.PC += 2;
                        cycles += 8;
                        return 0;

                    # RES b, (self.pc_state.HL) 
                    elif (extended_op_code == 0x86):
                        self.memory.write(self.pc_state.HL, 
                            self.memory.read(self.pc_state.HL) & ~(0x1 << ((tmp8 >> 3) & 7)));
                        self.pc_state.PC += 2;
                        cycles += 12;
                        return 0;

                    # SET b, r
                    elif ((extended_op_code == 0xC0) or # SET b, self.pc_state.B
                          (extended_op_code == 0xC1) or # SET b, C
                          (extended_op_code == 0xC2) or # SET b, D
                          (extended_op_code == 0xC3) or # SET b, E
                          (extended_op_code == 0xC4) or # SET b, H
                          (extended_op_code == 0xC5) or # SET b, L
                          (extended_op_code == 0xC7)): # SET b, self.pc_state.A
                        *r[tmp8&0x7] = *r[tmp8&0x7] | (0x1 << ((tmp8 >> 3) & 7));
                        self.pc_state.PC += 2;
                        cycles += 8;
                        return 0;

                    elif (extended_op_code == 0xC6): # SET b, (self.pc_state.HL) 
                        self.memory.write(self.pc_state.HL,
                            self.memory.read(self.pc_state.HL) | (0x1 << ((tmp8 >> 3) & 7)));
                        self.pc_state.PC += 2;
                        cycles += 15;
                        return 0;
                    else:
                        pass

                    extended_op_code = atPC[1]

                    #uint8 *r8;

                    # RLC r
                    if  ((extended_op_code == 0x00) or # RLC self.pc_state.B
                         (extended_op_code == 0x01) or # RLC C
                         (extended_op_code == 0x02) or # RLC D
                         (extended_op_code == 0x03) or # RLC E
                         (extended_op_code == 0x04) or # RLC H
                         (extended_op_code == 0x05) or # RLC L
                         (extended_op_code == 0x07)):  # RLC self.pc_state.A
                        r8 = r[tmp8 & 0x7];
                        *r8 = (*r8 << 1) | ((*r8 >> 7) & 0x1);
                        self.pc_state.Fstatus.value = FlagTables::getStatusOr(*r8);
                        self.pc_state.Fstatus.status.C = *r8 & 0x1; # bit-7 of src = bit-0
                        self.pc_state.PC+=2;
                        cycles+=8;

                    elif (extended_op_code == 0x06): # RLC (self.pc_state.HL)
                        tmp8 = self.memory.read(self.pc_state.HL);
                        self.memory.write(self.pc_state.HL, (tmp8 << 1) | ((tmp8 >> 7) & 0x1));
                        self.pc_state.Fstatus.value = FlagTables::getStatusOr(self.memory.read(self.pc_state.HL));
                        self.pc_state.Fstatus.status.C = (tmp8 >> 7) & 0x1; # bit-7 of src
                        self.pc_state.PC+=2;
                        cycles+=15;

                    # RRC r
                    elif ((extended_op_code == 0x08) or # RRC self.pc_state.B
                          (extended_op_code == 0x09) or # RRC C
                          (extended_op_code == 0x0A) or # RRC D
                          (extended_op_code == 0x0B) or # RRC E
                          (extended_op_code == 0x0C) or # RRC H
                          (extended_op_code == 0x0D) or # RRC L
                          (extended_op_code == 0x0F)): # RRC self.pc_state.A
                        r8 = r[tmp8 & 0x7];
                        *r8 = (*r8 >> 1) | ((*r8 & 0x1) << 7);
                        self.pc_state.Fstatus.value = FlagTables::getStatusOr(*r8);
                        self.pc_state.Fstatus.status.C = (*r8 >> 7) & 0x1; # bit-0 of src
                        self.pc_state.PC+=2;
                        cycles+=8;

                    elif (extended_op_code == 0x0E): # RRC (self.pc_state.HL)
                        tmp8 = self.memory.read(self.pc_state.HL);
                        self.memory.write(self.pc_state.HL,(tmp8 >> 1) | ((tmp8 & 0x1) << 7));
                        self.pc_state.Fstatus.value = FlagTables::getStatusOr(self.memory.read(self.pc_state.HL));
                        self.pc_state.Fstatus.status.C = tmp8 & 0x1; # bit-0 of src
                        self.pc_state.PC+=2;
                        cycles+=8;

                        # RL r
                    elif ((extended_op_code == 0x10) or # RL self.pc_state.B
                          (extended_op_code == 0x11) or # RL C
                          (extended_op_code == 0x12) or # RL D
                          (extended_op_code == 0x13) or # RL E
                          (extended_op_code == 0x14) or # RL H
                          (extended_op_code == 0x15) or # RL L
                          (extended_op_code == 0x17)): # RL self.pc_state.A
                        r8 = r[atPC[1] & 0x7];
                        tmp8 = *r8;
                        *r8 = (*r8 << 1) | (self.pc_state.Fstatus.status.C);
                        self.pc_state.Fstatus.value = FlagTables::getStatusOr(*r8);
                        self.pc_state.Fstatus.status.C = (tmp8 >> 7) & 0x1;
                        self.pc_state.PC+=2;
                        cycles+=8;

                        # RR r
                    elif ((extended_op_code == 0x18) or # RR self.pc_state.B
                          (extended_op_code == 0x19) or # RR C
                          (extended_op_code == 0x1A) or # RR D
                          (extended_op_code == 0x1B) or # RR E
                          (extended_op_code == 0x1C) or # RR H
                          (extended_op_code == 0x1D) or # RR L
                          (extended_op_code == 0x1F)): # RR self.pc_state.A
                        r8 = r[atPC[1] & 0x7];
                        tmp8 = *r8;
                        *r8 = (*r8 >> 1) | (self.pc_state.Fstatus.status.C << 7);
                        self.pc_state.Fstatus.value = FlagTables::getStatusOr(*r8);
                        self.pc_state.Fstatus.status.C = tmp8 & 0x1;
                        self.pc_state.PC+=2;
                        cycles+=8;

                    # SLA r
                    elif ((extended_op_code == 0x20) or # SLA self.pc_state.B
                          (extended_op_code == 0x21) or # SLA C
                          (extended_op_code == 0x22) or # SLA D
                          (extended_op_code == 0x23) or # SLA E
                          (extended_op_code == 0x24) or # SLA H
                          (extended_op_code == 0x25) or # SLA L
                          (extended_op_code == 0x27)): # SLA self.pc_state.A
                        tmp8 = (*r[atPC[1] & 0x7] >> 7) & 0x1;
                        *r[atPC[1] & 0x7] = 
                                *r[atPC[1]&0x7] << 1;
                        self.pc_state.Fstatus.value = FlagTables::getStatusOr(*r[atPC[1]&0x7]);
                        self.pc_state.Fstatus.status.C = tmp8;

                        self.pc_state.PC += 2;
                        cycles += 8;

                    elif (extended_op_code == 0x26): # SLA (self.pc_state.HL) 
                        tmp8 = (self.memory.read(self.pc_state.HL) >> 7) & 0x1;
                        self.memory.write(self.pc_state.HL, self.memory.read(self.pc_state.HL) << 1);
                        self.pc_state.Fstatus.value = FlagTables::getStatusOr(self.memory.read(self.pc_state.HL));
                        self.pc_state.Fstatus.status.C = tmp8;

                        self.pc_state.PC += 2;
                        cycles += 15;

                    # SRA r
                    elif ((extended_op_code == 0x28) or # SRA self.pc_state.B
                          (extended_op_code == 0x29) or # SRA C
                          (extended_op_code == 0x2A) or # SRA D
                          (extended_op_code == 0x2B) or # SRA E
                          (extended_op_code == 0x2C) or # SRA H
                          (extended_op_code == 0x2D) or # SRA L
                          (extended_op_code == 0x2F)): # SRA self.pc_state.A
                        r8 = r[atPC[1]&0x7];
                        tmp8 = *r8;
                        *r8 = (*r8 & 0x80) | ((*r8 >> 1) & 0x7F);

                        self.pc_state.Fstatus.value = FlagTables::getStatusOr(*r8);
                        self.pc_state.Fstatus.status.C = tmp8 & 0x1;

                        self.pc_state.PC += 2;
                        cycles += 8;

                    elif (extended_op_code == 0x2E): # SRA (self.pc_state.HL)
                        tmp8 = self.memory.read(self.pc_state.HL);
                        self.memory.write(self.pc_state.HL, (tmp8 & 0x80) | ((tmp8 >> 1) & 0x7F));

                        self.pc_state.Fstatus.value = FlagTables::getStatusOr(self.memory.read(self.pc_state.HL));
                        self.pc_state.Fstatus.status.C = tmp8 & 0x1;

                        self.pc_state.PC += 2;
                        cycles += 15;

                    # SLL r
                    elif ((extended_op_code == 0x30) or # SLL self.pc_state.B
                          (extended_op_code == 0x31) or # SLL C
                          (extended_op_code == 0x32) or # SLL D
                          (extended_op_code == 0x33) or # SLL E
                          (extended_op_code == 0x34) or # SLL H
                          (extended_op_code == 0x35) or # SLL L
                          (extended_op_code == 0x37)): # SLL self.pc_state.A
                        tmp8 = (*r[atPC[1] & 0x7] >> 7) & 0x1;
                        *r[atPC[1] & 0x7] = 
                                *r[atPC[1]&0x7] << 1 | 0x1;
                        self.pc_state.Fstatus.value = FlagTables::getStatusOr(*r[atPC[1]&0x7]);
                        self.pc_state.Fstatus.status.C = tmp8;

                        self.pc_state.PC += 2;
                        cycles += 8;

                    elif (extended_op_code == 0x36): # SLL (self.pc_state.HL) 
                        tmp8 = (self.memory.read(self.pc_state.HL) >> 7) & 0x1;
                        self.memory.write(self.pc_state.HL, self.memory.read(self.pc_state.HL) << 1 | 0x1);
                        self.pc_state.Fstatus.value = FlagTables::getStatusOr(self.memory.read(self.pc_state.HL));
                        self.pc_state.Fstatus.status.C = tmp8;

                        self.pc_state.PC += 2;
                        cycles += 15;

                    # SRL r
                    elif ((extended_op_code == 0x38) or # SRL self.pc_state.B
                          (extended_op_code == 0x39) or # SRL C
                          (extended_op_code == 0x3A) or # SRL D
                          (extended_op_code == 0x3B) or # SRL E
                          (extended_op_code == 0x3C) or # SRL H
                          (extended_op_code == 0x3D) or # SRL L
                          (extended_op_code == 0x3F)): # SRL self.pc_state.A
                        r8 = r[atPC[1]&0x7];
                        tmp8 = *r8;
                        *r8 = (*r8 >> 1) & 0x7F;

                        self.pc_state.Fstatus.value = FlagTables::getStatusOr(*r8);
                        self.pc_state.Fstatus.status.C = tmp8 & 0x1;

                        self.pc_state.PC += 2;
                        cycles += 8;

                    elif (extended_op_code == 0x3E): # SRL (self.pc_state.HL)
                        tmp8 = self.memory.read(self.pc_state.HL);
                        self.memory.write(self.pc_state.HL, (tmp8 >> 1) & 0x7F);

                        self.pc_state.Fstatus.value = FlagTables::getStatusOr(self.memory.read(self.pc_state.HL));
                        self.pc_state.Fstatus.status.C = tmp8 & 0x1;

                        self.pc_state.PC += 2;
                        cycles += 15;

                    else:
                        errors::warning("OP 0xCB n, value n unsupported");
                        return -1;

                # CALL Z, nn
            elif (op_code == 0xCC):
                self.pc_state.PC += 3;
                if (self.pc_state.Fstatus.status.Z == 1):
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCLow);
                    self.pc_state.PC = self.memory.read16(self.pc_state.PC-2);

                    cycles += 7;
                else:
                    cycles += 10;

                # CALL nn
            elif (op_code == 0xCD):
                self.pc_state.PC += 3;
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCLow);
                self.pc_state.PC = self.memory.read16(self.pc_state.PC-2);

                cycles += 17;

                # self.pc_state.ADC nn
            elif (op_code == 0xCE):
                self.pc_state.A = add8c(self.pc_state.A, atPC[1], self.pc_state.Fstatus.status.C);
                self.pc_state.PC+=2;
                cycles+=4;

                # RST 08h
            elif (op_code == 0xCF):
                self.pc_state.PC += 1
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCLow);

                self.pc_state.PC = 0x08;

                cycles += 11;

                # RET NC
            elif (op_code == 0xD0):
                if (self.pc_state.Fstatus.status.C == 0):
                    self.pc_state.PCLow  = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    self.pc_state.PCHigh = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    cycles += 11;
                else:
                    self.pc_state.PC += 1
                    cycles+=5;

                  # POP self.pc_state.DE
            elif (op_code == 0xD1):
                self.pc_state.E = self.memory.read(self.pc_state.SP);
                self.pc_state.SP += 1
                self.pc_state.D = self.memory.read(self.pc_state.SP);
                self.pc_state.SP += 1
                self.pc_state.PC += 1
                cycles += 10;

                # CALL NC, nn  
            elif (op_code == 0xD4):
                self.pc_state.PC += 3;
                if (self.pc_state.Fstatus.status.C == 0):
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCLow);
                    self.pc_state.PC = self.memory.read16(self.pc_state.PC-2);

                    cycles += 7;
                else:
                    cycles += 10;

                # PUSH self.pc_state.DE
            elif (op_code == 0xD5):
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.D);
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.E);
                self.pc_state.PC += 1

                cycles +=11;

                # SUB n
            elif (op_code == 0xD6):
                self.pc_state.F = FlagTables::getStatusSub(self.pc_state.A,atPC[1]);
                self.pc_state.A = self.pc_state.A - atPC[1];
                self.pc_state.PC += 2;
                cycles += 7;

                # RST 10h
            elif (op_code == 0xD7):
                self.pc_state.PC += 1
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCLow);

                self.pc_state.PC = 0x10;

                cycles += 11;
                
                # RET C
            elif (op_code == 0xD8):
                if (self.pc_state.Fstatus.status.C == 1):
                    self.pc_state.PCLow  = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    self.pc_state.PCHigh = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    cycles += 11;
                else:
                    self.pc_state.PC += 1
                    cycles+=5;

                # IN self.pc_state.A, (N)
            elif (op_code == 0xDB):
                self.pc_state.A = Ports::instance()->portRead(atPC[1]);
                self.pc_state.PC += 2;
                cycles += 11;

                # Call C, nn
            elif (op_code == 0xDC):
                self.pc_state.PC += 3;
                if (self.pc_state.Fstatus.status.C == 1):
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCLow);
                    self.pc_state.PC = self.memory.read16(self.pc_state.PC-2);
                    cycles += 17;
                else:
                    cycles += 10;

                # Sself.pc_state.BC n 
            elif (op_code == 0xDE):
                self.pc_state.A = sub8c(self.pc_state.A, atPC[1], self.pc_state.Fstatus.status.C);
                self.pc_state.PC+=2;
                cycles+=7;

                # RST 18h
            elif (op_code == 0xDF):
                self.pc_state.PC += 1
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCLow);

                self.pc_state.PC = 0x18;

                cycles += 11;

                # RET PO  
            elif (op_code == 0xE0):
                if (self.pc_state.Fstatus.status.PV == 0):
                    self.pc_state.PCLow  = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    self.pc_state.PCHigh = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    cycles += 11;
                else:
                    self.pc_state.PC += 1
                    cycles+=5;

                # POP self.pc_state.HL
            elif (op_code == 0xE1):
                self.pc_state.L = self.memory.read(self.pc_state.SP);
                self.pc_state.SP += 1
                self.pc_state.H = self.memory.read(self.pc_state.SP);
                self.pc_state.SP += 1

                self.pc_state.PC += 1

                cycles += 10;

                # JP PO, nn   Parity Odd 
            elif (op_code == 0xE2):
                if (self.pc_state.Fstatus.status.PV == 0):
                    self.pc_state.PC = self.memory.read16(self.pc_state.PC+1);
                else:
                    self.pc_state.PC += 3;

                cycles +=10;

                # EX (self.pc_state.SP), self.pc_state.HL
            elif (op_code == 0xE3):
                tmp8 = self.memory.read(self.pc_state.SP);
                self.memory.write(self.pc_state.SP, self.pc_state.L);
                self.pc_state.L = tmp8;
                tmp8 = self.memory.read(self.pc_state.SP+1);
                self.memory.write(self.pc_state.SP+1, self.pc_state.H);
                self.pc_state.H = tmp8;
                self.pc_state.PC += 1
                cycles += 19;

                # CALL PO, nn 
            elif (op_code == 0xE4):
                self.pc_state.PC += 3;
                if (self.pc_state.Fstatus.status.PV == 0):
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCLow);
                    self.pc_state.PC = self.memory.read16(self.pc_state.PC-2);
                    cycles += 7;

                cycles += 10;


                # PUSH self.pc_state.HL
            elif (op_code == 0xE5):
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.H);
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.L);
                self.pc_state.PC += 1

                cycles +=11;

                # RST 20h
            elif (op_code == 0xE7):
                self.pc_state.PC += 1
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCLow);

                self.pc_state.PC = 0x20;

                cycles += 11;

                # RET PE  
            elif (op_code == 0xE8):
                if (self.pc_state.Fstatus.status.PV == 1):
                    self.pc_state.PCLow  = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    self.pc_state.PCHigh = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    cycles += 11;
                else:
                    self.pc_state.PC += 1
                    cycles+=5;

                # Don't know how many cycles
                # LD self.pc_state.PC, self.pc_state.HL
            elif (op_code == 0xE9):
                self.pc_state.PC = self.pc_state.HL;
                cycles+=6;

                # JP PE, nn   Parity Even 
            elif (op_code == 0xEA):
                if (self.pc_state.Fstatus.status.PV == 1):
                    self.pc_state.PC = self.memory.read16(self.pc_state.PC+1);
                else:
                    self.pc_state.PC += 3;

                cycles +=10;

                # EX self.pc_state.DE, self.pc_state.HL
            elif (op_code == 0xEB):
                tmp16 = self.pc_state.DE;
                self.pc_state.DE = self.pc_state.HL;
                self.pc_state.HL = tmp16;
                self.pc_state.PC += 1
                cycles+=4;

                # CALL PE, nn
            elif (op_code == 0xEC):
                self.pc_state.PC += 3;
                if (self.pc_state.Fstatus.status.PV == 1):
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCLow);
                    self.pc_state.PC = self.memory.read16(self.pc_state.PC-2);
                    cycles += 7;

                cycles += 10;

                # XOR n
            elif (op_code == 0xEE): 
                self.pc_state.A = self.pc_state.A ^ atPC[1];
                self.pc_state.Fstatus.value = FlagTables::getStatusOr(self.pc_state.A);
                self.pc_state.PC+=2;
                cycles+=7;

                # RST 28h
            elif (op_code == 0xEF):
                self.pc_state.PC += 1
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCLow);

                self.pc_state.PC = 0x28;

                cycles += 11;

                # RET P, if Positive
            elif (op_code == 0xF0):
                if (self.pc_state.Fstatus.status.S == 0):
                    self.pc_state.PCLow  = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    self.pc_state.PCHigh = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    cycles += 11;
                else:
                    self.pc_state.PC += 1
                    cycles+=5;

                # POP self.pc_state.AF
            elif (op_code == 0xF1):
                self.pc_state.F = self.memory.read(self.pc_state.SP);
                self.pc_state.SP += 1
                self.pc_state.A = self.memory.read(self.pc_state.SP);
                self.pc_state.SP += 1

                self.pc_state.PC += 1

                cycles+=10;

                # JP P, nn    if Positive
            elif (op_code == 0xF2):
                if (self.pc_state.Fstatus.status.S == 0):
                    self.pc_state.PC = self.memory.read16(self.pc_state.PC+1);
                else:
                    self.pc_state.PC += 3;

                cycles +=10;

              # Disable interupts
              # DI
            elif (op_code == 0xF3):
                self.pc_state.IFF1 = 0;
                self.pc_state.IFF2 = 0;
                self.pc_state.PC += 1

                cycles+=4;

                # CALL P, nn  if Positive
            elif (op_code == 0xF4):
                self.pc_state.PC += 3;
                if (self.pc_state.Fstatus.status.S == 0):
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCLow);
                    self.pc_state.PC = self.memory.read16(self.pc_state.PC-2);
                    cycles += 7;

                cycles += 10;

                # PUSH self.pc_state.AF
            elif (op_code == 0xF5):
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.A);
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.F);
                self.pc_state.PC += 1

                cycles+=11;

                # OR n
            elif (op_code == 0xF6):
                self.pc_state.A = self.pc_state.A | atPC[1];
                self.pc_state.Fstatus.value = FlagTables::getStatusOr(self.pc_state.A);
                self.pc_state.PC += 2;
                cycles+=7;

                # RST 30h
            elif (op_code == 0xF7):
                self.pc_state.PC += 1
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCLow);

                self.pc_state.PC = 0x30;

                cycles += 11;

                # RET M  if Negative
            elif (op_code == 0xF8):
                if (self.pc_state.Fstatus.status.S == 1):
                    self.pc_state.PCLow  = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    self.pc_state.PCHigh = self.memory.read(self.pc_state.SP);
                    self.pc_state.SP += 1
                    cycles += 11;
                else:
                    self.pc_state.PC += 1
                    cycles+=5;

                # LD self.pc_state.SP, self.pc_state.HL
            elif (op_code == 0xF9):
                self.pc_state.SP = self.pc_state.HL;
                self.pc_state.PC += 1
                cycles+=6;

                # JP M, nn    if Negative
            elif (op_code == 0xFA):
                if (self.pc_state.Fstatus.status.S == 1):
                    self.pc_state.PC = self.memory.read16(self.pc_state.PC+1);
                else:
                    self.pc_state.PC += 3;

                cycles +=10;

                # Enable interupts
                # EI
            elif (op_code == 0xFB):
                self.pc_state.PC += 1

                # Process next instruction before enabling interupts
                step(false); # Single step, no loop

                self.pc_state.IFF1 = 1;
                self.pc_state.IFF2 = 1;
                cycles+=4;

                  # Check for any pending interupts
                if (interuptor->pollInterupts(cycles) == true):
                    interupt();


                # CALL M, nn  if Negative
            elif (op_code == 0xFC):
                self.pc_state.PC += 3;
                if (self.pc_state.Fstatus.status.S == 1):
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                    self.pc_state.SP -= 1
                    self.memory.write(self.pc_state.SP, self.pc_state.PCLow);
                    self.pc_state.PC = self.memory.read16(self.pc_state.PC-2);

                    cycles += 7;
                else:
                    cycles += 10;

                # RST 38h
            elif (op_code == 0xFF):
                self.pc_state.PC += 1
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                self.pc_state.SP -= 1
                self.memory.write(self.pc_state.SP, self.pc_state.PCLow);

                self.pc_state.PC = 0x38;

                cycles += 11;

            elif (op_code == 0xDD):
                # Temporary, until `all instructions are covered'
                instruction = 
                        InstructionStore::instance()->getExtendedDD(&atPC[1]);
                if (instruction):
                    cycles += instruction->execute(memory);
                else:
                    extended_op_code = atPC[1]

                    # LD self.pc_state.IX, nn
                    if (extended_op_code == 0x21):
                        self.pc_state.IX = self.memory.read16(self.pc_state.PC+2);
                        self.pc_state.PC += 4;

                        cycles +=20;

                        # LD (nn), self.pc_state.IX
                    elif (extended_op_code == 0x22):
                        self.memory.write(self.memory.read16(self.pc_state.PC+2), self.pc_state.IXLow);
                        self.memory.write(self.memory.read16(self.pc_state.PC+2)+1, self.pc_state.IXHigh);
                        self.pc_state.PC += 4;

                        cycles += 20;

                        # LD self.pc_state.IX, (nn)
                    elif (extended_op_code == 0x2A):
                        self.pc_state.IX = self.memory.read16(self.memory.read16(self.pc_state.PC+2));
                        self.pc_state.PC += 4;

                        cycles += 20;

                        # INC (self.pc_state.IX+d)
                    elif (extended_op_code == 0x34):
                        tmp16 = self.pc_state.IX + (int) (signed char) atPC[2];
                        self.memory.write(tmp16, self.memory.read(tmp16) + 1);
                        self.pc_state.F = (self.pc_state.F & Instruction::FLAG_MASK_INC8) | 
                    FlagTables::getStatusInc8(self.memory.read(tmp16));
                        self.pc_state.PC+=3;
                        cycles+=23;

                        # self.pc_state.DEC (self.pc_state.IX+d)
                    elif (extended_op_code == 0x35):
                        tmp16 = self.pc_state.IX + (int) (signed char) atPC[2];
                        self.memory.write(tmp16, self.memory.read(tmp16) - 1);
                        self.pc_state.F = (self.pc_state.F & Instruction::FLAG_MASK_DEC8) | FlagTables::getStatusDec8(self.memory.read(tmp16));
                        self.pc_state.PC+=3;
                        cycles+=23;

                        # LD (self.pc_state.IX + d), n
                    elif (extended_op_code == 0x36):
                        tmp16 = self.pc_state.IX + (int) (signed char) atPC[2];
                        self.memory.write(tmp16, atPC[3]);
                        self.pc_state.PC += 4;
                        cycles += 19;

                        # LD r, (self.pc_state.IX+e)
                    elif ((extended_op_code == 0x46) or
                          (extended_op_code == 0x4E) or
                          (extended_op_code == 0x56) or
                          (extended_op_code == 0x5E) or
                          (extended_op_code == 0x66) or
                          (extended_op_code == 0x6E) or
                          (extended_op_code == 0x7E)):
                        *r[(atPC[1] >> 3) & 0x7] = 
                                    self.memory.read(self.pc_state.IX + 
                                         (int) (signed char) atPC[2]);
                        self.pc_state.PC += 3;
                        cycles += 19;

                        # LD (self.pc_state.IX+d), r
                    elif ((extended_op_code == 0x70) or
                          (extended_op_code == 0x71) or
                          (extended_op_code == 0x72) or
                          (extended_op_code == 0x73) or
                          (extended_op_code == 0x74) or
                          (extended_op_code == 0x75) or
                          (extended_op_code == 0x77)):
                        self.memory.write(self.pc_state.IX + (int) (signed char) atPC[2],
                                      *r[atPC[1] & 0x7]); 
                        self.pc_state.PC += 3;
                        cycles += 19;

                        # self.pc_state.ADD self.pc_state.A,(self.pc_state.IX+d)
                    elif (extended_op_code == 0x86):
                        tmp8 = self.memory.read(self.pc_state.IX + 
                                         (int) (signed char) atPC[2]);
                        self.pc_state.Fstatus.value = FlagTables::getStatusAdd(self.pc_state.A, tmp8);
                        self.pc_state.A = self.pc_state.A + tmp8;
                        self.pc_state.PC += 3;
                        cycles += 19;

                        # self.pc_state.ADC (self.pc_state.IX + d)
                    elif (extended_op_code == 0x8E):
                        self.pc_state.A = add8c(self.pc_state.A, self.memory.read(self.pc_state.IX + (int) (signed char)
                                        atPC[2]), self.pc_state.Fstatus.status.C);
                        self.pc_state.PC+=3;
                        cycles+=19;

                        # SUB (self.pc_state.IX + d)
                    elif (extended_op_code == 0x96):
                        tmp8 = self.memory.read(self.pc_state.IX + 
                                         (int) (signed char) atPC[2]);
                        self.pc_state.F = FlagTables::getStatusSub(self.pc_state.A,tmp8);
                        self.pc_state.A = self.pc_state.A - tmp8;
                        self.pc_state.PC += 3;
                        cycles += 19;

                        # self.pc_state.AND (self.pc_state.IX + d)
                    elif (extended_op_code == 0xA6):
                        self.pc_state.A = self.pc_state.A & self.memory.read(self.pc_state.IX +
                                         (int) (signed char) atPC[2]);
                        self.pc_state.PC+=3;
                        self.pc_state.Fstatus.value = FlagTables::getStatusAnd(self.pc_state.A);

                        cycles+=19;

                        # XOR (self.pc_state.IX + d)
                    elif (extended_op_code == 0xAE):
                        self.pc_state.A = self.pc_state.A ^ self.memory.read(self.pc_state.IX +
                                         (int) (signed char) atPC[2]);
                        self.pc_state.PC+=3;
                        self.pc_state.Fstatus.value = FlagTables::getStatusOr(self.pc_state.A);

                        cycles += 19;

                        # OR (self.pc_state.IX + d)
                    elif (extended_op_code == 0xB6):
                        tmp8 = self.memory.read(self.pc_state.IX + 
                                         (int) (signed char) atPC[2]);
                        self.pc_state.A = self.pc_state.A | tmp8;
                        self.pc_state.Fstatus.value = FlagTables::getStatusOr(self.pc_state.A);
                        self.pc_state.PC += 3;
                        cycles += 19;

                        # CP (self.pc_state.IX + d)
                    elif (extended_op_code == 0xBE):
                        tmp8 = self.memory.read(self.pc_state.IX + 
                                         (int) (signed char) atPC[2]);
                        self.pc_state.F = FlagTables::getStatusSub(self.pc_state.A,tmp8);
                        self.pc_state.PC+=3;
                        cycles+=19;

                    # Probably should turn this into a lookup table
                    elif (extended_op_code == 0xCB):
                        tmp16 = self.pc_state.IX + (int) (signed char) atPC[2];
                        tmp8 = self.memory.read(tmp16);
                        t8 = atPC[3];

                        if ((t8 & 0xC7) == 0x46): # self.pc_state.BIT b, (self.pc_state.IX + d)
                            tmp8 = (tmp8 >> ((t8 & 0x38) >> 3)) & 0x1;
                            self.pc_state.Fstatus.status.Z = tmp8 ^ 0x1;;
                            self.pc_state.Fstatus.status.PV = FlagTables::calculateParity(tmp8);
                            self.pc_state.Fstatus.status.H = 1;
                            self.pc_state.Fstatus.status.N = 0;
                            self.pc_state.Fstatus.status.S = 0;
                        elif ((t8 & 0xC7) == 0x86): # RES b, (self.pc_state.IX + d)
                            tmp8 = tmp8 & ~(0x1 << ((t8 >> 3) & 0x7));
                            self.memory.write(tmp16,tmp8);
                        elif ((t8 & 0xC7) == 0xC6): # SET b, (self.pc_state.IX + d)
                            tmp8 = tmp8 | (0x1 << ((t8 >> 3) & 0x7));
                            self.memory.write(tmp16,tmp8);
                        else:
                            errors::unsupported("Instruction arg for 0xDD 0xCB");

                        self.pc_state.PC += 4;

                        cycles += 23;

                    # POP self.pc_state.IX
                    elif (extended_op_code == 0xE1):
                        self.pc_state.IXLow = self.memory.read(self.pc_state.SP);
                        self.pc_state.SP += 1
                        self.pc_state.IXHigh = self.memory.read(self.pc_state.SP);
                        self.pc_state.SP += 1
                        self.pc_state.PC += 2;
                        cycles += 14;

                        # EX (self.pc_state.SP), self.pc_state.IX
                    elif (extended_op_code == 0xE3):
                        tmp8 = self.memory.read(self.pc_state.SP);
                        self.memory.write(self.pc_state.SP, self.pc_state.IXLow);
                        self.pc_state.IXLow = tmp8;
                        tmp8 = self.memory.read(self.pc_state.SP+1);
                        self.memory.write(self.pc_state.SP+1, self.pc_state.IXHigh);
                        self.pc_state.IXHigh = tmp8;
                        self.pc_state.PC+=2;
                        cycles += 23;

                    # PUSH self.pc_state.IX
                    elif (extended_op_code == 0xE5):
                        self.pc_state.SP -= 1
                        self.memory.write(self.pc_state.SP, self.pc_state.IXHigh);
                        self.pc_state.SP -= 1
                        self.memory.write(self.pc_state.SP, self.pc_state.IXLow);
                        self.pc_state.PC += 2;

                        cycles +=15;

                        # Don't know how many cycles
                        # LD self.pc_state.PC, self.pc_state.IX
                    elif (extended_op_code == 0xE9):
                        self.pc_state.PC = self.pc_state.IX;
                        cycles+=6;

                    else:
        std::cout << "Unsupported op code DD " << std::hex << 
                                (int) atPC[1] << std::endl;
                        return -1;

            elif (op_code == 0xFD):
                # Temporary, until `all instructions are covered'
                instruction = 
                        InstructionStore::instance()->getExtendedFD(&atPC[1]);
                if (instruction):
                    cycles += instruction->execute(memory);
                else:
                    extended_op_code = atPC[1]

                    # LD self.pc_state.IY, (nn)
                    if (extended_op_code == 0x21):
                        self.pc_state.IY = self.memory.read16(self.pc_state.PC+2);
                        self.pc_state.PC += 4;
                        cycles += 20;

                        # LD (nn), self.pc_state.IY
                    elif (extended_op_code == 0x22):
                        self.memory.write(self.memory.read16(self.pc_state.PC+2), self.pc_state.IYLow);
                        self.memory.write(self.memory.read16(self.pc_state.PC+2)+1, self.pc_state.IYHigh);
                        self.pc_state.PC += 4;

                        cycles += 20;

                        # LD self.pc_state.IY, (nn)
                    elif (extended_op_code == 0x2A):
                        self.pc_state.IY = self.memory.read16(self.memory.read16(self.pc_state.PC+2));
                        self.pc_state.PC += 4;

                        cycles += 20;

                        # INC (self.pc_state.IY+d)
                    elif (extended_op_code == 0x34):
                        tmp16 = self.pc_state.IY + (int) (signed char) atPC[2];
                        self.memory.write(tmp16, self.memory.read(tmp16) + 1);
                        self.pc_state.F = (self.pc_state.F & Instruction::FLAG_MASK_INC8) | 
                    FlagTables::getStatusInc8(self.memory.read(tmp16));
                        self.pc_state.PC+=3;
                        cycles+=23;

                        # self.pc_state.DEC (self.pc_state.IY+d)
                    elif (extended_op_code == 0x35):
                        tmp16 = self.pc_state.IY + (int) (signed char) atPC[2];
                        self.memory.write(tmp16, self.memory.read(tmp16) - 1);
                        self.pc_state.F = (self.pc_state.F & Instruction::FLAG_MASK_DEC8) | FlagTables::getStatusDec8(self.memory.read(tmp16));
                        self.pc_state.PC+=3;
                        cycles+=23;

                        # LD (self.pc_state.IY + d), n
                    elif (extended_op_code == 0x36):
                        tmp16 = self.pc_state.IY + (int) (signed char) atPC[2];
                        self.memory.write(tmp16, atPC[3]);
                        self.pc_state.PC += 4;
                        cycles += 19;

                        # LD r, (self.pc_state.IY+e)
                    elif ((extended_op_code == 0x46) or
                          (extended_op_code == 0x4E) or
                          (extended_op_code == 0x56) or
                          (extended_op_code == 0x5E) or
                          (extended_op_code == 0x66) or
                          (extended_op_code == 0x6E) or
                          (extended_op_code == 0x7E)):
                        *r[(atPC[1] >> 3) & 0x7] = 
                                    self.memory.read(self.pc_state.IY + 
                                         (int) (signed char) atPC[2]);
                        self.pc_state.PC += 3;
                        cycles += 19;

                        # LD (self.pc_state.IY+d), r
                    elif ((extended_op_code == 0x70) or # LD (self.pc_state.IY+d), self.pc_state.B
                          (extended_op_code == 0x71) or # LD (self.pc_state.IY+d), C
                          (extended_op_code == 0x72) or # LD (self.pc_state.IY+d), D
                          (extended_op_code == 0x73) or # LD (self.pc_state.IY+d), E
                          (extended_op_code == 0x74) or # LD (self.pc_state.IY+d), H
                          (extended_op_code == 0x75) or # LD (self.pc_state.IY+d), L
                          (extended_op_code == 0x77)): # LD (self.pc_state.IY+d), self.pc_state.A
                        self.memory.write(self.pc_state.IY + (int) (signed char) atPC[2],
                                      *r[atPC[1] & 0x7]); 
                        self.pc_state.PC += 3;
                        cycles += 19;

                        # self.pc_state.ADD self.pc_state.A,(self.pc_state.IY+d)
                    elif (extended_op_code == 0x86):
                        tmp8 = self.memory.read(self.pc_state.IY + 
                                         (int) (signed char) atPC[2]);
                        self.pc_state.Fstatus.value = FlagTables::getStatusAdd(self.pc_state.A,tmp8);
                        self.pc_state.A = self.pc_state.A + tmp8;
                        self.pc_state.PC += 3;
                        cycles += 19;

                        # self.pc_state.ADC (self.pc_state.IY + d)
                    elif (extended_op_code == 0x8E):
                        self.pc_state.A = add8c(self.pc_state.A, self.memory.read(self.pc_state.IY + (int) (signed char)
                                        atPC[2]), self.pc_state.Fstatus.status.C);
                        self.pc_state.PC+=3;
                        cycles+=19;

                        # SUB (self.pc_state.IY + d)
                    elif (extended_op_code == 0x96):
                        tmp8 = self.memory.read(self.pc_state.IY + 
                                         (int) (signed char) atPC[2]);
                        self.pc_state.F = FlagTables::getStatusSub(self.pc_state.A,tmp8);
                        self.pc_state.A = self.pc_state.A - tmp8;
                        self.pc_state.PC += 3;
                        cycles += 19;

                        # self.pc_state.AND (self.pc_state.IY + d)
                    elif (extended_op_code == 0xA6):
                        self.pc_state.A = self.pc_state.A & self.memory.read(self.pc_state.IY +
                                         (int) (signed char) atPC[2]);
                        self.pc_state.PC+=3;
                        self.pc_state.Fstatus.value = FlagTables::getStatusAnd(self.pc_state.A);

                        cycles+=19;

                        # XOR (self.pc_state.IY + d)
                    elif (extended_op_code == 0xAE):
                        self.pc_state.A = self.pc_state.A ^ self.memory.read(self.pc_state.IY +
                                         (int) (signed char) atPC[2]);
                        self.pc_state.PC+=3;
                        self.pc_state.Fstatus.value = FlagTables::getStatusOr(self.pc_state.A);

                        cycles += 19;

                        # OR (self.pc_state.IY + d)
                    elif (extended_op_code == 0xB6):
                        tmp8 = self.memory.read(self.pc_state.IY + 
                                         (int) (signed char) atPC[2]);
                        self.pc_state.A = self.pc_state.A | tmp8;
                        self.pc_state.Fstatus.value = FlagTables::getStatusOr(self.pc_state.A);
                        self.pc_state.PC += 3;
                        cycles += 19;

                        # CP (self.pc_state.IY + d)
                    elif (extended_op_code == 0xBE):
                        tmp8 = self.memory.read(self.pc_state.IY + 
                                         (int) (signed char) atPC[2]);
                        self.pc_state.F = FlagTables::getStatusSub(self.pc_state.A,tmp8);
                        self.pc_state.PC+=3;
                        cycles+=19;

                    # Probably should turn this into a lookup table
                    elif (extended_op_code == 0xCB):
                        tmp16 = self.pc_state.IY + (int) (signed char) atPC[2];
                        tmp8 = self.memory.read(tmp16);
                        t8 = atPC[3];

                        if ((t8 & 0xC7) == 0x46): # self.pc_state.BIT b, (self.pc_state.IY + d)
                            tmp8 = (tmp8 >> ((t8 & 0x38) >> 3)) & 0x1;
                            self.pc_state.Fstatus.status.Z = tmp8 ^ 0x1;;
                            self.pc_state.Fstatus.status.PV = FlagTables::calculateParity(tmp8);
                            self.pc_state.Fstatus.status.H = 1;
                            self.pc_state.Fstatus.status.N = 0;
                            self.pc_state.Fstatus.status.S = 0;
                        elif ((t8 & 0xC7) == 0x86): # RES b, (self.pc_state.IY + d)
                            tmp8 = tmp8 & ~(0x1 << ((t8 >> 3) & 0x7));
                            self.memory.write(tmp16,tmp8);
                        elif ((t8 & 0xC7) == 0xC6): # SET b, (self.pc_state.IY + d)
                            tmp8 = tmp8 | (0x1 << ((t8 >> 3) & 0x7));
                            self.memory.write(tmp16,tmp8);
                        else:
                            errors::unsupported("Instruction arg for 0xFD 0xCB");

                        self.pc_state.PC += 4;

                        cycles += 23;
                       
                    # POP self.pc_state.IY
                    elif (extended_op_code == 0xE1):
                        self.pc_state.IYLow = self.memory.read(self.pc_state.SP);
                        self.pc_state.SP += 1
                        self.pc_state.IYHigh = self.memory.read(self.pc_state.SP);
                        self.pc_state.SP += 1
                        self.pc_state.PC += 2;
                        cycles += 14;

                        # EX (self.pc_state.SP), self.pc_state.IY
                    elif (extended_op_code == 0xE3):
                        tmp8 = self.memory.read(self.pc_state.SP);
                        self.memory.write(self.pc_state.SP, self.pc_state.IYLow);
                        self.pc_state.IYLow = tmp8;
                        tmp8 = self.memory.read(self.pc_state.SP+1);
                        self.memory.write(self.pc_state.SP+1, self.pc_state.IYHigh);
                        self.pc_state.IYHigh = tmp8;
                        self.pc_state.PC+=2;
                        cycles += 23;

                    # PUSH self.pc_state.IY
                    elif (extended_op_code == 0xE5):
                        self.pc_state.SP -= 1
                        self.memory.write(self.pc_state.SP, self.pc_state.IYHigh);
                        self.pc_state.SP -= 1
                        self.memory.write(self.pc_state.SP, self.pc_state.IYLow);
                        self.pc_state.PC += 2;

                        cycles +=15;

                        # Don't know how many cycles
                        # LD self.pc_state.PC, self.pc_state.IY
                    elif (extended_op_code == 0xE9):
                        self.pc_state.PC = self.pc_state.IY;
                        cycles+=6;

                    else:
        std::cout << "Unsupported op code FD " <<
                                (int) atPC[1] << std::endl;
                        return -1;

              # Extended op_code
            elif (op_code == 0xED):
                # Temporary, until `all instructions are covered'
                instruction = InstructionStore::instance()->getExtendedED(&atPC[1]);
                if (instruction):
                    cycles += instruction->execute(memory);
                else:
                    extended_op_code = atPC[1]
                      # IN r, (C)
                    if ((extended_op_code == 0x40) or
                        (extended_op_code == 0x48) or
                        (extended_op_code == 0x50) or
                        (extended_op_code == 0x58) or
                        (extended_op_code == 0x60) or
                        (extended_op_code == 0x68) or
                        (extended_op_code == 0x78)):
                        *r[(atPC[1] >> 3) & 0x7] = Ports::instance()->portRead(self.pc_state.C);
                        self.pc_state.PC += 2;
                        cycles += 12;

                      # OUT (C), r
                    elif ((extended_op_code == 0x41) or # OUT (C), self.pc_state.B
                          (extended_op_code == 0x49) or # OUT (C), C
                          (extended_op_code == 0x51) or # OUT (C), D
                          (extended_op_code == 0x59) or # OUT (C), E
                          (extended_op_code == 0x61) or # OUT (C), H
                          (extended_op_code == 0x69) or # OUT (C), L
                          (extended_op_code == 0x79)): # OUT (C), self.pc_state.A
                        Ports::instance()->portWrite(self.pc_state.C, *r[(atPC[1] >> 3) & 0x7]);
                        self.pc_state.PC += 2;
                        cycles +=3;

                      # Sself.pc_state.BC self.pc_state.HL, self.pc_state.BC
                    elif (extended_op_code == 0x42):
                        self.pc_state.HL = sub16c(self.pc_state.HL, self.pc_state.BC, self.pc_state.Fstatus.status.C);

                        self.pc_state.PC += 2;
                        cycles += 15;

                        # LD (nn), self.pc_state.BC
                    elif (extended_op_code == 0x43):
                        self.memory.write(self.memory.read16(self.pc_state.PC+2), self.pc_state.C);
                        self.memory.write(self.memory.read16(self.pc_state.PC+2)+1, self.pc_state.B);
                        self.pc_state.PC += 4;

                        cycles += 20;

                      # NEG
                    elif (extended_op_code == 0x44):
                        self.pc_state.Fstatus.value = FlagTables::getStatusSub(0,self.pc_state.A);
                        self.pc_state.A = -self.pc_state.A;
                        self.pc_state.PC += 2;
                        cycles+=8;

                      # LD I, self.pc_state.A
                    elif (extended_op_code == 0x47):
                        self.pc_state.I = self.pc_state.A;
                        self.pc_state.PC += 2;
                        cycles += 9;

                        # self.pc_state.ADC self.pc_state.HL, self.pc_state.BC
                    elif (extended_op_code == 0x4A):
                        self.pc_state.HL = add16c(self.pc_state.HL, self.pc_state.BC, self.pc_state.Fstatus.status.C);
                        self.pc_state.PC+=2;
                        cycles+=15;

                        # Load 16-bit self.pc_state.BC register
                        # LD self.pc_state.BC, (nn)
                    elif (extended_op_code == 0x4B):
                        self.pc_state.BC = self.memory.read16(self.memory.read16(self.pc_state.PC+2)); 
                        self.pc_state.PC += 4;
                        cycles += 20;

                        # Fself.pc_state.IXME, should check, since there is only one
                        # interupting device, this is the same as normal ret
                        # RETI
                    elif (extended_op_code == 0x4D): 
                        self.pc_state.PCLow  = self.memory.read(self.pc_state.SP);
                        self.pc_state.SP += 1
                        self.pc_state.PCHigh = self.memory.read(self.pc_state.SP);
                        self.pc_state.SP += 1

                        cycles += 14;
                                
                      # Sself.pc_state.BC self.pc_state.HL, self.pc_state.DE
                    elif (extended_op_code == 0x52):
                        self.pc_state.HL = sub16c(self.pc_state.HL, self.pc_state.DE, self.pc_state.Fstatus.status.C);

                        self.pc_state.PC += 2;
                        cycles += 4;

                        # LD (nn), self.pc_state.DE
                    elif (extended_op_code == 0x53):
                        self.memory.write(self.memory.read16(self.pc_state.PC+2), self.pc_state.E);
                        self.memory.write(self.memory.read16(self.pc_state.PC+2)+1, self.pc_state.D);
                        self.pc_state.PC += 4;

                        cycles += 20;

                        # self.pc_state.IM 1
                    elif (extended_op_code == 0x56):
                        self.pc_state.PC+=2;
                        self.pc_state.IM = 1;

                        cycles += 2;

                        # LD self.pc_state.A, I
                    elif (extended_op_code == 0x57):
                        self.pc_state.A = self.pc_state.I;
                        self.pc_state.Fstatus.status.N = 0;
                        self.pc_state.Fstatus.status.H = 0;
                        self.pc_state.Fstatus.status.PV = self.pc_state.IFF2;
                        self.pc_state.Fstatus.status.S = (self.pc_state.A & 0x80) >> 7;
                        self.pc_state.Fstatus.status.Z = (self.pc_state.A == 0)?1:0;

                        self.pc_state.PC += 2;
                        cycles += 9;

                        # self.pc_state.ADC self.pc_state.HL, self.pc_state.DE
                    elif (extended_op_code == 0x5A):
                        self.pc_state.HL = add16c(self.pc_state.HL, self.pc_state.DE, self.pc_state.Fstatus.status.C);
                        self.pc_state.PC+=2;
                        cycles+=4;

                        # LD self.pc_state.DE, (nn)    
                    elif (extended_op_code == 0x5B):
                        self.pc_state.DE = self.memory.read16(self.memory.read16(self.pc_state.PC+2));
                        self.pc_state.PC += 4;
                        cycles += 20;

                        # Fself.pc_state.IXME, not sure about this
                        # LD self.pc_state.A, R
                    elif (extended_op_code == 0x5F):
                        self.pc_state.R =  (self.pc_state.R & 0x80) | ((cycles + self.pc_state.R + 1) & 0x7F);
                        self.pc_state.A = self.pc_state.R;
                        self.pc_state.Fstatus.status.N = 0;
                        self.pc_state.Fstatus.status.H = 0;
                        self.pc_state.Fstatus.status.PV = self.pc_state.IFF2;
                        self.pc_state.Fstatus.status.S = (self.pc_state.A & 0x80) >> 7;
                        self.pc_state.Fstatus.status.Z = (self.pc_state.A == 0)?1:0;

                        self.pc_state.PC += 2;
                        cycles += 9;

                        # Fself.pc_state.IXME, can't find existance of this instruction
                        # LD (nn), self.pc_state.HL
                    elif (extended_op_code == 0x63):
                        self.memory.write(self.memory.read16(self.pc_state.PC+2), self.pc_state.L);
                        self.memory.write(self.memory.read16(self.pc_state.PC+2)+1, self.pc_state.H);
                        self.pc_state.PC += 4;

                        cycles += 16;

                        # RRD, wacky instruction
                    elif (extended_op_code == 0x67):
                        tmp8 = self.pc_state.A;
                        self.pc_state.A = (self.pc_state.A & 0xF0) | (self.memory.read(self.pc_state.HL) & 0xF);
                        self.memory.write(self.pc_state.HL, 
                               ((self.memory.read(self.pc_state.HL) >> 4) & 0xF) | 
                               ((tmp8 << 4) & 0xF0));

                        tmp8 = self.pc_state.Fstatus.status.C;
                        self.pc_state.Fstatus.value = FlagTables::getStatusOr(self.pc_state.A);
                        self.pc_state.Fstatus.status.C = tmp8;

                        self.pc_state.PC+=2;
                        cycles += 18;

                        # self.pc_state.ADC self.pc_state.HL, self.pc_state.HL
                    elif (extended_op_code == 0x6A):
                        self.pc_state.HL = add16c(self.pc_state.HL, self.pc_state.HL, self.pc_state.Fstatus.status.C);
                        self.pc_state.PC+=2;
                        cycles+=4;

                        # Fself.pc_state.IXME, not sure about the existance of this instruction
                        # LD self.pc_state.HL, (nn)
                    elif (extended_op_code == 0x6B):
                        self.pc_state.HL = self.memory.read16(self.memory.read16(self.pc_state.PC+2));
                        self.pc_state.PC += 4;

                        cycles += 20;

                        # LD (nn), self.pc_state.SP
                    elif (extended_op_code == 0x73):
                        self.memory.write(self.memory.read16(self.pc_state.PC+2), self.pc_state.SPLow);
                        self.memory.write(self.memory.read16(self.pc_state.PC+2)+1, self.pc_state.SPHigh);
                        self.pc_state.PC += 4;

                        cycles += 6;

                        # self.pc_state.ADC self.pc_state.HL, self.pc_state.SP
                    elif (extended_op_code == 0x7A):
                        self.pc_state.HL = add16c(self.pc_state.HL, self.pc_state.SP, self.pc_state.Fstatus.status.C);
                        self.pc_state.PC+=2;
                        cycles+=15;

                        # Load 16-bit self.pc_state.BC register
                        # LD self.pc_state.SP, (nn)
                    elif (extended_op_code == 0x7B):
                        self.pc_state.SP = self.memory.read16(self.memory.read16(self.pc_state.PC+2)); 
                        self.pc_state.PC += 4;
                        cycles += 20;

                        # LDI
                    elif (extended_op_code == 0xA0):
                        self.memory.write(self.pc_state.DE, self.memory.read(self.pc_state.HL));
                        self.pc_state.DE += 1
                        self.pc_state.HL += 1
                        self.pc_state.BC -= 1
                        self.pc_state.Fstatus.status.PV = (self.pc_state.BC != 0) ? 1:0;
                        self.pc_state.Fstatus.status.H = 0;
                        self.pc_state.Fstatus.status.N = 0;
                        self.pc_state.PC += 2;

                        cycles += 16;

                        # CPI
                    elif (extended_op_code == 0xA1):
                        self.pc_state.F = FlagTables::getStatusSub(self.pc_state.A,self.memory.read(self.pc_state.HL));
                        self.pc_state.HL += 1
                        self.pc_state.BC -= 1
                        self.pc_state.Fstatus.status.PV = (self.pc_state.BC != 0) ? 1:0;
                        self.pc_state.PC += 2;
                        cycles += 16;

                        # INI
                    elif (extended_op_code == 0xA2):
                        self.pc_state.B -= 1
                        self.memory.write(self.pc_state.HL, Ports::instance()->portRead(self.pc_state.C));
                        self.pc_state.HL += 1
                        self.pc_state.Fstatus.status.N = 1;
                        if (self.pc_state.B == 0):
                            self.pc_state.Fstatus.status.Z = 1;
                        else:
                            self.pc_state.Fstatus.status.Z = 0;

                        self.pc_state.PC += 2;
                        cycles += 16;

                        # OUTI
                    elif (extended_op_code == 0xA3):
                        self.pc_state.B -= 1
                        Ports::instance()->portWrite(self.pc_state.C, self.memory.read(self.pc_state.HL));
                        self.pc_state.HL += 1
                        self.pc_state.Fstatus.status.Z = (self.pc_state.B == 0) ? 1:0;
                        self.pc_state.Fstatus.status.N = 1;
                        self.pc_state.PC += 2;
                        cycles += 16;

                        # OUTD
                    elif (extended_op_code == 0xAB):
                        self.pc_state.B -= 1
                        Ports::instance()->portWrite(self.pc_state.C, self.memory.read(self.pc_state.HL));
                        self.pc_state.HL -= 1
                        self.pc_state.Fstatus.status.Z = (self.pc_state.B == 0) ? 1:0;
                        self.pc_state.Fstatus.status.N = 1;
                        self.pc_state.PC += 2;
                        cycles += 16;

                        # LDIR
                    elif (extended_op_code == 0xB0):
                        if (self.pc_state.BC >= 4):
                            self.memory.write(self.pc_state.DE, self.pc_state.HL, 4);
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

                        self.pc_state.Fstatus.status.H = 0;
                        self.pc_state.Fstatus.status.PV = 0;
                        self.pc_state.Fstatus.status.N = 1; # hmmm, not sure
                        if (self.pc_state.BC == 0):
                            self.pc_state.Fstatus.status.N = 0;
                            self.pc_state.PC += 2;
                            cycles -=5;

                        # CPIR
                    elif (extended_op_code == 0xB1):
                        self.pc_state.BC -= 1
                        tmp8 = self.pc_state.Fstatus.status.C;
                        self.pc_state.F = FlagTables::getStatusSub(self.pc_state.A,self.memory.read(self.pc_state.HL));
                        self.pc_state.HL += 1
                        self.pc_state.Fstatus.status.C = tmp8; 

                        if ((self.pc_state.BC == 0)||(self.pc_state.Fstatus.status.Z == 1)):
                            self.pc_state.Fstatus.status.PV = 0; 
                            self.pc_state.PC += 2;
                            cycles += 16;
                        else:
                            self.pc_state.Fstatus.status.PV = 1; 
                            cycles += 21;

                        # Should speed this function up a bit
                        # Flags match emulator, not z80 document
                        # OTIR (port)
                    elif (extended_op_code == 0xB3):
                        if (self.pc_state.B >= 8):
                            self.pc_state.B -= 8;
                            Ports::instance()->portWrite(self.pc_state.C, self.memory.read(self.pc_state.HL,8), 8);
                            self.pc_state.HL+= 8;
                            cycles += 168;
                        else:
                            self.pc_state.B -= 1
                            Ports::instance()->portWrite(self.pc_state.C, self.memory.read(self.pc_state.HL));
                            self.pc_state.HL += 1
                            cycles += 21;
                        self.pc_state.Fstatus.status.S = 0; # Unknown
                        self.pc_state.Fstatus.status.H = 0; # Unknown
                        self.pc_state.Fstatus.status.PV = 0; # Unknown
                        self.pc_state.Fstatus.status.N = 1;
                        self.pc_state.Fstatus.status.Z = 0;
                        if (self.pc_state.B == 0):
                            self.pc_state.Fstatus.status.Z = 1;
                            self.pc_state.PC += 2;
                            cycles -= 5;

                        # LDDR
                    elif (extended_op_code == 0xB8):
                        self.memory.write(self.pc_state.DE, self.memory.read(self.pc_state.HL));
                        self.pc_state.DE -= 1
                        self.pc_state.HL -= 1
                        self.pc_state.BC -= 1
                        if (self.pc_state.BC == 0):
                            self.pc_state.PC += 2;
                            cycles += 16;
                            self.pc_state.Fstatus.status.N = 0;
                            self.pc_state.Fstatus.status.H = 0;
                            self.pc_state.Fstatus.status.PV = 0;
                        else:
                            cycles += 21;


                    else:
                        std::cout << "Unsupported op_code 0xED 0x" << 
                        std::hex << (int) atPC[1] << std::endl;
                        return -1;

            else:
        std::cout << "Unsupported op_code 0x" << 
                        std::hex << (int) atPC[0] << std::endl;
                return -1;

    return 0

    def populate_instruction_map(self):
        self.instruction_lookup[0xC3] = instructions.JumpInstruction(self.clocks, self.pc_state, self.memory)
        pass
