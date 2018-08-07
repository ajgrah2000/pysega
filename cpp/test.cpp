//#include "opcodegenerator.h"
#include <iostream>
#include <iomanip>

typedef union 
{
    union
    {
        unsigned char reg8;

        struct
        {
        unsigned char a:1;
        unsigned char b:2;
        unsigned char c:3;
        unsigned char d:2;
        };
    };
} Bit;

int main(void)
{
    /*
    OpCodeGenerator::CodeReferenceMap input_map;
    OpCodeGenerator::OpCodeReferenceMap output_map;
    int fixed_mask = 0xF2;
    int fixed_value = 0xF3;
    uint8 a, b, c, d;
    input_map[0] = &a;
    input_map[1] = &b;
    input_map[2] = &c;
    input_map[3] = &d;

    output_map = 
            OpCodeGenerator::getOpCode(fixed_mask, 
                                       fixed_value, 
                                       input_map);

    OpCodeGenerator::OpCodeReferenceMap::iterator it;
    for (it = output_map.begin();
         it != output_map.end();
         ++it)
    {
        std::cout << "first: " << std::hex <<  (int) it->first << std::endl;
    }
    */

    Bit bit;
    bit.reg8 = 0x0;
    for (unsigned int i = 0; i < 8; i++)
    {
        bit.c = i;
        std::cout << "first: " << std::hex <<  (int) bit.reg8 << std::endl;
    }
}
