#include "opcodegenerator.h"
#include <iostream>

OpCodeGenerator::OpCodeGenerator()
{
}

OpCodeGenerator::OpCodeReferenceMap OpCodeGenerator::getOpCode(uint8 fixed_mask, uint8 fixed_value, OpCodeGenerator::CodeReferenceMap &reference_map)
{

    if ((~fixed_mask & fixed_value) != 0)
    {
        std::cerr << "getOpCode: fixed value mask seems incorrect." << std::endl;
        uint8 display = fixed_mask;
        for (int i = 0; i < sizeof(uint8)*8; i++)
        {

            uint8 max_bit = 1 << (sizeof(uint8) - 1);
            std::cerr << ((display & max_bit) ? : '0','1');
            display = (display << 1) & 0xFE;

        }
        std::cerr << std::endl;

    }

    uint8 shifted_mask = fixed_mask;

    // Find the location of the 'zero'
    int shift_count = 0;
    while(shifted_mask & 1)
    {
        shifted_mask = shifted_mask >> 1;
        shift_count++;

    }

    OpCodeReferenceMap output;

    CodeReferenceMap::const_iterator it;
   
    for (it = reference_map.begin();
         it != reference_map.end();
         ++it)
    {
        uint8 opcode = fixed_value | (it->first << shift_count);
        output.insert(OpCodeReferenceMap::value_type(opcode,it->second));
    }

    return output;
}
