import ctypes

class Instruction(object):

    def __init__(self, clocks, pc_state, instruction_exec):
        self.clocks = clocks
        self.pc_state = pc_state
        self.instruction_exec = instruction_exec

    def execute(self):
        pass

    def _exec(self, data):
        return self.instruction_exec(data)

class JumpInstruction(Instruction):
     
    def __init__(self, clocks, pc_state, memory):
        super(JumpInstruction, self).__init__(clocks, pc_state, None)
        self.memory = memory

    def execute(self):
        self.pc_state.PC = self.memory.read16(self.pc_state.PC + 1)
        self.clocks.system_clock += 10

class InstructionExec(object):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    def NOP_exec(self, data):
        """NOP"""
        self.pc_state.PC = self.pc_state.PC + 1
        return int(data)
