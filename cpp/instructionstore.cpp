#include "instructionstore.h"
#include <iostream>

#include "instructions.h"

InstructionStore *InstructionStore::self = NULL;

InstructionStore::InstructionStore()
:totalMissing(0)
{
}

void InstructionStore::dump()
{
    std::map<int, int>::const_iterator it;
    for (it = decode_map.begin();
         it != decode_map.end();
         ++it)
    {
        if (it->second > 0)
            std::cout << std::dec << " " << (int) it->second << " : " << std::hex << it->first << std::endl;
    }

    std::cout << "Unique: " << decode_map.size() << std::endl;
    std::cout << "Total Executed Missing: " << totalMissing << std::endl;
    std::cout << std::flush;
}

InstructionStore::~InstructionStore()
{
}

InstructionStore *InstructionStore::instance()
{
    if (self == NULL)
    {
        self = new InstructionStore();
        self->initialise();
    }

    return self;
}

void InstructionStore::initialise()
{
    // Initialise the maps used to generate the register lookup.
    initialiseRegisterLookup();

    instructions = new InstructionInterface *[0xff];
    extendedFDInstructions = new InstructionInterface *[0xff];
    extendedEDInstructions = new InstructionInterface *[0xff];
    extendedDDInstructions = new InstructionInterface *[0xff];
    extendedCBInstructions = new InstructionInterface *[0xff];

    for (int i = 0; i < 0xff; i++)
    {
        instructions[i] = NULL;
        extendedFDInstructions[i] = NULL;
        extendedEDInstructions[i] = NULL;
        extendedDDInstructions[i] = NULL;
        extendedCBInstructions[i] = NULL;
    }

    instructions[0x00] = new Noop();
    instructions[0x01] = new Load16BC();
    instructions[0x02] = new LD_mem_r(CPUState::instance()->BC, CPUState::instance()->A); // LD (BC), A
    instructions[0x03] = new INC_BC(); // INC cpu_state->BC
    instructions[0x04] = new INC_r(CPUState::instance()->B); // INC cpu_state->B
//    instructions[0x06] = new LD_r(CPUState::instance()->B);
    instructions[0x07] = new RLCA();  //RLCA
    instructions[0x09] = new ADD16(CPUState::instance()->HL,
                                   CPUState::instance()->BC,11);
    instructions[0x0A] = new LD_r_mem(CPUState::instance()->A, CPUState::instance()->BC); // LD A, (BC)
    instructions[0x0B] = new DEC_16(CPUState::instance()->BC, 6);
    instructions[0x0C] = new INC_r(CPUState::instance()->C); // INC C
    //instructions[0x0E] = new LD_r(CPUState::instance()->C); // LD C, n
    instructions[0x0F] = new RRCA();
    instructions[0x10] = new DJNZ(); // DJNZ n
    instructions[0x11] = new LD_16_nn(CPUState::instance()->DE); // LD DE, nn
    instructions[0x12] = new LD_mem_r(CPUState::instance()->DE, CPUState::instance()->A); // LD (DE), A
    instructions[0x21] = new LD_16_nn(CPUState::instance()->HL); // LD HL, nn
    instructions[0x2A] = new LD_r16_mem(CPUState::instance()->HL); // LD HL, (nn)
    instructions[0x31] = new LD_16_nn(CPUState::instance()->SP); // LD DE, nn
    instructions[0x13] = new INC_16(CPUState::instance()->DE, 6);
    instructions[0x14] = new INC_r(CPUState::instance()->D); // INC D
    //instructions[0x16] = new LD_r(CPUState::instance()->D); // LD D, n
    instructions[0x19] = new ADD16(CPUState::instance()->HL,
                                   CPUState::instance()->DE,11);
    instructions[0x1A] = new LD_r_mem(CPUState::instance()->A, CPUState::instance()->DE); // LD A, (DE)
    instructions[0x1B] = new DEC_16(CPUState::instance()->DE, 6);

    instructions[0x1C] = new INC_r(CPUState::instance()->E); // INC E
    //instructions[0x1E] = new LD_r(CPUState::instance()->E); // LD E, n

    instructions[0x20] = new JRNZe(); // JR NZ, e

    instructions[0x23] = new INC_16(CPUState::instance()->HL, 6);

    instructions[0x24] = new INC_r(CPUState::instance()->H); // INC H
    //instructions[0x26] = new LD_r(CPUState::instance()->H); // LD H, n
    instructions[0x28] = new JRZe(); // JR Z, e
    instructions[0x29] = new ADD16(CPUState::instance()->HL,
                                   CPUState::instance()->HL,11);
    instructions[0x2B] = new DEC_16(CPUState::instance()->HL, 6);

    instructions[0x2C] = new INC_r(CPUState::instance()->L); // INC L
    //instructions[0x2E] = new LD_r(CPUState::instance()->L); // LD L, n
    instructions[0x33] = new INC_16(CPUState::instance()->SP, 6);
    instructions[0x34] = new INC_HL(); // INC HL
    instructions[0x35] = new DEC_HL(); // DEC HL

    instructions[0x36] = new LD_mem_n(CPUState::instance()->HL); // LD (HL), n

    instructions[0x39] = new ADD16(CPUState::instance()->HL,
                                   CPUState::instance()->SP,11);

    instructions[0x3A] = new LD_r8_mem(CPUState::instance()->A); // LD A, (n)
    instructions[0x3B] = new DEC_16(CPUState::instance()->SP, 6);
    instructions[0x3C] = new INC_r(CPUState::instance()->A); // INC A
    //instructions[0x3E] = new LD_r(CPUState::instance()->A); // LD A, n

    instructions[0x70] = new LD_mem_r(CPUState::instance()->HL, CPUState::instance()->B); // LD (HL), B
    instructions[0x71] = new LD_mem_r(CPUState::instance()->HL, CPUState::instance()->C); // LD (HL), C
    instructions[0x72] = new LD_mem_r(CPUState::instance()->HL, CPUState::instance()->D); // LD (HL), D
    instructions[0x73] = new LD_mem_r(CPUState::instance()->HL, CPUState::instance()->E); // LD (HL), E
    instructions[0x74] = new LD_mem_r(CPUState::instance()->HL, CPUState::instance()->H); // LD (HL), H
    instructions[0x75] = new LD_mem_r(CPUState::instance()->HL, CPUState::instance()->L); // LD (HL), L
    instructions[0x77] = new LD_mem_r(CPUState::instance()->HL, CPUState::instance()->A); // LD (HL), A

    instructions[0x80] = new ADD_r(CPUState::instance()->B); // ADD r, cpu_state->A
    instructions[0x81] = new ADD_r(CPUState::instance()->C); // ADD r, cpu_state->A
    instructions[0x82] = new ADD_r(CPUState::instance()->D); // ADD r, cpu_state->A
    instructions[0x83] = new ADD_r(CPUState::instance()->E); // ADD r, cpu_state->A
    instructions[0x84] = new ADD_r(CPUState::instance()->H); // ADD r, cpu_state->A
    instructions[0x85] = new ADD_r(CPUState::instance()->L); // ADD r, cpu_state->A
    instructions[0x87] = new ADD_r(CPUState::instance()->A); // ADD r, cpu_state->A

    instructions[0xA0] = new AND_r(CPUState::instance()->B); // AND r, cpu_state->A
    instructions[0xA1] = new AND_r(CPUState::instance()->C); // AND r, cpu_state->A
    instructions[0xA2] = new AND_r(CPUState::instance()->D); // AND r, cpu_state->A
    instructions[0xA3] = new AND_r(CPUState::instance()->E); // AND r, cpu_state->A
    instructions[0xA4] = new AND_r(CPUState::instance()->H); // AND r, cpu_state->A
    instructions[0xA5] = new AND_r(CPUState::instance()->L); // AND r, cpu_state->A
    instructions[0xA7] = new AND_r(CPUState::instance()->A); // AND r, cpu_state->A

    instructions[0xA8] = new XOR_r(CPUState::instance()->B); // XOR r, cpu_state->A
    instructions[0xA9] = new XOR_r(CPUState::instance()->C); // XOR r, cpu_state->A
    instructions[0xAA] = new XOR_r(CPUState::instance()->D); // XOR r, cpu_state->A
    instructions[0xAB] = new XOR_r(CPUState::instance()->E); // XOR r, cpu_state->A
    instructions[0xAC] = new XOR_r(CPUState::instance()->H); // XOR r, cpu_state->A
    instructions[0xAD] = new XOR_r(CPUState::instance()->L); // XOR r, cpu_state->A
    instructions[0xAF] = new XOR_r(CPUState::instance()->A); // XOR r, cpu_state->A

    instructions[0xB0] = new OR_r(CPUState::instance()->B); // OR r, cpu_state->A
    instructions[0xB1] = new OR_r(CPUState::instance()->C); // OR r, cpu_state->A
    instructions[0xB2] = new OR_r(CPUState::instance()->D); // OR r, cpu_state->A
    instructions[0xB3] = new OR_r(CPUState::instance()->E); // OR r, cpu_state->A
    instructions[0xB4] = new OR_r(CPUState::instance()->H); // OR r, cpu_state->A
    instructions[0xB5] = new OR_r(CPUState::instance()->L); // OR r, cpu_state->A
    instructions[0xB7] = new OR_r(CPUState::instance()->A); // OR r, cpu_state->A

    instructions[0xB8] = new CP_r(CPUState::instance()->B); // CP r, cpu_state->A
    instructions[0xB9] = new CP_r(CPUState::instance()->C); // CP r, cpu_state->A
    instructions[0xBA] = new CP_r(CPUState::instance()->D); // CP r, cpu_state->A
    instructions[0xBB] = new CP_r(CPUState::instance()->E); // CP r, cpu_state->A
    instructions[0xBC] = new CP_r(CPUState::instance()->H); // CP r, cpu_state->A
    instructions[0xBD] = new CP_r(CPUState::instance()->L); // CP r, cpu_state->A
    instructions[0xBF] = new CP_r(CPUState::instance()->A); // CP r, cpu_state->A

    instructions[0xD3] = new OUT_n_A(); // OUT (n), cpu_state->A
    instructions[0xD2] = new JPNC(); // JP NC
    instructions[0xD9] = new EXX(); // EXX
    instructions[0xDA] = new JPCnn(); // JP C, nn

    instructions[0xE6] = new AND_n(); // AND n
    instructions[0xFE] = new CP_n(); // CP n

    DEC_R dec_r;
    dec_r.reg8 = 0x05;

    LD_R_MEM ld_r_hl;
    ld_r_hl.reg8 = 0x46;

    LD_R_MEM ld_r_n;
    ld_r_n.reg8 = 0x06;

    register_lookup_Type::iterator it_r1 = register_lookup.begin();
    for (it_r1 = register_lookup.begin();
         it_r1 != register_lookup.end();
         ++it_r1)
    {
        dec_r.r = it_r1->first;
        ld_r_hl.r = it_r1->first;
        ld_r_n.r = it_r1->first;
        instructions[dec_r.reg8] = new DEC_r(*(it_r1->second)); // DEC r
        instructions[ld_r_hl.reg8] = new LD_r_mem(*(it_r1->second), CPUState::instance()->HL); // LD r, (HL)
        instructions[ld_r_n.reg8] = new LD_r(*(it_r1->second)); // LD C, n
        std::cout << "Store: " << std::hex << (int) dec_r.reg8 << 
                     " " << (int) ld_r_hl.reg8 << 
                     " " << (int) ld_r_n.reg8 << std::endl;
    }

    // Generate all of the standard register load instructions
    //
    // LD r, r'
    //
    LD_Struct ld;
    ld.reg8 = 0x40;

    it_r1 = register_lookup.begin();
    register_lookup_Type::iterator it_r2 = register_lookup.begin();
    for (it_r1 = register_lookup.begin();
         it_r1 != register_lookup.end();
         ++it_r1)
    {
        for (it_r2 = register_lookup.begin();
             it_r2 != register_lookup.end();
             ++it_r2)
        {
            ld.r1 = it_r1->first;
            ld.r2 = it_r2->first;

            int instruction_code = ld.reg8;

            instructions[instruction_code] = new LD_r_r(*(it_r1->second), *(it_r2->second));
        std::cout << "Store: " << std::hex << (int) instruction_code << std::endl;
        }
    }


    instructions[0xC9] = new RET(); // RET

    initialiseExtendedFD();
    initialiseExtendedED();
    initialiseExtendedDD();
    initialiseExtendedCB();
}

