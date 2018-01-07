import pygame
import sys

class Joystick(object):
    PORT1_J1UP_BIT     = (1 << 0)
    PORT1_J1DOWN_BIT   = (1 << 1)
    PORT1_J1LEFT_BIT   = (1 << 2)
    PORT1_J1RIGHT_BIT  = (1 << 3)
    PORT1_J1FIREA_BIT  = (1 << 4)
    PORT1_J1FIREB_BIT  = (1 << 5)
    PORT1_J2UP_BIT     = (1 << 6)
    PORT1_J2DOWN_BIT   = (1 << 7)
    PORT2_J2LEFT_BIT   = (1 << 0)
    PORT2_J2RIGHT_BIT  = (1 << 1)
    PORT2_J2FIREA_BIT  = (1 << 2)
    PORT2_J2FIREB_BIT  = (1 << 3)
    PORT2_RESET_BIT    = (1 << 4)
    PORT2_UNUSED_BIT   = (1 << 5)
    PORT2_LG1_BIT      = (1 << 6)
    PORT2_LG2_BIT      = (1 << 7)

    def __init__(self):
        self._port1_value = 0xFF
        self._port2_value = 0xFF
        self._lastY = 0;

    def _set_bit(self, initial, mask, value):
        if value:
            result = initial | mask
        else:
            result = (initial & ((~mask) & 0xFF))

        return result


    PORT1_J1UP_BIT     = (1 << 0)

    def setYpos(self, y):
    
        if ((y == self._lg2y) and (y != self._lastY)):
            self.lg2(0);
        elif ((y == self._lg1y) and (y != self._lastY)):
            self.lg1(0);
        else:
            self.lg1(1);
            self.lg2(1);

        self._lastY = y;

    def getXpos(self, vcounter):
        return self._x

    def readPort1(self):
        return self._port1_value

    def readPort2(self):
        return self._port2_value

    def j1Up(self, value):
        self._port1_value = self._set_bit(self._port1_value, self.PORT1_J1UP_BIT, value)

    def j1Down(self, value):
        self._port1_value = self._set_bit(self._port1_value, self.PORT1_J1DOWN_BIT, value)

    def j1Left(self, value):
        self._port1_value = self._set_bit(self._port1_value, self.PORT1_J1LEFT_BIT, value)

    def j1Right(self, value):
        self._port1_value = self._set_bit(self._port1_value, self.PORT1_J1RIGHT_BIT, value)

    def j1FireA(self, value):
        self._port1_value = self._set_bit(self._port1_value, self.PORT1_J1FIREA_BIT, value)

    def j1FireB(self, value):
        self._port1_value = self._set_bit(self._port1_value, self.PORT1_J1FIREB_BIT, value)

    def j2Up(self, value):
        self._port1_value = self._set_bit(self._port1_value, self.PORT1_J2UP_BIT, value)

    def j2Down(self, value):
        self._port1_value = self._set_bit(self._port1_value, self.PORT1_J2DOWN_BIT, value)

    def j2Left(self, value):
        self._port2_value = self._set_bit(self._port2_value, self.PORT2_J2LEFT_BIT, value)

    def j2Right(self, value):
        self._port2_value = self._set_bit(self._port2_value, self.PORT2_J2RIGHT_BIT, value)

    def j2FireA(self, value):
        self._port2_value = self._set_bit(self._port2_value, self.PORT2_J2FIREA_BIT, value)

    def j2FireB(self, value):
        self._port2_value = self._set_bit(self._port2_value, self.PORT2_J2FIREB_BIT, value)

    def reset(self, value):
        self._port2_value = self._set_bit(self._port2_value, self.PORT2_RESET_BIT, value)

    def lg1(self, value):
        if (value == 0):
            self._x = lg1x

        self._port2_value = self._set_bit(self._port2_value, self.PORT2_LG1_BIT, value)
    def lg2(self, value):
        if (value == 0):
            self._x = lg2x

        self._port2_value = self._set_bit(self._port2_value, self.PORT2_LG2_BIT, value)

    def lg1pos(self, x, y):
        self._lg1x = x
        self._lg1y = y

    def lg2pos(self, x, y):
        self._lg2x = x
        self._lg2y = y

class Input(object):
    def __init__(self):
        self.quit = 0x0

    def refresh_inputs(self):
        pass

    def get_quit(self):
        self.refresh_inputs()
        return self.quit

    def handle_events(self, event):
        if event.type== pygame.KEYDOWN:
            if event.key == pygame.K_q: # Dodgy quit
                # TODO: find a better way to quit/stop pygame.
                pygame.quit()
            elif event.key == pygame.K_UP:
                self.joystick.j1Up(0);
            elif event.key == pygame.K_DOWN:
                self.joystick.j1Down(0);
            elif event.key == pygame.K_LEFT:
                self.joystick.j1Left(0);
            elif event.key == pygame.K_RIGHT:
                self.joystick.j1Right(0);
            elif event.key == pygame.K_z:
                self.joystick.j1FireA(0);
            elif event.key == pygame.K_x:
                self.joystick.j1FireB(0);
            elif event.key == pygame.K_r:
                self.joystick.reset(0);
        elif event.type== pygame.KEYUP:
            if event.key == event.key == pygame.K_UP:
                self.joystick.j1Up(1);
            elif event.key == pygame.K_DOWN:
                self.joystick.j1Down(1);
            elif event.key == pygame.K_LEFT:
                self.joystick.j1Left(1);
            elif event.key == pygame.K_RIGHT:
                self.joystick.j1Right(1);
            elif event.key == pygame.K_z:
                self.joystick.j1FireA(1);
            elif event.key == pygame.K_x:
                self.joystick.j1FireB(1);
            elif event.key == pygame.K_r:
                self.joystick.reset(1);
