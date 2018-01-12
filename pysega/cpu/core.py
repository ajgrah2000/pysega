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

    def initialise(self):
        self.instruction_lookup.populate_instruction_map(self.clocks, self.pc_state, self.memory)

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

    def step(self, loop=True, debug=False):
     op_code = self.memory.read(self.pc_state.PC)
    
#    static uint16 tmp16;
#    static uint8 tmp8, t8;
#    static const Byte *atPC;

#     while True:
     if True:

          # Check for any possible interupts
      if debug:
          print ("%d %d"%(self.clocks.cycles, self._nextPossibleInterupt))

      if (self.clocks.cycles >= self._nextPossibleInterupt):
          self.interuptor.setCycle(self.clocks.cycles);
          self._nextPossibleInterupt = self.interuptor.getNextInterupt(self.clocks.cycles);

      atPC = self.memory.readMulti(self.pc_state.PC);
      op_code = atPC[0]
      if debug:
          print("%d %x %x (%x) %s"%(self.clocks.cycles, op_code, self.pc_state.PC, atPC[0], self.pc_state))

      # This will raise an exception for unsupported op_code
      instruction = self.instruction_lookup.getInstruction(op_code)
      if instruction:
        self.clocks.cycles += instruction.execute(self.memory)
      else:
            # EI
            if (op_code == 0xFB):
                self.pc_state.PC += 1
           
                # Process next instruction before enabling interupts
                self.step(False); # Single step, no loop
           
                self.pc_state.IFF1 = 1;
                self.pc_state.IFF2 = 1;
                self.clocks.cycles+=4;
           
                  # Check for any pending interupts
                if (self.interuptor.pollInterupts(self.clocks.cycles) == True):
                    self.interupt()

            elif (op_code == 0xCB):
                # Temporary, until `all instructions are covered'
                instruction = self.instruction_lookup.getExtendedCB(atPC[1]);# &atPC[1]);
                if (instruction != None):
                    self.clocks.cycles += instruction.execute(self.memory);
                else:
                    errors.warning("OP 0xCB n, value %x unsupported"%(atPC[1]));
                    return -1;


            elif (op_code == 0xDD):
                # Temporary, until `all instructions are covered'
                instruction = self.instruction_lookup.getExtendedDD(atPC[1]);# &atPC[1]);
                if (instruction):
                    self.clocks.cycles += instruction.execute(self.memory);
                else:
                    print("Unsupported op code DD %x"%(atPC[1]))
                    return -1;

            elif (op_code == 0xFD):
                # Temporary, until `all instructions are covered'
                instruction = self.instruction_lookup.getExtendedFD(atPC[1]);# &atPC[1]);
                if (instruction):
                    self.clocks.cycles += instruction.execute(self.memory);
                else:
                    print("Unsupported op code FD %x"%(atPC[1]))
                    return -1;

              # Extended op_code
            elif (op_code == 0xED):
                # Temporary, until `all instructions are covered'
                instruction = self.instruction_lookup.getExtendedED(atPC[1]);# &atPC[1]);
                if (instruction):
                    self.clocks.cycles += instruction.execute(self.memory);
                else:
                    print("Unsupported op code ED %x"%(atPC[1]))
                    return -1;

            else:
                print("Unsupported op code %x"%(atPC[0]))
                return -1;

     return 0
