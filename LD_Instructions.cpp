#include "LD_Instructions.h"
#include "flagtables.h"

#include <iostream>
#include "ports.h"

int Load16BC::execute(Z80memory *memory)
{
    // Load 16-bit cpu_state->BC register
    // LD cpu_state->BC, 0x
    
    cpu_state->BC = memory->read16(cpu_state->PC+1); 
    cpu_state->PC += 3;

    return 10;
}

int LD_r::execute(Z80memory *memory)
{
    // This can be optimised.
    r = memory->read(cpu_state->PC + 1);
    cpu_state->PC += 2;
    return 7;
}

// Load the 8 bit value 'n' into memory.
int LD_mem_n::execute(Z80memory *memory)
{
    memory->write(addr, memory->read(cpu_state->PC +1));
    cpu_state->PC += 2;

    return 10;
}

// Load the register into memory.
int LD_mem_r::execute(Z80memory *memory)
{
    memory->write(addr, r);
    cpu_state->PC ++;

    return 7;
}

// Load the value at the address into a register.
int LD_r_mem::execute(Z80memory *memory)
{
    r = memory->read(addr);
    cpu_state->PC++;
    return 7;
}

// Load the value at the address into a register.
int LD_r16_mem::execute(Z80memory *memory)
{
    r = memory->read16(memory->read16(cpu_state->PC+1));
    cpu_state->PC += 3;

    return 20;
}

// Load the value at the address into a register.
int LD_r8_mem::execute(Z80memory *memory)
{
    r = memory->read(memory->read16(cpu_state->PC+1));
    cpu_state->PC += 3;

    return 13;
}

// Load any register to any other register.
int LD_r_r::execute(Z80memory *memory)
{
    dst = src;
    cpu_state->PC++;

    return 4;
}

int LD_16_nn::execute(Z80memory *memory)
{
    r16= memory->read16(cpu_state->PC+1); 
    cpu_state->PC += 3;
    return 10;
}

