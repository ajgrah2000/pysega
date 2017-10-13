#ifndef JOYSTICK_H
#define JOYSTICK_H

#include "SDL.h"
#include "types.h"
#include "readInterface.h"

class Joystick
{
    public:
        Joystick();
        static Byte readPort1(void *object);
        static Byte readPort2(void *object);
        class ReadPort1 : public ReadInterface
        {
                virtual Byte read(void *arg){return readPort1(arg);};
        };
        static ReadPort1 readPort1Function;
        class ReadPort2 : public ReadInterface
        {
                virtual Byte read(void *arg){return readPort2(arg);};
        };
        static ReadPort2 readPort2Function;

        static void j1Up(int value);
        static void j1Down(int value);
        static void j1Left(int value);
        static void j1Right(int value);
        static void j1FireA(int value);
        static void j1FireB(int value);
        static void j2Up(int value);
        static void j2Down(int value);
        static void j2Left(int value);
        static void j2Right(int value);
        static void j2FireA(int value);
        static void j2FireB(int value);
        static void reset(int value);
        static void lg1(int value);
        static void lg2(int value);

        static void lg1pos(int x, int y);
        static void lg2pos(int x, int y);

        static void setYpos(Byte y);
        static Byte getXpos(void);

    private:
        Byte realReadPort1(void);
        Byte realReadPort2(void);

        // Status bits are low (0) when the butten is pressed
        // and high (1) otherwise 
        typedef union port1Status_union
        {
            struct
            {
                unsigned char j1Up:1, j1Down:1, j1Left:1, j1Right:1, 
                              j1FireA:1, j1FireB:1, j2Up:1, j2Down:1;
            } statusBits;

            Byte value;
        } Port1Status;

        static Port1Status port1Status;

        // Status bits are low (0) when the butten is pressed
        // and high (1) otherwise 
        typedef union port2Status_union
        {
            struct
            {
                unsigned char j2Left:1, j2Right:1, j2FireA:1, j2FireB:1,
                              reset:1, unused:1, lg1:1, lg2:1;
            } statusBits;

            Byte value;

        } Port2Status;

        static Port2Status port2Status;

        static int lg1x, lg1y, lg2x, lg2y, x;
};

#endif

