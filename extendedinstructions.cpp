#include "extendedinstructions.h"
#include "instructionstore.h"
#include <iostream>

// Increment the program counter
// get the 'extended' instruction.
// Return the result of the `execute'
int ExtendedInstruction::execute(Z80memory *memory)
{
    std::cerr << "ERROR: execute not implemented" << std::cerr;

    cpu_state->PC++;

    const Byte *atPC = memory->readMulti(cpu_state->PC);

    InstructionInterface *instruction = 
            InstructionStore::instance()->getExtendedED(atPC);

    if (instruction == NULL)
    {
        // Roll back the instruction.
        cpu_state->PC--;
        return 0;
    }
    else
    {
        return instruction->execute(memory);
    }
}

int Instruction4x::execute(Z80memory *memory)
{
    memory->write(memory->read16(cpu_state->PC+2), cpu_state->C);
    memory->write(memory->read16(cpu_state->PC+2)+1, cpu_state->B);
    cpu_state->PC += 4;

    return 20;
}
