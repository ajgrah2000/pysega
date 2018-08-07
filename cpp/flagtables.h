#ifndef FLAGTABLE_H
#define FLAGTABLE_H

#include "types.h"

class FlagTables 
{
    public: 
            static void init();

            // Calculate the flags set as a result of an 8-bit increment
            // instruction.  The index to the array is the value after
            // incrmentation.
            static char getStatusInc8(Byte value);
            static char getStatusDec8(Byte value);
            static char getStatusOr(Byte value);
            static char getStatusAnd(Byte value);
            static char getStatusAdd(Byte value1, Byte value2);
            static char getStatusSub(Byte value1, Byte value2);
            static int calculateParity(int a);

    protected: 
            static void createStatusInc8Table();
            static void createStatusDec8Table();
            static void createStatusOrTable();
            static void createStatusAndTable();
            static void createStatusAddTable(void);
            static void createStatusSubTable(void);

            static unsigned char flagTableInc8[MAXBYTE];
            static unsigned char flagTableDec8[MAXBYTE];

            static unsigned char flagTableOr[MAXBYTE];
            static unsigned char flagTableAnd[MAXBYTE];

            static unsigned char flagTableAdd[MAXBYTE][MAXBYTE];
            static unsigned char flagTableSub[MAXBYTE][MAXBYTE];
            static bool initialised;
};
#endif
