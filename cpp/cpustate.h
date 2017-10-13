#ifndef CPUSTATE_H
#define CPUSTATE_H

#include "types.h"

// Holds all of the cpu registers
class CPUState
{
    public:

        static CPUState *instance();
        virtual ~CPUState();

        uint16 PC, IX, IY, SP;
        uint16 AF, BC, DE, HL;
        uint16 AF_, BC_, DE_, HL_;
        uint8  &A, &B, &C, &D, &E, &H, &L, &F;
        uint8  &SPHigh, &SPLow;
        uint8  &PCHigh, &PCLow;
        uint8  &IXHigh, &IXLow;
        uint8  &IYHigh, &IYLow;
        uint8  I, R;
        uint8  IM;
        uint8  IFF1, IFF2;
        Status &Fstatus;

        void printState(void);

    protected:

    private:
        static CPUState *self;
        CPUState();


};

#endif // CPUSTATE_H
