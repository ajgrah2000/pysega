"""
    Implementations of different cartridge types.
"""

class GenericCartridge(object):

    def __init__(self, file_name):
        self.cartridge_banks = [[]]
        self.ram = []
        self._file_name = file_name

        self._load_cartridge(file_name)

    def get_save_state(self):
        # TODO
        state = {}
        return state

    def set_save_state(self, state):
        # TODO
        pass

    def read(self, address):
        data = self.cartridge_banks[self.current_bank][address]
        return data

    def write(self, address, data):
        pass

    def _load_cartridge(self, filename):
        total_bytes_read = 0

        print("Opening:", filename)

        with open(filename, 'rb') as rom_file:

            self.max_cartridge = [[]]

if __name__ == '__main__':
    pass
