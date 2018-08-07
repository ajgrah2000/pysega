#ifndef OPCODEGENERATOR_H
#define OPCODEGENERATOR_H

#include <map>
#include "types.h"

class OpCodeGenerator
{
    public:
        // Map the 'value' to a reference.
        // The value starts at '0', ie shifting is performed by the op code
        // generate function.
        typedef std::map<uint8, uint8 const *> CodeReferenceMap;
        typedef std::map<uint8, uint8 const *> OpCodeReferenceMap;

        OpCodeGenerator();

        // Get an opcode, given the 'fixed_bits' and the 'register_bits'
        // The 'register_bits' are simply a mask to show where the register
        // bits go. If they overlap the 'fixed_bits', then the overlapping bits
        // will be ignored.
        static OpCodeReferenceMap getOpCode(uint8 fixed_mask, uint8 fixed_value, CodeReferenceMap &reference_map);

};
#endif
