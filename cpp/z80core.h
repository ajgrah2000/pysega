#ifndef Z80CORE_H
#define Z80CORE_H
#include "readInterface.h"
#include "writeInterface.h"
#include "interuptor.h"
#include "interupt.h"
#include "types.h"
#include "z80memory.h"
#include "cpustate.h"

class Z80core : public Interupt
{
    public:
        Z80core(uint32 &cycles);
        virtual ~Z80core();
        int step(bool loop = true);
        void setMemory(Z80memory *memory);
        void interupt(void);
        void setNextPossibleInterupt(uint32 nextPossibleInterupt);
        void nminterupt(void);
        void dumpHistory(void);
        unsigned int getCycle(void);
        void setInteruptor(Interuptor *interuptor);

    protected:
        void initialiseInstructions();

    private:

        CPUState *cpu_state;

        static const unsigned int IRQIM1ADDR  = 0x38;


        Interuptor *interuptor;
        Z80memory *memory;
        uint8  *r[8]; // register pointers;

        static const unsigned int FREQLENGTH = 0x1000;
        void printFrequency(void);

        uint16 loopCycles;
        uint32 nextPossibleInterupt;

        uint32 &cycles;

        uint16 add16c(int16 a, int16 b, int16 c);
        uint8 add8c(int8 a, int8 b, int8 c);
        uint8 sub8c(int8 a, int8 b, int8 c);
        uint16 sub16c(int16 a, int16 b, int16 c);
        void calculateDAAAdd(void);
        void calculateDAASub(void);
        unsigned short read16(const Byte *address);
};
#endif 
