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

      atPC = memory->readMulti(cpu_state->PC);
      std::cout << std::hex << (int) atPC[0] << " " << (int) cpu_state->PC << std::endl;

      # This will raise an exception for unsupported op_code
      if op_code in self.instruction_lookup:
        cycles += self.instruction_lookup[op_code].execute()
      else:
        op_code = atPC[0]
                # EX cpu_state->AF, cpu_state->AF'
            if (op_code == 0x08):
                tmp16 = cpu_state->AF;
                cpu_state->AF = cpu_state->AF_;
                cpu_state->AF_ = tmp16;

                cpu_state->PC++;
                cycles+=4;

                # LD (cpu_state->DE), cpu_state->A
            elif (op_code == 0x12):
                memory->write(cpu_state->DE, cpu_state->A);
                cpu_state->PC++;
                cycles += 7;

                # RLA
            elif (op_code == 0x17):
                tmp8 = cpu_state->A;
                cpu_state->A = (cpu_state->A << 1) | (cpu_state->Fstatus.status.C);
                cpu_state->Fstatus.status.C = (tmp8 & 0x80) >> 7;
                cpu_state->Fstatus.status.H = 0;
                cpu_state->Fstatus.status.N = 0;
                cpu_state->PC++;
                cycles+=4;

                # Relative jump
                # JR e
            elif (op_code == 0x18):
                cpu_state->PC += (int) (signed char) atPC[1];
                cpu_state->PC += 2;

                cycles += 12;

                # RRA
            elif (op_code == 0x1F):
                tmp8 = cpu_state->A;
                cpu_state->A = (cpu_state->A >> 1) | (cpu_state->Fstatus.status.C << 7);
                cpu_state->Fstatus.status.C = tmp8 & 0x1;
                cpu_state->Fstatus.status.H = 0;
                cpu_state->Fstatus.status.N = 0;
                cpu_state->PC++;
                cycles+=4;

                # LD (nn), cpu_state->HL
            elif (op_code == 0x22):
                memory->write(memory->read16(cpu_state->PC+1), cpu_state->L);
                memory->write(memory->read16(cpu_state->PC+1)+1, cpu_state->H);
                cpu_state->PC += 3;

                cycles += 16;

                # Really need to put this into a table
            elif (op_code == 0x27):
                if (cpu_state->Fstatus.status.N == 0): # cpu_state->Addition instruction
                    calculateDAAAdd();
                else: # Subtraction instruction
                    calculateDAASub();
                cpu_state->PC++;
                cycles+=4;

                # CPL
            elif (op_code == 0x2F):
                cpu_state->Fstatus.status.H = 1;
                cpu_state->Fstatus.status.N = 1;
                cpu_state->A ^= 0xFF;
                cpu_state->PC++;

                cycles+=4;

                # JR NC, e
            elif (op_code == 0x30):
                if (cpu_state->Fstatus.status.C == 0):
                    cpu_state->PC += (int) (signed char) atPC[1];
                    cycles+=5;

                cpu_state->PC += 2;
                cycles += 7;


                # LD (nn), cpu_state->A
            elif (op_code == 0x32):
                memory->write(memory->read16(cpu_state->PC+1), cpu_state->A);
                cpu_state->PC +=3;

                cycles += 13;

                # SCF
            elif (op_code == 0x37):
                 cpu_state->Fstatus.status.H = 0;
                 cpu_state->Fstatus.status.N = 0;
                 cpu_state->Fstatus.status.C = 1;
                 cpu_state->PC++;
                 cycles += 4;

                # JR C, e
            elif (op_code == 0x38):
                if (cpu_state->Fstatus.status.C == 1):
                    cpu_state->PC += (int) (signed char) atPC[1];
                    cycles+=5;

                cpu_state->PC += 2;
                cycles += 7;

                # CCF
            elif (op_code == 0x3F):
                cpu_state->Fstatus.status.H = cpu_state->Fstatus.status.C;
                cpu_state->Fstatus.status.N = 0;
                cpu_state->Fstatus.status.C = 1-cpu_state->Fstatus.status.C; #Invert carry flag
                cpu_state->PC++;
                cycles += 4;

            elif (op_code == 0x76): # LD (cpu_state->HL), (cpu_state->HL)
                cpu_state->PC++;
                cycles += 7;

            elif (op_code == 0x86): # cpu_state->ADD (cpu_state->HL) 
                cpu_state->Fstatus.value = FlagTables::getStatusAdd(cpu_state->A,memory->read(cpu_state->HL));
                cpu_state->A = cpu_state->A + memory->read(cpu_state->HL);
                cpu_state->PC++;
                cycles+=7;

                # cpu_state->ADC r
            elif (op_code == 0x88): # cpu_state->ADC cpu_state->B
            elif (op_code == 0x89): # cpu_state->ADC C
            elif (op_code == 0x8A): # cpu_state->ADC D
            elif (op_code == 0x8B): # cpu_state->ADC E
            elif (op_code == 0x8C): # cpu_state->ADC H
            elif (op_code == 0x8D): # cpu_state->ADC L
            elif (op_code == 0x8F): # cpu_state->ADC cpu_state->A
                cpu_state->A = add8c(cpu_state->A, *r[atPC[0]&0x7], cpu_state->Fstatus.status.C);
                cpu_state->PC++;
                cycles+=4;

                # cpu_state->ADC (cpu_state->HL)
            elif (op_code == 0x8E):
                cpu_state->A = add8c(cpu_state->A, memory->read(cpu_state->HL), cpu_state->Fstatus.status.C);
                cpu_state->PC++;
                cycles+=7;

                # SUB r
            elif (op_code == 0x90): # SUB cpu_state->B
            elif (op_code == 0x91): # SUB C
            elif (op_code == 0x92): # SUB D
            elif (op_code == 0x93): # SUB E
            elif (op_code == 0x94): # SUB H
            elif (op_code == 0x95): # SUB L
            elif (op_code == 0x97): # SUB cpu_state->A
                cpu_state->F = FlagTables::getStatusSub(cpu_state->A,*r[atPC[0] & 0x7]);
                cpu_state->A = cpu_state->A - *r[atPC[0] & 0x7];
                cpu_state->PC++;
                cycles+=4;

                # SUB (cpu_state->HL) 
            elif (op_code == 0x96):
                cpu_state->F = FlagTables::getStatusSub(cpu_state->A,memory->read(cpu_state->HL));
                cpu_state->A = cpu_state->A - memory->read(cpu_state->HL);
                cpu_state->PC++;
                cycles+=7;

                # Scpu_state->BC r
            elif (op_code == 0x98): # Scpu_state->BC cpu_state->B
            elif (op_code == 0x99): # Scpu_state->BC C
            elif (op_code == 0x9A): # Scpu_state->BC D
            elif (op_code == 0x9B): # Scpu_state->BC E
            elif (op_code == 0x9C): # Scpu_state->BC H
            elif (op_code == 0x9D): # Scpu_state->BC L
            elif (op_code == 0x9F): # Scpu_state->BC cpu_state->A
                cpu_state->A = sub8c(cpu_state->A, *r[atPC[0]&0x7], cpu_state->Fstatus.status.C);
                cpu_state->PC++;
                cycles+=4;

                # Scpu_state->BC (cpu_state->HL)
            elif (op_code == 0x9E):
                cpu_state->A = sub8c(cpu_state->A, memory->read(cpu_state->HL), cpu_state->Fstatus.status.C);
                cpu_state->PC++;
                cycles+=7;

                # cpu_state->AND r
            elif (op_code == 0xA0): # cpu_state->AND cpu_state->B
            elif (op_code == 0xA1): # cpu_state->AND C
            elif (op_code == 0xA2): # cpu_state->AND D
            elif (op_code == 0xA3): # cpu_state->AND E
            elif (op_code == 0xA4): # cpu_state->AND H
            elif (op_code == 0xA5): # cpu_state->AND L
                cpu_state->A = cpu_state->A & *r[atPC[0]&0x7];
                cpu_state->PC++;
                cpu_state->Fstatus.value = FlagTables::getStatusAnd(cpu_state->A);

                cycles+=4;

                # cpu_state->AND (cpu_state->HL)
            elif (op_code == 0xA6):
                cpu_state->A = cpu_state->A & memory->read(cpu_state->HL);
                cpu_state->PC++;
                cpu_state->Fstatus.value = FlagTables::getStatusAnd(cpu_state->A);

                cycles+=7;

            elif (op_code == 0xA7): # cpu_state->AND cpu_state->A
                cpu_state->PC++;
                cpu_state->Fstatus.value = FlagTables::getStatusAnd(cpu_state->A);
                cycles+=4;

                # XOR (cpu_state->HL)
            elif (op_code == 0xAE):
                cpu_state->A = cpu_state->A ^ memory->read(cpu_state->HL);
                cpu_state->PC++;
                cpu_state->Fstatus.value = FlagTables::getStatusOr(cpu_state->A);

                cycles += 7;

                # OR (cpu_state->HL)
            elif (op_code == 0xB6):
                cpu_state->A = cpu_state->A | memory->read(cpu_state->HL);
                cpu_state->PC++;
                cpu_state->Fstatus.value = FlagTables::getStatusOr(cpu_state->A);

                cycles += 7;

                # CP (cpu_state->HL) 
            elif (op_code == 0xBE):
                cpu_state->F = FlagTables::getStatusSub(cpu_state->A,memory->read(cpu_state->HL));
                cpu_state->PC++;

                cycles+=7;

                # RET NZ
            elif (op_code == 0xC0):
                if (cpu_state->Fstatus.status.Z == 0):
                    cpu_state->PCLow  = memory->read(cpu_state->SP++);
                    cpu_state->PCHigh = memory->read(cpu_state->SP++);
                    cycles += 11;
                else:
                    cpu_state->PC++;
                    cycles+=5;

                # POP cpu_state->BC
            elif (op_code == 0xC1):
                cpu_state->C = memory->read(cpu_state->SP++);
                cpu_state->B = memory->read(cpu_state->SP++);

                cpu_state->PC++;

                cycles += 10;

                # JP NZ, nn
            elif (op_code == 0xC2):
                if (cpu_state->Fstatus.status.Z == 0):
                    cpu_state->PC = memory->read16(cpu_state->PC+1);
                else:
                    cpu_state->PC += 3;

                cycles += 10;

                # JP nn
            elif (op_code == 0xC3):
                cpu_state->PC = memory->read16(cpu_state->PC+1);

                cycles+=10;

                # CALL NZ, nn
            elif (op_code == 0xC4):
                cpu_state->PC += 3;
                if (cpu_state->Fstatus.status.Z == 0):
                    cpu_state->SP--;
                    memory->write(cpu_state->SP, cpu_state->PCHigh);
                    cpu_state->SP--;
                    memory->write(cpu_state->SP, cpu_state->PCLow);
                    cpu_state->PC = memory->read16(cpu_state->PC-2);
                    cycles += 7;

                cycles += 10;

                # PUSH cpu_state->BC
            elif (op_code == 0xC5):
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->B);
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->C);
                cpu_state->PC++;

                cycles +=11;

                # cpu_state->ADD n
            elif (op_code == 0xC6):
                cpu_state->Fstatus.value = FlagTables::getStatusAdd(cpu_state->A,atPC[1]);
                cpu_state->A = cpu_state->A + atPC[1];
                cpu_state->PC+=2;
                cycles+=7;

                # RST 00h
            elif (op_code == 0xC7):
                cpu_state->PC++;
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCHigh);
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCLow);

                cpu_state->PC = 0x00;

                cycles += 11;

                # RET Z
            elif (op_code == 0xC8):
                if (cpu_state->Fstatus.status.Z == 1):
                    cpu_state->PCLow  = memory->read(cpu_state->SP++);
                    cpu_state->PCHigh = memory->read(cpu_state->SP++);
                    cycles += 11;
                else:
                    cpu_state->PC++;
                    cycles+=5;

                # JP Z, nn
            elif (op_code == 0xCA):
                if (cpu_state->Fstatus.status.Z == 1):
                    cpu_state->PC = memory->read16(cpu_state->PC+1);
                else:
                    cpu_state->PC += 3;

                cycles += 10;

            elif (op_code == 0xCB):
                    extended_op_code = atPC[1] & 0xC7;

                    # cpu_state->Bit b, r
                    if (extended_op_code == 0x40):
                    elif (extended_op_code == 0x41):
                    elif (extended_op_code == 0x42):
                    elif (extended_op_code == 0x43):
                    elif (extended_op_code == 0x44):
                    elif (extended_op_code == 0x45):
                    elif (extended_op_code == 0x47):
                        cpu_state->Fstatus.status.Z = 
                                   (*r[tmp8&0x7] >> ((tmp8 >> 3) & 7)) ^ 0x1;
                        cpu_state->Fstatus.status.PV = FlagTables::calculateParity(*r[tmp8&0x7]);
                        cpu_state->Fstatus.status.H = 1;
                        cpu_state->Fstatus.status.N = 0;
                        cpu_state->Fstatus.status.S = 0;
                        cpu_state->PC += 2;
                        cycles += 8;
                        return 0;

                    # cpu_state->Bit b, (cpu_state->HL) 
                    elif (extended_op_code == 0x46):
                        cpu_state->Fstatus.status.Z = (memory->read(cpu_state->HL) >> 
                                            ((tmp8 >> 3) & 7)) ^ 0x1;
                        cpu_state->Fstatus.status.H = 1;
                        cpu_state->Fstatus.status.N = 0;
                        cpu_state->Fstatus.status.S = 0;
                        cpu_state->PC += 2;
                        cycles += 12;
                        return 0;

                    # RES b, r
                    elif (extended_op_code == 0x80):
                    elif (extended_op_code == 0x81):
                    elif (extended_op_code == 0x82):
                    elif (extended_op_code == 0x83):
                    elif (extended_op_code == 0x84):
                    elif (extended_op_code == 0x85):
                    elif (extended_op_code == 0x87):
                        *r[tmp8&0x7] = *r[tmp8&0x7] & ~(0x1 << ((tmp8 >> 3) & 7));
                        cpu_state->PC += 2;
                        cycles += 8;
                        return 0;

                    # RES b, (cpu_state->HL) 
                    elif (extended_op_code == 0x86):
                        memory->write(cpu_state->HL, 
                            memory->read(cpu_state->HL) & ~(0x1 << ((tmp8 >> 3) & 7)));
                        cpu_state->PC += 2;
                        cycles += 12;
                        return 0;

                    # SET b, r
                    elif (extended_op_code == 0xC0): # SET b, cpu_state->B
                    elif (extended_op_code == 0xC1): # SET b, C
                    elif (extended_op_code == 0xC2): # SET b, D
                    elif (extended_op_code == 0xC3): # SET b, E
                    elif (extended_op_code == 0xC4): # SET b, H
                    elif (extended_op_code == 0xC5): # SET b, L
                    elif (extended_op_code == 0xC7): # SET b, cpu_state->A
                        *r[tmp8&0x7] = *r[tmp8&0x7] | (0x1 << ((tmp8 >> 3) & 7));
                        cpu_state->PC += 2;
                        cycles += 8;
                        return 0;

                    elif (extended_op_code == 0xC6): # SET b, (cpu_state->HL) 
                        memory->write(cpu_state->HL,
                            memory->read(cpu_state->HL) | (0x1 << ((tmp8 >> 3) & 7)));
                        cpu_state->PC += 2;
                        cycles += 15;
                        return 0;
                    else:
                        pass

                    extended_op_code = atPC[1]

                    #uint8 *r8;

                    # RLC r
                    if  ((extended_op_code == 0x00) or # RLC cpu_state->B
                         (extended_op_code == 0x01) or # RLC C
                         (extended_op_code == 0x02) or # RLC D
                         (extended_op_code == 0x03) or # RLC E
                         (extended_op_code == 0x04) or # RLC H
                         (extended_op_code == 0x05) or # RLC L
                         (extended_op_code == 0x07)):  # RLC cpu_state->A
                        r8 = r[tmp8 & 0x7];
                        *r8 = (*r8 << 1) | ((*r8 >> 7) & 0x1);
                        cpu_state->Fstatus.value = FlagTables::getStatusOr(*r8);
                        cpu_state->Fstatus.status.C = *r8 & 0x1; # bit-7 of src = bit-0
                        cpu_state->PC+=2;
                        cycles+=8;

                    elif (extended_op_code == 0x06): # RLC (cpu_state->HL)
                        tmp8 = memory->read(cpu_state->HL);
                        memory->write(cpu_state->HL, (tmp8 << 1) | ((tmp8 >> 7) & 0x1));
                        cpu_state->Fstatus.value = FlagTables::getStatusOr(memory->read(cpu_state->HL));
                        cpu_state->Fstatus.status.C = (tmp8 >> 7) & 0x1; # bit-7 of src
                        cpu_state->PC+=2;
                        cycles+=15;

                    # RRC r
                    elif ((extended_op_code == 0x08) or # RRC cpu_state->B
                          (extended_op_code == 0x09) or # RRC C
                          (extended_op_code == 0x0A) or # RRC D
                          (extended_op_code == 0x0B) or # RRC E
                          (extended_op_code == 0x0C) or # RRC H
                          (extended_op_code == 0x0D) or # RRC L
                          (extended_op_code == 0x0F)): # RRC cpu_state->A
                        r8 = r[tmp8 & 0x7];
                        *r8 = (*r8 >> 1) | ((*r8 & 0x1) << 7);
                        cpu_state->Fstatus.value = FlagTables::getStatusOr(*r8);
                        cpu_state->Fstatus.status.C = (*r8 >> 7) & 0x1; # bit-0 of src
                        cpu_state->PC+=2;
                        cycles+=8;

                    elif (extended_op_code == 0x0E): # RRC (cpu_state->HL)
                        tmp8 = memory->read(cpu_state->HL);
                        memory->write(cpu_state->HL,(tmp8 >> 1) | ((tmp8 & 0x1) << 7));
                        cpu_state->Fstatus.value = FlagTables::getStatusOr(memory->read(cpu_state->HL));
                        cpu_state->Fstatus.status.C = tmp8 & 0x1; # bit-0 of src
                        cpu_state->PC+=2;
                        cycles+=8;

                        # RL r
                    elif ((extended_op_code == 0x10) or # RL cpu_state->B
                          (extended_op_code == 0x11) or # RL C
                          (extended_op_code == 0x12) or # RL D
                          (extended_op_code == 0x13) or # RL E
                          (extended_op_code == 0x14) or # RL H
                          (extended_op_code == 0x15) or # RL L
                          (extended_op_code == 0x17)): # RL cpu_state->A
                        r8 = r[atPC[1] & 0x7];
                        tmp8 = *r8;
                        *r8 = (*r8 << 1) | (cpu_state->Fstatus.status.C);
                        cpu_state->Fstatus.value = FlagTables::getStatusOr(*r8);
                        cpu_state->Fstatus.status.C = (tmp8 >> 7) & 0x1;
                        cpu_state->PC+=2;
                        cycles+=8;

                        # RR r
                    elif ((extended_op_code == 0x18) or # RR cpu_state->B
                          (extended_op_code == 0x19) or # RR C
                          (extended_op_code == 0x1A) or # RR D
                          (extended_op_code == 0x1B) or # RR E
                          (extended_op_code == 0x1C) or # RR H
                          (extended_op_code == 0x1D) or # RR L
                          (extended_op_code == 0x1F)): # RR cpu_state->A
                        r8 = r[atPC[1] & 0x7];
                        tmp8 = *r8;
                        *r8 = (*r8 >> 1) | (cpu_state->Fstatus.status.C << 7);
                        cpu_state->Fstatus.value = FlagTables::getStatusOr(*r8);
                        cpu_state->Fstatus.status.C = tmp8 & 0x1;
                        cpu_state->PC+=2;
                        cycles+=8;

                    # SLA r
                    elif ((extended_op_code == 0x20) or # SLA cpu_state->B
                          (extended_op_code == 0x21) or # SLA C
                          (extended_op_code == 0x22) or # SLA D
                          (extended_op_code == 0x23) or # SLA E
                          (extended_op_code == 0x24) or # SLA H
                          (extended_op_code == 0x25) or # SLA L
                          (extended_op_code == 0x27)): # SLA cpu_state->A
                        tmp8 = (*r[atPC[1] & 0x7] >> 7) & 0x1;
                        *r[atPC[1] & 0x7] = 
                                *r[atPC[1]&0x7] << 1;
                        cpu_state->Fstatus.value = FlagTables::getStatusOr(*r[atPC[1]&0x7]);
                        cpu_state->Fstatus.status.C = tmp8;

                        cpu_state->PC += 2;
                        cycles += 8;

                    elif (extended_op_code == 0x26): # SLA (cpu_state->HL) 
                        tmp8 = (memory->read(cpu_state->HL) >> 7) & 0x1;
                        memory->write(cpu_state->HL, memory->read(cpu_state->HL) << 1);
                        cpu_state->Fstatus.value = FlagTables::getStatusOr(memory->read(cpu_state->HL));
                        cpu_state->Fstatus.status.C = tmp8;

                        cpu_state->PC += 2;
                        cycles += 15;

                    # SRA r
                    elif ((extended_op_code == 0x28) or # SRA cpu_state->B
                          (extended_op_code == 0x29) or # SRA C
                          (extended_op_code == 0x2A) or # SRA D
                          (extended_op_code == 0x2B) or # SRA E
                          (extended_op_code == 0x2C) or # SRA H
                          (extended_op_code == 0x2D) or # SRA L
                          (extended_op_code == 0x2F)): # SRA cpu_state->A
                        r8 = r[atPC[1]&0x7];
                        tmp8 = *r8;
                        *r8 = (*r8 & 0x80) | ((*r8 >> 1) & 0x7F);

                        cpu_state->Fstatus.value = FlagTables::getStatusOr(*r8);
                        cpu_state->Fstatus.status.C = tmp8 & 0x1;

                        cpu_state->PC += 2;
                        cycles += 8;

                    elif (extended_op_code == 0x2E): # SRA (cpu_state->HL)
                        tmp8 = memory->read(cpu_state->HL);
                        memory->write(cpu_state->HL, (tmp8 & 0x80) | ((tmp8 >> 1) & 0x7F));

                        cpu_state->Fstatus.value = FlagTables::getStatusOr(memory->read(cpu_state->HL));
                        cpu_state->Fstatus.status.C = tmp8 & 0x1;

                        cpu_state->PC += 2;
                        cycles += 15;

                    # SLL r
                    elif ((extended_op_code == 0x30) or # SLL cpu_state->B
                          (extended_op_code == 0x31) or # SLL C
                          (extended_op_code == 0x32) or # SLL D
                          (extended_op_code == 0x33) or # SLL E
                          (extended_op_code == 0x34) or # SLL H
                          (extended_op_code == 0x35) or # SLL L
                          (extended_op_code == 0x37)): # SLL cpu_state->A
                        tmp8 = (*r[atPC[1] & 0x7] >> 7) & 0x1;
                        *r[atPC[1] & 0x7] = 
                                *r[atPC[1]&0x7] << 1 | 0x1;
                        cpu_state->Fstatus.value = FlagTables::getStatusOr(*r[atPC[1]&0x7]);
                        cpu_state->Fstatus.status.C = tmp8;

                        cpu_state->PC += 2;
                        cycles += 8;

                    elif (extended_op_code == 0x36): # SLL (cpu_state->HL) 
                        tmp8 = (memory->read(cpu_state->HL) >> 7) & 0x1;
                        memory->write(cpu_state->HL, memory->read(cpu_state->HL) << 1 | 0x1);
                        cpu_state->Fstatus.value = FlagTables::getStatusOr(memory->read(cpu_state->HL));
                        cpu_state->Fstatus.status.C = tmp8;

                        cpu_state->PC += 2;
                        cycles += 15;

                    # SRL r
                    elif ((extended_op_code == 0x38) or # SRL cpu_state->B
                          (extended_op_code == 0x39) or # SRL C
                          (extended_op_code == 0x3A) or # SRL D
                          (extended_op_code == 0x3B) or # SRL E
                          (extended_op_code == 0x3C) or # SRL H
                          (extended_op_code == 0x3D) or # SRL L
                          (extended_op_code == 0x3F)): # SRL cpu_state->A
                        r8 = r[atPC[1]&0x7];
                        tmp8 = *r8;
                        *r8 = (*r8 >> 1) & 0x7F;

                        cpu_state->Fstatus.value = FlagTables::getStatusOr(*r8);
                        cpu_state->Fstatus.status.C = tmp8 & 0x1;

                        cpu_state->PC += 2;
                        cycles += 8;

                    elif (extended_op_code == 0x3E): # SRL (cpu_state->HL)
                        tmp8 = memory->read(cpu_state->HL);
                        memory->write(cpu_state->HL, (tmp8 >> 1) & 0x7F);

                        cpu_state->Fstatus.value = FlagTables::getStatusOr(memory->read(cpu_state->HL));
                        cpu_state->Fstatus.status.C = tmp8 & 0x1;

                        cpu_state->PC += 2;
                        cycles += 15;

                    else:
                        errors::warning("OP 0xCB n, value n unsupported");
                        return -1;

                # CALL Z, nn
            elif (op_code == 0xCC):
                cpu_state->PC += 3;
                if (cpu_state->Fstatus.status.Z == 1):
                    cpu_state->SP--;
                    memory->write(cpu_state->SP, cpu_state->PCHigh);
                    cpu_state->SP--;
                    memory->write(cpu_state->SP, cpu_state->PCLow);
                    cpu_state->PC = memory->read16(cpu_state->PC-2);

                    cycles += 7;
                else:
                    cycles += 10;

                # CALL nn
            elif (op_code == 0xCD):
                cpu_state->PC += 3;
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCHigh);
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCLow);
                cpu_state->PC = memory->read16(cpu_state->PC-2);

                cycles += 17;

                # cpu_state->ADC nn
            elif (op_code == 0xCE):
                cpu_state->A = add8c(cpu_state->A, atPC[1], cpu_state->Fstatus.status.C);
                cpu_state->PC+=2;
                cycles+=4;

                # RST 08h
            elif (op_code == 0xCF):
                cpu_state->PC++;
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCHigh);
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCLow);

                cpu_state->PC = 0x08;

                cycles += 11;

                # RET NC
            elif (op_code == 0xD0):
                if (cpu_state->Fstatus.status.C == 0):
                    cpu_state->PCLow  = memory->read(cpu_state->SP++);
                    cpu_state->PCHigh = memory->read(cpu_state->SP++);
                    cycles += 11;
                else:
                    cpu_state->PC++;
                    cycles+=5;

                  # POP cpu_state->DE
            elif (op_code == 0xD1):
                cpu_state->E = memory->read(cpu_state->SP++);
                cpu_state->D = memory->read(cpu_state->SP++);
                cpu_state->PC++;
                cycles += 10;

                # CALL NC, nn  
            elif (op_code == 0xD4):
                cpu_state->PC += 3;
                if (cpu_state->Fstatus.status.C == 0):
                    cpu_state->SP--;
                    memory->write(cpu_state->SP, cpu_state->PCHigh);
                    cpu_state->SP--;
                    memory->write(cpu_state->SP, cpu_state->PCLow);
                    cpu_state->PC = memory->read16(cpu_state->PC-2);

                    cycles += 7;
                else:
                    cycles += 10;

                # PUSH cpu_state->DE
            elif (op_code == 0xD5):
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->D);
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->E);
                cpu_state->PC++;

                cycles +=11;

                # SUB n
            elif (op_code == 0xD6):
                cpu_state->F = FlagTables::getStatusSub(cpu_state->A,atPC[1]);
                cpu_state->A = cpu_state->A - atPC[1];
                cpu_state->PC += 2;
                cycles += 7;

                # RST 10h
            elif (op_code == 0xD7):
                cpu_state->PC++;
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCHigh);
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCLow);

                cpu_state->PC = 0x10;

                cycles += 11;
                
                # RET C
            elif (op_code == 0xD8):
                if (cpu_state->Fstatus.status.C == 1):
                    cpu_state->PCLow  = memory->read(cpu_state->SP++);
                    cpu_state->PCHigh = memory->read(cpu_state->SP++);
                    cycles += 11;
                else:
                    cpu_state->PC++;
                    cycles+=5;

                # IN cpu_state->A, (N)
            elif (op_code == 0xDB):
                cpu_state->A = Ports::instance()->portRead(atPC[1]);
                cpu_state->PC += 2;
                cycles += 11;

                # Call C, nn
            elif (op_code == 0xDC):
                cpu_state->PC += 3;
                if (cpu_state->Fstatus.status.C == 1):
                    cpu_state->SP--;
                    memory->write(cpu_state->SP, cpu_state->PCHigh);
                    cpu_state->SP--;
                    memory->write(cpu_state->SP, cpu_state->PCLow);
                    cpu_state->PC = memory->read16(cpu_state->PC-2);
                    cycles += 17;
                else:
                    cycles += 10;

                # Scpu_state->BC n 
            elif (op_code == 0xDE):
                cpu_state->A = sub8c(cpu_state->A, atPC[1], cpu_state->Fstatus.status.C);
                cpu_state->PC+=2;
                cycles+=7;

                # RST 18h
            elif (op_code == 0xDF):
                cpu_state->PC++;
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCHigh);
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCLow);

                cpu_state->PC = 0x18;

                cycles += 11;

                # RET PO  
            elif (op_code == 0xE0):
                if (cpu_state->Fstatus.status.PV == 0):
                    cpu_state->PCLow  = memory->read(cpu_state->SP++);
                    cpu_state->PCHigh = memory->read(cpu_state->SP++);
                    cycles += 11;
                else:
                    cpu_state->PC++;
                    cycles+=5;

                # POP cpu_state->HL
            elif (op_code == 0xE1):
                cpu_state->L = memory->read(cpu_state->SP++);
                cpu_state->H = memory->read(cpu_state->SP++);

                cpu_state->PC++;

                cycles += 10;

                # JP PO, nn   Parity Odd 
            elif (op_code == 0xE2):
                if (cpu_state->Fstatus.status.PV == 0):
                    cpu_state->PC = memory->read16(cpu_state->PC+1);
                else:
                    cpu_state->PC += 3;

                cycles +=10;

                # EX (cpu_state->SP), cpu_state->HL
            elif (op_code == 0xE3):
                tmp8 = memory->read(cpu_state->SP);
                memory->write(cpu_state->SP, cpu_state->L);
                cpu_state->L = tmp8;
                tmp8 = memory->read(cpu_state->SP+1);
                memory->write(cpu_state->SP+1, cpu_state->H);
                cpu_state->H = tmp8;
                cpu_state->PC++;
                cycles += 19;

                # CALL PO, nn 
            elif (op_code == 0xE4):
                cpu_state->PC += 3;
                if (cpu_state->Fstatus.status.PV == 0):
                    cpu_state->SP--;
                    memory->write(cpu_state->SP, cpu_state->PCHigh);
                    cpu_state->SP--;
                    memory->write(cpu_state->SP, cpu_state->PCLow);
                    cpu_state->PC = memory->read16(cpu_state->PC-2);
                    cycles += 7;

                cycles += 10;


                # PUSH cpu_state->HL
            elif (op_code == 0xE5):
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->H);
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->L);
                cpu_state->PC++;

                cycles +=11;

                # RST 20h
            elif (op_code == 0xE7):
                cpu_state->PC++;
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCHigh);
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCLow);

                cpu_state->PC = 0x20;

                cycles += 11;

                # RET PE  
            elif (op_code == 0xE8):
                if (cpu_state->Fstatus.status.PV == 1):
                    cpu_state->PCLow  = memory->read(cpu_state->SP++);
                    cpu_state->PCHigh = memory->read(cpu_state->SP++);
                    cycles += 11;
                else:
                    cpu_state->PC++;
                    cycles+=5;

                # Don't know how many cycles
                # LD cpu_state->PC, cpu_state->HL
            elif (op_code == 0xE9):
                cpu_state->PC = cpu_state->HL;
                cycles+=6;

                # JP PE, nn   Parity Even 
            elif (op_code == 0xEA):
                if (cpu_state->Fstatus.status.PV == 1):
                    cpu_state->PC = memory->read16(cpu_state->PC+1);
                else:
                    cpu_state->PC += 3;

                cycles +=10;

                # EX cpu_state->DE, cpu_state->HL
            elif (op_code == 0xEB):
                tmp16 = cpu_state->DE;
                cpu_state->DE = cpu_state->HL;
                cpu_state->HL = tmp16;
                cpu_state->PC++;
                cycles+=4;

                # CALL PE, nn
            elif (op_code == 0xEC):
                cpu_state->PC += 3;
                if (cpu_state->Fstatus.status.PV == 1):
                    cpu_state->SP--;
                    memory->write(cpu_state->SP, cpu_state->PCHigh);
                    cpu_state->SP--;
                    memory->write(cpu_state->SP, cpu_state->PCLow);
                    cpu_state->PC = memory->read16(cpu_state->PC-2);
                    cycles += 7;

                cycles += 10;

                # XOR n
            elif (op_code == 0xEE): 
                cpu_state->A = cpu_state->A ^ atPC[1];
                cpu_state->Fstatus.value = FlagTables::getStatusOr(cpu_state->A);
                cpu_state->PC+=2;
                cycles+=7;

                # RST 28h
            elif (op_code == 0xEF):
                cpu_state->PC++;
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCHigh);
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCLow);

                cpu_state->PC = 0x28;

                cycles += 11;

                # RET P, if Positive
            elif (op_code == 0xF0):
                if (cpu_state->Fstatus.status.S == 0):
                    cpu_state->PCLow  = memory->read(cpu_state->SP++);
                    cpu_state->PCHigh = memory->read(cpu_state->SP++);
                    cycles += 11;
                else:
                    cpu_state->PC++;
                    cycles+=5;

                # POP cpu_state->AF
            elif (op_code == 0xF1):
                cpu_state->F = memory->read(cpu_state->SP++);
                cpu_state->A = memory->read(cpu_state->SP++);

                cpu_state->PC++;

                cycles+=10;

                # JP P, nn    if Positive
            elif (op_code == 0xF2):
                if (cpu_state->Fstatus.status.S == 0):
                    cpu_state->PC = memory->read16(cpu_state->PC+1);
                else:
                    cpu_state->PC += 3;

                cycles +=10;

              # Disable interupts
              # DI
            elif (op_code == 0xF3):
                cpu_state->IFF1 = 0;
                cpu_state->IFF2 = 0;
                cpu_state->PC++;

                cycles+=4;

                # CALL P, nn  if Positive
            elif (op_code == 0xF4):
                cpu_state->PC += 3;
                if (cpu_state->Fstatus.status.S == 0):
                    cpu_state->SP--;
                    memory->write(cpu_state->SP, cpu_state->PCHigh);
                    cpu_state->SP--;
                    memory->write(cpu_state->SP, cpu_state->PCLow);
                    cpu_state->PC = memory->read16(cpu_state->PC-2);
                    cycles += 7;

                cycles += 10;

                # PUSH cpu_state->AF
            elif (op_code == 0xF5):
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->A);
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->F);
                cpu_state->PC++;

                cycles+=11;

                # OR n
            elif (op_code == 0xF6):
                cpu_state->A = cpu_state->A | atPC[1];
                cpu_state->Fstatus.value = FlagTables::getStatusOr(cpu_state->A);
                cpu_state->PC += 2;
                cycles+=7;

                # RST 30h
            elif (op_code == 0xF7):
                cpu_state->PC++;
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCHigh);
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCLow);

                cpu_state->PC = 0x30;

                cycles += 11;

                # RET M  if Negative
            elif (op_code == 0xF8):
                if (cpu_state->Fstatus.status.S == 1):
                    cpu_state->PCLow  = memory->read(cpu_state->SP++);
                    cpu_state->PCHigh = memory->read(cpu_state->SP++);
                    cycles += 11;
                else:
                    cpu_state->PC++;
                    cycles+=5;

                # LD cpu_state->SP, cpu_state->HL
            elif (op_code == 0xF9):
                cpu_state->SP = cpu_state->HL;
                cpu_state->PC++;
                cycles+=6;

                # JP M, nn    if Negative
            elif (op_code == 0xFA):
                if (cpu_state->Fstatus.status.S == 1):
                    cpu_state->PC = memory->read16(cpu_state->PC+1);
                else:
                    cpu_state->PC += 3;

                cycles +=10;

                # Enable interupts
                # EI
            elif (op_code == 0xFB):
                cpu_state->PC++;

                # Process next instruction before enabling interupts
                step(false); # Single step, no loop

                cpu_state->IFF1 = 1;
                cpu_state->IFF2 = 1;
                cycles+=4;

                  # Check for any pending interupts
                if (interuptor->pollInterupts(cycles) == true):
                    interupt();


                # CALL M, nn  if Negative
            elif (op_code == 0xFC):
                cpu_state->PC += 3;
                if (cpu_state->Fstatus.status.S == 1):
                    cpu_state->SP--;
                    memory->write(cpu_state->SP, cpu_state->PCHigh);
                    cpu_state->SP--;
                    memory->write(cpu_state->SP, cpu_state->PCLow);
                    cpu_state->PC = memory->read16(cpu_state->PC-2);

                    cycles += 7;
                else:
                    cycles += 10;

                # RST 38h
            elif (op_code == 0xFF):
                cpu_state->PC++;
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCHigh);
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCLow);

                cpu_state->PC = 0x38;

                cycles += 11;

            elif (op_code == 0xDD):
                # Temporary, until `all instructions are covered'
                instruction = 
                        InstructionStore::instance()->getExtendedDD(&atPC[1]);
                if (instruction):
                    cycles += instruction->execute(memory);
                else:
                    extended_op_code = atPC[1]

                    # LD cpu_state->IX, nn
                    if (extended_op_code == 0x21):
                        cpu_state->IX = memory->read16(cpu_state->PC+2);
                        cpu_state->PC += 4;

                        cycles +=20;

                        # LD (nn), cpu_state->IX
                    elif (extended_op_code == 0x22):
                        memory->write(memory->read16(cpu_state->PC+2), cpu_state->IXLow);
                        memory->write(memory->read16(cpu_state->PC+2)+1, cpu_state->IXHigh);
                        cpu_state->PC += 4;

                        cycles += 20;

                        # LD cpu_state->IX, (nn)
                    elif (extended_op_code == 0x2A):
                        cpu_state->IX = memory->read16(memory->read16(cpu_state->PC+2));
                        cpu_state->PC += 4;

                        cycles += 20;

                        # INC (cpu_state->IX+d)
                    elif (extended_op_code == 0x34):
                        tmp16 = cpu_state->IX + (int) (signed char) atPC[2];
                        memory->write(tmp16, memory->read(tmp16) + 1);
                        cpu_state->F = (cpu_state->F & Instruction::FLAG_MASK_INC8) | 
                    FlagTables::getStatusInc8(memory->read(tmp16));
                        cpu_state->PC+=3;
                        cycles+=23;

                        # cpu_state->DEC (cpu_state->IX+d)
                    elif (extended_op_code == 0x35):
                        tmp16 = cpu_state->IX + (int) (signed char) atPC[2];
                        memory->write(tmp16, memory->read(tmp16) - 1);
                        cpu_state->F = (cpu_state->F & Instruction::FLAG_MASK_DEC8) | FlagTables::getStatusDec8(memory->read(tmp16));
                        cpu_state->PC+=3;
                        cycles+=23;

                        # LD (cpu_state->IX + d), n
                    elif (extended_op_code == 0x36):
                        tmp16 = cpu_state->IX + (int) (signed char) atPC[2];
                        memory->write(tmp16, atPC[3]);
                        cpu_state->PC += 4;
                        cycles += 19;

                        # LD r, (cpu_state->IX+e)
                    elif ((extended_op_code == 0x46) or
                          (extended_op_code == 0x4E) or
                          (extended_op_code == 0x56) or
                          (extended_op_code == 0x5E) or
                          (extended_op_code == 0x66) or
                          (extended_op_code == 0x6E) or
                          (extended_op_code == 0x7E)):
                        *r[(atPC[1] >> 3) & 0x7] = 
                                    memory->read(cpu_state->IX + 
                                         (int) (signed char) atPC[2]);
                        cpu_state->PC += 3;
                        cycles += 19;

                        # LD (cpu_state->IX+d), r
                    elif ((extended_op_code == 0x70) or
                          (extended_op_code == 0x71) or
                          (extended_op_code == 0x72) or
                          (extended_op_code == 0x73) or
                          (extended_op_code == 0x74) or
                          (extended_op_code == 0x75) or
                          (extended_op_code == 0x77)):
                        memory->write(cpu_state->IX + (int) (signed char) atPC[2],
                                      *r[atPC[1] & 0x7]); 
                        cpu_state->PC += 3;
                        cycles += 19;

                        # cpu_state->ADD cpu_state->A,(cpu_state->IX+d)
                    elif (extended_op_code == 0x86):
                        tmp8 = memory->read(cpu_state->IX + 
                                         (int) (signed char) atPC[2]);
                        cpu_state->Fstatus.value = FlagTables::getStatusAdd(cpu_state->A, tmp8);
                        cpu_state->A = cpu_state->A + tmp8;
                        cpu_state->PC += 3;
                        cycles += 19;

                        # cpu_state->ADC (cpu_state->IX + d)
                    elif (extended_op_code == 0x8E):
                        cpu_state->A = add8c(cpu_state->A, memory->read(cpu_state->IX + (int) (signed char)
                                        atPC[2]), cpu_state->Fstatus.status.C);
                        cpu_state->PC+=3;
                        cycles+=19;

                        # SUB (cpu_state->IX + d)
                    elif (extended_op_code == 0x96):
                        tmp8 = memory->read(cpu_state->IX + 
                                         (int) (signed char) atPC[2]);
                        cpu_state->F = FlagTables::getStatusSub(cpu_state->A,tmp8);
                        cpu_state->A = cpu_state->A - tmp8;
                        cpu_state->PC += 3;
                        cycles += 19;

                        # cpu_state->AND (cpu_state->IX + d)
                    elif (extended_op_code == 0xA6):
                        cpu_state->A = cpu_state->A & memory->read(cpu_state->IX +
                                         (int) (signed char) atPC[2]);
                        cpu_state->PC+=3;
                        cpu_state->Fstatus.value = FlagTables::getStatusAnd(cpu_state->A);

                        cycles+=19;

                        # XOR (cpu_state->IX + d)
                    elif (extended_op_code == 0xAE):
                        cpu_state->A = cpu_state->A ^ memory->read(cpu_state->IX +
                                         (int) (signed char) atPC[2]);
                        cpu_state->PC+=3;
                        cpu_state->Fstatus.value = FlagTables::getStatusOr(cpu_state->A);

                        cycles += 19;

                        # OR (cpu_state->IX + d)
                    elif (extended_op_code == 0xB6):
                        tmp8 = memory->read(cpu_state->IX + 
                                         (int) (signed char) atPC[2]);
                        cpu_state->A = cpu_state->A | tmp8;
                        cpu_state->Fstatus.value = FlagTables::getStatusOr(cpu_state->A);
                        cpu_state->PC += 3;
                        cycles += 19;

                        # CP (cpu_state->IX + d)
                    elif (extended_op_code == 0xBE):
                        tmp8 = memory->read(cpu_state->IX + 
                                         (int) (signed char) atPC[2]);
                        cpu_state->F = FlagTables::getStatusSub(cpu_state->A,tmp8);
                        cpu_state->PC+=3;
                        cycles+=19;

                    # Probably should turn this into a lookup table
                    elif (extended_op_code == 0xCB):
                        tmp16 = cpu_state->IX + (int) (signed char) atPC[2];
                        tmp8 = memory->read(tmp16);
                        t8 = atPC[3];

                        if ((t8 & 0xC7) == 0x46): # cpu_state->BIT b, (cpu_state->IX + d)
                            tmp8 = (tmp8 >> ((t8 & 0x38) >> 3)) & 0x1;
                            cpu_state->Fstatus.status.Z = tmp8 ^ 0x1;;
                            cpu_state->Fstatus.status.PV = FlagTables::calculateParity(tmp8);
                            cpu_state->Fstatus.status.H = 1;
                            cpu_state->Fstatus.status.N = 0;
                            cpu_state->Fstatus.status.S = 0;
                        elif ((t8 & 0xC7) == 0x86): # RES b, (cpu_state->IX + d)
                            tmp8 = tmp8 & ~(0x1 << ((t8 >> 3) & 0x7));
                            memory->write(tmp16,tmp8);
                        elif ((t8 & 0xC7) == 0xC6): # SET b, (cpu_state->IX + d)
                            tmp8 = tmp8 | (0x1 << ((t8 >> 3) & 0x7));
                            memory->write(tmp16,tmp8);
                        else:
                            errors::unsupported("Instruction arg for 0xDD 0xCB");

                        cpu_state->PC += 4;

                        cycles += 23;

                    # POP cpu_state->IX
                    elif (extended_op_code == 0xE1):
                        cpu_state->IXLow = memory->read(cpu_state->SP++);
                        cpu_state->IXHigh = memory->read(cpu_state->SP++);
                        cpu_state->PC += 2;
                        cycles += 14;

                        # EX (cpu_state->SP), cpu_state->IX
                    elif (extended_op_code == 0xE3):
                        tmp8 = memory->read(cpu_state->SP);
                        memory->write(cpu_state->SP, cpu_state->IXLow);
                        cpu_state->IXLow = tmp8;
                        tmp8 = memory->read(cpu_state->SP+1);
                        memory->write(cpu_state->SP+1, cpu_state->IXHigh);
                        cpu_state->IXHigh = tmp8;
                        cpu_state->PC+=2;
                        cycles += 23;

                    # PUSH cpu_state->IX
                    elif (extended_op_code == 0xE5):
                        cpu_state->SP--;
                        memory->write(cpu_state->SP, cpu_state->IXHigh);
                        cpu_state->SP--;
                        memory->write(cpu_state->SP, cpu_state->IXLow);
                        cpu_state->PC += 2;

                        cycles +=15;

                        # Don't know how many cycles
                        # LD cpu_state->PC, cpu_state->IX
                    elif (extended_op_code == 0xE9):
                        cpu_state->PC = cpu_state->IX;
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

                    # LD cpu_state->IY, (nn)
                    if (extended_op_code == 0x21):
                        cpu_state->IY = memory->read16(cpu_state->PC+2);
                        cpu_state->PC += 4;
                        cycles += 20;

                        # LD (nn), cpu_state->IY
                    elif (extended_op_code == 0x22):
                        memory->write(memory->read16(cpu_state->PC+2), cpu_state->IYLow);
                        memory->write(memory->read16(cpu_state->PC+2)+1, cpu_state->IYHigh);
                        cpu_state->PC += 4;

                        cycles += 20;

                        # LD cpu_state->IY, (nn)
                    elif (extended_op_code == 0x2A):
                        cpu_state->IY = memory->read16(memory->read16(cpu_state->PC+2));
                        cpu_state->PC += 4;

                        cycles += 20;

                        # INC (cpu_state->IY+d)
                    elif (extended_op_code == 0x34):
                        tmp16 = cpu_state->IY + (int) (signed char) atPC[2];
                        memory->write(tmp16, memory->read(tmp16) + 1);
                        cpu_state->F = (cpu_state->F & Instruction::FLAG_MASK_INC8) | 
                    FlagTables::getStatusInc8(memory->read(tmp16));
                        cpu_state->PC+=3;
                        cycles+=23;

                        # cpu_state->DEC (cpu_state->IY+d)
                    elif (extended_op_code == 0x35):
                        tmp16 = cpu_state->IY + (int) (signed char) atPC[2];
                        memory->write(tmp16, memory->read(tmp16) - 1);
                        cpu_state->F = (cpu_state->F & Instruction::FLAG_MASK_DEC8) | FlagTables::getStatusDec8(memory->read(tmp16));
                        cpu_state->PC+=3;
                        cycles+=23;

                        # LD (cpu_state->IY + d), n
                    elif (extended_op_code == 0x36):
                        tmp16 = cpu_state->IY + (int) (signed char) atPC[2];
                        memory->write(tmp16, atPC[3]);
                        cpu_state->PC += 4;
                        cycles += 19;

                        # LD r, (cpu_state->IY+e)
                    elif ((extended_op_code == 0x46) or
                          (extended_op_code == 0x4E) or
                          (extended_op_code == 0x56) or
                          (extended_op_code == 0x5E) or
                          (extended_op_code == 0x66) or
                          (extended_op_code == 0x6E) or
                          (extended_op_code == 0x7E)):
                        *r[(atPC[1] >> 3) & 0x7] = 
                                    memory->read(cpu_state->IY + 
                                         (int) (signed char) atPC[2]);
                        cpu_state->PC += 3;
                        cycles += 19;

                        # LD (cpu_state->IY+d), r
                    elif ((extended_op_code == 0x70) or # LD (cpu_state->IY+d), cpu_state->B
                          (extended_op_code == 0x71) or # LD (cpu_state->IY+d), C
                          (extended_op_code == 0x72) or # LD (cpu_state->IY+d), D
                          (extended_op_code == 0x73) or # LD (cpu_state->IY+d), E
                          (extended_op_code == 0x74) or # LD (cpu_state->IY+d), H
                          (extended_op_code == 0x75) or # LD (cpu_state->IY+d), L
                          (extended_op_code == 0x77)): # LD (cpu_state->IY+d), cpu_state->A
                        memory->write(cpu_state->IY + (int) (signed char) atPC[2],
                                      *r[atPC[1] & 0x7]); 
                        cpu_state->PC += 3;
                        cycles += 19;

                        # cpu_state->ADD cpu_state->A,(cpu_state->IY+d)
                    elif (extended_op_code == 0x86):
                        tmp8 = memory->read(cpu_state->IY + 
                                         (int) (signed char) atPC[2]);
                        cpu_state->Fstatus.value = FlagTables::getStatusAdd(cpu_state->A,tmp8);
                        cpu_state->A = cpu_state->A + tmp8;
                        cpu_state->PC += 3;
                        cycles += 19;

                        # cpu_state->ADC (cpu_state->IY + d)
                    elif (extended_op_code == 0x8E):
                        cpu_state->A = add8c(cpu_state->A, memory->read(cpu_state->IY + (int) (signed char)
                                        atPC[2]), cpu_state->Fstatus.status.C);
                        cpu_state->PC+=3;
                        cycles+=19;

                        # SUB (cpu_state->IY + d)
                    elif (extended_op_code == 0x96):
                        tmp8 = memory->read(cpu_state->IY + 
                                         (int) (signed char) atPC[2]);
                        cpu_state->F = FlagTables::getStatusSub(cpu_state->A,tmp8);
                        cpu_state->A = cpu_state->A - tmp8;
                        cpu_state->PC += 3;
                        cycles += 19;

                        # cpu_state->AND (cpu_state->IY + d)
                    elif (extended_op_code == 0xA6):
                        cpu_state->A = cpu_state->A & memory->read(cpu_state->IY +
                                         (int) (signed char) atPC[2]);
                        cpu_state->PC+=3;
                        cpu_state->Fstatus.value = FlagTables::getStatusAnd(cpu_state->A);

                        cycles+=19;

                        # XOR (cpu_state->IY + d)
                    elif (extended_op_code == 0xAE):
                        cpu_state->A = cpu_state->A ^ memory->read(cpu_state->IY +
                                         (int) (signed char) atPC[2]);
                        cpu_state->PC+=3;
                        cpu_state->Fstatus.value = FlagTables::getStatusOr(cpu_state->A);

                        cycles += 19;

                        # OR (cpu_state->IY + d)
                    elif (extended_op_code == 0xB6):
                        tmp8 = memory->read(cpu_state->IY + 
                                         (int) (signed char) atPC[2]);
                        cpu_state->A = cpu_state->A | tmp8;
                        cpu_state->Fstatus.value = FlagTables::getStatusOr(cpu_state->A);
                        cpu_state->PC += 3;
                        cycles += 19;

                        # CP (cpu_state->IY + d)
                    elif (extended_op_code == 0xBE):
                        tmp8 = memory->read(cpu_state->IY + 
                                         (int) (signed char) atPC[2]);
                        cpu_state->F = FlagTables::getStatusSub(cpu_state->A,tmp8);
                        cpu_state->PC+=3;
                        cycles+=19;

                    # Probably should turn this into a lookup table
                    elif (extended_op_code == 0xCB):
                        tmp16 = cpu_state->IY + (int) (signed char) atPC[2];
                        tmp8 = memory->read(tmp16);
                        t8 = atPC[3];

                        if ((t8 & 0xC7) == 0x46): # cpu_state->BIT b, (cpu_state->IY + d)
                            tmp8 = (tmp8 >> ((t8 & 0x38) >> 3)) & 0x1;
                            cpu_state->Fstatus.status.Z = tmp8 ^ 0x1;;
                            cpu_state->Fstatus.status.PV = FlagTables::calculateParity(tmp8);
                            cpu_state->Fstatus.status.H = 1;
                            cpu_state->Fstatus.status.N = 0;
                            cpu_state->Fstatus.status.S = 0;
                        elif ((t8 & 0xC7) == 0x86): # RES b, (cpu_state->IY + d)
                            tmp8 = tmp8 & ~(0x1 << ((t8 >> 3) & 0x7));
                            memory->write(tmp16,tmp8);
                        elif ((t8 & 0xC7) == 0xC6): # SET b, (cpu_state->IY + d)
                            tmp8 = tmp8 | (0x1 << ((t8 >> 3) & 0x7));
                            memory->write(tmp16,tmp8);
                        else:
                            errors::unsupported("Instruction arg for 0xFD 0xCB");

                        cpu_state->PC += 4;

                        cycles += 23;
                       
                    # POP cpu_state->IY
                    elif (extended_op_code == 0xE1):
                        cpu_state->IYLow = memory->read(cpu_state->SP++);
                        cpu_state->IYHigh = memory->read(cpu_state->SP++);
                        cpu_state->PC += 2;
                        cycles += 14;

                        # EX (cpu_state->SP), cpu_state->IY
                    elif (extended_op_code == 0xE3):
                        tmp8 = memory->read(cpu_state->SP);
                        memory->write(cpu_state->SP, cpu_state->IYLow);
                        cpu_state->IYLow = tmp8;
                        tmp8 = memory->read(cpu_state->SP+1);
                        memory->write(cpu_state->SP+1, cpu_state->IYHigh);
                        cpu_state->IYHigh = tmp8;
                        cpu_state->PC+=2;
                        cycles += 23;

                    # PUSH cpu_state->IY
                    elif (extended_op_code == 0xE5):
                        cpu_state->SP--;
                        memory->write(cpu_state->SP, cpu_state->IYHigh);
                        cpu_state->SP--;
                        memory->write(cpu_state->SP, cpu_state->IYLow);
                        cpu_state->PC += 2;

                        cycles +=15;

                        # Don't know how many cycles
                        # LD cpu_state->PC, cpu_state->IY
                    elif (extended_op_code == 0xE9):
                        cpu_state->PC = cpu_state->IY;
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
                        *r[(atPC[1] >> 3) & 0x7] = Ports::instance()->portRead(cpu_state->C);
                        cpu_state->PC += 2;
                        cycles += 12;

                      # OUT (C), r
                    elif ((extended_op_code == 0x41) or # OUT (C), cpu_state->B
                          (extended_op_code == 0x49) or # OUT (C), C
                          (extended_op_code == 0x51) or # OUT (C), D
                          (extended_op_code == 0x59) or # OUT (C), E
                          (extended_op_code == 0x61) or # OUT (C), H
                          (extended_op_code == 0x69) or # OUT (C), L
                          (extended_op_code == 0x79)): # OUT (C), cpu_state->A
                        Ports::instance()->portWrite(cpu_state->C, *r[(atPC[1] >> 3) & 0x7]);
                        cpu_state->PC += 2;
                        cycles +=3;

                      # Scpu_state->BC cpu_state->HL, cpu_state->BC
                    elif (extended_op_code == 0x42):
                        cpu_state->HL = sub16c(cpu_state->HL, cpu_state->BC, cpu_state->Fstatus.status.C);

                        cpu_state->PC += 2;
                        cycles += 15;

                        # LD (nn), cpu_state->BC
                    elif (extended_op_code == 0x43):
                        memory->write(memory->read16(cpu_state->PC+2), cpu_state->C);
                        memory->write(memory->read16(cpu_state->PC+2)+1, cpu_state->B);
                        cpu_state->PC += 4;

                        cycles += 20;

                      # NEG
                    elif (extended_op_code == 0x44):
                        cpu_state->Fstatus.value = FlagTables::getStatusSub(0,cpu_state->A);
                        cpu_state->A = -cpu_state->A;
                        cpu_state->PC += 2;
                        cycles+=8;

                      # LD I, cpu_state->A
                    elif (extended_op_code == 0x47):
                        cpu_state->I = cpu_state->A;
                        cpu_state->PC += 2;
                        cycles += 9;

                        # cpu_state->ADC cpu_state->HL, cpu_state->BC
                    elif (extended_op_code == 0x4A):
                        cpu_state->HL = add16c(cpu_state->HL, cpu_state->BC, cpu_state->Fstatus.status.C);
                        cpu_state->PC+=2;
                        cycles+=15;

                        # Load 16-bit cpu_state->BC register
                        # LD cpu_state->BC, (nn)
                    elif (extended_op_code == 0x4B):
                        cpu_state->BC = memory->read16(memory->read16(cpu_state->PC+2)); 
                        cpu_state->PC += 4;
                        cycles += 20;

                        # Fcpu_state->IXME, should check, since there is only one
                        # interupting device, this is the same as normal ret
                        # RETI
                    elif (extended_op_code == 0x4D): 
                        cpu_state->PCLow  = memory->read(cpu_state->SP++);
                        cpu_state->PCHigh = memory->read(cpu_state->SP++);

                        cycles += 14;
                                
                      # Scpu_state->BC cpu_state->HL, cpu_state->DE
                    elif (extended_op_code == 0x52):
                        cpu_state->HL = sub16c(cpu_state->HL, cpu_state->DE, cpu_state->Fstatus.status.C);

                        cpu_state->PC += 2;
                        cycles += 4;

                        # LD (nn), cpu_state->DE
                    elif (extended_op_code == 0x53):
                        memory->write(memory->read16(cpu_state->PC+2), cpu_state->E);
                        memory->write(memory->read16(cpu_state->PC+2)+1, cpu_state->D);
                        cpu_state->PC += 4;

                        cycles += 20;

                        # cpu_state->IM 1
                    elif (extended_op_code == 0x56):
                        cpu_state->PC+=2;
                        cpu_state->IM = 1;

                        cycles += 2;

                        # LD cpu_state->A, I
                    elif (extended_op_code == 0x57):
                        cpu_state->A = cpu_state->I;
                        cpu_state->Fstatus.status.N = 0;
                        cpu_state->Fstatus.status.H = 0;
                        cpu_state->Fstatus.status.PV = cpu_state->IFF2;
                        cpu_state->Fstatus.status.S = (cpu_state->A & 0x80) >> 7;
                        cpu_state->Fstatus.status.Z = (cpu_state->A == 0)?1:0;

                        cpu_state->PC += 2;
                        cycles += 9;

                        # cpu_state->ADC cpu_state->HL, cpu_state->DE
                    elif (extended_op_code == 0x5A):
                        cpu_state->HL = add16c(cpu_state->HL, cpu_state->DE, cpu_state->Fstatus.status.C);
                        cpu_state->PC+=2;
                        cycles+=4;

                        # LD cpu_state->DE, (nn)    
                    elif (extended_op_code == 0x5B):
                        cpu_state->DE = memory->read16(memory->read16(cpu_state->PC+2));
                        cpu_state->PC += 4;
                        cycles += 20;

                        # Fcpu_state->IXME, not sure about this
                        # LD cpu_state->A, R
                    elif (extended_op_code == 0x5F):
                        cpu_state->R =  (cpu_state->R & 0x80) | ((cycles + cpu_state->R + 1) & 0x7F);
                        cpu_state->A = cpu_state->R;
                        cpu_state->Fstatus.status.N = 0;
                        cpu_state->Fstatus.status.H = 0;
                        cpu_state->Fstatus.status.PV = cpu_state->IFF2;
                        cpu_state->Fstatus.status.S = (cpu_state->A & 0x80) >> 7;
                        cpu_state->Fstatus.status.Z = (cpu_state->A == 0)?1:0;

                        cpu_state->PC += 2;
                        cycles += 9;

                        # Fcpu_state->IXME, can't find existance of this instruction
                        # LD (nn), cpu_state->HL
                    elif (extended_op_code == 0x63):
                        memory->write(memory->read16(cpu_state->PC+2), cpu_state->L);
                        memory->write(memory->read16(cpu_state->PC+2)+1, cpu_state->H);
                        cpu_state->PC += 4;

                        cycles += 16;

                        # RRD, wacky instruction
                    elif (extended_op_code == 0x67):
                        tmp8 = cpu_state->A;
                        cpu_state->A = (cpu_state->A & 0xF0) | (memory->read(cpu_state->HL) & 0xF);
                        memory->write(cpu_state->HL, 
                               ((memory->read(cpu_state->HL) >> 4) & 0xF) | 
                               ((tmp8 << 4) & 0xF0));

                        tmp8 = cpu_state->Fstatus.status.C;
                        cpu_state->Fstatus.value = FlagTables::getStatusOr(cpu_state->A);
                        cpu_state->Fstatus.status.C = tmp8;

                        cpu_state->PC+=2;
                        cycles += 18;

                        # cpu_state->ADC cpu_state->HL, cpu_state->HL
                    elif (extended_op_code == 0x6A):
                        cpu_state->HL = add16c(cpu_state->HL, cpu_state->HL, cpu_state->Fstatus.status.C);
                        cpu_state->PC+=2;
                        cycles+=4;

                        # Fcpu_state->IXME, not sure about the existance of this instruction
                        # LD cpu_state->HL, (nn)
                    elif (extended_op_code == 0x6B):
                        cpu_state->HL = memory->read16(memory->read16(cpu_state->PC+2));
                        cpu_state->PC += 4;

                        cycles += 20;

                        # LD (nn), cpu_state->SP
                    elif (extended_op_code == 0x73):
                        memory->write(memory->read16(cpu_state->PC+2), cpu_state->SPLow);
                        memory->write(memory->read16(cpu_state->PC+2)+1, cpu_state->SPHigh);
                        cpu_state->PC += 4;

                        cycles += 6;

                        # cpu_state->ADC cpu_state->HL, cpu_state->SP
                    elif (extended_op_code == 0x7A):
                        cpu_state->HL = add16c(cpu_state->HL, cpu_state->SP, cpu_state->Fstatus.status.C);
                        cpu_state->PC+=2;
                        cycles+=15;

                        # Load 16-bit cpu_state->BC register
                        # LD cpu_state->SP, (nn)
                    elif (extended_op_code == 0x7B):
                        cpu_state->SP = memory->read16(memory->read16(cpu_state->PC+2)); 
                        cpu_state->PC += 4;
                        cycles += 20;

                        # LDI
                    elif (extended_op_code == 0xA0):
                        memory->write(cpu_state->DE++, memory->read(cpu_state->HL++));
                        cpu_state->BC--;
                        cpu_state->Fstatus.status.PV = (cpu_state->BC != 0) ? 1:0;
                        cpu_state->Fstatus.status.H = 0;
                        cpu_state->Fstatus.status.N = 0;
                        cpu_state->PC += 2;

                        cycles += 16;

                        # CPI
                    elif (extended_op_code == 0xA1):
                        cpu_state->F = FlagTables::getStatusSub(cpu_state->A,memory->read(cpu_state->HL++));
                        cpu_state->BC--;
                        cpu_state->Fstatus.status.PV = (cpu_state->BC != 0) ? 1:0;
                        cpu_state->PC += 2;
                        cycles += 16;

                        # INI
                    elif (extended_op_code == 0xA2):
                        cpu_state->B--;
                        memory->write(cpu_state->HL++, Ports::instance()->portRead(cpu_state->C));
                        cpu_state->Fstatus.status.N = 1;
                        if (cpu_state->B == 0):
                            cpu_state->Fstatus.status.Z = 1;
                        else:
                            cpu_state->Fstatus.status.Z = 0;

                        cpu_state->PC += 2;
                        cycles += 16;

                        # OUTI
                    elif (extended_op_code == 0xA3):
                        cpu_state->B--;
                        Ports::instance()->portWrite(cpu_state->C, memory->read(cpu_state->HL++));
                        cpu_state->Fstatus.status.Z = (cpu_state->B == 0) ? 1:0;
                        cpu_state->Fstatus.status.N = 1;
                        cpu_state->PC += 2;
                        cycles += 16;

                        # OUTD
                    elif (extended_op_code == 0xAB):
                        cpu_state->B--;
                        Ports::instance()->portWrite(cpu_state->C, memory->read(cpu_state->HL--));
                        cpu_state->Fstatus.status.Z = (cpu_state->B == 0) ? 1:0;
                        cpu_state->Fstatus.status.N = 1;
                        cpu_state->PC += 2;
                        cycles += 16;

                        # LDIR
                    elif (extended_op_code == 0xB0):
                        if (cpu_state->BC >= 4):
                            memory->write(cpu_state->DE, cpu_state->HL, 4);
                            cpu_state->DE += 4;
                            cpu_state->HL += 4;
                            cpu_state->BC -= 4;
                            cycles += 84;
                        else:
                            cpu_state->BC--;
                            memory->write(cpu_state->DE++, memory->read(cpu_state->HL++));
                            cycles += 21;

                        cpu_state->Fstatus.status.H = 0;
                        cpu_state->Fstatus.status.PV = 0;
                        cpu_state->Fstatus.status.N = 1; # hmmm, not sure
                        if (cpu_state->BC == 0):
                            cpu_state->Fstatus.status.N = 0;
                            cpu_state->PC += 2;
                            cycles -=5;

                        # CPIR
                    elif (extended_op_code == 0xB1):
                        cpu_state->BC--;
                        tmp8 = cpu_state->Fstatus.status.C;
                        cpu_state->F = FlagTables::getStatusSub(cpu_state->A,memory->read(cpu_state->HL++));
                        cpu_state->Fstatus.status.C = tmp8; 

                        if ((cpu_state->BC == 0)||(cpu_state->Fstatus.status.Z == 1)):
                            cpu_state->Fstatus.status.PV = 0; 
                            cpu_state->PC += 2;
                            cycles += 16;
                        else:
                            cpu_state->Fstatus.status.PV = 1; 
                            cycles += 21;

                        # Should speed this function up a bit
                        # Flags match emulator, not z80 document
                        # OTIR (port)
                    elif (extended_op_code == 0xB3):
                        if (cpu_state->B >= 8):
                            cpu_state->B -= 8;
                            Ports::instance()->portWrite(cpu_state->C, memory->read(cpu_state->HL,8), 8);
                            cpu_state->HL+= 8;
                            cycles += 168;
                        else:
                            cpu_state->B--;
                            Ports::instance()->portWrite(cpu_state->C, memory->read(cpu_state->HL++));
                            cycles += 21;
                        cpu_state->Fstatus.status.S = 0; # Unknown
                        cpu_state->Fstatus.status.H = 0; # Unknown
                        cpu_state->Fstatus.status.PV = 0; # Unknown
                        cpu_state->Fstatus.status.N = 1;
                        cpu_state->Fstatus.status.Z = 0;
                        if (cpu_state->B == 0):
                            cpu_state->Fstatus.status.Z = 1;
                            cpu_state->PC += 2;
                            cycles -= 5;

                        # LDDR
                    elif (extended_op_code == 0xB8):
                        memory->write(cpu_state->DE--, memory->read(cpu_state->HL--));
                        cpu_state->BC--;
                        if (cpu_state->BC == 0):
                            cpu_state->PC += 2;
                            cycles += 16;
                            cpu_state->Fstatus.status.N = 0;
                            cpu_state->Fstatus.status.H = 0;
                            cpu_state->Fstatus.status.PV = 0;
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
