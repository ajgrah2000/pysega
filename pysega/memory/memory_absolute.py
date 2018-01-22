import memory

""" Map the current 'pc' address to an 'absolute' address.  The
structure of the 'absolute' address is somewhat arbitrary, but  the
idea is to be fairly sensible with the layout to make the mapping
sensible and efficient.

segments:

cartridge - ROM - 0x4000 * 64 (0x3F)
cartridge - RAM - 0x4000 * 2
system    - RAM - 0x2000


ROM - 0x000000 - 0x0FFFFF
ROM - 0x100000 - 0x1FFFFF
RAM   0x200000 - 0x207FFF
RAM   0x208000 - 0x20A000

-> Total = 3F 0x42

mapped memory:
    0x0000 - 0x03FF                     -> ROM (bank 0) (0x0000 - 0x03FF)
    0x0400 - 0x3FFF + (0xFFFD(0-0x3F))          -> ROM (bank x) (0x0400 - 0x4000)
    0x4000 - 0x7FFF + (0xFFFE(0-0x3F))          -> ROM (bank x) (0x0000 - 0x4000)
    0x8000 - 0xBFFF + (0xFFFF(0-0x3F) + 0xFFFC(0x0C)) -> ROM (bank x) (0x0000 - 0x4000) or RAM (bank x)
- 11x0
    0xC000 - 0xDFFF                     -> System RAM   (0x0000 - 0x2000)
    0xE000 - 0xFFFF                     -> System RAM   (0x0000 - 0x2000) (mirror)


    0x0000 - 0x03FF                     -> ROM (bank 0) (0x0000 - 0x03FF)
    0x0400 - 0x3FFF + (0xFFFD)          -> ROM (bank x) (0x0400 - 0x4000)

    0x4000 - 0x7FFF + (0xFFFE)          -> ROM (bank x) (0x0000 - 0x4000)
    0x8000 - 0xBFFF + (0xFFFF + 0xFFFC) -> ROM (bank x) (0x0000 - 0x4000) or RAM (bank x)

    0xC000 - 0xDFFF                     -> System RAM   (0x0000 - 0x2000)
    0xE000 - 0xFFFF                     -> System RAM   (0x0000 - 0x2000) (mirror)


    absolute = page[(address >> 13)] | address & 0x1FFF


    | 6-bit - page 0| 6-bit - page 1| 6-bit - page 2 | 1-bit - ram/rom select | 1-bit - ram select | 3 - sub-page address | 13 - address

    all bits -> 6 + 6 + 6 + 18



"""

#        page_select = (address >> 14)
#        bank_address = address & self.LOWERMASK 
#        page0_bank = self._paging_register_page0


