import pygame
import sys

class DummyJoystick(object):
    def __init__(self):
        pass

    def setYpos(self, vcounter):
        pass

    def readPort1(self):
        print "Joystic port 1 not implemented"
        return 0

    def readPort2(self):
        print "Joystic port 2 not implemented"
        return 0


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
                self.quit = 0x1

                # TODO: find a better way to quit/stop pygame.
                pygame.quit()
                sys.exit()
        elif event.type== pygame.KEYUP:
            pass
