#ifndef TYPES_H
#define TYPES_H

#ifndef NULL
#define NULL 0
#endif

#define MAXBYTE 256

typedef char int8;
typedef int int32;
typedef short int16;
typedef unsigned int uint32;
typedef unsigned short uint16;
typedef unsigned char uint8;
typedef unsigned char Byte;

typedef struct
{
    uint8 l, h;
} Register;

typedef union 
{
    struct
    {
        unsigned char C:1, N:1, PV:1, X1:1, H:1, X2:1, Z:1, S:1;
    } status;
    uint8 value;
} Status;

#endif