void InstructionStore::initialiseRegisterLookup()
{
    register_lookup[7] = &(CPUState::instance()->A);
    register_lookup[0] = &(CPUState::instance()->B);
    register_lookup[1] = &(CPUState::instance()->C);
    register_lookup[2] = &(CPUState::instance()->D);
    register_lookup[3] = &(CPUState::instance()->E);
    register_lookup[4] = &(CPUState::instance()->H);
    register_lookup[5] = &(CPUState::instance()->L);
}

// Extended '0xED' instructions
void InstructionStore::initialiseExtendedED()
{
    extendedEDInstructions[0x43] = new Instruction4x(); 
}

// Extended '0xDD' instructions
void InstructionStore::initialiseExtendedDD()
{
//    extendedDDInstructions[0x43] = new Instruction4x(); 
    extendedDDInstructions[0x09] = new ADD16(CPUState::instance()->IX,
                                   CPUState::instance()->BC,15,2);
    extendedDDInstructions[0x19] = new ADD16(CPUState::instance()->IX,
                                   CPUState::instance()->DE,15,2);
    extendedDDInstructions[0x23] = new INC_16(CPUState::instance()->IX,
                                   10,2);
    extendedDDInstructions[0x29] = new ADD16(CPUState::instance()->IX,
                                   CPUState::instance()->IX,15,2);
    extendedDDInstructions[0x2B] = new DEC_16(CPUState::instance()->IX, 10,2);
    extendedDDInstructions[0x39] = new ADD16(CPUState::instance()->IX,
                                   CPUState::instance()->SP,15,2);
}

