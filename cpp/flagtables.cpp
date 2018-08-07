#include "flagtables.h"
#include <iostream>

unsigned char FlagTables::flagTableInc8[MAXBYTE];
unsigned char FlagTables::flagTableDec8[MAXBYTE];

unsigned char FlagTables::flagTableOr[MAXBYTE];
unsigned char FlagTables::flagTableAnd[MAXBYTE];

unsigned char FlagTables::flagTableAdd[MAXBYTE][MAXBYTE];
unsigned char FlagTables::flagTableSub[MAXBYTE][MAXBYTE];

bool FlagTables::initialised = false;

void FlagTables::init()
{
    if (false == initialised)
    {
        createStatusInc8Table();
        createStatusDec8Table();
        createStatusOrTable();
        createStatusAndTable();
        createStatusAddTable();
        createStatusSubTable();

        // Inc 8
        Status status;
        status.value = 0;

        status.status.N = 0;
        status.status.C = 0;

        for (unsigned int i =0; i < MAXBYTE; i++)
        {
            status.status.S  = (i & 0x80) ? 1:0; // Is negative
            status.status.Z  = (i==0) ? 1:0; // Is zero
            status.status.H  = ((i & 0xF) == 0) ? 1:0; // Half carry 
            status.status.PV = (i==0x80) ? 1:0; // Was 7F

            flagTableInc8[i] = status.value;
        }

        // Dec 8
        status.value = 0;
        status.status.N = 1;
        status.status.C = 0; // Carry unchanged, set to 0 to allow OR 

        for (unsigned int i =0; i < MAXBYTE; i++)
        {
            status.status.S  = (i & 0x80) ? 1:0; // Is negative
            status.status.Z  = (i==0) ? 1:0; // Is zero
            status.status.H  = ((i & 0xF) == 0xF) ? 1:0; // Half borrow
            status.status.PV = (i==0x7F) ? 1:0; // Was 80 

            flagTableDec8[i] = status.value;
        }
        initialised = true;
    }
}

void FlagTables::createStatusInc8Table()
{
    // Inc 8
    Status status;
    status.value = 0;

    status.status.N = 0;
    status.status.C = 0;

    for (unsigned int i =0; i < MAXBYTE; i++)
    {
        status.status.S  = (i & 0x80) ? 1:0; // Is negative
        status.status.Z  = (i==0) ? 1:0; // Is zero
        status.status.H  = ((i & 0xF) == 0) ? 1:0; // Half carry 
        status.status.PV = (i==0x80) ? 1:0; // Was 7F

        flagTableInc8[i] = status.value;
    }
}

void FlagTables::createStatusDec8Table()
{
    // Inc 8
    Status status;
    status.value = 0;

    status.status.N = 0;
    status.status.C = 0; // Carry unchanged, set to 0 to allow OR 

    for (unsigned int i =0; i < MAXBYTE; i++)
    {
        status.status.S  = (i & 0x80) ? 1:0; // Is negative
        status.status.Z  = (i==0) ? 1:0; // Is zero
        status.status.H  = ((i & 0xF) == 0xF) ? 1:0; // Half borrow
        status.status.PV = (i==0x7F) ? 1:0; // Was 80 

        flagTableDec8[i] = status.value;
    }
}

/* Calculate flags associated with parity */
void FlagTables::createStatusOrTable(void)
{
    /* Calculate a parity lookup table */
    Status status;

    for (unsigned int i = 0; i < MAXBYTE; i++)
    {
        status.value = 0;

        status.status.PV = calculateParity(i);
        status.status.Z = (i == 0)? 1:0; // Zero
        status.status.S = (i & 0x80) ? 1:0; // Sign

        flagTableOr[i] = status.value;
    }
}

/* Calculate flags associated with parity */
void FlagTables::createStatusAndTable(void)
{
    /* Calculate a parity lookup table */
    Status status;

    for (unsigned int i = 0; i < MAXBYTE; i++)
    {
        status.value = 0;

        status.status.H = 1;
        status.status.PV = calculateParity(i);
        status.status.Z = (i == 0)? 1:0; // Zero
        status.status.S = (i & 0x80) ? 1:0; // Sign

        flagTableAnd[i] = status.value;
    }
}

