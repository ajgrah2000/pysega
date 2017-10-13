#include "instruction.h"
#include "cpustate.h"
#include "types.h"
#include "flagtables.h"

CPUState *Instruction::cpu_state = NULL;

const Byte Instruction::FLAG_MASK_INC8 = 0x01; // Bits to leave unchanged
const Byte Instruction::FLAG_MASK_DEC8 = 0x01; // Bits to leave unchanged

Byte * Instruction::r[8];

Instruction::Instruction()
{
    cpu_state = CPUState::instance();

    // Register index array, makes for more compact cases
    r[0] = &cpu_state->B;
    r[1] = &cpu_state->C;
    r[2] = &cpu_state->D;
    r[3] = &cpu_state->E;
    r[4] = &cpu_state->H;
    r[5] = &cpu_state->L;
    r[6] = NULL;
    r[7] = &cpu_state->A;

    FlagTables::init(); 
}

Instruction::~Instruction()
{
}

int Instruction::execute(Z80memory *memory)
{
    return 0;
}
