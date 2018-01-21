from .. import errors

class MemoryBaseLegacy(object):
    """ Memory map management of sega master system/cartridges/ram
    """
    MEMREGISTERS    = 0xFFFC
    RAMSELECTADDR   = 0xFFFC
    MAPCARTRAM      = 0x08
    PAGEOFRAM       = 0x04
    PAGEOFRAMBITPOS = 2

    PAGE0      = 0x400
    PAGE1      = 0x4000
    PAGE2      = 0x8000
    RAM_OFFSET = 0xC000
    PAGING_REGISTERS = 0xFFFC
    RAM_SIZE   = 0x2000

    MEMMAPSIZE = 0x10000
    UPPERSHIFT = 14
    LOWERMASK  = 0x03FFF

class MemoryReference(MemoryBaseLegacy):
    """ Memory map management of sega master system/cartridges/ram
    """

    def __init__(self):
        self._last_page_number = 0
        self._last_bank_number = 0

        self._ram     = [0] * self.RAM_SIZE

        # Complete memory map
        self._memory_map     = None

    def _initialise_memory(self):
        """ Initialise memory bank allocations. """

        self._memory_map     = [0] * self.MEMMAPSIZE

    def read(self, address):
        return self._translate_read(address)

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
        self._translate_write(address, int(data))

    def set_cartridge(self, cartridge):
        self.cartridge = cartridge

        self._initialise_memory()

    def _translate_read(self, address):
        """ Un-optimised address translation, uses paging registers. 
        """

        address = address & 0xFFFF # ADDRESS_MASK
        bank_address = address & 0x3FFF # BANK_MASK

        if(address < self.PAGE0):
            result = self.cartridge.cartridge_banks[0][bank_address]
        elif(address < self.PAGE1):
            page0_bank = self._memory_map[0xFFFD]
            result = self.cartridge.cartridge_banks[page0_bank][bank_address]
        elif(address < self.PAGE2):
            page1_bank = self._memory_map[0xFFFE]
            result = self.cartridge.cartridge_banks[page1_bank][bank_address]
        elif(address < self.RAM_OFFSET):
            ram_select = self._memory_map[0xFFFC]

            if (ram_select & 0x8): # page2_is_cartridge_ram
              if (ram_select & 0x4):
                cartridge_ram_page = 1
              else:
                cartridge_ram_page = 0
      
              result = self.cartridge.ram[cartridge_ram_page][bank_address]
            else:
              page2_bank = self._memory_map[0xFFFF]
              result = self.cartridge.cartridge_banks[page2_bank][bank_address]
        elif(address < self.PAGING_REGISTERS):
            # This covers RAM & Mirrored RAM
            result = self._ram[address & (self.RAM_SIZE - 1)]
        else:
            result = self._memory_map[address]

        return result


    def _translate_write(self, address, data):
        """ Un-optimised address translation, uses paging registers. 
        """

        address = address & 0xFFFF # ADDRESS_MASK
        bank_address = address & 0x3FFF # BANK_MASK

        if(address >= self.PAGING_REGISTERS):
            self._memory_map[address] = data
        elif(address < self.PAGE2):
            # No writes to PAGE0, PAGE1
            pass
        elif(address < self.RAM_OFFSET):
            ram_select = self._memory_map[0xFFFC]
            if (ram_select & 0x8): # page2_is_cartridge_ram
              if (ram_select & 0x4):
                cartridge_ram_page = 1
              else:
                cartridge_ram_page = 0
      
              self.cartridge.ram[cartridge_ram_page][bank_address] = data
        elif(address < self.PAGING_REGISTERS):
            # This covers RAM & Mirrored RAM
            self._ram[address & (self.RAM_SIZE - 1)] = data

