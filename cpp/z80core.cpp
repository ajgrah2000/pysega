#include "z80core.h"
#include "errors.h"
#include "flagtables.h"

#include "ports.h"

#include "instructionstore.h"
#include "instruction.h"

#include <iostream>
#include <exception>


Z80core::Z80core(uint32 &cycles):
                   cycles(cycles)
{
    cpu_state = CPUState::instance();

    cycles = 0;
    nextPossibleInterupt = 0;

    // Register index array, makes for more compact cases
    r[0] = &cpu_state->B;
    r[1] = &cpu_state->C;
    r[2] = &cpu_state->D;
    r[3] = &cpu_state->E;
    r[4] = &cpu_state->H;
    r[5] = &cpu_state->L;
    r[6] = NULL;
    r[7] = &cpu_state->A;


}

Z80core::~Z80core()
{
    std::cout << "Destroying Z80core object" << std::endl;

    InstructionStore::instance()->dump();
}

int Z80core::step(bool loop)
{
    static uint16 tmp16;
    static uint8 tmp8, t8;
    static const Byte *atPC;

    do
    {

        std::cout << std::dec << cycles << " " << nextPossibleInterupt << std::endl;
        // Check for any possible interupts
    if (cycles >= nextPossibleInterupt)
    {
        interuptor->setCycle(cycles);
        nextPossibleInterupt = interuptor->getNextInterupt(cycles);
    }

    atPC = memory->readMulti(cpu_state->PC);
    std::cout << std::dec << cycles << " ";
    std::cout << std::hex << (int) atPC[0] << " " << (int) cpu_state->PC << " (" << (int) atPC[0] << ") ";
    cpu_state->printState();

    InstructionInterface *instruction = 
            InstructionStore::instance()->getInstruction(atPC);

    if (instruction != NULL)
    {
        cycles += instruction->execute(memory);
    }
    else
    {
    switch(atPC[0])
    {
            // EX cpu_state->AF, cpu_state->AF'
        case 0x08:
            tmp16 = cpu_state->AF;
            cpu_state->AF = cpu_state->AF_;
            cpu_state->AF_ = tmp16;

            cpu_state->PC++;
            cycles+=4;
            break;

            // LD (cpu_state->DE), cpu_state->A
        case 0x12:
            memory->write(cpu_state->DE, cpu_state->A);
            cpu_state->PC++;
            cycles += 7;
            break;

            // RLA
        case 0x17:
            tmp8 = cpu_state->A;
            cpu_state->A = (cpu_state->A << 1) | (cpu_state->Fstatus.status.C);
            cpu_state->Fstatus.status.C = (tmp8 & 0x80) >> 7;
            cpu_state->Fstatus.status.H = 0;
            cpu_state->Fstatus.status.N = 0;
            cpu_state->PC++;
            cycles+=4;
            break;

            // Relative jump
            // JR e
        case 0x18:
            cpu_state->PC += (int) (signed char) atPC[1];
            cpu_state->PC += 2;

            cycles += 12;
            break;

            // RRA
        case 0x1F:
            tmp8 = cpu_state->A;
            cpu_state->A = (cpu_state->A >> 1) | (cpu_state->Fstatus.status.C << 7);
            cpu_state->Fstatus.status.C = tmp8 & 0x1;
            cpu_state->Fstatus.status.H = 0;
            cpu_state->Fstatus.status.N = 0;
            cpu_state->PC++;
            cycles+=4;
            break;

            // LD (nn), cpu_state->HL
        case 0x22:
            memory->write(memory->read16(cpu_state->PC+1), cpu_state->L);
            memory->write(memory->read16(cpu_state->PC+1)+1, cpu_state->H);
            cpu_state->PC += 3;

            cycles += 16;
            break;

            // Really need to put this into a table
        case 0x27:
            if (cpu_state->Fstatus.status.N == 0) // cpu_state->Addition instruction
                calculateDAAAdd();
            else // Subtraction instruction
                calculateDAASub();
            cpu_state->PC++;
            cycles+=4;
            break;

            // CPL
        case 0x2F:
            cpu_state->Fstatus.status.H = 1;
            cpu_state->Fstatus.status.N = 1;
            cpu_state->A ^= 0xFF;
            cpu_state->PC++;

            cycles+=4;
            break;

            // JR NC, e
        case 0x30:
            if (cpu_state->Fstatus.status.C == 0)
            {
                cpu_state->PC += (int) (signed char) atPC[1];
                cycles+=5;
            }

            cpu_state->PC += 2;
            cycles += 7;
            break;


            // LD (nn), cpu_state->A
        case 0x32:
            memory->write(memory->read16(cpu_state->PC+1), cpu_state->A);
            cpu_state->PC +=3;

            cycles += 13;
            break;

            // SCF
        case 0x37:
             cpu_state->Fstatus.status.H = 0;
             cpu_state->Fstatus.status.N = 0;
             cpu_state->Fstatus.status.C = 1;
             cpu_state->PC++;
             cycles += 4;
             break;

            // JR C, e
        case 0x38:
            if (cpu_state->Fstatus.status.C == 1)
            {
                cpu_state->PC += (int) (signed char) atPC[1];
                cycles+=5;
            }

            cpu_state->PC += 2;
            cycles += 7;
            break;

            // CCF
        case 0x3F:
            cpu_state->Fstatus.status.H = cpu_state->Fstatus.status.C;
            cpu_state->Fstatus.status.N = 0;
            cpu_state->Fstatus.status.C = 1-cpu_state->Fstatus.status.C; //Invert carry flag
            cpu_state->PC++;
            cycles += 4;
            break;

        case 0x76: // LD (cpu_state->HL), (cpu_state->HL)
            cpu_state->PC++;
            cycles += 7;
            break;

        case 0x86: // cpu_state->ADD (cpu_state->HL) 
            cpu_state->Fstatus.value = FlagTables::getStatusAdd(cpu_state->A,memory->read(cpu_state->HL));
            cpu_state->A = cpu_state->A + memory->read(cpu_state->HL);
            cpu_state->PC++;
            cycles+=7;
            break;

            // cpu_state->ADC r
        case 0x88: // cpu_state->ADC cpu_state->B
        case 0x89: // cpu_state->ADC C
        case 0x8A: // cpu_state->ADC D
        case 0x8B: // cpu_state->ADC E
        case 0x8C: // cpu_state->ADC H
        case 0x8D: // cpu_state->ADC L
        case 0x8F: // cpu_state->ADC cpu_state->A
            cpu_state->A = add8c(cpu_state->A, *r[atPC[0]&0x7], cpu_state->Fstatus.status.C);
            cpu_state->PC++;
            cycles+=4;
            break;

            // cpu_state->ADC (cpu_state->HL)
        case 0x8E:
            cpu_state->A = add8c(cpu_state->A, memory->read(cpu_state->HL), cpu_state->Fstatus.status.C);
            cpu_state->PC++;
            cycles+=7;
            break;

            // SUB r
        case 0x90: // SUB cpu_state->B
        case 0x91: // SUB C
        case 0x92: // SUB D
        case 0x93: // SUB E
        case 0x94: // SUB H
        case 0x95: // SUB L
        case 0x97: // SUB cpu_state->A
            cpu_state->F = FlagTables::getStatusSub(cpu_state->A,*r[atPC[0] & 0x7]);
            cpu_state->A = cpu_state->A - *r[atPC[0] & 0x7];
            cpu_state->PC++;
            cycles+=4;
            break;

            // SUB (cpu_state->HL) 
        case 0x96:
            cpu_state->F = FlagTables::getStatusSub(cpu_state->A,memory->read(cpu_state->HL));
            cpu_state->A = cpu_state->A - memory->read(cpu_state->HL);
            cpu_state->PC++;
            cycles+=7;
            break;

            // Scpu_state->BC r
        case 0x98: // Scpu_state->BC cpu_state->B
        case 0x99: // Scpu_state->BC C
        case 0x9A: // Scpu_state->BC D
        case 0x9B: // Scpu_state->BC E
        case 0x9C: // Scpu_state->BC H
        case 0x9D: // Scpu_state->BC L
        case 0x9F: // Scpu_state->BC cpu_state->A
            cpu_state->A = sub8c(cpu_state->A, *r[atPC[0]&0x7], cpu_state->Fstatus.status.C);
            cpu_state->PC++;
            cycles+=4;
            break;

            // Scpu_state->BC (cpu_state->HL)
        case 0x9E:
            cpu_state->A = sub8c(cpu_state->A, memory->read(cpu_state->HL), cpu_state->Fstatus.status.C);
            cpu_state->PC++;
            cycles+=7;
            break;

            // cpu_state->AND r
        case 0xA0: // cpu_state->AND cpu_state->B
        case 0xA1: // cpu_state->AND C
        case 0xA2: // cpu_state->AND D
        case 0xA3: // cpu_state->AND E
        case 0xA4: // cpu_state->AND H
        case 0xA5: // cpu_state->AND L
            cpu_state->A = cpu_state->A & *r[atPC[0]&0x7];
            cpu_state->PC++;
            cpu_state->Fstatus.value = FlagTables::getStatusAnd(cpu_state->A);

            cycles+=4;
            break;

            // cpu_state->AND (cpu_state->HL)
        case 0xA6:
            cpu_state->A = cpu_state->A & memory->read(cpu_state->HL);
            cpu_state->PC++;
            cpu_state->Fstatus.value = FlagTables::getStatusAnd(cpu_state->A);

            cycles+=7;
            break;

        case 0xA7: // cpu_state->AND cpu_state->A
            cpu_state->PC++;
            cpu_state->Fstatus.value = FlagTables::getStatusAnd(cpu_state->A);
            cycles+=4;
            break;

            // XOR (cpu_state->HL)
        case 0xAE:
            cpu_state->A = cpu_state->A ^ memory->read(cpu_state->HL);
            cpu_state->PC++;
            cpu_state->Fstatus.value = FlagTables::getStatusOr(cpu_state->A);

            cycles += 7;
            break;

            // OR (cpu_state->HL)
        case 0xB6:
            cpu_state->A = cpu_state->A | memory->read(cpu_state->HL);
            cpu_state->PC++;
            cpu_state->Fstatus.value = FlagTables::getStatusOr(cpu_state->A);

            cycles += 7;
            break;

            // CP (cpu_state->HL) 
        case 0xBE:
            cpu_state->F = FlagTables::getStatusSub(cpu_state->A,memory->read(cpu_state->HL));
            cpu_state->PC++;

            cycles+=7;
            break;

            // RET NZ
        case 0xC0:
            if (cpu_state->Fstatus.status.Z == 0)
            {
                cpu_state->PCLow  = memory->read(cpu_state->SP++);
                cpu_state->PCHigh = memory->read(cpu_state->SP++);
                cycles += 11;
            }
            else
            {
                cpu_state->PC++;
                cycles+=5;
            }
            break;

            // POP cpu_state->BC
        case 0xC1:
            cpu_state->C = memory->read(cpu_state->SP++);
            cpu_state->B = memory->read(cpu_state->SP++);

            cpu_state->PC++;

            cycles += 10;
            break;

            // JP NZ, nn
        case 0xC2:
            if (cpu_state->Fstatus.status.Z == 0)
                cpu_state->PC = memory->read16(cpu_state->PC+1);
            else
                cpu_state->PC += 3;

            cycles += 10;
            break;

            // JP nn
        case 0xC3:
            cpu_state->PC = memory->read16(cpu_state->PC+1);

            cycles+=10;
            break;

            // CALL NZ, nn
        case 0xC4:
            cpu_state->PC += 3;
            if (cpu_state->Fstatus.status.Z == 0)
            {
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCHigh);
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCLow);
                cpu_state->PC = memory->read16(cpu_state->PC-2);
                cycles += 7;
            }

            cycles += 10;
            break;

            // PUSH cpu_state->BC
        case 0xC5:
            cpu_state->SP--;
            memory->write(cpu_state->SP, cpu_state->B);
            cpu_state->SP--;
            memory->write(cpu_state->SP, cpu_state->C);
            cpu_state->PC++;

            cycles +=11;
            break;

            // cpu_state->ADD n
        case 0xC6:
            cpu_state->Fstatus.value = FlagTables::getStatusAdd(cpu_state->A,atPC[1]);
            cpu_state->A = cpu_state->A + atPC[1];
            cpu_state->PC+=2;
            cycles+=7;
            break;

            // RST 00h
        case 0xC7:
            cpu_state->PC++;
            cpu_state->SP--;
            memory->write(cpu_state->SP, cpu_state->PCHigh);
            cpu_state->SP--;
            memory->write(cpu_state->SP, cpu_state->PCLow);

            cpu_state->PC = 0x00;

            cycles += 11;
            break;

            // RET Z
        case 0xC8:
            if (cpu_state->Fstatus.status.Z == 1)
            {
                cpu_state->PCLow  = memory->read(cpu_state->SP++);
                cpu_state->PCHigh = memory->read(cpu_state->SP++);
                cycles += 11;
            }
            else
            {
                cpu_state->PC++;
                cycles+=5;
            }
            break;

            // JP Z, nn
        case 0xCA:
            if (cpu_state->Fstatus.status.Z == 1)
                cpu_state->PC = memory->read16(cpu_state->PC+1);
            else
                cpu_state->PC += 3;

            cycles += 10;
            break;

        case 0xCB:
            tmp8 = atPC[1];
            switch (tmp8 & 0xC7)
            {
                // cpu_state->Bit b, r
                case 0x40:
                case 0x41:
                case 0x42:
                case 0x43:
                case 0x44:
                case 0x45:
                case 0x47:
                    cpu_state->Fstatus.status.Z = 
                               (*r[tmp8&0x7] >> ((tmp8 >> 3) & 7)) ^ 0x1;
                    cpu_state->Fstatus.status.PV = FlagTables::calculateParity(*r[tmp8&0x7]);
                    cpu_state->Fstatus.status.H = 1;
                    cpu_state->Fstatus.status.N = 0;
                    cpu_state->Fstatus.status.S = 0;
                    cpu_state->PC += 2;
                    cycles += 8;
                    return 0;

                // cpu_state->Bit b, (cpu_state->HL) 
                case 0x46:
                    cpu_state->Fstatus.status.Z = (memory->read(cpu_state->HL) >> 
                                        ((tmp8 >> 3) & 7)) ^ 0x1;
                    cpu_state->Fstatus.status.H = 1;
                    cpu_state->Fstatus.status.N = 0;
                    cpu_state->Fstatus.status.S = 0;
                    cpu_state->PC += 2;
                    cycles += 12;
                    return 0;

                // RES b, r
                case 0x80:
                case 0x81:
                case 0x82:
                case 0x83:
                case 0x84:
                case 0x85:
                case 0x87:
                    *r[tmp8&0x7] = *r[tmp8&0x7] & ~(0x1 << ((tmp8 >> 3) & 7));
                    cpu_state->PC += 2;
                    cycles += 8;
                    return 0;

                // RES b, (cpu_state->HL) 
                case 0x86:
                    memory->write(cpu_state->HL, 
                        memory->read(cpu_state->HL) & ~(0x1 << ((tmp8 >> 3) & 7)));
                    cpu_state->PC += 2;
                    cycles += 12;
                    return 0;

                // SET b, r
                case 0xC0: // SET b, cpu_state->B
                case 0xC1: // SET b, C
                case 0xC2: // SET b, D
                case 0xC3: // SET b, E
                case 0xC4: // SET b, H
                case 0xC5: // SET b, L
                case 0xC7: // SET b, cpu_state->A
                    *r[tmp8&0x7] = *r[tmp8&0x7] | (0x1 << ((tmp8 >> 3) & 7));
                    cpu_state->PC += 2;
                    cycles += 8;
                    return 0;

                case 0xC6: // SET b, (cpu_state->HL) 
                    memory->write(cpu_state->HL,
                        memory->read(cpu_state->HL) | (0x1 << ((tmp8 >> 3) & 7)));
                    cpu_state->PC += 2;
                    cycles += 15;
                    return 0;

                default:
                    ;
            }
            switch(atPC[1])
            {
                uint8 *r8;

                // RLC r
                case 0x00: // RLC cpu_state->B
                case 0x01: // RLC C
                case 0x02: // RLC D
                case 0x03: // RLC E
                case 0x04: // RLC H
                case 0x05: // RLC L
                case 0x07: // RLC cpu_state->A
                    r8 = r[tmp8 & 0x7];
                    *r8 = (*r8 << 1) | ((*r8 >> 7) & 0x1);
                    cpu_state->Fstatus.value = FlagTables::getStatusOr(*r8);
                    cpu_state->Fstatus.status.C = *r8 & 0x1; // bit-7 of src = bit-0
                    cpu_state->PC+=2;
                    cycles+=8;
                    break;

                case 0x06: // RLC (cpu_state->HL)
                    tmp8 = memory->read(cpu_state->HL);
                    memory->write(cpu_state->HL, (tmp8 << 1) | ((tmp8 >> 7) & 0x1));
                    cpu_state->Fstatus.value = FlagTables::getStatusOr(memory->read(cpu_state->HL));
                    cpu_state->Fstatus.status.C = (tmp8 >> 7) & 0x1; // bit-7 of src
                    cpu_state->PC+=2;
                    cycles+=15;
                    break;

                // RRC r
                case 0x08: // RRC cpu_state->B
                case 0x09: // RRC C
                case 0x0A: // RRC D
                case 0x0B: // RRC E
                case 0x0C: // RRC H
                case 0x0D: // RRC L
                case 0x0F: // RRC cpu_state->A
                    r8 = r[tmp8 & 0x7];
                    *r8 = (*r8 >> 1) | ((*r8 & 0x1) << 7);
                    cpu_state->Fstatus.value = FlagTables::getStatusOr(*r8);
                    cpu_state->Fstatus.status.C = (*r8 >> 7) & 0x1; // bit-0 of src
                    cpu_state->PC+=2;
                    cycles+=8;
                    break;

                case 0x0E: // RRC (cpu_state->HL)
                    tmp8 = memory->read(cpu_state->HL);
                    memory->write(cpu_state->HL,(tmp8 >> 1) | ((tmp8 & 0x1) << 7));
                    cpu_state->Fstatus.value = FlagTables::getStatusOr(memory->read(cpu_state->HL));
                    cpu_state->Fstatus.status.C = tmp8 & 0x1; // bit-0 of src
                    cpu_state->PC+=2;
                    cycles+=8;
                    break;

                    // RL r
                case 0x10: // RL cpu_state->B
                case 0x11: // RL C
                case 0x12: // RL D
                case 0x13: // RL E
                case 0x14: // RL H
                case 0x15: // RL L
                case 0x17: // RL cpu_state->A
                    r8 = r[atPC[1] & 0x7];
                    tmp8 = *r8;
                    *r8 = (*r8 << 1) | (cpu_state->Fstatus.status.C);
                    cpu_state->Fstatus.value = FlagTables::getStatusOr(*r8);
                    cpu_state->Fstatus.status.C = (tmp8 >> 7) & 0x1;
                    cpu_state->PC+=2;
                    cycles+=8;
                    break;

                    // RR r
                case 0x18: // RR cpu_state->B
                case 0x19: // RR C
                case 0x1A: // RR D
                case 0x1B: // RR E
                case 0x1C: // RR H
                case 0x1D: // RR L
                case 0x1F: // RR cpu_state->A
                    r8 = r[atPC[1] & 0x7];
                    tmp8 = *r8;
                    *r8 = (*r8 >> 1) | (cpu_state->Fstatus.status.C << 7);
                    cpu_state->Fstatus.value = FlagTables::getStatusOr(*r8);
                    cpu_state->Fstatus.status.C = tmp8 & 0x1;
                    cpu_state->PC+=2;
                    cycles+=8;
                    break;

                // SLA r
                case 0x20: // SLA cpu_state->B
                case 0x21: // SLA C
                case 0x22: // SLA D
                case 0x23: // SLA E
                case 0x24: // SLA H
                case 0x25: // SLA L
                case 0x27: // SLA cpu_state->A
                    tmp8 = (*r[atPC[1] & 0x7] >> 7) & 0x1;
                    *r[atPC[1] & 0x7] = 
                            *r[atPC[1]&0x7] << 1;
                    cpu_state->Fstatus.value = FlagTables::getStatusOr(*r[atPC[1]&0x7]);
                    cpu_state->Fstatus.status.C = tmp8;

                    cpu_state->PC += 2;
                    cycles += 8;
                    break;

                case 0x26: // SLA (cpu_state->HL) 
                    tmp8 = (memory->read(cpu_state->HL) >> 7) & 0x1;
                    memory->write(cpu_state->HL, memory->read(cpu_state->HL) << 1);
                    cpu_state->Fstatus.value = FlagTables::getStatusOr(memory->read(cpu_state->HL));
                    cpu_state->Fstatus.status.C = tmp8;

                    cpu_state->PC += 2;
                    cycles += 15;
                    break;

                // SRA r
                case 0x28: // SRA cpu_state->B
                case 0x29: // SRA C
                case 0x2A: // SRA D
                case 0x2B: // SRA E
                case 0x2C: // SRA H
                case 0x2D: // SRA L
                case 0x2F: // SRA cpu_state->A
                    r8 = r[atPC[1]&0x7];
                    tmp8 = *r8;
                    *r8 = (*r8 & 0x80) | ((*r8 >> 1) & 0x7F);

                    cpu_state->Fstatus.value = FlagTables::getStatusOr(*r8);
                    cpu_state->Fstatus.status.C = tmp8 & 0x1;

                    cpu_state->PC += 2;
                    cycles += 8;
                    break;

                case 0x2E: // SRA (cpu_state->HL)
                    tmp8 = memory->read(cpu_state->HL);
                    memory->write(cpu_state->HL, (tmp8 & 0x80) | ((tmp8 >> 1) & 0x7F));

                    cpu_state->Fstatus.value = FlagTables::getStatusOr(memory->read(cpu_state->HL));
                    cpu_state->Fstatus.status.C = tmp8 & 0x1;

                    cpu_state->PC += 2;
                    cycles += 15;
                    break;

                // SLL r
                case 0x30: // SLL cpu_state->B
                case 0x31: // SLL C
                case 0x32: // SLL D
                case 0x33: // SLL E
                case 0x34: // SLL H
                case 0x35: // SLL L
                case 0x37: // SLL cpu_state->A
                    tmp8 = (*r[atPC[1] & 0x7] >> 7) & 0x1;
                    *r[atPC[1] & 0x7] = 
                            *r[atPC[1]&0x7] << 1 | 0x1;
                    cpu_state->Fstatus.value = FlagTables::getStatusOr(*r[atPC[1]&0x7]);
                    cpu_state->Fstatus.status.C = tmp8;

                    cpu_state->PC += 2;
                    cycles += 8;
                    break;

                case 0x36: // SLL (cpu_state->HL) 
                    tmp8 = (memory->read(cpu_state->HL) >> 7) & 0x1;
                    memory->write(cpu_state->HL, memory->read(cpu_state->HL) << 1 | 0x1);
                    cpu_state->Fstatus.value = FlagTables::getStatusOr(memory->read(cpu_state->HL));
                    cpu_state->Fstatus.status.C = tmp8;

                    cpu_state->PC += 2;
                    cycles += 15;
                    break;

                // SRL r
                case 0x38: // SRL cpu_state->B
                case 0x39: // SRL C
                case 0x3A: // SRL D
                case 0x3B: // SRL E
                case 0x3C: // SRL H
                case 0x3D: // SRL L
                case 0x3F: // SRL cpu_state->A
                    r8 = r[atPC[1]&0x7];
                    tmp8 = *r8;
                    *r8 = (*r8 >> 1) & 0x7F;

                    cpu_state->Fstatus.value = FlagTables::getStatusOr(*r8);
                    cpu_state->Fstatus.status.C = tmp8 & 0x1;

                    cpu_state->PC += 2;
                    cycles += 8;
                    break;

                case 0x3E: // SRL (cpu_state->HL)
                    tmp8 = memory->read(cpu_state->HL);
                    memory->write(cpu_state->HL, (tmp8 >> 1) & 0x7F);

                    cpu_state->Fstatus.value = FlagTables::getStatusOr(memory->read(cpu_state->HL));
                    cpu_state->Fstatus.status.C = tmp8 & 0x1;

                    cpu_state->PC += 2;
                    cycles += 15;
                    break;

                default:
                    errors::warning("OP 0xCB n, value n unsupported");
                    return -1;
            }
            break;

            // CALL Z, nn
        case 0xCC:
            cpu_state->PC += 3;
            if (cpu_state->Fstatus.status.Z == 1)
            {
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCHigh);
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCLow);
                cpu_state->PC = memory->read16(cpu_state->PC-2);

                cycles += 7;
            }
            else
                cycles += 10;
            break;

            // CALL nn
        case 0xCD:
            cpu_state->PC += 3;
            cpu_state->SP--;
            memory->write(cpu_state->SP, cpu_state->PCHigh);
            cpu_state->SP--;
            memory->write(cpu_state->SP, cpu_state->PCLow);
            cpu_state->PC = memory->read16(cpu_state->PC-2);

            cycles += 17;
            break;

            // cpu_state->ADC nn
        case 0xCE:
            cpu_state->A = add8c(cpu_state->A, atPC[1], cpu_state->Fstatus.status.C);
            cpu_state->PC+=2;
            cycles+=4;
            break;

            // RST 08h
        case 0xCF:
            cpu_state->PC++;
            cpu_state->SP--;
            memory->write(cpu_state->SP, cpu_state->PCHigh);
            cpu_state->SP--;
            memory->write(cpu_state->SP, cpu_state->PCLow);

            cpu_state->PC = 0x08;

            cycles += 11;
            break;

            // RET NC
        case 0xD0:
            if (cpu_state->Fstatus.status.C == 0)
            {
                cpu_state->PCLow  = memory->read(cpu_state->SP++);
                cpu_state->PCHigh = memory->read(cpu_state->SP++);
                cycles += 11;
            }
            else
            {
                cpu_state->PC++;
                cycles+=5;
            }
            break;

              // POP cpu_state->DE
        case 0xD1:
            cpu_state->E = memory->read(cpu_state->SP++);
            cpu_state->D = memory->read(cpu_state->SP++);
            cpu_state->PC++;
            cycles += 10;
            break;

            // CALL NC, nn  
        case 0xD4:
            cpu_state->PC += 3;
            if (cpu_state->Fstatus.status.C == 0)
            {
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCHigh);
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCLow);
                cpu_state->PC = memory->read16(cpu_state->PC-2);

                cycles += 7;
            }
            else
                cycles += 10;
            break;

            // PUSH cpu_state->DE
        case 0xD5:
            cpu_state->SP--;
            memory->write(cpu_state->SP, cpu_state->D);
            cpu_state->SP--;
            memory->write(cpu_state->SP, cpu_state->E);
            cpu_state->PC++;

            cycles +=11;
            break;

            // SUB n
        case 0xD6:
            cpu_state->F = FlagTables::getStatusSub(cpu_state->A,atPC[1]);
            cpu_state->A = cpu_state->A - atPC[1];
            cpu_state->PC += 2;
            cycles += 7;
            break;

            // RST 10h
        case 0xD7:
            cpu_state->PC++;
            cpu_state->SP--;
            memory->write(cpu_state->SP, cpu_state->PCHigh);
            cpu_state->SP--;
            memory->write(cpu_state->SP, cpu_state->PCLow);

            cpu_state->PC = 0x10;

            cycles += 11;
            break;
            
            // RET C
        case 0xD8:
            if (cpu_state->Fstatus.status.C == 1)
            {
                cpu_state->PCLow  = memory->read(cpu_state->SP++);
                cpu_state->PCHigh = memory->read(cpu_state->SP++);
                cycles += 11;
            }
            else
            {
                cpu_state->PC++;
                cycles+=5;
            }
            break;

            // IN cpu_state->A, (N)
        case 0xDB:
            cpu_state->A = Ports::instance()->portRead(atPC[1]);
            cpu_state->PC += 2;
            cycles += 11;
            break;

            // Call C, nn
        case 0xDC:
            cpu_state->PC += 3;
            if (cpu_state->Fstatus.status.C == 1)
            {
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCHigh);
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCLow);
                cpu_state->PC = memory->read16(cpu_state->PC-2);
                cycles += 17;
            }
            else
                cycles += 10;

            break;

            // Scpu_state->BC n 
        case 0xDE:
            cpu_state->A = sub8c(cpu_state->A, atPC[1], cpu_state->Fstatus.status.C);
            cpu_state->PC+=2;
            cycles+=7;
            break;

            // RST 18h
        case 0xDF:
            cpu_state->PC++;
            cpu_state->SP--;
            memory->write(cpu_state->SP, cpu_state->PCHigh);
            cpu_state->SP--;
            memory->write(cpu_state->SP, cpu_state->PCLow);

            cpu_state->PC = 0x18;

            cycles += 11;
            break;

            // RET PO  
        case 0xE0:
            if (cpu_state->Fstatus.status.PV == 0)
            {
                cpu_state->PCLow  = memory->read(cpu_state->SP++);
                cpu_state->PCHigh = memory->read(cpu_state->SP++);
                cycles += 11;
            }
            else
            {
                cpu_state->PC++;
                cycles+=5;
            }
            break;

            // POP cpu_state->HL
        case 0xE1:
            cpu_state->L = memory->read(cpu_state->SP++);
            cpu_state->H = memory->read(cpu_state->SP++);

            cpu_state->PC++;

            cycles += 10;
            break;

            // JP PO, nn   Parity Odd 
        case 0xE2:
            if (cpu_state->Fstatus.status.PV == 0)
                cpu_state->PC = memory->read16(cpu_state->PC+1);
            else
                cpu_state->PC += 3;

            cycles +=10;
            break;

            // EX (cpu_state->SP), cpu_state->HL
        case 0xE3:
            tmp8 = memory->read(cpu_state->SP);
            memory->write(cpu_state->SP, cpu_state->L);
            cpu_state->L = tmp8;
            tmp8 = memory->read(cpu_state->SP+1);
            memory->write(cpu_state->SP+1, cpu_state->H);
            cpu_state->H = tmp8;
            cpu_state->PC++;
            cycles += 19;
            break;

            // CALL PO, nn 
        case 0xE4:
            cpu_state->PC += 3;
            if (cpu_state->Fstatus.status.PV == 0)
            {
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCHigh);
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCLow);
                cpu_state->PC = memory->read16(cpu_state->PC-2);
                cycles += 7;
            }

            cycles += 10;
            break;


            // PUSH cpu_state->HL
        case 0xE5:
            cpu_state->SP--;
            memory->write(cpu_state->SP, cpu_state->H);
            cpu_state->SP--;
            memory->write(cpu_state->SP, cpu_state->L);
            cpu_state->PC++;

            cycles +=11;
            break;

            // RST 20h
        case 0xE7:
            cpu_state->PC++;
            cpu_state->SP--;
            memory->write(cpu_state->SP, cpu_state->PCHigh);
            cpu_state->SP--;
            memory->write(cpu_state->SP, cpu_state->PCLow);

            cpu_state->PC = 0x20;

            cycles += 11;
            break;

            // RET PE  
        case 0xE8:
            if (cpu_state->Fstatus.status.PV == 1)
            {
                cpu_state->PCLow  = memory->read(cpu_state->SP++);
                cpu_state->PCHigh = memory->read(cpu_state->SP++);
                cycles += 11;
            }
            else
            {
                cpu_state->PC++;
                cycles+=5;
            }
            break;

            // Don't know how many cycles
            // LD cpu_state->PC, cpu_state->HL
        case 0xE9:
            cpu_state->PC = cpu_state->HL;
            cycles+=6;
            break;

            // JP PE, nn   Parity Even 
        case 0xEA:
            if (cpu_state->Fstatus.status.PV == 1)
                cpu_state->PC = memory->read16(cpu_state->PC+1);
            else
                cpu_state->PC += 3;

            cycles +=10;
            break;

            // EX cpu_state->DE, cpu_state->HL
        case 0xEB:
            tmp16 = cpu_state->DE;
            cpu_state->DE = cpu_state->HL;
            cpu_state->HL = tmp16;
            cpu_state->PC++;
            cycles+=4;
            break;

            // CALL PE, nn
        case 0xEC:
            cpu_state->PC += 3;
            if (cpu_state->Fstatus.status.PV == 1)
            {
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCHigh);
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCLow);
                cpu_state->PC = memory->read16(cpu_state->PC-2);
                cycles += 7;
            }

            cycles += 10;
            break;

            // XOR n
        case 0xEE: 
            cpu_state->A = cpu_state->A ^ atPC[1];
            cpu_state->Fstatus.value = FlagTables::getStatusOr(cpu_state->A);
            cpu_state->PC+=2;
            cycles+=7;
            break;

            // RST 28h
        case 0xEF:
            cpu_state->PC++;
            cpu_state->SP--;
            memory->write(cpu_state->SP, cpu_state->PCHigh);
            cpu_state->SP--;
            memory->write(cpu_state->SP, cpu_state->PCLow);

            cpu_state->PC = 0x28;

            cycles += 11;
            break;

            // RET P, if Positive
        case 0xF0:
            if (cpu_state->Fstatus.status.S == 0)
            {
                cpu_state->PCLow  = memory->read(cpu_state->SP++);
                cpu_state->PCHigh = memory->read(cpu_state->SP++);
                cycles += 11;
            }
            else
            {
                cpu_state->PC++;
                cycles+=5;
            }
            break;

            // POP cpu_state->AF
        case 0xF1:
            cpu_state->F = memory->read(cpu_state->SP++);
            cpu_state->A = memory->read(cpu_state->SP++);

            cpu_state->PC++;

            cycles+=10;
            break;

            // JP P, nn    if Positive
        case 0xF2:
            if (cpu_state->Fstatus.status.S == 0)
                cpu_state->PC = memory->read16(cpu_state->PC+1);
            else
                cpu_state->PC += 3;

            cycles +=10;
            break;

          // Disable interupts
          // DI
        case 0xF3:
            cpu_state->IFF1 = 0;
            cpu_state->IFF2 = 0;
            cpu_state->PC++;

            cycles+=4;
            break;

            // CALL P, nn  if Positive
        case 0xF4:
            cpu_state->PC += 3;
            if (cpu_state->Fstatus.status.S == 0)
            {
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCHigh);
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCLow);
                cpu_state->PC = memory->read16(cpu_state->PC-2);
                cycles += 7;
            }

            cycles += 10;
            break;

            // PUSH cpu_state->AF
        case 0xF5:
            cpu_state->SP--;
            memory->write(cpu_state->SP, cpu_state->A);
            cpu_state->SP--;
            memory->write(cpu_state->SP, cpu_state->F);
            cpu_state->PC++;

            cycles+=11;
            break;

            // OR n
        case 0xF6:
            cpu_state->A = cpu_state->A | atPC[1];
            cpu_state->Fstatus.value = FlagTables::getStatusOr(cpu_state->A);
            cpu_state->PC += 2;
            cycles+=7;
            break;

            // RST 30h
        case 0xF7:
            cpu_state->PC++;
            cpu_state->SP--;
            memory->write(cpu_state->SP, cpu_state->PCHigh);
            cpu_state->SP--;
            memory->write(cpu_state->SP, cpu_state->PCLow);

            cpu_state->PC = 0x30;

            cycles += 11;
            break;

            // RET M  if Negative
        case 0xF8:
            if (cpu_state->Fstatus.status.S == 1)
            {
                cpu_state->PCLow  = memory->read(cpu_state->SP++);
                cpu_state->PCHigh = memory->read(cpu_state->SP++);
                cycles += 11;
            }
            else
            {
                cpu_state->PC++;
                cycles+=5;
            }
            break;

            // LD cpu_state->SP, cpu_state->HL
        case 0xF9:
            cpu_state->SP = cpu_state->HL;
            cpu_state->PC++;
            cycles+=6;
            break;

            // JP M, nn    if Negative
        case 0xFA:
            if (cpu_state->Fstatus.status.S == 1)
                cpu_state->PC = memory->read16(cpu_state->PC+1);
            else
                cpu_state->PC += 3;

            cycles +=10;
            break;

            // Enable interupts
            // EI
        case 0xFB:
            cpu_state->PC++;

            // Process next instruction before enabling interupts
            step(false); // Single step, no loop

            cpu_state->IFF1 = 1;
            cpu_state->IFF2 = 1;
            cycles+=4;

              // Check for any pending interupts
            if (interuptor->pollInterupts(cycles) == true)
                interupt();

            break;

            // CALL M, nn  if Negative
        case 0xFC:
            cpu_state->PC += 3;
            if (cpu_state->Fstatus.status.S == 1)
            {
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCHigh);
                cpu_state->SP--;
                memory->write(cpu_state->SP, cpu_state->PCLow);
                cpu_state->PC = memory->read16(cpu_state->PC-2);

                cycles += 7;
            }
            else
                cycles += 10;
            break;

            // RST 38h
        case 0xFF:
            cpu_state->PC++;
            cpu_state->SP--;
            memory->write(cpu_state->SP, cpu_state->PCHigh);
            cpu_state->SP--;
            memory->write(cpu_state->SP, cpu_state->PCLow);

            cpu_state->PC = 0x38;

            cycles += 11;
            break;

        case 0xDD:
            // Temporary, until `all instructions are covered'
            instruction = 
                    InstructionStore::instance()->getExtendedDD(&atPC[1]);
            if (instruction != NULL)
            {
                cycles += instruction->execute(memory);
            }
            else
            {
            switch(atPC[1])
            {
                // LD cpu_state->IX, nn
                case 0x21:
                    cpu_state->IX = memory->read16(cpu_state->PC+2);
                    cpu_state->PC += 4;

                    cycles +=20;
                    break;

                    // LD (nn), cpu_state->IX
                case 0x22:
                    memory->write(memory->read16(cpu_state->PC+2), cpu_state->IXLow);
                    memory->write(memory->read16(cpu_state->PC+2)+1, cpu_state->IXHigh);
                    cpu_state->PC += 4;

                    cycles += 20;
                    break;

                    // LD cpu_state->IX, (nn)
                case 0x2A:
                    cpu_state->IX = memory->read16(memory->read16(cpu_state->PC+2));
                    cpu_state->PC += 4;

                    cycles += 20;
                    break;

                    // INC (cpu_state->IX+d)
                case 0x34:
                    tmp16 = cpu_state->IX + (int) (signed char) atPC[2];
                    memory->write(tmp16, memory->read(tmp16) + 1);
                    cpu_state->F = (cpu_state->F & Instruction::FLAG_MASK_INC8) | 
                FlagTables::getStatusInc8(memory->read(tmp16));
                    cpu_state->PC+=3;
                    cycles+=23;
                    break;

                    // cpu_state->DEC (cpu_state->IX+d)
                case 0x35:
                    tmp16 = cpu_state->IX + (int) (signed char) atPC[2];
                    memory->write(tmp16, memory->read(tmp16) - 1);
                    cpu_state->F = (cpu_state->F & Instruction::FLAG_MASK_DEC8) | FlagTables::getStatusDec8(memory->read(tmp16));
                    cpu_state->PC+=3;
                    cycles+=23;
                    break;

                    // LD (cpu_state->IX + d), n
                case 0x36:
                    tmp16 = cpu_state->IX + (int) (signed char) atPC[2];
                    memory->write(tmp16, atPC[3]);
                    cpu_state->PC += 4;
                    cycles += 19;
                    break;

                    // LD r, (cpu_state->IX+e)
                case 0x46:
                case 0x4E:
                case 0x56:
                case 0x5E:
                case 0x66:
                case 0x6E:
                case 0x7E:
                    *r[(atPC[1] >> 3) & 0x7] = 
                                memory->read(cpu_state->IX + 
                                     (int) (signed char) atPC[2]);
                    cpu_state->PC += 3;
                    cycles += 19;
                    break;

                    // LD (cpu_state->IX+d), r
                case 0x70:
                case 0x71:
                case 0x72:
                case 0x73:
                case 0x74:
                case 0x75:
                case 0x77:
                    memory->write(cpu_state->IX + (int) (signed char) atPC[2],
                                  *r[atPC[1] & 0x7]); 
                    cpu_state->PC += 3;
                    cycles += 19;
                    break;

                    // cpu_state->ADD cpu_state->A,(cpu_state->IX+d)
                case 0x86:
                    tmp8 = memory->read(cpu_state->IX + 
                                     (int) (signed char) atPC[2]);
                    cpu_state->Fstatus.value = FlagTables::getStatusAdd(cpu_state->A, tmp8);
                    cpu_state->A = cpu_state->A + tmp8;
                    cpu_state->PC += 3;
                    cycles += 19;
                    break;

                    // cpu_state->ADC (cpu_state->IX + d)
                case 0x8E:
                    cpu_state->A = add8c(cpu_state->A, memory->read(cpu_state->IX + (int) (signed char)
                                    atPC[2]), cpu_state->Fstatus.status.C);
                    cpu_state->PC+=3;
                    cycles+=19;
                    break;

                    // SUB (cpu_state->IX + d)
                case 0x96:
                    tmp8 = memory->read(cpu_state->IX + 
                                     (int) (signed char) atPC[2]);
                    cpu_state->F = FlagTables::getStatusSub(cpu_state->A,tmp8);
                    cpu_state->A = cpu_state->A - tmp8;
                    cpu_state->PC += 3;
                    cycles += 19;
                    break;

                    // cpu_state->AND (cpu_state->IX + d)
                case 0xA6:
                    cpu_state->A = cpu_state->A & memory->read(cpu_state->IX +
                                     (int) (signed char) atPC[2]);
                    cpu_state->PC+=3;
                    cpu_state->Fstatus.value = FlagTables::getStatusAnd(cpu_state->A);

                    cycles+=19;
                    break;

                    // XOR (cpu_state->IX + d)
                case 0xAE:
                    cpu_state->A = cpu_state->A ^ memory->read(cpu_state->IX +
                                     (int) (signed char) atPC[2]);
                    cpu_state->PC+=3;
                    cpu_state->Fstatus.value = FlagTables::getStatusOr(cpu_state->A);

                    cycles += 19;
                    break;

                    // OR (cpu_state->IX + d)
                case 0xB6:
                    tmp8 = memory->read(cpu_state->IX + 
                                     (int) (signed char) atPC[2]);
                    cpu_state->A = cpu_state->A | tmp8;
                    cpu_state->Fstatus.value = FlagTables::getStatusOr(cpu_state->A);
                    cpu_state->PC += 3;
                    cycles += 19;
                    break;

                    // CP (cpu_state->IX + d)
                case 0xBE:
                    tmp8 = memory->read(cpu_state->IX + 
                                     (int) (signed char) atPC[2]);
                    cpu_state->F = FlagTables::getStatusSub(cpu_state->A,tmp8);
                    cpu_state->PC+=3;
                    cycles+=19;
                    break;

                // Probably should turn this into a lookup table
                case 0xCB:
                    tmp16 = cpu_state->IX + (int) (signed char) atPC[2];
                    tmp8 = memory->read(tmp16);
                    t8 = atPC[3];

                    if ((t8 & 0xC7) == 0x46) // cpu_state->BIT b, (cpu_state->IX + d)
                    {
                        tmp8 = (tmp8 >> ((t8 & 0x38) >> 3)) & 0x1;
                        cpu_state->Fstatus.status.Z = tmp8 ^ 0x1;;
                        cpu_state->Fstatus.status.PV = FlagTables::calculateParity(tmp8);
                        cpu_state->Fstatus.status.H = 1;
                        cpu_state->Fstatus.status.N = 0;
                        cpu_state->Fstatus.status.S = 0;
                    }
                    else if ((t8 & 0xC7) == 0x86) // RES b, (cpu_state->IX + d)
                    {
                        tmp8 = tmp8 & ~(0x1 << ((t8 >> 3) & 0x7));
                        memory->write(tmp16,tmp8);
                    }
                    else if ((t8 & 0xC7) == 0xC6) // SET b, (cpu_state->IX + d)
                    {
                        tmp8 = tmp8 | (0x1 << ((t8 >> 3) & 0x7));
                        memory->write(tmp16,tmp8);
                    }
                    else
                        errors::unsupported("Instruction arg for 0xDD 0xCB");

                    cpu_state->PC += 4;

                    cycles += 23;
                    break;

                // POP cpu_state->IX
                case 0xE1:
                    cpu_state->IXLow = memory->read(cpu_state->SP++);
                    cpu_state->IXHigh = memory->read(cpu_state->SP++);
                    cpu_state->PC += 2;
                    cycles += 14;
                    break;

                    // EX (cpu_state->SP), cpu_state->IX
                case 0xE3:
                    tmp8 = memory->read(cpu_state->SP);
                    memory->write(cpu_state->SP, cpu_state->IXLow);
                    cpu_state->IXLow = tmp8;
                    tmp8 = memory->read(cpu_state->SP+1);
                    memory->write(cpu_state->SP+1, cpu_state->IXHigh);
                    cpu_state->IXHigh = tmp8;
                    cpu_state->PC+=2;
                    cycles += 23;
                    break;


                // PUSH cpu_state->IX
                case 0xE5:
                    cpu_state->SP--;
                    memory->write(cpu_state->SP, cpu_state->IXHigh);
                    cpu_state->SP--;
                    memory->write(cpu_state->SP, cpu_state->IXLow);
                    cpu_state->PC += 2;

                    cycles +=15;
                    break;

                    // Don't know how many cycles
                    // LD cpu_state->PC, cpu_state->IX
                case 0xE9:
                    cpu_state->PC = cpu_state->IX;
                    cycles+=6;
                    break;

                default:
    std::cout << "Unsupported op code DD " << std::hex << 
                            (int) atPC[1] << std::endl;
                    return -1;
            }
            }
            break;

        case 0xFD:
            // Temporary, until `all instructions are covered'
            instruction = 
                    InstructionStore::instance()->getExtendedFD(&atPC[1]);
            if (instruction != NULL)
            {
                cycles += instruction->execute(memory);
            }
            else
            {
            switch(atPC[1])
            {
                // LD cpu_state->IY, (nn)
                case 0x21:
                    cpu_state->IY = memory->read16(cpu_state->PC+2);
                    cpu_state->PC += 4;
                    cycles += 20;
                    break;

                    // LD (nn), cpu_state->IY
                case 0x22:
                    memory->write(memory->read16(cpu_state->PC+2), cpu_state->IYLow);
                    memory->write(memory->read16(cpu_state->PC+2)+1, cpu_state->IYHigh);
                    cpu_state->PC += 4;

                    cycles += 20;
                    break;

                    // LD cpu_state->IY, (nn)
                case 0x2A:
                    cpu_state->IY = memory->read16(memory->read16(cpu_state->PC+2));
                    cpu_state->PC += 4;

                    cycles += 20;
                    break;

                    // INC (cpu_state->IY+d)
                case 0x34:
                    tmp16 = cpu_state->IY + (int) (signed char) atPC[2];
                    memory->write(tmp16, memory->read(tmp16) + 1);
                    cpu_state->F = (cpu_state->F & Instruction::FLAG_MASK_INC8) | 
                FlagTables::getStatusInc8(memory->read(tmp16));
                    cpu_state->PC+=3;
                    cycles+=23;
                    break;

                    // cpu_state->DEC (cpu_state->IY+d)
                case 0x35:
                    tmp16 = cpu_state->IY + (int) (signed char) atPC[2];
                    memory->write(tmp16, memory->read(tmp16) - 1);
                    cpu_state->F = (cpu_state->F & Instruction::FLAG_MASK_DEC8) | FlagTables::getStatusDec8(memory->read(tmp16));
                    cpu_state->PC+=3;
                    cycles+=23;
                    break;

                    // LD (cpu_state->IY + d), n
                case 0x36:
                    tmp16 = cpu_state->IY + (int) (signed char) atPC[2];
                    memory->write(tmp16, atPC[3]);
                    cpu_state->PC += 4;
                    cycles += 19;
                    break;

                    // LD r, (cpu_state->IY+e)
                case 0x46:
                case 0x4E:
                case 0x56:
                case 0x5E:
                case 0x66:
                case 0x6E:
                case 0x7E:
                    *r[(atPC[1] >> 3) & 0x7] = 
                                memory->read(cpu_state->IY + 
                                     (int) (signed char) atPC[2]);
                    cpu_state->PC += 3;
                    cycles += 19;
                    break;

                    // LD (cpu_state->IY+d), r
                case 0x70: // LD (cpu_state->IY+d), cpu_state->B
                case 0x71: // LD (cpu_state->IY+d), C
                case 0x72: // LD (cpu_state->IY+d), D
                case 0x73: // LD (cpu_state->IY+d), E
                case 0x74: // LD (cpu_state->IY+d), H
                case 0x75: // LD (cpu_state->IY+d), L
                case 0x77: // LD (cpu_state->IY+d), cpu_state->A
                    memory->write(cpu_state->IY + (int) (signed char) atPC[2],
                                  *r[atPC[1] & 0x7]); 
                    cpu_state->PC += 3;
                    cycles += 19;
                    break;

                    // cpu_state->ADD cpu_state->A,(cpu_state->IY+d)
                case 0x86:
                    tmp8 = memory->read(cpu_state->IY + 
                                     (int) (signed char) atPC[2]);
                    cpu_state->Fstatus.value = FlagTables::getStatusAdd(cpu_state->A,tmp8);
                    cpu_state->A = cpu_state->A + tmp8;
                    cpu_state->PC += 3;
                    cycles += 19;
                    break;

                    // cpu_state->ADC (cpu_state->IY + d)
                case 0x8E:
                    cpu_state->A = add8c(cpu_state->A, memory->read(cpu_state->IY + (int) (signed char)
                                    atPC[2]), cpu_state->Fstatus.status.C);
                    cpu_state->PC+=3;
                    cycles+=19;
                    break;

                    // SUB (cpu_state->IY + d)
                case 0x96:
                    tmp8 = memory->read(cpu_state->IY + 
                                     (int) (signed char) atPC[2]);
                    cpu_state->F = FlagTables::getStatusSub(cpu_state->A,tmp8);
                    cpu_state->A = cpu_state->A - tmp8;
                    cpu_state->PC += 3;
                    cycles += 19;
                    break;

                    // cpu_state->AND (cpu_state->IY + d)
                case 0xA6:
                    cpu_state->A = cpu_state->A & memory->read(cpu_state->IY +
                                     (int) (signed char) atPC[2]);
                    cpu_state->PC+=3;
                    cpu_state->Fstatus.value = FlagTables::getStatusAnd(cpu_state->A);

                    cycles+=19;
                    break;

                    // XOR (cpu_state->IY + d)
                case 0xAE:
                    cpu_state->A = cpu_state->A ^ memory->read(cpu_state->IY +
                                     (int) (signed char) atPC[2]);
                    cpu_state->PC+=3;
                    cpu_state->Fstatus.value = FlagTables::getStatusOr(cpu_state->A);

                    cycles += 19;
                    break;

                    // OR (cpu_state->IY + d)
                case 0xB6:
                    tmp8 = memory->read(cpu_state->IY + 
                                     (int) (signed char) atPC[2]);
                    cpu_state->A = cpu_state->A | tmp8;
                    cpu_state->Fstatus.value = FlagTables::getStatusOr(cpu_state->A);
                    cpu_state->PC += 3;
                    cycles += 19;
                    break;

                    // CP (cpu_state->IY + d)
                case 0xBE:
                    tmp8 = memory->read(cpu_state->IY + 
                                     (int) (signed char) atPC[2]);
                    cpu_state->F = FlagTables::getStatusSub(cpu_state->A,tmp8);
                    cpu_state->PC+=3;
                    cycles+=19;
                    break;

                // Probably should turn this into a lookup table
                case 0xCB:
                    tmp16 = cpu_state->IY + (int) (signed char) atPC[2];
                    tmp8 = memory->read(tmp16);
                    t8 = atPC[3];

                    if ((t8 & 0xC7) == 0x46) // cpu_state->BIT b, (cpu_state->IY + d)
                    {
                        tmp8 = (tmp8 >> ((t8 & 0x38) >> 3)) & 0x1;
                        cpu_state->Fstatus.status.Z = tmp8 ^ 0x1;;
                        cpu_state->Fstatus.status.PV = FlagTables::calculateParity(tmp8);
                        cpu_state->Fstatus.status.H = 1;
                        cpu_state->Fstatus.status.N = 0;
                        cpu_state->Fstatus.status.S = 0;
                    }
                    else if ((t8 & 0xC7) == 0x86) // RES b, (cpu_state->IY + d)
                    {
                        tmp8 = tmp8 & ~(0x1 << ((t8 >> 3) & 0x7));
                        memory->write(tmp16,tmp8);
                    }
                    else if ((t8 & 0xC7) == 0xC6) // SET b, (cpu_state->IY + d)
                    {
                        tmp8 = tmp8 | (0x1 << ((t8 >> 3) & 0x7));
                        memory->write(tmp16,tmp8);
                    }
                    else
                        errors::unsupported("Instruction arg for 0xFD 0xCB");

                    cpu_state->PC += 4;

                    cycles += 23;
                    break;
                   
                // POP cpu_state->IY
                case 0xE1:
                    cpu_state->IYLow = memory->read(cpu_state->SP++);
                    cpu_state->IYHigh = memory->read(cpu_state->SP++);
                    cpu_state->PC += 2;
                    cycles += 14;
                    break;

                    // EX (cpu_state->SP), cpu_state->IY
                case 0xE3:
                    tmp8 = memory->read(cpu_state->SP);
                    memory->write(cpu_state->SP, cpu_state->IYLow);
                    cpu_state->IYLow = tmp8;
                    tmp8 = memory->read(cpu_state->SP+1);
                    memory->write(cpu_state->SP+1, cpu_state->IYHigh);
                    cpu_state->IYHigh = tmp8;
                    cpu_state->PC+=2;
                    cycles += 23;
                    break;

                // PUSH cpu_state->IY
                case 0xE5:
                    cpu_state->SP--;
                    memory->write(cpu_state->SP, cpu_state->IYHigh);
                    cpu_state->SP--;
                    memory->write(cpu_state->SP, cpu_state->IYLow);
                    cpu_state->PC += 2;

                    cycles +=15;
                    break;

                    // Don't know how many cycles
                    // LD cpu_state->PC, cpu_state->IY
                case 0xE9:
                    cpu_state->PC = cpu_state->IY;
                    cycles+=6;
                    break;

                default:
    std::cout << "Unsupported op code FD " <<
                            (int) atPC[1] << std::endl;
                    return -1;
            }
            }

            break;

          // Extended opcodes
        case 0xED:
            // Temporary, until `all instructions are covered'
            instruction = 
                    InstructionStore::instance()->getExtendedED(&atPC[1]);
            if (instruction != NULL)
            {
                cycles += instruction->execute(memory);
            }
            else
            {
            switch(atPC[1])
            {
                  // IN r, (C)
                case 0x40:
                case 0x48:
                case 0x50:
                case 0x58:
                case 0x60:
                case 0x68:
                case 0x78:
                    *r[(atPC[1] >> 3) & 0x7] = Ports::instance()->portRead(cpu_state->C);
                    cpu_state->PC += 2;
                    cycles += 12;
                    break;

                  // OUT (C), r
                case 0x41: // OUT (C), cpu_state->B
                case 0x49: // OUT (C), C
                case 0x51: // OUT (C), D
                case 0x59: // OUT (C), E
                case 0x61: // OUT (C), H
                case 0x69: // OUT (C), L
                case 0x79: // OUT (C), cpu_state->A
                    Ports::instance()->portWrite(cpu_state->C, *r[(atPC[1] >> 3) & 0x7]);
                    cpu_state->PC += 2;
                    cycles +=3;
                    break;

                  // Scpu_state->BC cpu_state->HL, cpu_state->BC
                case 0x42:
                    cpu_state->HL = sub16c(cpu_state->HL, cpu_state->BC, cpu_state->Fstatus.status.C);

                    cpu_state->PC += 2;
                    cycles += 15;
                    break;

                    // LD (nn), cpu_state->BC
                case 0x43:
                    memory->write(memory->read16(cpu_state->PC+2), cpu_state->C);
                    memory->write(memory->read16(cpu_state->PC+2)+1, cpu_state->B);
                    cpu_state->PC += 4;

                    cycles += 20;
                    break;

                  // NEG
                case 0x44:
                    cpu_state->Fstatus.value = FlagTables::getStatusSub(0,cpu_state->A);
                    cpu_state->A = -cpu_state->A;
                    cpu_state->PC += 2;
                    cycles+=8;
                    break;

                  // LD I, cpu_state->A
                case 0x47:
                    cpu_state->I = cpu_state->A;
                    cpu_state->PC += 2;
                    cycles += 9;
                    break;

                    // cpu_state->ADC cpu_state->HL, cpu_state->BC
                case 0x4A:
                    cpu_state->HL = add16c(cpu_state->HL, cpu_state->BC, cpu_state->Fstatus.status.C);
                    cpu_state->PC+=2;
                    cycles+=15;
                    break;

                    // Load 16-bit cpu_state->BC register
                    // LD cpu_state->BC, (nn)
                case 0x4B:
                    cpu_state->BC = memory->read16(memory->read16(cpu_state->PC+2)); 
                    cpu_state->PC += 4;
                    cycles += 20;
                    break;

                    // Fcpu_state->IXME, should check, since there is only one
                    // interupting device, this is the same as normal ret
                    // RETI
                case 0x4D: 
                    cpu_state->PCLow  = memory->read(cpu_state->SP++);
                    cpu_state->PCHigh = memory->read(cpu_state->SP++);

                    cycles += 14;
                    break;
                            
                  // Scpu_state->BC cpu_state->HL, cpu_state->DE
                case 0x52:
                    cpu_state->HL = sub16c(cpu_state->HL, cpu_state->DE, cpu_state->Fstatus.status.C);

                    cpu_state->PC += 2;
                    cycles += 15;
                    break;

                    // LD (nn), cpu_state->DE
                case 0x53:
                    memory->write(memory->read16(cpu_state->PC+2), cpu_state->E);
                    memory->write(memory->read16(cpu_state->PC+2)+1, cpu_state->D);
                    cpu_state->PC += 4;

                    cycles += 20;
                    break;

                    // cpu_state->IM 1
                case 0x56:
                    cpu_state->PC+=2;
                    cpu_state->IM = 1;

                    cycles += 2;
                    break;

                    // LD cpu_state->A, I
                case 0x57:
                    cpu_state->A = cpu_state->I;
                    cpu_state->Fstatus.status.N = 0;
                    cpu_state->Fstatus.status.H = 0;
                    cpu_state->Fstatus.status.PV = cpu_state->IFF2;
                    cpu_state->Fstatus.status.S = (cpu_state->A & 0x80) >> 7;
                    cpu_state->Fstatus.status.Z = (cpu_state->A == 0)?1:0;

                    cpu_state->PC += 2;
                    cycles += 9;
                    break;

                    // cpu_state->ADC cpu_state->HL, cpu_state->DE
                case 0x5A:
                    cpu_state->HL = add16c(cpu_state->HL, cpu_state->DE, cpu_state->Fstatus.status.C);
                    cpu_state->PC+=2;
                    cycles+=15;
                    break;

                    // LD cpu_state->DE, (nn)    
                case 0x5B:
                    cpu_state->DE = memory->read16(memory->read16(cpu_state->PC+2));
                    cpu_state->PC += 4;
                    cycles += 20;
                    break;

                    // Fcpu_state->IXME, not sure about this
                    // LD cpu_state->A, R
                case 0x5F:
                    cpu_state->R =  (cpu_state->R & 0x80) | ((cycles + cpu_state->R + 1) & 0x7F);
                    cpu_state->A = cpu_state->R;
                    cpu_state->Fstatus.status.N = 0;
                    cpu_state->Fstatus.status.H = 0;
                    cpu_state->Fstatus.status.PV = cpu_state->IFF2;
                    cpu_state->Fstatus.status.S = (cpu_state->A & 0x80) >> 7;
                    cpu_state->Fstatus.status.Z = (cpu_state->A == 0)?1:0;

                    cpu_state->PC += 2;
                    cycles += 9;
                    break;

                    // Fcpu_state->IXME, can't find existance of this instruction
                    // LD (nn), cpu_state->HL
                case 0x63:
                    memory->write(memory->read16(cpu_state->PC+2), cpu_state->L);
                    memory->write(memory->read16(cpu_state->PC+2)+1, cpu_state->H);
                    cpu_state->PC += 4;

                    cycles += 16;
                    break;

                    // RRD, wacky instruction
                case 0x67:
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
                    break;

                    // cpu_state->ADC cpu_state->HL, cpu_state->HL
                case 0x6A:
                    cpu_state->HL = add16c(cpu_state->HL, cpu_state->HL, cpu_state->Fstatus.status.C);
                    cpu_state->PC+=2;
                    cycles+=15;
                    break;

                    // Fcpu_state->IXME, not sure about the existance of this instruction
                    // LD cpu_state->HL, (nn)
                case 0x6B:
                    cpu_state->HL = memory->read16(memory->read16(cpu_state->PC+2));
                    cpu_state->PC += 4;

                    cycles += 20;
                    break;

                    // LD (nn), cpu_state->SP
                case 0x73:
                    memory->write(memory->read16(cpu_state->PC+2), cpu_state->SPLow);
                    memory->write(memory->read16(cpu_state->PC+2)+1, cpu_state->SPHigh);
                    cpu_state->PC += 4;

                    cycles += 6;
                    break;

                    // cpu_state->ADC cpu_state->HL, cpu_state->SP
                case 0x7A:
                    cpu_state->HL = add16c(cpu_state->HL, cpu_state->SP, cpu_state->Fstatus.status.C);
                    cpu_state->PC+=2;
                    cycles+=15;
                    break;

                    // Load 16-bit cpu_state->BC register
                    // LD cpu_state->SP, (nn)
                case 0x7B:
                    cpu_state->SP = memory->read16(memory->read16(cpu_state->PC+2)); 
                    cpu_state->PC += 4;
                    cycles += 20;
                    break;

                    // LDI
                case 0xA0:
                    memory->write(cpu_state->DE++, memory->read(cpu_state->HL++));
                    cpu_state->BC--;
                    cpu_state->Fstatus.status.PV = (cpu_state->BC != 0) ? 1:0;
                    cpu_state->Fstatus.status.H = 0;
                    cpu_state->Fstatus.status.N = 0;
                    cpu_state->PC += 2;

                    cycles += 16;
                    break;

                    // CPI
                case 0xA1:
                    cpu_state->F = FlagTables::getStatusSub(cpu_state->A,memory->read(cpu_state->HL++));
                    cpu_state->BC--;
                    cpu_state->Fstatus.status.PV = (cpu_state->BC != 0) ? 1:0;
                    cpu_state->PC += 2;
                    cycles += 16;
                    break;

                    // INI
                case 0xA2:
                    cpu_state->B--;
                    memory->write(cpu_state->HL++, Ports::instance()->portRead(cpu_state->C));
                    cpu_state->Fstatus.status.N = 1;
                    if (cpu_state->B == 0)
                        cpu_state->Fstatus.status.Z = 1;
                    else
                        cpu_state->Fstatus.status.Z = 0;

                    cpu_state->PC += 2;
                    cycles += 16;
                    break;

                    // OUTI
                case 0xA3:
                    cpu_state->B--;
                    Ports::instance()->portWrite(cpu_state->C, memory->read(cpu_state->HL++));
                    cpu_state->Fstatus.status.Z = (cpu_state->B == 0) ? 1:0;
                    cpu_state->Fstatus.status.N = 1;
                    cpu_state->PC += 2;
                    cycles += 16;
                    break;

                    // OUTD
                case 0xAB:
                    cpu_state->B--;
                    Ports::instance()->portWrite(cpu_state->C, memory->read(cpu_state->HL--));
                    cpu_state->Fstatus.status.Z = (cpu_state->B == 0) ? 1:0;
                    cpu_state->Fstatus.status.N = 1;
                    cpu_state->PC += 2;
                    cycles += 16;
                    break;

                    // LDIR
                case 0xB0:
                    if (cpu_state->BC >= 4)
                    {
                        memory->write(cpu_state->DE, cpu_state->HL, 4);
                        cpu_state->DE += 4;
                        cpu_state->HL += 4;
                        cpu_state->BC -= 4;
                        cycles += 84;
                    }
                    else
                    {
                        cpu_state->BC--;
                        memory->write(cpu_state->DE++, memory->read(cpu_state->HL++));
                        cycles += 21;
                    }

                    cpu_state->Fstatus.status.H = 0;
                    cpu_state->Fstatus.status.PV = 0;
                    cpu_state->Fstatus.status.N = 1; // hmmm, not sure
                    if (cpu_state->BC == 0)
                    {
                        cpu_state->Fstatus.status.N = 0;
                        cpu_state->PC += 2;
                        cycles -=5;
                    }
                    break;

                    // CPIR
                case 0xB1:
                    cpu_state->BC--;
                    tmp8 = cpu_state->Fstatus.status.C;
                    cpu_state->F = FlagTables::getStatusSub(cpu_state->A,memory->read(cpu_state->HL++));
                    cpu_state->Fstatus.status.C = tmp8; 

                    if ((cpu_state->BC == 0)||(cpu_state->Fstatus.status.Z == 1))
                    {
                        cpu_state->Fstatus.status.PV = 0; 
                        cpu_state->PC += 2;
                        cycles += 16;
                    }
                    else
                    {
                        cpu_state->Fstatus.status.PV = 1; 
                        cycles += 21;
                    }
                    break;

                    // Should speed this function up a bit
                    // Flags match emulator, not z80 document
                    // OTIR (port)
                case 0xB3:
                    if (cpu_state->B >= 8)
                    {
                        cpu_state->B -= 8;
                        Ports::instance()->portWrite(cpu_state->C, memory->read(cpu_state->HL,8), 8);
                        cpu_state->HL+= 8;
                        cycles += 168;
                    }
                    else
                    {
                        cpu_state->B--;
                        Ports::instance()->portWrite(cpu_state->C, memory->read(cpu_state->HL++));
                        cycles += 21;
                    }
                    cpu_state->Fstatus.status.S = 0; // Unknown
                    cpu_state->Fstatus.status.H = 0; // Unknown
                    cpu_state->Fstatus.status.PV = 0; // Unknown
                    cpu_state->Fstatus.status.N = 1;
                    cpu_state->Fstatus.status.Z = 0;
                    if (cpu_state->B == 0)
                    {
                        cpu_state->Fstatus.status.Z = 1;
                        cpu_state->PC += 2;
                        cycles -= 5;
                    }
                    break;

                    // LDDR
                case 0xB8:
                    memory->write(cpu_state->DE--, memory->read(cpu_state->HL--));
                    cpu_state->BC--;
                    if (cpu_state->BC == 0)
                    {
                        cpu_state->PC += 2;
                        cycles += 16;
                        cpu_state->Fstatus.status.N = 0;
                        cpu_state->Fstatus.status.H = 0;
                        cpu_state->Fstatus.status.PV = 0;
                    }
                    else
                        cycles += 21;

                    break;

                default:
                    std::cout << "Unsupported opcode 0xED 0x" << 
                    std::hex << (int) atPC[1] << std::endl;
                    return -1;

            }
            }
            break;

        default:
    std::cout << "Unsupported opcode 0x" << 
                    std::hex << (int) atPC[0] << std::endl;
            return -1;
    }
    }
    }
    while(loop);

    return 0;
}