// Extended '0xFD' instructions
void InstructionStore::initialiseExtendedFD()
{
//    extendedFDInstructions[] = new Instruction4x(); 
    extendedFDInstructions[0x09] = new ADD16(CPUState::instance()->IY,
                                   CPUState::instance()->BC,15,2);
    extendedFDInstructions[0x19] = new ADD16(CPUState::instance()->IY,
                                   CPUState::instance()->DE,15,2);
    extendedFDInstructions[0x23] = new INC_16(CPUState::instance()->IY,
                                   10,2);
    extendedFDInstructions[0x29] = new ADD16(CPUState::instance()->IY,
                                   CPUState::instance()->IY,15,2);
    extendedFDInstructions[0x2B] = new DEC_16(CPUState::instance()->IY, 10,2);
    extendedFDInstructions[0x39] = new ADD16(CPUState::instance()->IY,
                                   CPUState::instance()->SP,15,2);
}

// Extended '0xCB' instructions
void InstructionStore::initialiseExtendedCB()
{
    extendedCBInstructions[0x43] = NULL; 
}

InstructionInterface *InstructionStore::getInstruction(const Byte *instructionAddress)
{
    // Only count instructions that we haven't dealt with yet.
    if (instructions[instructionAddress[0]] == NULL)
    {
        // Keep a total
        ++totalMissing;
        decode_map[instructionAddress[0]]++;
    }

    return instructions[instructionAddress[0]];
}

// Get Extended '0xDD' instructions
InstructionInterface *InstructionStore::getExtendedDD(const Byte *instructionAddress)
{
    return extendedDDInstructions[instructionAddress[0]];
}

// Get Extended '0xED' instructions
InstructionInterface *InstructionStore::getExtendedED(const Byte *instructionAddress)
{
    return extendedEDInstructions[instructionAddress[0]];
}

// Get Extended '0xFD' instructions
InstructionInterface *InstructionStore::getExtendedFD(const Byte *instructionAddress)
{
    return extendedFDInstructions[instructionAddress[0]];
}

// Get Extended '0xCB' instructions
InstructionInterface *InstructionStore::getExtendedCB(const Byte *instructionAddress)
{
    return extendedCBInstructions[instructionAddress[0]];
}
