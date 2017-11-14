class Memory(object):
    """ Memory map management of sega master system/cartridges/ram
    """
    MEMREGISTERS    = 0xFFFC
    RAMSELECTADDR   = 0xFFFC
    MAPCARTRAM      = 0x08
    PAGEOFRAM       = 0x04
    PAGEOFRAMBITPOS = 2

    RAMOFFSET  = 0xC000

    PAGE0      = 0x400
    PAGE1      = 0x4000
    PAGE2      = 0x8000

    MEMMAPSIZE = 0x10000
    UPPERSHIFT = 14
    LOWERMASK  = 0x03FFF

    def __init__(self):
        self._last_page_number = 0
        self._last_bank_number = 0

    def _initialise_memory(self):
        """ Initialise memory bank allocations. """

        self._memory_map     = [0] * self.MEMMAPSIZE
        self._memory_map_ref = [[0] * self.cartridge.BANK_SIZE] * (self.MEMMAPSIZE >> self.UPPERSHIFT)

        # Copy 1K into memory map, this will not change
        for i in range(self.PAGE0):
            self._memory_map[i] = self.cartridge.cartridge_banks[0][i]

        # Copy to 'map ref'
        for i in range(self.cartridge.BANK_SIZE):
            self._memory_map_ref[0][i] = self._memory_map[i]

        # Copy bank 1 to memory
        if (self.cartridge.num_banks > 1):
            for i in range(self.cartridge.BANK_SIZE):
                self._memory_map_ref[1][i] = self.cartridge.cartridge_banks[1][i]
        else:
            for i in range(self.cartridge.BANK_SIZE):
                self._memory_map_ref[1][i] = self._memory_map[(1 << self.UPPERSHIFT) + i]

        # Copy bank 2 to memory
        if (self.cartridge.num_banks > 2):
            for i in range(self.cartridge.BANK_SIZE):
                self._memory_map_ref[2][i] = self.cartridge.cartridge_banks[2][i]
        else:
            for i in range(self.cartridge.BANK_SIZE):
                self._memory_map_ref[2][i] = self._memory_map[(2 << self.UPPERSHIFT) + i]

        for i in range(self.cartridge.BANK_SIZE):
            self._memory_map_ref[3][i] = self._memory_map[(3 << self.UPPERSHIFT) + i]

        print ("MemoryMap Initialisation finished")

    def read(self, address):
        return self._memory_map_ref[address >> self.UPPERSHIFT][address & self.LOWERMASK]

    def read(self, address, length):

        result = [0] * length

        for i in range(length):
            result[i] = read(address + i)

        return result

    def read16(self, address):
        return self.read(address) + (self.read(address + 1) << 8)

    def write(self, dest, src, length):
        """ write multiple bytes to memory.
        """

        if (((dest + length) >= self.MEMMAPSIZE) or (dest < self.RAMOFFSET)):
            raise Exception("Write out of range" + address)

        if ((dest+length) >= self.MEMREGISTERS):
            for i in range(length):
                self.write(dest+i, self.read(src+i))

        for i in range(length):
            self._memory_map[dest+i] = self.read(src+i)

    def write(self, address, data):
        if ((address >= self.MEMMAPSIZE) or (address < self.RAMOFFSET)):
            raise Exception("Write out of range" + address)
    
        # Detect paging
        if (address >= self.MEMREGISTERS):
            if (address == self.RAMSELECTADDR):
                # if cartridge RAM is currently mapped, save it.
                if (self._memory_map[self.RAMSELECTADDR] & self.MAPCARTRAM):
                    bank_number = (self._memory_map[self.RAMSELECTADDR] & self.PAGEOFRAM ) >> self.PAGEOFRAMBITPOS
                    self._save_cartridge_ram(bank_number)
    
                # If cartridge RAM is enabled, swap in, otherwise swap in a ROM
                # page into bank 2.
                #  
                if (data & self.MAPCARTRAM):
                    bank_number = (data & self.PAGEOFRAM ) >> self.PAGEOFRAMBITPOS
                    self._swap_ram(bank_number)
                else:
                    self._swap_page(2, self._memory_map[self.PAGE2BANKADDR])

            # Perform a page swap
            elif (address == self.PAGE0BANKADDR):
                self._swap_page(0, data)
            elif (address == self.PAGE1BANKADDR):
                self._swap_page(1, data)
            elif (address == self.PAGE2BANKADDR):
                self._swap_page(2, data)
    
        self._memory_map[address] = data


    def _swap_page(self, page_number, bank_number):
        """ Swap a ROM bank from the cartridge into the memory map.
            The first 1K of the memory map never changes.
        """

        if ((self._last_bank_number != bank_number) or (self._last_page_number != page_number)):
            # Not sure what would happen with a dodgy cartridge size
            # ie non power of 2
            if (bank_number >= self.cartridge.num_banks):
                bank_number = bank_number % self.cartridge.num_banks
    
            # Ensure that the swap doesn't try to overwrite the RAM.
            if ((page_number == 2) and (self._memory_map[self.RAMSELECTADDR] & self.MAPCARTRAM)):
                return
    
            # Page 0 swaps should be rare, so copying them shouldn't be too bad
            if (page_number == 0):
                offset = page_number*self.cartridge.BANK_SIZE + self.PAGE0
    
                for i in range(self.cartridge.BANK_SIZE-self.PAGE0):
                  self._memory_map[offset + i] = cartridgeBanks[bank_number][self.PAGE0 + i]
            else:
                for i in range(self.cartridge.BANK_SIZE):
                    self._memory_map_ref[page_number][i] = cartridgeBanks[bank_number][i]
    
    
            self._last_page_number = page_number
            self._last_bank_number = bank_number

    def _swap_ram(self, bank_number):

        print("Swapping in  cartridge RAM bank number %d"%(bank_number))

        # Swap the RAM into the memory map (page 2)
        for i in range(self.cartridge.BANK_SIZE):
            self._memory_map[PAGE2 + i] = self.cartridge.ram[bank_number][i];
    
        for i in range(self.cartridge.BANK_SIZE):
            self._memory_map_ref[2][i] = self.cartridge.cartridge_banks[bank_number][i]

    def _save_cartridge_ram(bank_number):
        print("Saving cartridge RAM bank number %d"%(bank_number))
    
        for i in range(self.cartridge.BANK_SIZE):
            self.cartridge.ram[bank_number][i] = self._memory_map[PAGE2 + i]

    def set_cartridge(self, cartridge):
        self.cartridge = cartridge

        self._initialise_memory()

    def set_z80memory(self, z80memory):
        self.z80memory = z80memory

    def write(self, address, data):
        self.cartridge.write(address, data)

    def read(self, address):
        return self.cartridge.read(address)

    def readMulti(self, address):
        print("readMulti not implemented")
        return [self.read(address + x) for x in range(3)]
