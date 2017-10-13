#include "z80debug.h"

#include <stdio.h>
#include <iostream>
#include <iomanip>

z80debug::z80debug(int history)
{
    this->history = history;
    currentPos = 0;
    historyFull = 0;

    PC = new int[history];
    SP = new int[history];
    atSPlow  = new int[history];
    atSPhigh = new int[history];
    AF = new int[history];
    BC = new int[history];
    DE = new int[history];
    HL = new int[history];
    IX = new int[history];
    IY = new int[history];
    OP = new int[history];
    IM = new int[history];
    IFF1 = new int[history];
}
void z80debug::storeRegisters(int PCtmp, int SPtmp, 
                              int atSPlowtmp, int atSPhightmp, 
                              int AFtmp, int BCtmp, int DEtmp, int HLtmp, 
                              int IXtmp, int IYtmp,
                              int OPtmp, int IMtmp, int IFF1tmp)
{
    PC[currentPos] = PCtmp;
    SP[currentPos] = SPtmp;
    atSPlow[currentPos] = atSPlowtmp;
    atSPhigh[currentPos] = atSPhightmp;
    AF[currentPos] = AFtmp;
    BC[currentPos] = BCtmp;
    DE[currentPos] = DEtmp;
    HL[currentPos] = HLtmp;
    IX[currentPos] = IXtmp;
    IY[currentPos] = IYtmp;
    OP[currentPos] = OPtmp;
    IM[currentPos] = IMtmp;
    IFF1[currentPos] = IFF1tmp;

    currentPos++;
    if (currentPos >= history)
    {
        historyFull = true;
        currentPos = 0;
    }
}

void z80debug::dumpAndPause(void)
{
    if (currentPos > 0)
        dump(currentPos - 1);
    else if (historyFull)
        dump(history - 1);
    else
        std::cout << "History empty" << std::endl;

    getchar();
}

void z80debug::dump(int i)
{
    std::cout << std::hex << std::setfill('0') << std::setiosflags(std::ios::uppercase) <<
                "AF:" << std::setw(4) << (int) AF[i] <<
                " HL:" << std::setw(4) << (int) HL[i] <<
                " DE:" << std::setw(4) << (int) DE[i] <<
                " BC:" << std::setw(4) << (int) BC[i] <<
                " PC:" << std::setw(4) << (int) PC[i] <<
                " SP:" << std::setw(4) << (int) SP[i] <<
                " IX:" << std::setw(4) << (int) IX[i] << 
                " IY:" << std::setw(4) << (int) IY[i] << std::endl; 
    std::cout << std::setw(2) <<
                "AT PC: [" << (int) OP[i] << "]   " <<
                "AT SP: [" << std::setw(2) << (int) atSPhigh[i] << 
                              std::setw(2) << (int) atSPlow[i]  << "]   ";
    std::cout << "[" << (((AF[i] & 0x80) == 0)?".":"S") << 
                       (((AF[i] & 0x40) == 0)?".":"Z") <<
                       (((AF[i] & 0x10) == 0)?".":"H") <<
                       (((AF[i] & 0x04) == 0)?".":"P") <<
                       (((AF[i] & 0x02) == 0)?".":"N") <<
                       (((AF[i] & 0x01) == 0)?".":"C");
    std::cout << "]   ";
    std::cout << "IM" << IM[i] << ": " << ((IFF1[i] == 0) ? "DI":"EI");
    std::cout << std::endl;
}

void z80debug::dumpHistory(void)
{
    unsigned int i;

    if (historyFull)
        i = (currentPos + 1) % history;
    else
        i = 0;

    while (i != currentPos)
    {
        dump(i);
        i = (i + 1) % history;
    }
}

