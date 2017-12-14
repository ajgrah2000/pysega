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
//    std::cout << "State: PC: " << PC << std::endl;
    std::cout << "A:" << (int) A;
    std::cout << " SP:" << (int) SP;
    std::cout << " B:" << (int) B;
    std::cout << " C:" << (int) C;
    std::cout << " D:" << (int) D;
    std::cout << " E:" << (int) E;
    std::cout << " HLHigh:" << (int) H;
    std::cout << " HLLow:" << (int) L;
    std::cout << " F:";
    std::cout << " PCHigh:" << (int) ((PC >> 8) & 0xFF);
    std::cout << " PCLow:"  << (int) ((PC) & 0xFF);
    std::cout << " SPHigh:" << (int) ((SP >> 8) & 0xFF);
    std::cout << " SPLow:"  << (int) (SP & 0xFF);
    std::cout << " IXHigh:" << (int) ((IX >> 8) & 0xFF);
    std::cout << " IXLow:"  << (int) (IX & 0xFF);
    std::cout << " IYHigh:" << (int) ((IY >> 8) & 0xFF);
    std::cout << " IYLow:"  << (int) (IY & 0xFF);
    std::cout << std::endl;
//       std::cout << "(C:0 N:0 PV:0 X1:0 H:0 X2:0 Z:0 S:0)

}
