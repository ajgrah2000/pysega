#from . import addressing
from . import instructions
from . import pc_state

class Core(object):
    """
        CPU Core - Contains op code mappings.
    """
    def __init__(self, clocks, memory, pc_state):
        self.clocks    = clocks
        self.memory    = memory
        self.pc_state  = pc_state

        self.instruction_exe = instructions.InstructionExec(self.pc_state)

        self.instruction_lookup = [instructions.Instruction(self.clocks, self.pc_state, self.instruction_exe)] * 256

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
        self.populate_instruction_map()

    def step(self):
        op_code = self.memory.read(self.pc_state.PC)
        print "%x"%(op_code)
    
        # This will raise an exception for unsupported op_code
        self.instruction_lookup[op_code].execute()

    def populate_instruction_map(self):
        self.instruction_lookup[0xC3] = instructions.JumpInstruction(self.clocks, self.pc_state, self.memory)
        pass
