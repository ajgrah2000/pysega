#include "input.h"
#include "joystick.h"

#include "SDL.h"
#include <unistd.h>
#include <signal.h>
#include <iostream>
#include <exception>
#include <pthread.h>

Joystick *Input::joystick = NULL;
bool Input::power = true;

Input::Input(Joystick *joystick)
{
    this->joystick = joystick;
    SDL_InitSubSystem(SDL_INIT_EVENTTHREAD);
}

void Input::processInput(void)
{
    pthread_t t;
    pthread_create (&t, NULL, Input::thread, this);
}

void *Input::thread(void *object)
{
    ((Input *)object)->processEvents();
    std::cout << "Thread complete?" << std::endl;
    return NULL;
}

bool Input::get_power(void)
{
    return power;
}

void Input::processEvents(void)
{
    SDL_Event event;
    SDL_MouseButtonEvent *mouseButtonEvent = &(event.button);

    power = true;
        
    while(power)
    {
        SDL_WaitEvent(&event);

        switch(event.type){
            case SDL_MOUSEBUTTONDOWN:
                switch(mouseButtonEvent->button)
                {
                    case 1:
                        joystick->j1FireA(0);
                        joystick->lg1pos(mouseButtonEvent->x,
                                         mouseButtonEvent->y);
                        break;
                    case 3:
                        joystick->j2FireA(0);
                        joystick->lg1pos(mouseButtonEvent->x,
                                         mouseButtonEvent->y);
                        break;
                    default:
                        break;
                }
                break;
            case SDL_MOUSEBUTTONUP:
                switch(mouseButtonEvent->button)
                {
                    case 1:
                        joystick->j1FireA(1);
                        break;
                    case 3:
                        joystick->j2FireA(1);
                        break;
                    default:
                        break;
                }
                break;
            case SDL_KEYDOWN:
                switch(event.key.keysym.sym)
                {
                    case SDLK_UP:
                        joystick->j1Up(0);
                        break;
                    case SDLK_DOWN:
                        joystick->j1Down(0);
                        break;
                    case SDLK_LEFT:
                        joystick->j1Left(0);
                        break;
                    case SDLK_RIGHT:
                        joystick->j1Right(0);
                        break;
                    case SDLK_z:
                        joystick->j1FireA(0);
                        break;
                    case SDLK_x:
                        joystick->j1FireB(0);
                        break;
                    case SDLK_r:
                        joystick->reset(0);
                        break;
                    case SDLK_q: // Dodgy quit
                        power = false;
                        break;
                    default:
                        break;
                }
                break;
            case SDL_KEYUP:
                switch(event.key.keysym.sym)
                {
                    case SDLK_UP:
                        joystick->j1Up(1);
                        break;
                    case SDLK_DOWN:
                        joystick->j1Down(1);
                        break;
                    case SDLK_LEFT:
                        joystick->j1Left(1);
                        break;
                    case SDLK_RIGHT:
                        joystick->j1Right(1);
                        break;
                    case SDLK_z:
                        joystick->j1FireA(1);
                        break;
                    case SDLK_x:
                        joystick->j1FireB(1);
                        break;
                    case SDLK_r:
                        joystick->reset(1);
                        break;
                    default:
                        break;
                }
                break;
            default:
                break;
        }


    }
    std::cout << "Stopping thread" << std::endl;
}
