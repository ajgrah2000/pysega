import unittest
import pysega.memory.memory as memory
import pysega.memory.memory_legacy as memory_legacy

class MemoryReferenceImplementation(object):
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

    def __init__(self):
        self._last_page_number = 0
        self._last_bank_number = 0

        self._ram     = [0] * self.RAM_SIZE

        # 'cache' of memory.  Copy of memory to ready from, updated when paging changes.
        self._cached_read = [0] * self.MEMMAPSIZE
        self._pages = [None] * 4

        # Complete memory map
        self._memory_map     = [0] * self.MEMMAPSIZE

    def set_cartridge(self, cartridge):
        self.cartridge = cartridge

    def read(self, address):
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
        else:
            # control register values reads are the contents of ram.
            # This covers RAM & Mirrored RAM
            result = self._ram[address & (self.RAM_SIZE - 1)]

        return result


    def write(self, address, data):
        """ Un-optimised address translation, uses paging registers. 
        """

        address = address & 0xFFFF # ADDRESS_MASK
        bank_address = address & 0x3FFF # BANK_MASK

        if(address >= self.RAM_OFFSET):
            # This covers RAM & Mirrored RAM
            self._ram[address & (self.RAM_SIZE - 1)] = data

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
            else:
              page2_bank = self._memory_map[0xFFFF]
              #self.cartridge.cartridge_banks[page2_bank][bank_address] = data

def get_generated_rom_data(bank, bank_address):
    return (bank_address & 0xC0) + bank

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
#        cartridge.cartridge_banks[i] = [(x & 0xC0) + i for x in range(BANK_SIZE)]
        cartridge.cartridge_banks[i] = [get_generated_rom_data(i,x) for x in range(BANK_SIZE)]

    return cartridge

