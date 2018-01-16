#from . import addressing
from . import instructions
from . import instruction_store
from . import pc_state
from . import flagtables
from .. import errors

class Core(object):
    """
        CPU Core - Contains op code mappings.
    """

    IRQIM1ADDR = 0x38;

    def __init__(self, clocks, memory, pc_state, ports, interuptor):

        self.clocks     = clocks
        self.memory     = memory
        self.pc_state   = pc_state
        self.ports      = ports
        self.interuptor = interuptor

        self.instruction_exe = instructions.InstructionExec(self.pc_state)

        self.instruction_lookup = instruction_store.InstructionStore(self.clocks, self.pc_state, self.ports, self.instruction_exe)

        self._nextPossibleInterupt = 0

        flagtables.FlagTables.init()

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

    def interupt(self):
        if (self.pc_state.IFF1 == 1):
            if (self.pc_state.IM == 1):
                self.pc_state.SP -= 1;
                self.memory.write(self.pc_state.SP, self.pc_state.PCHigh);
                self.pc_state.SP -= 1;
                self.memory.write(self.pc_state.SP, self.pc_state.PCLow);
                self.pc_state.PC = self.IRQIM1ADDR;

                # Disable maskable interupts
                self.pc_state.IFF1 = 0;
            else:
                errors.unsupported("interupt mode not supported");

    def initialise(self):
        self.instruction_lookup.populate_instruction_map(self.clocks, self.pc_state, self.memory, self.interupt, self.interuptor.pollInterupts, self.step)

    def step_debug(self):
    
          print ("%d %d"%(self.clocks.cycles, self._nextPossibleInterupt))
  
          if (self.clocks.cycles >= self._nextPossibleInterupt):
              self.interuptor.setCycle(self.clocks.cycles);
              self._nextPossibleInterupt = self.interuptor.getNextInterupt(self.clocks.cycles);
  
          op_code = self.memory.read(self.pc_state.PC);

          print("%d %x %x (%x) %s"%(self.clocks.cycles, op_code, self.pc_state.PC, op_code, self.pc_state))
  
          # This will raise an exception for unsupported op_code
          # Need to add cycles *after* to ensure during recursive calls (ie
          # EI), the 'child' clock increase doesn't get clobbered. (ie self.clocks isn't on stack).
          self.clocks.cycles = self.instruction_lookup.getInstruction(op_code).execute(self.memory) + self.clocks.cycles

    def step(self):
    
          if (self.clocks.cycles >= self._nextPossibleInterupt):
              self.interuptor.setCycle(self.clocks.cycles);
              self._nextPossibleInterupt = self.interuptor.getNextInterupt(self.clocks.cycles);
  
          op_code = self.memory.read(self.pc_state.PC);

          # This will raise an exception for unsupported op_code
          # Need to add cycles *after* to ensure during recursive calls (ie
          # EI), the 'child' clock increase doesn't get clobbered. (ie self.clocks isn't on stack).
          self.clocks.cycles = self.instruction_lookup.getInstruction(op_code).execute(self.memory) + self.clocks.cycles