unsigned short Z80core::read16(const Byte *address)
{
    return address[0] + (unsigned int) (address[1] << 8);
}

void Z80core::setNextPossibleInterupt(unsigned int nextPossibleInterupt)
{
    this->nextPossibleInterupt = nextPossibleInterupt;
}

void Z80core::interupt(void)
{
    if (cpu_state->IFF1 == 1)
    {
        if (cpu_state->IM == 1)
        {
            cpu_state->SP--;
            memory->write(cpu_state->SP, cpu_state->PCHigh);
            cpu_state->SP--;
            memory->write(cpu_state->SP, cpu_state->PCLow);
            cpu_state->PC = IRQIM1ADDR;

            // Disable maskable interupts
            cpu_state->IFF1 = 0;
        }
        else
            errors::unsupported("interupt mode not supported");
    }
}

void Z80core::nminterupt(void)
{
    errors::unsupported("nminterupts not supported");
}

void Z80core::setMemory(Z80memory *memory)
{
    this->memory = memory;
}



/* Calculate the result of the DAA functio */
void Z80core::calculateDAAAdd(void)
{
    uint8 upper = (cpu_state->A >> 4) & 0xF;
    uint8 lower = cpu_state->A & 0xF;
    
    if (cpu_state->Fstatus.status.C == 0)
    {
        if ((upper <= 9) &&
            (cpu_state->Fstatus.status.H == 0) &&
            (lower <= 9))
             ;
        else if ((upper <= 8) &&
            (cpu_state->Fstatus.status.H == 0) &&
            ((lower >= 0xA) && (lower <= 0xF)))
            cpu_state->A += 0x06;
        else if ((upper <= 9) &&
            (cpu_state->Fstatus.status.H == 1) &&
            (lower <= 0x3))
            cpu_state->A += 0x06;
        else if (((upper >= 0xA) && (upper <= 0xF)) &&
            (cpu_state->Fstatus.status.H == 0) &&
            (lower <= 0x9))
        {
            cpu_state->A += 0x60;
            cpu_state->Fstatus.status.C = 1;
        }
        else if (((upper >= 0x9) && (upper <= 0xF)) &&
            (cpu_state->Fstatus.status.H == 0) &&
            ((lower >= 0xA) && (lower <= 0xF)))
        {
            cpu_state->A += 0x66;
            cpu_state->Fstatus.status.C = 1;
        }
        else if (((upper >= 0xA) && (upper <= 0xF)) &&
            (cpu_state->Fstatus.status.H == 1) &&
            (lower <= 0x3))
        {
            cpu_state->A += 0x66;
            cpu_state->Fstatus.status.C = 1;
        }
    }
    else
    {
        if ((upper <= 0x2) &&
            (cpu_state->Fstatus.status.H == 0) &&
            (lower <= 0x9))
            cpu_state->A += 0x60;
        else if ((upper <= 0x2) &&
            (cpu_state->Fstatus.status.H == 0) &&
            ((lower >= 0xA) && (lower <= 0xF)))
            cpu_state->A += 0x66;
        else if ((upper <= 0x3) &&
            (cpu_state->Fstatus.status.H == 1) &&
            (lower <= 0x3))
            cpu_state->A += 0x66;
    }
    cpu_state->Fstatus.status.PV = FlagTables::calculateParity(cpu_state->A);
    cpu_state->Fstatus.status.S  = (cpu_state->A & 0x80) ? 1:0; // Is negative
    cpu_state->Fstatus.status.Z  = (cpu_state->A==0) ? 1:0; // Is zero
}

