#ifndef INSTRUCTIONINTERFACE_H
#define INSTRUCTIONINTERFACE_H

#include "z80memory.h"

class InstructionInterface
{

    public:
        virtual ~InstructionInterface(){};

        // Execute the instruction
        virtual int execute(Z80memory *memory) = 0;
};

#endif // INSTRUCTION_H
