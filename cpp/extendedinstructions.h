#ifndef EXTENDEDINSTRUCTION_H
#define EXTENDEDINSTRUCTION_H

#include <map>
#include "instruction.h"

class ExtendedInstruction : public Instruction
{ public: int execute(Z80memory *memory); };

class Instruction4x : public Instruction
{ public: int execute(Z80memory *memory); };


#endif 