// Fcpu_state->IXME, table in z80 guide is wrong, need to check values by hand
void Z80core::calculateDAASub(void)
{
    uint8 upper = (cpu_state->A >> 4) & 0xF;
    uint8 lower = cpu_state->A & 0xF;

    if (cpu_state->Fstatus.status.C == 0)
    {
        if ((upper <= 0x9) &&
            (cpu_state->Fstatus.status.H == 0) &&
            (lower <= 0x9))
            ;
        else if ((upper <= 0x8) &&
            (cpu_state->Fstatus.status.H == 1) &&
            ((lower >= 0x6) && (lower <= 0xF)))
            cpu_state->A += 0xFA;
    } 
    else
    {
        if (((upper >= 0x7) && (upper <= 0xF)) &&
            (cpu_state->Fstatus.status.H == 0) &&
            (lower <= 0x9))
            cpu_state->A += 0xA0;
        else if (((upper >= 0x6) && (upper <= 0xF)) &&
            (cpu_state->Fstatus.status.H == 1) &&
            ((lower >= 0x6) && (lower <= 0xF)))
        {
            cpu_state->Fstatus.status.H = 0;
            cpu_state->A += 0x9A;
        }
    }
    cpu_state->Fstatus.status.PV = FlagTables::calculateParity(cpu_state->A);
    cpu_state->Fstatus.status.S  = (cpu_state->A & 0x80) ? 1:0; // Is negative
    cpu_state->Fstatus.status.Z  = (cpu_state->A==0) ? 1:0; // Is zero
}

