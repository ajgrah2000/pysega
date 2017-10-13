#include "cpustate.h"

#include <iostream>

CPUState *CPUState::self = NULL;

CPUState::CPUState():
        A((uint8 &) ((Register &) AF).h),
        B((uint8 &) ((Register &) BC).h),
        C((uint8 &) ((Register &) BC).l),
        D((uint8 &) ((Register &) DE).h),
        E((uint8 &) ((Register &) DE).l),
        H((uint8 &) ((Register &) HL).h),
        L((uint8 &) ((Register &) HL).l),
        F((uint8 &) ((Register &) AF).l),
        SPHigh((uint8 &) ((Register &) SP).h),
        SPLow ((uint8 &) ((Register &) SP).l),
        PCHigh((uint8 &) ((Register &) PC).h),
        PCLow ((uint8 &) ((Register &) PC).l),
        IXHigh((uint8 &) ((Register &) IX).h),
        IXLow ((uint8 &) ((Register &) IX).l),
        IYHigh((uint8 &) ((Register &) IY).h),
        IYLow ((uint8 &) ((Register &) IY).l),
        Fstatus((Status &) ((Register &) AF).l)

{
    /* Initialising registers */
    PC = IX = IY = SP = 0;
    AF = BC = DE = HL = 0;
    AF_ = BC_ = DE_ = HL_ = 0;
    I = R = 0;
    IM = 0;
    IFF1 = 0;
    IFF2 = 0;
}

CPUState::~CPUState()
{
}

CPUState *CPUState::instance()
{
    if (self == NULL)
    {
        self = new CPUState();
    }

    return self;
}

void CPUState::printState(void)
{
    std::cout << "State: PC: " << PC << std::endl;
}
