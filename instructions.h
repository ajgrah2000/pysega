#ifndef INSTRUCTIONS_H
#define INSTRUCTIONS_H

#include "cpustate.h"
#include "types.h"
#include "instruction.h"
#include "LD_Instructions.h"
#include "extendedinstructions.h"


class Noop : public Instruction
{ public: int execute(Z80memory *memory); };

class OUT_n_A : public Instruction
{ public: int execute(Z80memory *memory); }; 

class RRCA : public Instruction
{ public: int execute(Z80memory *memory); }; 

class AND_r : public Instruction
{
    public:
        AND_r(uint8 &src):Instruction(),src(src){}
        int execute(Z80memory *memory); 

    protected:
    uint8 &src;
};

class AND_n : public Instruction
{ public: int execute(Z80memory *memory); }; 

class OR_r : public Instruction
{
    public:
        OR_r(uint8 &src):Instruction(),src(src){}
        int execute(Z80memory *memory); 

    protected:
    uint8 &src;
};

class XOR_r : public Instruction
{
    public:
        XOR_r(uint8 &src):Instruction(),src(src){}
        int execute(Z80memory *memory); 

    protected:
    uint8 &src;
};

class EXX : public Instruction
{
    public: int execute(Z80memory *memory); 
};

class CP_n : public Instruction
{ public: int execute(Z80memory *memory); }; 

class CP_r : public Instruction_r
{
    public: CP_r(uint8 &r):Instruction_r(r){}
            int execute(Z80memory *memory); 
};

class JRZe : public Instruction
{ public: int execute(Z80memory *memory); };

class JPNC : public Instruction
{ public: int execute(Z80memory *memory); };

class JPCnn : public Instruction
{ public: int execute(Z80memory *memory); };

class JRNZe : public Instruction
{ public: int execute(Z80memory *memory); };

class INC_r : public Instruction_r
{ public: INC_r(uint8 &r):Instruction_r(r){}
    int execute(Z80memory *memory); };

class INC_16 : public Instruction
{ public: INC_16(uint16 &r, uint8 cycles, uint8 pcInc = 1)
    :r(r),cycles(cycles),pcInc(pcInc){}
    uint16 &r;
    uint8 cycles;
    uint8 pcInc;
    int execute(Z80memory *memory); 
};

class DEC_16 : public Instruction
{ public: DEC_16(uint16 &r, uint8 cycles, uint8 pcInc = 1)
    :r(r),cycles(cycles),pcInc(pcInc){}
    uint16 &r;
    uint8 cycles;
    uint8 pcInc;
    int execute(Z80memory *memory); 
};

class DEC_r : public Instruction_r
{ public: DEC_r(uint8 &r):Instruction_r(r){}
    int execute(Z80memory *memory); };

class INC_BC : public Instruction
{ public: int execute(Z80memory *memory); };

class INC_HL : public Instruction
{ public: int execute(Z80memory *memory); };

class DEC_HL : public Instruction
{ public: int execute(Z80memory *memory); };

class DJNZ : public Instruction
{ public: int execute(Z80memory *memory); };

class RET : public Instruction
{ public: int execute(Z80memory *memory); };

// Addition instructions

class ADD16 : public Instruction
{ public: 
    ADD16(uint16 &dst, uint16 &add, int cycles, int pcInc = 1); 
  protected:
    uint16 &dst;
    uint16 &add;
    int cycles;
    int pcInc;

    int execute(Z80memory *memory); 
};

class ADD_r : public Instruction
{ public: ADD_r(uint8 &src):Instruction(), src(src){}; 
  protected:
    uint8 &src;
    int execute(Z80memory *memory); 
};

class RLCA : public Instruction
{ public: int execute(Z80memory *memory); };

#endif // INSTRUCTIONS_H
