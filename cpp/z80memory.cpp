#include "z80memory.h"
#include "errors.h"

#include <stdio.h>
#include <string>
#include <assert.h>
#include <iostream>
#include <stdexcept>
#include <memory.h>

Z80memory::Z80memory()
{
    memoryMap = new Byte[MEMMAPSIZE];
    memoryMapRef = new Byte *[MEMMAPSIZE >> UPPERSHIFT];

    for (unsigned int i(0); i < MEMMAPSIZE; ++i)
    {
        memoryMap[i] = 0;
    }
}

Z80memory::~Z80memory()
{
    std::cout << "Deleting memory" << std::endl;

    for (unsigned int i = 0; i < numBanks; i++)
    {
        delete cartridgeBanks[i];
    }

    delete [] cartridgeBanks;
    delete [] memoryMap;
    delete [] memoryMapRef;

    std::cout << "Memory deleted" << std::endl;
}

/***************** PUBLIC METHODS *****************/

/* Read a file into memory banks */
void Z80memory::loadCartridge(const char *filename)
{
    FILE *romFile;
    unsigned int bytesRead = 0, totalBytesRead = 0;
    Byte *maxCartridge[MAXBANKS];
    Byte *bank = NULL;

    std::cout << "Opening: " << filename << std::endl;
    romFile = fopen(filename, "r");

    assert(romFile != NULL);

    /* Read one bank at a time from the file */
    numBanks = 0;
    while (!feof(romFile))
    {
        bank = new Byte [BANKSIZE];
        bytesRead = fread(bank,
                          sizeof(Byte), 
                          BANKSIZE,
                          romFile);


        if (bytesRead != 0)
        {
            assert (numBanks < MAXBANKS);
            maxCartridge[numBanks++] = bank;
        }

        totalBytesRead += bytesRead;
    }

    /* Make sure the file wasn't empty */
    assert(numBanks > 0);

    if ((bytesRead > 0) && (bytesRead < BANKSIZE))
    {
        std::cerr << "Warning: Short Cartridge, padding bank" << std::endl;

        memset(&bank[bytesRead], 0, BANKSIZE-bytesRead);
    }

    /* `Copy' the data into the class */
    cartridgeBanks = new Byte *[numBanks];

    for (unsigned int i = 0; i < numBanks; i++)
        cartridgeBanks[i] = maxCartridge[i];

    std::cout << "Cartridge read:" << std::endl;
    std::cout << " banks = " << std::dec << numBanks << std::endl;
    std::cout << " bytes = " << totalBytesRead << std::endl;

    /* Allocate memory for possible battary pack RAM */
    cartridgeRAM = new Byte *[NUMRAMPAGES];
    for (unsigned int i = 0; i < NUMRAMPAGES; i++)
    {
        cartridgeRAM[i] = new Byte[BANKSIZE];
        memset(cartridgeRAM[i], 0, BANKSIZE);
    }

    initialiseMemoryMap();
}

/***************** PRIVATE METHODS *****************/

void Z80memory::initialiseMemoryMap(void)
{
    /* Copy 1K into memory map, this will not change */
    for (unsigned int i = 0; i < PAGE0; i++)
        memoryMap[i] = cartridgeBanks[0][i];

    memoryMapRef[0] = &memoryMap[0];

    for (unsigned int i = PAGE0; i < PAGE1; i++)
        memoryMap[i] = cartridgeBanks[0][i];

    /* Copy bank 1 to memory */
    if (numBanks > 1)
        memoryMapRef[1] = cartridgeBanks[1];
    else
        memoryMapRef[1] = &memoryMap[1 << UPPERSHIFT];

    /* Copy bank 2 to memory */
    if (numBanks > 2)
        memoryMapRef[2] = cartridgeBanks[2];
    else
        memoryMapRef[2] = &memoryMap[2 << UPPERSHIFT];

    memoryMapRef[3] = &memoryMap[3 << UPPERSHIFT];

    std::cout << "MemoryMap Initialisation finished" << std::endl;
}

const Byte *Z80memory::read(uint16 address, uint8 length)
{
    static Byte *tmp;
    if (address < (unsigned) (LOWERMASK - length))
        return &memoryMapRef[address >> UPPERSHIFT][address & LOWERMASK];
    else
    {
        delete tmp;
        tmp = new Byte[length];
        for (int i = 0; i < length; i++)
            tmp[i] = read(address + i);
        return tmp;
    }
}

