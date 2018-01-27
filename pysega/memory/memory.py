from .. import errors

class MemoryBase(object):
    """ Memory map management of sega master system/cartridges/ram
    """
    MEMREGISTERS    = 0xFFFC
    ADDRESS_MASK    = 0xFFFF
    RAMMASK         = 0xDFFF;

    RAM_SELECT_REGISTER        = 0xFFFC
    PAGE0_BANK_SELECT_REGISTER = 0xFFFD
    PAGE1_BANK_SELECT_REGISTER = 0xFFFE
    PAGE2_BANK_SELECT_REGISTER = 0xFFFF

    MAPCARTRAM      = 0x08
    PAGEOFRAM       = 0x04
    PAGEOFRAMBITPOS = 2

    # Memory map offsets
    PAGE0      = 0x400  # 0 to Page0 offset always holds bank 0 
    PAGE1      = 0x4000
    PAGE2      = 0x8000
    RAM_OFFSET = 0xC000
    RAM_SIZE   = 0x2000 # Upper RAM is mirrored

    MEMMAPSIZE = 0x10000
    UPPERSHIFT = 14
    LOWERMASK  = 0x03FFF

class MemoryShare(MemoryBase):
    """ Swap 'references' to arrays on bank switching instead of copying lists.
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
        self._pages = [None] * 4
        self._paging_register_page0 = 0
        self._paging_register_page1 = 1
        self._paging_register_page2 = 2
        self._paging_register_ram   = 0

        # Location to store the page references.
        self._memory_shared_lookup = [[0] * self.BANK_SIZE for x in range(4)]

        # Complete memory map
        self._memory_map     = None

    def read(self, address):
        """ Assumes 'address' is 'int' or accepts >> operator. """
        # Using constants here to increase speed.
        return self._memory_shared_lookup[address >> 14][address & 0x3FFF]

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

        self._populate_shared_lookups()
        self._update_fixed_read_page0()
        self._update_fixed_read_page1()
        self._update_fixed_read_page2_ram()

    def _populate_shared_lookups(self):
        for bank in range(self.cartridge.num_banks):
            # Page '0'/'1' lookup
            for address in range(self.PAGE0):
                bank_address = address & self.LOWERMASK # BANK_MASK
                self._page0_copies[bank][bank_address] = self.cartridge.cartridge_banks[0][bank_address]

            for address in range(self.PAGE0, self.PAGE1):
                bank_address = address & self.LOWERMASK # BANK_MASK
                self._page0_copies[bank][bank_address] = self.cartridge.cartridge_banks[bank][bank_address]

        self._memory_shared_lookup[3] = self._ram

    def _update_fixed_read_page0(self):
        page0_bank = self._paging_register_page0
        self._memory_shared_lookup[0] = self._page0_copies[page0_bank]

    def _update_fixed_read_page1(self):
        page1_bank = self._paging_register_page1
        self._memory_shared_lookup[1] = self.cartridge.cartridge_banks[page1_bank]

    def _update_fixed_read_page2_ram(self):
        ram_select = self._paging_register_ram

        if (ram_select & self.MAPCARTRAM): # page2_is_cartridge_ram
          if (ram_select & self.PAGEOFRAM):
            cartridge_ram_page = 1
          else:
            cartridge_ram_page = 0
      
          self._memory_shared_lookup[2] = self.cartridge.ram[cartridge_ram_page]

        else:
          page2_bank = self._paging_register_page2
          if (page2_bank < len(self.cartridge.cartridge_banks)):
             self._memory_shared_lookup[2] = self.cartridge.cartridge_banks[page2_bank]
          else:
             # Assume this is a 'transient' situation, force an error if
             # subsequently accessed.
             print("Page 2: slection larger than cratridge. 0x%x"%(data))
             self._memory_shared_lookup[2] = None

    def _write(self, address, data):
        address = address & self.ADDRESS_MASK # ADDRESS_MASK
        bank_address = address & self.LOWERMASK # BANK_MASK

        if(address >= self.RAM_OFFSET):
            # Memory control registers are written through to RAM
            self._ram[address & (self.RAM_SIZE - 1)] = data
            # Ram is 'half' size, so duplicate write to mirror section of array
            self._ram[(address & (self.RAM_SIZE - 1)) + self.RAM_SIZE] = data

            if(address >= self.MEMREGISTERS):
                # Should make these conditiona, 
                if (address == self.PAGE0_BANK_SELECT_REGISTER):
                    self._paging_register_page0 = data
                    if (self._pages[0] != data):
                        self._update_fixed_read_page0()
                        self._pages[0] = data
                elif (address == self.PAGE1_BANK_SELECT_REGISTER):
                    self._paging_register_page1 = data
                    if (self._pages[1] != data):
                        self._update_fixed_read_page1()
                        self._pages[1] = data
                elif ((address == self.RAM_SELECT_REGISTER) or (address == self.PAGE2_BANK_SELECT_REGISTER)):
                    if   (address == self.RAM_SELECT_REGISTER):
                        self._paging_register_ram = data
                    elif (address == self.PAGE2_BANK_SELECT_REGISTER):
                        self._paging_register_page2 = data
    
                    if (self._pages[2] != data):
                        self._update_fixed_read_page2_ram()
                        self._pages[2] = data
    
        elif (address < self.RAM_OFFSET) and (address >= self.PAGE2):
            ram_select = self._paging_register_ram
            if (ram_select & 0x8): # page2_is_cartridge_ram
              if (ram_select & 0x4):
                cartridge_ram_page = 1
              else:
                cartridge_ram_page = 0
      
              self.cartridge.ram[cartridge_ram_page][bank_address] = data
            else:
              print("Warning writting to ROM address %x"%(address))
        else:
            print("Warning to unexpected address %x"%(address))
