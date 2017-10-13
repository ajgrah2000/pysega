#ifndef INPUT_H
#define INPUT_H
#include "joystick.h"

#include <sys/types.h>

class Input
{
    public:
        Input(Joystick *joystick);
        void processInput(void);
        bool get_power(void);
    private:
        static void *thread(void *object);
        void processEvents(void);
        static Joystick *joystick;
        static bool power;
};
#endif
