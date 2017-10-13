#ifndef LD_INSTRUCTIONS_H
#define LD_INSTRUCTIONS_H

#include "cpustate.h"
#include "types.h"
#include "instruction.h"
#include "extendedinstructions.h"

class Load16BC : public Instruction
{ public: int execute(Z80memory *memory); }; 

// Load a 16-bit register with the value 'nn'
class LD_16_nn : public Instruction
{
  public: LD_16_nn(uint16 &r16):Instruction(),r16(r16){}
        int execute(Z80memory *memory); 
  protected: uint16 &r16;
};

class LD_r_r : public Instruction
{
    public:
        LD_r_r(uint8 &dst, uint8 &src):Instruction(),src(src),dst(dst){}
        int execute(Z80memory *memory); 

    protected:
    uint8 &src;
    uint8 &dst;
};

// LD (16 REG), n
// Load the value 'n' into the 16-bit address
class LD_mem_n : public Instruction
{
    public:
        LD_mem_n(uint16 &addr):Instruction(),addr(addr){}
        int execute(Z80memory *memory); 

    protected:
    uint16 &addr;
};

// LD (16 REG), r
// The register r into the 16-bit address
class LD_mem_r : public Instruction_r
{
    public:
        LD_mem_r(uint16 &addr, uint8 &r):Instruction_r(r),addr(addr){}
        int execute(Z80memory *memory); 

    protected:
    uint16 &addr;
};

// LD r, (16 REG)
// Load the value from the 16-bit address into the register
class LD_r_mem : public Instruction
{
    public:
        LD_r_mem(uint8 &r, uint16 &addr):Instruction(),r(r),addr(addr){}
        int execute(Z80memory *memory); 

    protected:
    uint8 &r;
    uint16 &addr;
};

// LD r, (nn)
// Load the value from the 16-bit address into the 16-bit register
class LD_r16_mem : public Instruction
{
    public:
        LD_r16_mem(uint16 &r):Instruction(),r(r){}
        int execute(Z80memory *memory); 

    protected:
    uint16 &r;
};

// LD r, (nn)
// Load the value from the 16-bit address into the 8-bit register
class LD_r8_mem : public Instruction
{
    public:
        LD_r8_mem(uint8 &r):Instruction(),r(r){}
        int execute(Z80memory *memory); 

    protected:
    uint8 &r;
};

class LD_r : public Instruction_r
{ public: 
    LD_r(uint8 &r):Instruction_r(r){}
    int execute(Z80memory *memory); 
};

#endif // LD_INSTRUCTIONS_H