uint16 Z80memory::read16(uint16 address)
{
    return read(address) + (unsigned int) (read(address+1) << 8);
}

/* write multiple bytes to memory */
void Z80memory::write(uint16 dest, uint16 src, uint8 length)
{
    if (((unsigned) (dest + length) >= MEMMAPSIZE) || (dest < RAMOFFSET))
        errors::warning("Z80memory: Write out of range");

    if ((unsigned) (dest+length) >= MEMREGISTERS)
    {
        for (uint16 i = 0; i < length; i++)
            write(dest+i, read(src+i));
    }

    for (int i = 0; i < length; i++)
        memoryMap[dest+i] = read(src+i);
}

void Z80memory::write(uint16 address, Byte data)
{
    if ((address >= MEMMAPSIZE) || (address < RAMOFFSET))
        errors::warning("Z80memory: Write out of range");

    /* Detect paging */
    if (address >= MEMREGISTERS)
    {
        if (address == RAMSELECTADDR)
        {
            int bankNumber;

            /* if cartridge RAM is currently mapped, save it */
            if (memoryMap[RAMSELECTADDR] & MAPCARTRAM)
            {
                bankNumber = (memoryMap[RAMSELECTADDR] & PAGEOFRAM )
                             >> PAGEOFRAMBITPOS;
                saveCartridgeRAM(bankNumber);
            }

            /* If cartridge RAM is enabled, swap in, otherwise swap in a ROM
             * page into bank 2.
             */ 
            if (data & MAPCARTRAM)
            {
                bankNumber = (data & PAGEOFRAM ) >> PAGEOFRAMBITPOS;
                swapRAM(bankNumber);
            }
            else
                swapPage(2, memoryMap[PAGE2BANKADDR]);
        }
        /* Perform a page swap */
        else if (address == PAGE0BANKADDR)
            swapPage(0, data);
        else if (address == PAGE1BANKADDR)
            swapPage(1, data);
        else if (address == PAGE2BANKADDR)
            swapPage(2, data);
    }

    memoryMap[address] = data;
}

/* Swap a ROM bank from the cartridge into the memory map.
   The first 1K of the memory map never changes.  */

void Z80memory::swapPage(Byte pageNumber, Byte bankNumber)
{
    unsigned int offset;
    static Byte lastPageNumber, lastBankNumber;

    if ((lastBankNumber != bankNumber) || (lastPageNumber != pageNumber))
    {
        // Not sure what would happen with a dodgy cartridge size
        // ie non power of 2
        if (bankNumber >= numBanks)
            bankNumber = bankNumber % numBanks;

        /* Ensure that the swap doesn't try to overwrite the RAM */
        if ((pageNumber == 2) && (memoryMap[RAMSELECTADDR] & MAPCARTRAM))
            return;

        // Page 0 swaps should be rare, so copying them shouldn't be too bad
        if (pageNumber == 0)
        {
            offset = pageNumber*BANKSIZE + PAGE0;

            memcpy(&memoryMap[offset], &cartridgeBanks[bankNumber][PAGE0],
                            BANKSIZE-PAGE0);
        }
        else
        {
            memoryMapRef[pageNumber] = cartridgeBanks[bankNumber];
        }


        lastPageNumber = pageNumber;
        lastBankNumber = bankNumber;
    }
}

void Z80memory::saveCartridgeRAM(Byte bankNumber)
{
    unsigned int offset = PAGE2;

    std::cout << "Saving cartridge RAM bank number " << 
            (int) bankNumber << std::endl;

    for (unsigned int i = 0; i < BANKSIZE; i++)
        cartridgeRAM[bankNumber][i] = memoryMap[offset++];
}

void Z80memory::swapRAM(Byte bankNumber)
{
    unsigned int offset = PAGE2;

    std::cout << "Swapping in  cartridge RAM bank number " << 
            (int) bankNumber << std::endl;

    /* Swap the RAM into the memory map (page 2) */
    for (unsigned int i = 0;i < BANKSIZE;i++)
        memoryMap[offset++] = cartridgeRAM[bankNumber][i];

    memoryMapRef[2] = cartridgeBanks[bankNumber];
}
