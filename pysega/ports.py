import errors

class Port(object):
    def __init__(self, read_func, write_func = None):
        self._write_func = write_func
        self._read_func = read_func

    def read(self):
        return self._read_func()

    def write(self, data):
        self._write_func(data)

class Ports(object):

    MAXPORTS    = 256;

    def __init__(self):
        self.read_ports  = [None] * self.MAXPORTS
        self.write_ports = [None] * self.MAXPORTS

    def addDeviceToPort(self, port_address, read_func, write_func = None):
        if read_func:
          self.read_ports[port_address] = Port(read_func, write_func)

        if write_func:
          self.write_ports[port_address] = Port(read_func, write_func)

    def portRead(self, port_address):
        if (self.read_ports[port_address]):
            return self.read_ports[port_address].read()
        else:
            errors.unsupported("Unsupported port address %s"%(port_address))
            return 0

    def portWrite(self, port_address, value):
        if (self.write_ports[port_address]):
            self.write_ports[port_address].write(value)
        else:
            errors.unsupported("Unsupported port address %s"%(port_address))

    def portMultiWrite(self, port_address, data, length):
        for i in range(length):
            self.portWrite(port_address, data[i])
