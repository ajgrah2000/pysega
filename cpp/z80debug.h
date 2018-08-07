#ifndef Z80DEBUG_H
#define Z80DEBUG_H
class z80debug
{
    public:
            z80debug(int history = 100);
            void storeRegisters(int PC, int SP, 
                           int atSPlow, int atSPhigh,
                           int AF, int BC, int DE, int HL, 
                           int IX, int IY,
                           int OP, int IM, int IFF1);
            void dumpAndPause(void);
            void dumpHistory(void);
    private:
            unsigned int history;
            unsigned int historyFull;
            unsigned int currentPos;
            int *PC, *SP, *atSPlow, *atSPhigh, *AF, *BC, *DE, *HL, *OP;
            int *IX, *IY;
            int *IM, *IFF1;

            void dump(int i);
};
#endif