// cpu_state->Add two 8 bit ints plus the carry bit, and set flags accordingly
uint8 Z80core::add8c(int8 a, int8 b, int8 c)
{
    static int16 r;
    static int8 rs;

    r = a + b + c;
    rs = a + b + c;
    cpu_state->Fstatus.status.S = (rs & 0x80) ? 1:0; // Negative
    cpu_state->Fstatus.status.Z = (rs == 0) ? 1:0; // Zero
    cpu_state->Fstatus.status.PV = (r != rs)  ? 1:0; // Overflow

    r = (a & 0xF) + (b & 0xF) + c;
    cpu_state->Fstatus.status.H = (r & 0x10) ? 1:0; // Half carry
    cpu_state->Fstatus.status.N = 0;

    r = (a & 0xFF) + (b & 0xFF) + c;
    cpu_state->Fstatus.status.C = (r & 0x100) ? 1:0; // Carry
    return a + b + c;
}

// Subtract two 8 bit ints and the carry bit, set flags accordingly
uint8 Z80core::sub8c(int8 a, int8 b, int8 c)
{
    static int16 r;
    static int8 rs;

    r = a - b - c;
    rs = a - b - c;
    cpu_state->Fstatus.status.S = (rs & 0x80) ? 1:0; // Negative
    cpu_state->Fstatus.status.Z = (rs == 0) ? 1:0; // Zero
    cpu_state->Fstatus.status.PV = (r != rs)  ? 1:0; // Overflow

    r = (a & 0xF) - (b & 0xF) - c;
    cpu_state->Fstatus.status.H = (r & 0x10) ? 1:0; // Half carry
    cpu_state->Fstatus.status.N = 1;

    r = (a & 0xFF) - (b & 0xFF) - c;
    cpu_state->Fstatus.status.C = (r & 0x100) ? 1:0; // Carry
    return a - b - c;
}

