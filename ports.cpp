#include "ports.h"
#include <iostream>

Ports::DummyRead Ports::dummyDeviceReadFunction;
Ports::DummyWrite Ports::dummyDeviceWriteFunction;

Ports *Ports::self = NULL;

Ports::Ports()
{
  
}

Ports::~Ports()
{
    std::cout << "Removing all ports" << std::endl;

    delete portDevicesRead;
    delete portDevicesWrite;
    delete portObjectsRead;
    delete portObjectsWrite;
}

Ports *Ports::instance()
{
    if(!self)
    {
        self = new Ports();
        self->init();
    }

    return self;
}

// Allocate the read and write port arrays.
bool Ports::init()
{
    portDevicesRead = new ReadInterface *[MAXPORTS];
    portDevicesWrite = new WriteInterface *[MAXPORTS];

    portObjectsRead = new void *[MAXPORTS];
    portObjectsWrite = new void *[MAXPORTS];
    for (unsigned int i = 0; i < MAXPORTS; i++)
    {
        // Initialise all of the ports to 'dummy', to catch crazy port access.
        portDevicesRead[i] = &dummyDeviceReadFunction;
        portDevicesWrite[i] = &dummyDeviceWriteFunction;
    }

    return true;
}

void Ports::addDeviceToPort(void *object, 
                             ReadInterface *read, 
                             Byte port)

{
    if (read != NULL)
    {
        portDevicesRead[port]  = read;
        portObjectsRead[port] = object;
    }

}

void Ports::addDeviceToPort(void *object, 
                              ReadInterface *read, 
                             WriteInterface *write, 
                             Byte port)
{
    if (read != NULL)
    {
        portDevicesRead[port]  = read;
        portObjectsRead[port] = object;
    }

    if (write != NULL)
        portDevicesWrite[port] = write;

    portObjectsWrite[port] = object;
}

Byte Ports::portRead(Byte port)
{
    return portDevicesRead[port]->read(portObjectsRead[port]);
}

void Ports::portWrite(Byte port, Byte data)
{
    portDevicesWrite[port]->write(portObjectsWrite[port], data);
}

void Ports::portWrite(Byte port, const Byte *data, uint16 length)
{
    portDevicesWrite[port]->write(portObjectsWrite[port], data, length);
}

Byte Ports::dummyDeviceRead(void *object)
{
    std::cout << "Device not implemented, no read" << std::endl;
    return 0;
}

void Ports::dummyDeviceWrite(void *object, Byte data)
{
/*
   std::cout << "Device not implemented (" << 
            (int) data << ") not written" << std::endl;
            */
}

void Ports::dummyDeviceWriteMultiple(void *object, 
                                       const Byte *data, uint16 length)
{
    std::cout << "Multiple write not implemented for this device (" << 
            (int) *data << ") not written" << std::endl;
}
