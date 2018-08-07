#ifndef SEGA_H
#define SEGA_H

#include "z80memory.h"
#include "z80core.h"
#include "vdp.h"
#include "input.h"
#include "joystick.h"
#include "sound.h"

class Sega
{
    public:
        Sega();
        virtual ~Sega();
        void loadCartridge(const char *fileName);
        void powerOn(void);
        void dumpHistory(void);
        void setFullSpeed(bool isFullSpeed);
    private:
        void configurePorts(void);
        static uint32 cycles;
        Z80core *z80core;
        Z80memory *memory;
        Vdp *vdp;
        Sound *sound;
        Joystick *joystick;
        Input *input;
        static bool existsInstance;
};
#endif
