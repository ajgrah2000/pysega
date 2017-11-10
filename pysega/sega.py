from .memory import memory
from .memory import z80memory
from .memory import cartridge
from .graphics import vdp
from . import clocks
from . import inputs

class Sega(object):
    def __init__(self, Graphics, audio, cpu):
        self.clocks    = clocks.Clock()
        self.pc_state  = cpu.pc_state.PC_State()
        self.inputs    = inputs.Input()
        self.memory    = memory.Memory()
        self.z80memory = z80memory.Z80Memory(self.clocks, self.inputs)
        self.vdp       = Graphics(self.clocks,  self.inputs, audio)
        self.core      = cpu.core.Core(self.clocks, self.memory, self.pc_state, self.vdp)

        self.core.initialise()

    def set_palette(self, palette_type):
        self.vdp.set_palette(palette_type)

    def insert_cartridge(self, cart_name):
        new_cart = cartridge.GenericCartridge(cart_name)
        self.memory.set_cartridge(new_cart)

    def get_save_state(self):
        """ TODO """
        state = {}
        return state

    def set_save_state(self, state):
        """ TODO """
        pass

    def power_on(self, stop_clock, no_delay=False, debug=False):

        self.memory.set_z80memory(self.z80memory)

        self.core.reset()

        step_func = self.core.step
        quit_func = self.inputs.get_quit

        try:
          if debug:
              if 0 == stop_clock:
                  while 0 == quit_func():
                      step_func()
              else:
                  clk = self.clocks
                  while clk.system_clock < stop_clock:
                      step_func()
          else:
              if 0 == stop_clock:
                  while 0 == quit_func():
                      step_func()
              else:
                  clk = self.clocks
                  while clk.system_clock < stop_clock:
                      step_func()
        except:
            op_code = self.memory.read(self.pc_state.PC)
            raise

        finally:
            pass

        print("Sega finished")