class MemoryCached(MemoryBaseLegacy):
    """ Memory map management of sega master system/cartridges/ram
    """

    def __init__(self):
        self._last_page_number = 0
        self._last_bank_number = 0

        self._ram     = [0] * self.RAM_SIZE

        # 'cache' of memory.  Copy of memory to ready from, updated when paging changes.
        self._cached_read = [0] * self.MEMMAPSIZE
        self._pages = [None] * 4

        # Complete memory map
        self._memory_map     = None

    def _initialise_memory(self):
        """ Initialise memory bank allocations. """

        self._memory_map     = [0] * self.MEMMAPSIZE

        self._memory_map[0xFFFE] = 1
        self._memory_map[0xFFFF] = 2

    def read(self, address):
        return self._cached_read[address & 0xFFFF]

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
        self._cache_write(address, int(data))

    def set_cartridge(self, cartridge):
        self.cartridge = cartridge

        self._initialise_memory()
        self._initialise_read_cache()

    def _initialise_read_cache(self):
        """ Un-optimised address translation, uses paging registers. 
        """

        self._update_fixed_read_page()
        self._update_fixed_read_page0()
        self._update_fixed_read_page1()
        self._update_fixed_read_page2_ram()

    def _update_fixed_read_page(self):
        bank_array = self.cartridge.cartridge_banks[0]
        for address in range(self.PAGE0):
            bank_address = address & 0x3FFF # BANK_MASK
            self._cached_read[address] = bank_array[bank_address]

    def _update_fixed_read_page0(self):
        page0_bank = self._memory_map[0xFFFD]
        bank_array = self.cartridge.cartridge_banks[page0_bank]
        for address in range(self.PAGE0, self.PAGE1):
            bank_address = address & 0x3FFF # BANK_MASK
            self._cached_read[address] = bank_array[bank_address]

    def _update_fixed_read_page1(self):
        page1_bank = self._memory_map[0xFFFE]
        bank_array = self.cartridge.cartridge_banks[page1_bank]
        for address in range(self.PAGE1, self.PAGE2):
            bank_address = address & 0x3FFF # BANK_MASK
            self._cached_read[address] = bank_array[bank_address]

    def _update_fixed_read_page2_ram(self):
        ram_select = self._memory_map[0xFFFC]

        if (ram_select & 0x8): # page2_is_cartridge_ram
          if (ram_select & 0x4):
            cartridge_ram_page = 1
          else:
            cartridge_ram_page = 0
      
          bank_array = self.cartridge.ram[cartridge_ram_page]
          for address in range(self.PAGE2, self.RAM_OFFSET):
              bank_address = address & 0x3FFF # BANK_MASK
              self._cached_read[address] = bank_array[bank_address]

        else:
          page2_bank = self._memory_map[0xFFFF]
          bank_array = self.cartridge.cartridge_banks[page2_bank]
          for address in range(self.PAGE2, self.RAM_OFFSET):
              bank_address = address & 0x3FFF # BANK_MASK
              self._cached_read[address] = bank_array[bank_address]

    def _cache_write(self, address, data):
        """ Perform write.
            Copy write to the 'cached' memory array.
            If a paging selection register is written, refresh the 'cached' memory array.
        """

        address = address & 0xFFFF # ADDRESS_MASK
        bank_address = address & 0x3FFF # BANK_MASK

        if (address >= self.RAM_OFFSET):
            # Mirrored ram exists in two locations, so write to both.
            self._cached_read[self.RAM_OFFSET + (address & (self.RAM_SIZE - 1))] = data
            self._cached_read[self.RAM_OFFSET + (address & (self.RAM_SIZE - 1)) + self.RAM_SIZE] = data

            if(address >= self.PAGING_REGISTERS):
                self._memory_map[address] = data
                self._cached_read[address] = data
    
                # Should make these conditiona, 
                if (address == 0xFFFD):
                    if (self._pages[0] != data):
                        self._update_fixed_read_page0()
                        self._pages[0] = data
                elif (address == 0xFFFE):
                    if (self._pages[1] != data):
                        self._update_fixed_read_page1()
                        self._pages[1] = data
                elif ((address == 0xFFFC) or (address == 0xFFFF)):
                    if (self._pages[2] != data):
                        self._update_fixed_read_page2_ram()
                        self._pages[2] = data
    
                self._cached_read[address] = data
    
        elif(address < self.PAGE0):
            pass
        elif(address < self.PAGE1):
            pass
        elif(address < self.PAGE2):
            pass
        elif(address < self.RAM_OFFSET):
            ram_select = self._memory_map[0xFFFC]
            if (ram_select & 0x8): # page2_is_cartridge_ram
              if (ram_select & 0x4):
                cartridge_ram_page = 1
              else:
                cartridge_ram_page = 0
      
              self.cartridge.ram[cartridge_ram_page][bank_address] = data
              page2_bank = self._memory_map[0xFFFF]
              self._cached_read[address] = data
