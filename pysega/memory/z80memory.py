
class Z80Memory(object):

    # TODO
    RAMSIZE = 64 * 1024
    def __init__(self, clock, inputs):
        self.ram = [0] * self.RAMSIZE

    def read(self, addr):
        # TODO
        return 0

    def write(self, addr, data):
        # TODO
        pass
