from .. import errors

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
    RAM_OFFSET = 0xC000
    PAGING_REGISTERS = 0xFFFC
    RAM_SIZE   = 0x2000

    MEMMAPSIZE = 0x10000
    UPPERSHIFT = 14
    LOWERMASK  = 0x03FFF

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

        if (((dest + length) >= self.MEMMAPSIZE) or (dest < self.RAMOFFSET)):
            errors.warning("Write out of range %x"%(dest + length))
            return

        for i in range(length):
            self.write(dest+i, self.read(src+i))

    def write(self, address, data):
        self._translate_write(address, int(data))

    def set_cartridge(self, cartridge):
        self.cartridge = cartridge

        self._initialise_memory()

    def set_z80memory(self, z80memory):
        self.z80memory = z80memory

    def readMulti(self, address):
        return [self.read(address + x) for x in range(10)]

    def _translate_read(self, address):
        """ Un-optimised address translation, uses paging registers. 
        """

        ADDRESS_MASK = 0xFFFF
        BANK_MASK = 0x3FFF
        address = address & ADDRESS_MASK
        bank_address = address & BANK_MASK

        ram_select = self._memory_map[0xFFFC]
        page0_bank = self._memory_map[0xFFFD]
        page1_bank = self._memory_map[0xFFFE]
        page2_bank = self._memory_map[0xFFFF]

        if (ram_select & 0x8):
          page2_is_cartridge_ram = True
        else:
          page2_is_cartridge_ram = False

        if (ram_select & 0x4):
          cartridge_ram_page = 1
        else:
          cartridge_ram_page = 0

        if(address < self.PAGE0):
            result = self.cartridge.cartridge_banks[0][bank_address]
        elif(address < self.PAGE1):
            result = self.cartridge.cartridge_banks[page0_bank][bank_address]
        elif(address < self.PAGE2):
            result = self.cartridge.cartridge_banks[page1_bank][bank_address]
        elif(address < self.RAM_OFFSET):
            if (page2_is_cartridge_ram):
              result = self.cartridge.ram[cartridge_ram_page][bank_address]
            else:
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

        ADDRESS_MASK = 0xFFFF
        BANK_MASK = 0x3FFF
        address = address & ADDRESS_MASK
        bank_address = address & BANK_MASK

        ram_select = self._memory_map[0xFFFC]
        page0_bank = self._memory_map[0xFFFD]
        page1_bank = self._memory_map[0xFFFE]
        page2_bank = self._memory_map[0xFFFF]

        if (ram_select & 0x8):
          page2_is_cartridge_ram = True
        else:
          page2_is_cartridge_ram = False

        if (ram_select & 0x4):
          cartridge_ram_page = 1
        else:
          cartridge_ram_page = 0

        if(address >= self.PAGING_REGISTERS):
            self._memory_map[address] = data
        elif(address < self.PAGE0):
            self.cartridge.cartridge_banks[0][bank_address] = data
        elif(address < self.PAGE1):
            self.cartridge.cartridge_banks[page0_bank][bank_address] = data
        elif(address < self.PAGE2):
            self.cartridge.cartridge_banks[page1_bank][bank_address] = data
        elif(address < self.RAM_OFFSET):
            if (page2_is_cartridge_ram):
              self.cartridge.ram[cartridge_ram_page][bank_address] = data
            else:
              self.cartridge.cartridge_banks[page2_bank][bank_address] = data
        elif(address < self.PAGING_REGISTERS):
            # This covers RAM & Mirrored RAM
            self._ram[address & (self.RAM_SIZE - 1)] = data

