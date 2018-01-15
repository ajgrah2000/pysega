import unittest
import pysega.memory.memory as memory

class MemoryReferenceImplementation(object):
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

        # 'cache' of memory.  Copy of memory to ready from, updated when paging changes.
        self._cached_read = [0] * self.MEMMAPSIZE
        self._pages = [None] * 4

        # Complete memory map
        self._memory_map     = None

    def initialise_test_memory(self, cartridge):
        """ Initialise memory bank allocations. """

        self.cartridge = cartridge
        self._memory_map     = [0] * self.MEMMAPSIZE

    def reference_read(self, address):
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


    def reference_write(self, address, data):
        """ Un-optimised address translation, uses paging registers. 
        """

        address = address & 0xFFFF # ADDRESS_MASK
        bank_address = address & 0x3FFF # BANK_MASK

        if(address >= self.PAGING_REGISTERS):
            self._memory_map[address] = data
        elif(address < self.PAGE0):
            self.cartridge.cartridge_banks[0][bank_address] = data
        elif(address < self.PAGE1):
            page0_bank = self._memory_map[0xFFFD]
            self.cartridge.cartridge_banks[page0_bank][bank_address] = data
        elif(address < self.PAGE2):
            page1_bank = self._memory_map[0xFFFE]
            self.cartridge.cartridge_banks[page1_bank][bank_address] = data
        elif(address < self.RAM_OFFSET):
            ram_select = self._memory_map[0xFFFC]
            if (ram_select & 0x8): # page2_is_cartridge_ram
              if (ram_select & 0x4):
                cartridge_ram_page = 1
              else:
                cartridge_ram_page = 0
      
              self.cartridge.ram[cartridge_ram_page][bank_address] = data
            else:
              page2_bank = self._memory_map[0xFFFF]
              self.cartridge.cartridge_banks[page2_bank][bank_address] = data
        elif(address < self.PAGING_REGISTERS):
            # This covers RAM & Mirrored RAM
            self._ram[address & (self.RAM_SIZE - 1)] = data


def generateTestCartridge():
    MAX_BANKS     = 64;
    BANK_SIZE     = 0x4000
    NUM_RAM_PAGES = 2;

    class  Cart(object):
        def __init__(self):
            self.ram = [[0 for i in range(BANK_SIZE)] for j in range(NUM_RAM_PAGES)]
            self.num_banks = MAX_BANKS - 2
        pass

    cartridge = Cart()
    cartridge.cartridge_banks = [[]] * MAX_BANKS

    for i in range(MAX_BANKS):
        cartridge.cartridge_banks[i] = [(x & 0xC0) + i for x in range(BANK_SIZE)]

    return cartridge

class TestMemoryPaging(unittest.TestCase):

    def setUp(self):
        self._catridge_ref = generateTestCartridge()
        self._catridge_uut = generateTestCartridge()
        self._catridge_uut2 = generateTestCartridge()

    def testMemoryRead(self):
        reference_memory = MemoryReferenceImplementation()
        uut_memory = memory.MemoryCached()
        uut2_memory = memory.MemoryShare()

        reference_memory.initialise_test_memory(self._catridge_ref)
        uut_memory.set_cartridge(self._catridge_uut)
        uut2_memory.set_cartridge(self._catridge_uut2)

        self.assertEqual(reference_memory.reference_read(0),0)
        self.assertEqual(reference_memory.reference_read(0x80),0x80)
        self.assertEqual(uut2_memory.read(0x80),0x80)

        PAGE2      = 0x8000
        reference_memory.reference_write(0xFFFC,0x8)
        uut_memory.write(0xFFFC,0x8)
        uut2_memory.write(0xFFFC,0x8)

        self.assertEqual(reference_memory.reference_read(0xFFFC),0x8)
        self.assertEqual(uut_memory.read(0xFFFC),0x8)

        reference_memory.reference_write(PAGE2,2)
        uut_memory.write(PAGE2,2)
        uut2_memory.write(PAGE2,2)

        for (a,d) in [(0xFFFC,0x80),(0xFFFD,0),(0xFFFE,1),(0xFFFF,2)]:
            reference_memory.reference_write(a,d)
            uut_memory.write(a,d)
            uut2_memory.write(a,d)

        reference_memory.reference_write(0xdfed,0xCD)
        uut_memory.write(0xdfed,0xCD)
        uut2_memory.write(0xdfed,0xCD)

        for i in range(0x10000):
            self.assertEqual(uut_memory.read(i),reference_memory.reference_read(i))
            self.assertEqual(uut2_memory.read(i),reference_memory.reference_read(i))
        reference_memory.reference_write(0x8000,0xC)
        uut_memory.write(0x8000,0xC)
        uut2_memory.write(0x8000,0xC)


        reference_memory.reference_write(0x4000,0xC)
        uut_memory.write(0x4000,0xC)
        uut2_memory.write(0x4000,0xC)

        self.assertEqual(reference_memory.reference_read(0x4000), 0xC)
        self.assertEqual(reference_memory.reference_read(0), 0x0)
        self.assertEqual(uut_memory.read(0x4000), 0xC)
        self.assertEqual(uut2_memory.read(0x4000), 0xC)

        self.assertEqual(uut_memory.read(0), 0x0)

        reference_memory.reference_write(0xFFFC,0xC)
        uut_memory.write(0xFFFC,0xC)
        uut2_memory.write(0xFFFC,0xC)

        for i in range(0x10000):
            self.assertEqual(uut_memory.read(i),reference_memory.reference_read(i))
            self.assertEqual(uut2_memory.read(i),reference_memory.reference_read(i))
        



