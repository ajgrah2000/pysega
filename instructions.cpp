#include "instructions.h"
#include "flagtables.h"

#include <iostream>
#include "ports.h"

int Noop::execute(Z80memory *memory)
{
    cpu_state->PC++;

    return 4;
}

    // RRCA
int RRCA::execute(Z80memory *memory)
{
    cpu_state->Fstatus.status.C = cpu_state->A & 0x1;
    cpu_state->Fstatus.status.H = 0;
    cpu_state->Fstatus.status.N = 0;
    cpu_state->A = (cpu_state->A >> 1) | ((cpu_state->A & 0x1) << 7);
    cpu_state->PC++;

    return 4;
}

int INC_BC::execute(Z80memory *memory)
{
    cpu_state->BC++;
    cpu_state->PC++;

    return 6;
}

// OUT (n), cpu_state->A
// Write register A, to port n
int OUT_n_A::execute(Z80memory *memory)
{
// Need to sort out port write.
     Ports::instance()->portWrite(memory->read(cpu_state->PC + 1), cpu_state->A);

     cpu_state->PC+=2;

     return 11;
}

  // DJNZ n
int DJNZ::execute(Z80memory *memory)
{
    int cycles = 8;

    cpu_state->B--;
    if (cpu_state->B != 0)
    {
        cpu_state->PC += (int) (signed char) memory->read(cpu_state->PC + 1);
        cycles+=5;
    }

    cpu_state->PC+=2;

    return cycles;
}

  // JR Z, e
int JRZe::execute(Z80memory *memory)
{
    int cycles = 7;

    if (cpu_state->Fstatus.status.Z == 1)
    {
        const Byte *atPC;
        atPC = memory->readMulti(cpu_state->PC);
        cpu_state->PC += (int) (signed char) atPC[1]; 
        cycles+=5;
    }
    cpu_state->PC += 2;

    return cycles;
}

  // JR NZ, e
int JRNZe::execute(Z80memory *memory)
{
    int cycles = 7;

    if (cpu_state->Fstatus.status.Z == 0)
    {
        const Byte *atPC;
        atPC = memory->readMulti(cpu_state->PC);
        cpu_state->PC += (int) (signed char) atPC[1]; 
        cycles+=5;
    }

    cpu_state->PC += 2;

    return cycles;
}
  // JP NC, e
int JPNC::execute(Z80memory *memory)
{
     if (cpu_state->Fstatus.status.C == 0)
         cpu_state->PC = memory->read16(cpu_state->PC+1);
     else
         cpu_state->PC += 3;

     return 10;
}

  // JP C, nn
int JPCnn::execute(Z80memory *memory)
{
     if (cpu_state->Fstatus.status.C == 1)
         cpu_state->PC = memory->read16(cpu_state->PC+1);
     else
         cpu_state->PC += 3;

     return 10;
}

int INC_16::execute(Z80memory *memory)
{
    r++;
    cpu_state->PC += pcInc;

    return cycles;
}

int DEC_16::execute(Z80memory *memory)
{
    r--;
    cpu_state->PC += pcInc;

    return cycles;
}

int INC_r::execute(Z80memory *memory)
{
    r++;
    cpu_state->F = (cpu_state->F & FLAG_MASK_INC8) | 
                FlagTables::getStatusInc8(r);
    cpu_state->PC++;

    return 4;
}

int DEC_r::execute(Z80memory *memory)
{
    r--;
    cpu_state->F = (cpu_state->F & FLAG_MASK_DEC8) | 
                FlagTables::getStatusDec8(r);
    cpu_state->PC++;

    return 4;
}


            // INC (cpu_state->HL)
int INC_HL::execute(Z80memory *memory)
{
    memory->write(cpu_state->HL, memory->read(cpu_state->HL) + 1);
    cpu_state->F = (cpu_state->F & FLAG_MASK_INC8) | 
            FlagTables::getStatusInc8(memory->read(cpu_state->HL));
    cpu_state->PC ++;
    return 11;
}