void FlagTables::createStatusAddTable(void)
{
    Status status;
    int16 r;
    int8 rc;
    int8 hr;

    for (unsigned int i = 0; i < MAXBYTE; i++)
    {
        for (unsigned int j = 0; j < MAXBYTE; j++)
        {
            r  = (char) i + (char) j;
            rc = (char) i + (char) j;
            hr = (i & 0xF) + (j & 0xF);

            status.value = 0; 
            status.status.S  = (rc &  0x80) ? 1:0;
            status.status.Z  = (rc == 0x00) ? 1:0;
            status.status.H  = (hr &  0x10) ? 1:0;
            status.status.PV = (r != rc) ? 1:0;
            status.status.N  = 0;
            r  = ((char) i & 0xFF) + ((char) j & 0xFF);
            status.status.C  = (r &  0x100) ? 1:0; // Not sure about this one

            flagTableAdd[i][j] = status.value;
        }
    }
}

/* Calculate flags associated with subtraction
   flagTableSub[cpu_state->A][cpu_state->B], represents cpu_state->A - cpu_state->B
   */
void FlagTables::createStatusSubTable(void)
{
    Status status;
    char rc;
    int r;
    int hr;

    for (unsigned int i = 0; i < MAXBYTE; i++)
    {
        for (unsigned int j = 0; j < MAXBYTE; j++)
        {
            unsigned int t = 0;
            r  = (char) i - (char) j;
            rc = (char) i - (char) j;
            hr  = ((char) i & 0xF) - ((char) j & 0xF);
            status.value = 0;
            status.status.S  = (rc & 0x80) ? 1:0; // result negative
            status.status.Z  = (r == 0) ? 1:0; // result zero
            status.status.H  = (hr & 0x10) ? 1:0;
            status.status.PV = (rc != r) ? 1:0; // overflow
            if (((char) i < 0) && ((char) j > 0))
            {
                if (j >= (0x80 - (i ^ 0xff)))
                {
                    t = 1;
                }
            }

            if (((char) i >= 0) && ((char) j < 0))
            {
                if ((i + 1) >= (((0x80 - (j ^ 0xff))) & 0xFF))
                {
                    t = 1;
                }
            }

            if (t != status.status.PV)
            {
                std::cout << "Hmm:" << (int) (i  & 0xFF)<< ", " << (int) (j & 0xFF) << std::endl;
            }

            if (rc != r)
            {
//                std::cout << "PV:" << (int) (i  & 0xFF)<< ", " << (int) (j & 0xFF) << std::endl;
            }

            status.status.N  = 1;
            r  = ((char) i & 0xFF) - ((char) j & 0xFF);
            status.status.C  = (r & 0x100) ? 1:0; // cpu_state->Borrow (?) 

            flagTableSub[i][j] = status.value;
        }
    }
}


char FlagTables::getStatusInc8(Byte value)
{
    return flagTableInc8[value];
} 

char FlagTables::getStatusDec8(Byte value)
{
    return flagTableDec8[value];
} 

char FlagTables::getStatusOr(Byte value)
{
    return flagTableOr[value];
}

char FlagTables::getStatusAnd(Byte value)
{
    return flagTableAnd[value];
}

char FlagTables::getStatusAdd(Byte value1, Byte value2)
{
    return flagTableAdd[value1][value2];
}

char FlagTables::getStatusSub(Byte value1, Byte value2)
{
    return flagTableSub[value1][value2];
}

/* Determine the parity flag (even = 1, odd = 0) */
int FlagTables::calculateParity(int a)
{
    int p;
    // Calculate Parity
    p = 1;
    // Step through each bit in the byte
    for (int b = 0; b < 8; b++)
        p = (p ^ (a >> b)) & 0x1;

    return p;
}
