#include "joystick.h"
#include "SDL.h"

#include <iostream>
#include <exception>

Joystick::ReadPort1 Joystick::readPort1Function;
Joystick::ReadPort2 Joystick::readPort2Function;

Joystick::Port1Status Joystick::port1Status;
Joystick::Port2Status Joystick::port2Status;
int Joystick::lg1x = 0;
int Joystick::lg1y = 0;
int Joystick::lg2x = 0;
int Joystick::lg2y = 0;
int Joystick::x = 0;

// Status bits = 1 for pressed, 0 for released
Joystick::Joystick(void)
{
    port1Status.value = 0xFF;
    port2Status.value = 0xFF;
}

Byte Joystick::readPort1(void *object)
{
    return ((Joystick *) object)->realReadPort1();
}

Byte Joystick::readPort2(void *object)
{
    return ((Joystick *) object)->realReadPort2();
}

Byte Joystick::realReadPort1(void)
{
    static Byte status;

    status = port1Status.value;

    return status;
}

Byte Joystick::realReadPort2(void)
{
    static Byte status;

    status = port2Status.value;

    return status;
}

void Joystick::j1Up(int value)
{
    port1Status.statusBits.j1Up = value;
}

void Joystick::j1Down(int value)
{
    port1Status.statusBits.j1Down = value;
}

void Joystick::j1Left(int value)
{
    port1Status.statusBits.j1Left = value;
}

void Joystick::j1Right(int value)
{
    port1Status.statusBits.j1Right = value;
}

void Joystick::j1FireA(int value)
{
    port1Status.statusBits.j1FireA = value;
}

void Joystick::j1FireB(int value)
{
    port1Status.statusBits.j1FireB = value;
}

void Joystick::j2Up(int value)
{
    port1Status.statusBits.j2Up = value;
}

void Joystick::j2Down(int value)
{
    port1Status.statusBits.j2Up = value;
}

void Joystick::j2Left(int value)
{
    port2Status.statusBits.j2Left = value;
}

void Joystick::j2Right(int value)
{
    port2Status.statusBits.j2Right = value;
}

void Joystick::j2FireA(int value)
{
    port2Status.statusBits.j2FireA = value;
}

void Joystick::j2FireB(int value)
{
    port2Status.statusBits.j2FireB = value;
}

void Joystick::reset(int value)
{
    port2Status.statusBits.reset = value;
}

void Joystick::lg1(int value)
{
    if (value == 0)
        x = lg1x;

    port2Status.statusBits.lg1 = value;
}

void Joystick::lg2(int value)
{
    if (value == 0)
        x = lg2x;

    port2Status.statusBits.lg2 = value;
}

void Joystick::lg1pos(int x, int y)
{
    lg1x = x;
    lg1y = y;
}

void Joystick::lg2pos(int x, int y)
{
    lg2x = x;
    lg2y = y;
}

void Joystick::setYpos(Byte y)
{
    static int lastY;

    if ((y == lg2y) && (y != lastY))
    {
        lg2(0);
    }
    else if ((y == lg1y) && (y != lastY))
    {
        lg1(0);
    }
    else
    {
        lg1(1);
        lg2(1);
    }
    lastY = y;
}

Byte Joystick::getXpos(void)
{
    return x;
}
