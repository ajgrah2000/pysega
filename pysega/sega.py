from .memory import memory
from .memory import memory_absolute
from .memory import cartridge
from .graphics import vdp
from . import clocks
from . import inputs
from . import ports

class DummyPort(object):
    def __init__(self):
        pass

    def writePort(self, value):
        print "Dummy write not implemented"
        pass

    def readPort(self):
        print "Dummy read not implemented"
        return 0

class DummySound(object):
    def __init__(self):
        pass

    def writePort(self, value):
        pass

class Sega(object):
    def __init__(self, Graphics, audio, cpu):
        self.clocks    = clocks.Clock()
        self.pc_state  = cpu.pc_state.PC_State()
        self.ports     = ports.Ports()
        self.inputs    = inputs.Input()
        #TODO: Fix, combine 'inputs' in a better way. 
        self.inputs.joystick  = inputs.Joystick() 

        self.sound     = DummySound()
#        self.memory    = memory.MemoryReference()
#        self.memory    = memory.MemoryCached()
#        self.memory    = memory.MemoryShare()
        self.memory    = memory_absolute.MemoryAbsolute()
        self.vdp       = Graphics(self.clocks,  self.inputs, audio)
        self.core      = cpu.core.Core(self.clocks, self.memory, self.pc_state, self.ports, self.vdp)

        self.vdp.setInterupt(self.core) # This can probably be decoupled.

        self.core.initialise()
        self.configure_ports(self.ports)

    def set_palette(self, palette_type):
        self.vdp.set_palette(palette_type)

    def configure_ports(self, ports):
        dummyPort = DummyPort()

        for i in range(0x100):
            ports.addDeviceToPort(i, dummyPort.readPort);

        # Add the vdp `BF' port to BF plus all the mirror ports
        # BF is the vdp control port
        for i in range(0x81, 0xC0, 2):
            ports.addDeviceToPort(i, self.vdp.readPortBF, self.vdp.writePortBF);
    
        # Add the vdp `BE' port to BE plus all the mirror ports
        # BF is the vdp data port
        for i in range(0x80, 0xC0,2):
            ports.addDeviceToPort(i, self.vdp.readPortBE, self.vdp.writePortBE)
    
        # Add the vdp and sound to port `7E' plus all the mirror ports
        # 7E is the vdp vCounter and sound port
        for i in range(0x40, 0x80, 2):
            ports.addDeviceToPort(i, self.vdp.readPort7E);
            ports.addDeviceToPort(i, None, self.sound.writePort);
    
        # Add the vdp and sound to port `7F' plus all the mirror ports
        # 7& is the vdp hCounter and sound port
        for i in range(0x41, 0x80, 2):
            ports.addDeviceToPort(i, self.vdp.readPort7F);
            ports.addDeviceToPort(i, None, self.sound.writePort);
    
        # Add the joystics to their ports
        ports.addDeviceToPort(0xDC, self.inputs.joystick.readPort1);
        ports.addDeviceToPort(0xDD, self.inputs.joystick.readPort2);

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

        self.core.reset()

        quit_func = self.inputs.get_quit

        try:
          if debug:
              step_func = self.core.step_debug
              if 0 == stop_clock:
                  while 0 == quit_func():
                      step_func()
              else:
                  clk = self.clocks
                  while clk.cycles < stop_clock:
                      step_func()
          else:
              step_func = self.core.step
              if 0 == stop_clock:
                  while 0 == quit_func():
                      step_func()
              else:
                  clk = self.clocks
                  while clk.cycles < stop_clock:
                      step_func()
        except:
            op_code = self.memory.read(self.pc_state.PC)
            raise

        finally:
            pass

        print("Sega finished")
