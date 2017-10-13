#ifndef INSTRUCTION_H
#define INSTRUCTION_H

#include "cpustate.h"
#include "instructioninterface.h"

typedef struct
{
    union
    {
        unsigned char reg8;

        struct
        {
            unsigned char r2:3;
            unsigned char r1:3;
            unsigned char code:2;
        };
    };
} LD_Struct;

typedef struct
{
    union
    {
        unsigned char reg8;

        struct
        {
            unsigned char pad1:3;
            unsigned char r:3;
            unsigned char pad2:2;
        };
    };
} DEC_R;

typedef struct
{
    union
    {
        unsigned char reg8;

        struct
        {
            unsigned char pad2:3;
            unsigned char r:3;
            unsigned char pad1:2;
        };
    };
} LD_R_MEM;

class Instruction : public InstructionInterface
{

    public:
        Instruction();
        virtual ~Instruction();

        // Return the number of cycles that the instruction took.
        int execute(Z80memory *memory);

        static const Byte FLAG_MASK_INC8;
        static const Byte FLAG_MASK_DEC8;

    protected:
        // 'Share' the cpu state
        static CPUState *cpu_state;

        static Byte *r[8];


    private:

};

class Instruction_r: public Instruction
{ public: Instruction_r(uint8 &r):Instruction(),r(r){}
  protected: uint8 &r; 
};

#endif // INSTRUCTION_H