// cpu_state->Add two 16 bit ints and set flags accordingly
uint16 Z80core::add16c(int16 a, int16 b, int16 c)
{
    static int32 r;
    static int16 rs;

    r = a + b + c;
    rs = a + b + c;
    cpu_state->Fstatus.status.S = (rs & 0x8000) ? 1:0; // Negative
    cpu_state->Fstatus.status.Z = (rs == 0) ? 1:0; // Zero
    cpu_state->Fstatus.status.PV = (r != rs)  ? 1:0; // Overflow

    r = (a & 0xFFF) + (b & 0xFFF) + c;
    cpu_state->Fstatus.status.H = (r & 0x1000) ? 1:0; // Half carry
    cpu_state->Fstatus.status.N = 0;

    r = (a & 0xFFFF) + (b & 0xFFFF) + c;
    cpu_state->Fstatus.status.C = (r & 0x10000) ? 1:0; // Carry
    return a + b + c;
}

uint16 Z80core::sub16c(int16 a, int16 b, int16 c)
{
    static int32 r;
    static int16 rs;

    r = a - b - c;
    rs = a - b - c;
    cpu_state->Fstatus.status.S = (rs & 0x8000) ? 1:0; // Negative
    cpu_state->Fstatus.status.Z = (rs == 0) ? 1:0; // Zero
    cpu_state->Fstatus.status.PV = (r != rs)  ? 1:0; // Overflow

    r = (a & 0xFFF) - (b & 0xFFF) - c;
    cpu_state->Fstatus.status.H = (r & 0x1000) ? 1:0; // Half carry
    cpu_state->Fstatus.status.N = 1;

    r = (a & 0xFFFF) - (b & 0xFFFF) - c;
    cpu_state->Fstatus.status.C = (r & 0x10000) ? 1:0; // Carry
    return a - b - c;
}

unsigned int Z80core::getCycle(void)
{
    return cycles;
}

void Z80core::setInteruptor(Interuptor *interuptor)
{
    this->interuptor = interuptor;
}
