"""
    Implementations of different cartridge types.
"""

class GenericCartridge(object):

    NUM_RAM_PAGES = 2
    BANK_SIZE     = 0x4000
    MAX_BANKS     = 64;
    LOWERMASK  = 0x03FFF

    def __init__(self, 
                 file_name, 
                 max_banks     = MAX_BANKS, 
                 bank_size     = BANK_SIZE, 
                 num_ram_pages = NUM_RAM_PAGES):

        self.cartridge_banks = [[]]
        self.ram             = []

        self._file_name    = file_name

        self.max_banks     = max_banks
        self.bank_size     = bank_size
        self.num_ram_pages = num_ram_pages

        self._load_cartridge(file_name)

    def get_save_state(self):
        # TODO
        state = {}
        return state

    def set_save_state(self, state):
        # TODO
        pass

    def read(self, address):
        data = self.cartridge_banks[self.current_bank][address & GenericCartridge.LOWERMASK]
        return data

    def write(self, address, data):
        pass

    def _load_cartridge(self, filename):
        total_bytes_read = 0

        self.max_cartridge = [[]] * self.max_banks

        print("Opening:", filename)

        with open(filename, 'rb') as rom_file:
            self.num_banks = 0

            full = rom_file.read()

            for bank in self._chunks(full, self.bank_size):
                bytes_read = len(bank)

                if (bytes_read > 0) and (bytes_read < self.bank_size):
                    print "Short Bank, padding with zeros"
                    # If the bank is short, pad it with zeros.
                    bank += bytearray('\000'.encode() * (self.bank_size-bytes_read))

#                bank += bytearray('\000'.encode() * (0x10000))
                self.max_cartridge[self.num_banks] = bytearray(bank)

                self.num_banks += 1
                total_bytes_read += bytes_read

            self.cartridge_banks = [[]] * self.num_banks

            for i in range(self.num_banks):
              self.cartridge_banks[i] = [x for x in self.max_cartridge[i]]

            # Set default bank
            self.current_bank = 0

            print("Cartridge read:")
            print(" banks = ", self.num_banks)
            print(" bytes = ", total_bytes_read)
            print(" first bank size = ", len(self.cartridge_banks[0]))

            # Allocate memory for possible battery back RAM
            self.ram = [[0]*self.bank_size] * self.num_ram_pages

    def _chunks(self, l, n):
        for i in range(0, len(l), n):
            yield l[i:i+n]


if __name__ == '__main__':
    pass
