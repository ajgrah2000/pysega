#from . import addressing
#from . import instructions
from . import pc_state

class Core(object):
    """
        CPU Core - Contains op code mappings.
    """
    def __init__(self, clocks, memory, pc_state):
        self.clocks    = clocks
        self.memory    = memory
        self.pc_state  = pc_state

    def get_save_state(self):
        # TODO
        state = {}
        return state

    def set_save_state(self, state):
        # TODO
        pass

    def reset(self):
        # TODO
        pass

    def initialise(self):
        # TODO
        pass

    def step(self):
        # TODO
        pass
