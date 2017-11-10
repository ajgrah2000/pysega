class InstructionStore(object):
    def __init__(self):
        self.instruction_lookup = [instructions.Instruction(self.clocks, self.pc_state, self.instruction_exe)] * 256
        self.instruction_cb_lookup = [instructions.Instruction(self.clocks, self.pc_state, self.instruction_exe)] * 256
        self.instruction_dd_lookup = [instructions.Instruction(self.clocks, self.pc_state, self.instruction_exe)] * 256
        self.instruction_ed_lookup = [instructions.Instruction(self.clocks, self.pc_state, self.instruction_exe)] * 256
        self.instruction_fd_lookup = [instructions.Instruction(self.clocks, self.pc_state, self.instruction_exe)] * 256

    def populate_instruction_map(self, clocks, pc_state, memory):
        self.instruction_lookup[0xC3] = instructions.JumpInstruction(clocks, pc_state, memory)

    def getInstruction(self, op_code):
      instruction = None
      if op_code in self.instruction_lookup:
          instruction = self.instruction_lookup[op_code]
      return instruction

    def getExtendedCB(self, cb_op_code):
      instruction = None
      if cb_op_code in self.instruction_cb_lookup:
          instruction = self.instruction_cb_lookup[cb_op_code]
      return instruction


    def getExtendedDD(self, dd_op_code):
      instruction = None
      if dd_op_code in self.instruction_dd_lookup:
          instruction = self.instruction_dd_lookup[dd_op_code]
      return instruction

    def getExtendedED(self, ed_op_code):
      instruction = None
      if ed_op_code in self.instruction_ed_lookup:
          instruction = self.instruction_ed_lookup[ed_op_code]
      return instruction

    def getExtendedFD(self, fd_op_code):
      instruction = None
      if fd_op_code in self.instruction_fd_lookup:
          instruction = self.instruction_fd_lookup[fd_op_code]
      return instruction