class TestMemoryPaging(unittest.TestCase):

    def setUp(self):
        self._catridge_ref = generateTestCartridge()
        self._catridge_uut = generateTestCartridge()
        self._catridge_uut2 = generateTestCartridge()

    def testMemoryRead(self):
        reference_memory = MemoryReferenceImplementation()
        uut_memory = memory_legacy.MemoryCached()
        uut2_memory = memory.MemoryShare()

        reference_memory.set_cartridge(self._catridge_ref)
        uut_memory.set_cartridge(self._catridge_uut)
        uut2_memory.set_cartridge(self._catridge_uut2)

        self.assertEqual(reference_memory.read(0),0)
        self.assertEqual(reference_memory.read(0x80),0x80)
        self.assertEqual(uut2_memory.read(0x80),0x80)

        PAGE2      = 0x8000
        reference_memory.write(0xFFFC,0x8)
        uut_memory.write(0xFFFC,0x8)
        uut2_memory.write(0xFFFC,0x8)

        self.assertEqual(reference_memory.read(0xFFFC),0x8)
        self.assertEqual(uut_memory.read(0xFFFC),0x8)

        reference_memory.write(PAGE2,2)
        uut_memory.write(PAGE2,2)
        uut2_memory.write(PAGE2,2)

        for (a,d) in [(0xFFFC,0x80),(0xFFFD,0),(0xFFFE,1),(0xFFFF,2)]:
            reference_memory.write(a,d)
            uut_memory.write(a,d)
            uut2_memory.write(a,d)

        reference_memory.write(0xdfed,0xCD)
        uut_memory.write(0xdfed,0xCD)
        uut2_memory.write(0xdfed,0xCD)

        for i in range(0x10000):
            self.assertEqual(uut_memory.read(i),reference_memory.read(i))
            self.assertEqual(uut2_memory.read(i),reference_memory.read(i))
        reference_memory.write(0x8000,0xC)
        uut_memory.write(0x8000,0xC)
        uut2_memory.write(0x8000,0xC)

        reference_memory.write(0x4000,0xC)
        uut_memory.write(0x4000,0xC)
        uut2_memory.write(0x4000,0xC)

        self.assertEqual(reference_memory.read(0x4000), 0x1)
        self.assertEqual(reference_memory.read(0), 0x0)
        self.assertEqual(uut_memory.read(0x4000), 0x1)
        self.assertEqual(uut2_memory.read(0x4000), 0x1)

        self.assertEqual(uut_memory.read(0), 0x0)

        reference_memory.write(0xFFFC,0xC)
        uut_memory.write(0xFFFC,0xC)
        uut2_memory.write(0xFFFC,0xC)

        for i in range(reference_memory.RAM_OFFSET, reference_memory.RAM_OFFSET + reference_memory.RAM_SIZE):
            self.assertEqual(uut_memory.read(i),uut_memory.read(i + reference_memory.RAM_SIZE))
            self.assertEqual(uut2_memory.read(i),uut2_memory.read(i + reference_memory.RAM_SIZE))
            self.assertEqual(reference_memory.read(i),reference_memory.read(i + reference_memory.RAM_SIZE))

        for i in range(0x10000):
            self.assertEqual(uut_memory.read(i),reference_memory.read(i))
            self.assertEqual(uut2_memory.read(i),reference_memory.read(i))

    def testMemoryAccesses(self):
        uut_memory = memory.MemoryShare()
        self.checkMemoryAccesses(uut_memory)

        uut_memory = MemoryReferenceImplementation()
        self.checkMemoryAccesses(uut_memory)

        uut_memory = memory_legacy.MemoryCached()
        self.checkMemoryAccesses(uut_memory)

    def checkMemoryAccesses(self, uut_memory):
        test_cartridge = generateTestCartridge()
        uut_memory.set_cartridge(test_cartridge)

        # Paging registers.
        self.assertEqual(uut_memory.read(0xFFFC),0x0)
        self.assertEqual(uut_memory.read(0xFFFD),0x0)
        self.assertEqual(uut_memory.read(0xFFFE),0x0)
        self.assertEqual(uut_memory.read(0xFFFF),0x0)

        # Check 'page 0' (ensure 'writes' to ROM addresses are ignored.)
        uut_memory.write(0x0, uut_memory.read(0x0) + 1)
        self.assertEqual(uut_memory.read(0x0),0x0)
        self.assertEqual(uut_memory.read(0x3FF),get_generated_rom_data(0, 0x3FF))
        uut_memory.write(0x400, uut_memory.read(0x400) + 1)
        self.assertEqual(uut_memory.read(0x400),get_generated_rom_data(0, 0x400))
        self.assertEqual(uut_memory.read(0x3FFF),get_generated_rom_data(0, 0x3FFF))

        # Change bank used for 'page0', ensure first section insn't swapped out.
        uut_memory.write(0xFFFD,0x9)
        uut_memory.write(0x0, uut_memory.read(0x0) + 1)
        self.assertEqual(uut_memory.read(0x0),0x0)
        self.assertEqual(uut_memory.read(0x3FF),get_generated_rom_data(0, 0x3FF))
        uut_memory.write(0x400, uut_memory.read(0x400) + 1)
        self.assertEqual(uut_memory.read(0x400),get_generated_rom_data(9, 0x400))
        self.assertEqual(uut_memory.read(0x3FFF),get_generated_rom_data(9, 0x3FFF))

        # Check 'page 1' (ensure 'writes' to ROM addresses are ignored.)
        uut_memory.write(0x4000, uut_memory.read(0x4000) + 1)
        self.assertEqual(uut_memory.read(0x4000),get_generated_rom_data(0, 0x0))
        self.assertEqual(uut_memory.read(0x7FFF),get_generated_rom_data(0, 0x3FFF))

        # Check 'page 2' (ensure 'writes' to ROM addresses are ignored.)
        uut_memory.write(0x8000, uut_memory.read(0x8000) + 1)
        self.assertEqual(uut_memory.read(0x8000),get_generated_rom_data(0, 0x0))
        self.assertEqual(uut_memory.read(0xBFFF),get_generated_rom_data(0, 0x3FFF))

        # Check writes to 'page 2' 'ram page 0'
        uut_memory.write(0xFFFC,0x08)
        self.assertEqual(uut_memory.read(0x8000),0x0)
        self.assertEqual(uut_memory.read(0xBFFF),0x0)
        uut_memory.write(0x8000, 0x11)
        uut_memory.write(0xBFFF, 0x21)
        self.assertEqual(uut_memory.read(0x8000),0x11)
        self.assertEqual(uut_memory.read(0xBFFF),0x21)

        # Check writes to 'page 2' 'ram page 1'
        uut_memory.write(0xFFFC,0x0C)
        self.assertEqual(uut_memory.read(0x8000),0x0)
        self.assertEqual(uut_memory.read(0xBFFF),0x0)
        uut_memory.write(0x8000, 0x13)
        uut_memory.write(0xBFFF, 0x23)
        self.assertEqual(uut_memory.read(0x8000),0x13)
        self.assertEqual(uut_memory.read(0xBFFF),0x23)

        # Check writes to 'page 2' 'ram page 0' (ensure previous value was remembered)
        uut_memory.write(0xFFFC,0x08)
        self.assertEqual(uut_memory.read(0x8000),0x11)
        self.assertEqual(uut_memory.read(0xBFFF),0x21)
        uut_memory.write(0x8000, 0x19)
        uut_memory.write(0xBFFF, 0x29)
        self.assertEqual(uut_memory.read(0x8000),0x19)
        self.assertEqual(uut_memory.read(0xBFFF),0x29)

        uut_memory.write(0xFFFC,0x0C)
        self.assertEqual(uut_memory.read(0x8000),0x13)
        self.assertEqual(uut_memory.read(0xBFFF),0x23)

        # Reset page registers
        uut_memory.write(0xFFFC,0x0)
        uut_memory.write(0xFFFD,0x0) # PAGE 0
        uut_memory.write(0xFFFE,0x0) # PAGE 1
        uut_memory.write(0xFFFF,0x0) # PAGE 2

        # Check RAM
        self.assertEqual(uut_memory.read(0xC000),0x0)
        self.assertEqual(uut_memory.read(0xDFFF),0x0)

        # Check Mirror RAM
        self.assertEqual(uut_memory.read(0xE000),0x0)
        self.assertEqual(uut_memory.read(0xFFFF),0x0)

        uut_memory.write(0xDFFF,0x55)
        uut_memory.write(0xE000,0x3)
        self.assertEqual(uut_memory.read(0xE000),0x3)
        self.assertEqual(uut_memory.read(0xC000),0x3)

        uut_memory.write(0xDFF0,0x9)
        self.assertEqual(uut_memory.read(0xDFF0),0x9)
        self.assertEqual(uut_memory.read(0xFFF0),0x9)

        # Although write maps to 'mirrored' controll register, don't change paging.
        uut_memory.write(0xDFFD,0x8)
        self.assertEqual(uut_memory.read(0xDFFD),0x8)
        self.assertEqual(uut_memory.read(0xFFFD),0x8)
        # Ensure cartridge ROM hasn't changed
        self.assertEqual(uut_memory.read(0x3FFF),get_generated_rom_data(0, 0x3FFF))

        # Change paging and mirrored ram value.
        uut_memory.write(0xFFFD,0x2)
        self.assertEqual(uut_memory.read(0xDFFD),0x2)
        self.assertEqual(uut_memory.read(0xFFFD),0x2)
        self.assertEqual(uut_memory.read(0x3FFF),get_generated_rom_data(2, 0x3FFF))

