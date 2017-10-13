#ifndef z80memory_h
#define z80memory_h

#include "types.h"

class Z80memory
{
    public:
            Z80memory();
            virtual ~Z80memory();
            void loadCartridge(const char *filename);

            void write(uint16 address, Byte data);
            void write(uint16 dest, uint16 src, uint8 length);
            inline const Byte *readMulti(uint16 address)
            {
            return &memoryMapRef[address >> UPPERSHIFT][address & LOWERMASK];
            }
            inline Byte read(uint16 address)
            {
    return memoryMapRef[address >> UPPERSHIFT][address & LOWERMASK];
            }
            const Byte * read(uint16 address, uint8 length);
            uint16 read16(uint16 address);
    private:
            void initialiseMemoryMap(void);
            void swapPage(Byte pageNumber, Byte bankNumber);
            void saveCartridgeRAM(Byte bankNumber);
            void swapRAM(Byte bankNumber);

            static const unsigned int MAXBANKS    = 64;
            static const unsigned int NUMRAMPAGES = 2;
            static const unsigned int BANKSIZE    = 0x4000;

            static const unsigned int MEMMAPSIZE = 0x10000;
            static const unsigned int UPPERSHIFT = 14;
            static const unsigned int LOWERMASK  = 0x03FFF;

            static const unsigned int PAGESIZE   = 0x4000;
            static const unsigned int PAGE0      = 0x400;
            static const unsigned int PAGE1      = 0x4000;
            static const unsigned int PAGE2      = 0x8000;
            static const unsigned int RAMOFFSET  = 0xC000;
            static const unsigned int MIRRORRAM  = 0xE000;

            static const unsigned int MEMREGISTERS  = 0xFFFC;

            static const unsigned int RAMSELECTADDR = 0xFFFC;
            static const Byte MAPCARTRAM      = 0x08;
            static const Byte PAGEOFRAM       = 0x04;
            static const Byte PAGEOFRAMBITPOS = 2;

            static const unsigned int PAGE0BANKADDR = 0xFFFD;
            static const unsigned int PAGE1BANKADDR = 0xFFFE;
            static const unsigned int PAGE2BANKADDR = 0xFFFF;

            unsigned int numBanks;
            Byte **cartridgeBanks;
            Byte **cartridgeRAM;
            Byte *memoryMap;
            Byte **memoryMapRef;

};
#endif