class MemoryAbsolute(memory.MemoryBase):
    """ Map the PC to an absolute address.
    """
    BANK_SIZE     = 0x4000
    MAX_BANKS     = 64;
    NUM_PAGES     = 3;

    def __init__(self):
        self._last_page_number = 0
        self._last_bank_number = 0

        self._ram     = [0] * self.RAM_SIZE * 2

        # 'Page0' always contains bank 0 for the first 'PAGE0' bytes, then up
        # to the page boundary may contain a different bank. This array is used
        # to copy the 'mixed' banks to all possible 'page0' pages.
        self._page0_copies = [[0] * self.BANK_SIZE for x in range(self.MAX_BANKS)]

        # Remember the last bank assignments per page, and only swap if they differ
        self.ABSOLUTE_PAGE_0_ROM_OFFSET = 0x000000
        self.ABSOLUTE_PAGE_X_ROM_OFFSET = 0x100000
        self.ABSOLUTE_CART_RAM_OFFSET   = 0x200000
        self.ABSOLUTE_SYS_RAM_OFFSET    = 0x208000
        self.ABSOLUTE_SEGMENT_SIZE      =   0x2000

        self._page_2     = 0
        self._ram_select = 0

        self._upper_mappings = [0x0000,   
                                self.ABSOLUTE_PAGE_X_ROM_OFFSET + (self.ABSOLUTE_SEGMENT_SIZE * 1), 
                                self.ABSOLUTE_PAGE_X_ROM_OFFSET + (self.ABSOLUTE_SEGMENT_SIZE * 2), 
                                self.ABSOLUTE_PAGE_X_ROM_OFFSET + (self.ABSOLUTE_SEGMENT_SIZE * 3), 
                                self.ABSOLUTE_PAGE_X_ROM_OFFSET + (self.ABSOLUTE_SEGMENT_SIZE * 4), 
                                self.ABSOLUTE_PAGE_X_ROM_OFFSET + (self.ABSOLUTE_SEGMENT_SIZE * 5),
                                self.ABSOLUTE_SYS_RAM_OFFSET, self.ABSOLUTE_SYS_RAM_OFFSET]

        # Complete memory map
        self._memory_map     = [0] * max(self.ABSOLUTE_CART_RAM_OFFSET + self.ABSOLUTE_SEGMENT_SIZE,
                                         self.ABSOLUTE_SYS_RAM_OFFSET + self.ABSOLUTE_SEGMENT_SIZE)

    def get_absolute_address(self, address):
        return self._upper_mappings[address >> 13] | address & 0x1FFF

    def read(self, address):
        """ Assumes 'address' is 'int' or accepts >> operator. """
        # Using constants here to increase speed.
        return self._memory_map[self.get_absolute_address(address)]

    def readArray(self, address, length):

        result = [0] * length

        for i in range(length):
            result[i] = self.read(address + i)

        return result

    def read16(self, address):
        return self.read(address) + (self.read(address + 1) << 8)

    def writeMulti(self, dest, src, length):
        """ write multiple bytes to memory.
        """

        if (((dest + length) >= self.MEMMAPSIZE) or (dest < self.RAM_OFFSET)):
            errors.warning("Write out of range %x"%(dest + length))
            return

        for i in range(length):
            self.write(dest+i, self.read(src+i))

    def write(self, address, data):
        # Should check inputs, see which instructions/condition can overflow
        self._write(address, int(data) & 0xFF)

    def set_cartridge(self, cartridge):
        self.cartridge = cartridge

        self._initialise_read()

    def _initialise_read(self):
        """ Un-optimised address translation, uses paging registers. 
        """

        self._populate_absolute_memory_map()
        self.write(0xFFFC, 0)
        self.write(0xFFFD, 0)
        self.write(0xFFFE, 1)
        self.write(0xFFFF, 2)

    def _populate_absolute_memory_map(self):
        for bank in range(self.cartridge.num_banks):
            # Page '0'/'1' lookup
            for address in range(self.PAGE0):
                bank_address = address & self.LOWERMASK # BANK_MASK
                self._memory_map[self.ABSOLUTE_PAGE_0_ROM_OFFSET  + bank_address + (bank * self.BANK_SIZE)] =  self.cartridge.cartridge_banks[0][bank_address]
                self._memory_map[self.ABSOLUTE_PAGE_X_ROM_OFFSET  + bank_address + (bank * self.BANK_SIZE)] =  self.cartridge.cartridge_banks[bank][bank_address]

            for address in range(self.PAGE0, self.PAGE1):
                bank_address = address & self.LOWERMASK # BANK_MASK
                self._memory_map[self.ABSOLUTE_PAGE_0_ROM_OFFSET  + bank_address + (bank * self.BANK_SIZE)] =  self.cartridge.cartridge_banks[bank][bank_address]
                self._memory_map[self.ABSOLUTE_PAGE_X_ROM_OFFSET  + bank_address + (bank * self.BANK_SIZE)] =  self.cartridge.cartridge_banks[bank][bank_address]


    def _write(self, address, data):
        address = address & self.ADDRESS_MASK # ADDRESS_MASK

        if(address >= self.RAM_OFFSET):
            if(address >= self.MEMREGISTERS):
                # Should make these conditiona, 
                if (address == self.PAGE0_BANK_SELECT_REGISTER):
                    self._upper_mappings[0] = self.ABSOLUTE_PAGE_0_ROM_OFFSET + (self.BANK_SIZE * data)
                    self._upper_mappings[1] = self.ABSOLUTE_PAGE_X_ROM_OFFSET + (self.BANK_SIZE * data) + self.ABSOLUTE_SEGMENT_SIZE
                elif (address == self.PAGE1_BANK_SELECT_REGISTER):
                    self._upper_mappings[2] = self.ABSOLUTE_PAGE_X_ROM_OFFSET + (self.BANK_SIZE * data)
                    self._upper_mappings[3] = self.ABSOLUTE_PAGE_X_ROM_OFFSET + (self.BANK_SIZE * data) + self.ABSOLUTE_SEGMENT_SIZE
                elif ((address == self.RAM_SELECT_REGISTER) or (address == self.PAGE2_BANK_SELECT_REGISTER)):
                    # Set the data first, to allow read-back of the registers.
                    #self._memory_map[self._upper_mappings[address >> 13] | address & 0x1FFF] = data

                    if (address == self.RAM_SELECT_REGISTER):
                        self._ram_select = data
                    elif (address == self.PAGE2_BANK_SELECT_REGISTER):
                        self._page_2     = data

                    if (self._ram_select & self.MAPCARTRAM): # page2_is_cartridge_ram
                      # Cart RAM select.
                      if (self._ram_select & self.PAGEOFRAM):
                        self._upper_mappings[4] = self.ABSOLUTE_CART_RAM_OFFSET + (self.ABSOLUTE_SEGMENT_SIZE * 2)
                        self._upper_mappings[5] = self.ABSOLUTE_CART_RAM_OFFSET + (self.ABSOLUTE_SEGMENT_SIZE * 3)
                      else:
                        self._upper_mappings[4] = self.ABSOLUTE_CART_RAM_OFFSET
                        self._upper_mappings[5] = self.ABSOLUTE_CART_RAM_OFFSET + self.ABSOLUTE_SEGMENT_SIZE
                    else:
                        self._upper_mappings[4] = self.ABSOLUTE_PAGE_X_ROM_OFFSET + (self.BANK_SIZE * self._page_2)
                        self._upper_mappings[5] = self.ABSOLUTE_PAGE_X_ROM_OFFSET + (self.BANK_SIZE * self._page_2) + self.ABSOLUTE_SEGMENT_SIZE
    
        if (self.get_absolute_address(address) >= min(self.ABSOLUTE_CART_RAM_OFFSET, self.ABSOLUTE_SYS_RAM_OFFSET)):
            self._memory_map[self.get_absolute_address(address)] = data

