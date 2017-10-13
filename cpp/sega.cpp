#include "sega.h"
#include <iostream>

#include "z80memory.h"
#include "ports.h"
#include "z80core.h"
#include "vdp.h"
#include "input.h"
#include "joystick.h"
#include "sound.h"

uint32 Sega::cycles = 0;
bool Sega::existsInstance = false;

Sega::Sega()
{
    if (existsInstance == false)
    {
        cycles = 0;

        memory   = new Z80memory;
        z80core  = new Z80core(cycles);
        vdp      = new Vdp(cycles);
        sound    = new Sound(cycles);
        joystick = new Joystick;
        input    = new Input(joystick);

        input->processInput();

        vdp->setInterupt(z80core);
        z80core->setInteruptor(vdp);

        z80core->setMemory(memory);

        configurePorts();

        existsInstance = true;
    }
}

Sega::~Sega(void)
{
    if (existsInstance == true)
    {
        delete z80core;
        delete vdp;
        delete memory;
        delete sound;
        delete joystick;

        existsInstance = false;
    }
}

void Sega::configurePorts(void)
{
      // Add the vdp `BF' port to BF plus all the mirror ports
      // BF is the vdp control port
    for (int i = 0x81; i <= 0xBF; i+=2)
    {
        Ports::instance()->addDeviceToPort(vdp, &Vdp::readPortBFFunction, &Vdp::writePortBFFunction, i);
    }

      // Add the vdp `BE' port to BE plus all the mirror ports
      // BF is the vdp data port
    for (int i = 0x80; i <= 0xBE; i+=2)
    {
        Ports::instance()->addDeviceToPort(vdp, &Vdp::readPortBEFunction, &Vdp::writePortBEFunction, i);
    }

      // Add the vdp and sound to port `7E' plus all the mirror ports
      // 7E is the vdp vCounter and sound port
    for (int i = 0x40; i <= 0x7E; i+=2)
    {
        Ports::instance()->addDeviceToPort(vdp, &Vdp::readPort7EFunction, i);
        Ports::instance()->addDeviceToPort(sound, NULL, &Sound::writePortFunction, i);
    }

      // Add the vdp and sound to port `7F' plus all the mirror ports
      // 7& is the vdp hCounter and sound port
    for (int i = 0x41; i <= 0x7F; i+=2)
    {
        Ports::instance()->addDeviceToPort(vdp, &Vdp::readPort7FFunction, i);
        Ports::instance()->addDeviceToPort(sound, NULL, &Sound::writePortFunction,  i);
    }

      // Add the joystics to their ports
    Ports::instance()->addDeviceToPort(joystick, &Joystick::readPort1Function, 0xDC);
    Ports::instance()->addDeviceToPort(joystick, &Joystick::readPort2Function, 0xDD);
}

void Sega::loadCartridge(const char *fileName)
{
    memory->loadCartridge(fileName);
}

void Sega::powerOn()
{
    while((z80core->step() != -1) && (input->get_power()))
    {
//	std::cout << "." << std::endl;
	;
    }
}

void Sega::setFullSpeed(bool isFullSpeed)
{
    vdp->setFullSpeed(isFullSpeed);
}