int DEC_HL::execute(Z80memory *memory)
{
    memory->write(cpu_state->HL, memory->read(cpu_state->HL) - 1);
    cpu_state->F = (cpu_state->F & FLAG_MASK_DEC8) | FlagTables::getStatusDec8(memory->read(cpu_state->HL));
    cpu_state->PC ++;
    return 11;
}

int RET::execute(Z80memory *memory)
{
    cpu_state->PCLow  = memory->read(cpu_state->SP++);
    cpu_state->PCHigh = memory->read(cpu_state->SP++);

    return 10;
}

// Addition instructions
ADD16::ADD16(uint16 &dst, uint16 &add, int cycles, int pcInc)
        :dst(dst),add(add),cycles(cycles),pcInc(pcInc)
{
}

int ADD16::execute(Z80memory *memory)
{
    static int32 r;

    r =  dst + add;

    r = (dst & 0xFFF) + (add & 0xFFF);
    cpu_state->Fstatus.status.H = (r & 0x1000) ? 1:0; // Half carry
    cpu_state->Fstatus.status.N = 0;

    r = (dst & 0xFFFF) + (add & 0xFFFF);
    cpu_state->Fstatus.status.C = (r & 0x10000) ? 1:0; // Carry

    dst += add;

    cpu_state->PC += pcInc;

    return cycles;
}

int ADD_r::execute(Z80memory *memory)
{
	cpu_state->Fstatus.value = FlagTables::getStatusAdd(cpu_state->A,src);
	cpu_state->A = cpu_state->A + src;
	cpu_state->PC++;
	return 4;
}

int AND_r::execute(Z80memory *memory)
{
    cpu_state->A = cpu_state->A & src;
    cpu_state->PC++;

    cpu_state->F = FlagTables::getStatusAnd(cpu_state->A);

    return 4;
}

int AND_n::execute(Z80memory *memory)
{

    cpu_state->A = cpu_state->A & memory->read(cpu_state->PC +1);
    cpu_state->PC += 2;
    cpu_state->Fstatus.value = FlagTables::getStatusAnd(cpu_state->A);

    return 7;
}

int OR_r::execute(Z80memory *memory)
{
    cpu_state->A = cpu_state->A | src;
    cpu_state->PC++;

    cpu_state->F = FlagTables::getStatusOr(cpu_state->A);

    return 4;
}

int XOR_r::execute(Z80memory *memory)
{
    cpu_state->A = cpu_state->A ^ src;
    cpu_state->PC++;

    cpu_state->F = FlagTables::getStatusOr(cpu_state->A);

    return 4;
}

int EXX::execute(Z80memory *memory)
{
    static uint16 tmp16;
    tmp16 = cpu_state->BC;
    cpu_state->BC = cpu_state->BC_;
    cpu_state->BC_ = tmp16;

    tmp16 = cpu_state->DE;
    cpu_state->DE = cpu_state->DE_;
    cpu_state->DE_ = tmp16;

    tmp16 = cpu_state->HL;
    cpu_state->HL = cpu_state->HL_;
    cpu_state->HL_ = tmp16;

    cpu_state->PC++;

    return 4;
}

int RLCA::execute(Z80memory *memory)
{
    cpu_state->A = (cpu_state->A << 1) | ((cpu_state->A >> 7) & 0x1);
    cpu_state->Fstatus.status.C = cpu_state->A & 0x1;
    cpu_state->Fstatus.status.N = 0;
    cpu_state->Fstatus.status.H = 0;
    cpu_state->PC++;
    return 4;
}

int CP_n::execute(Z80memory *memory)
{

    cpu_state->F = FlagTables::getStatusSub(cpu_state->A, memory->read(cpu_state->PC +1));
    cpu_state->PC += 2;

    return 7;
}

int CP_r::execute(Z80memory *memory)
{
    cpu_state->F = FlagTables::getStatusSub(cpu_state->A,r);
    cpu_state->PC++;

    return 4;
}
