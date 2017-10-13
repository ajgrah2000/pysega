import ctypes
import time
import pkg_resources

class Colors(object):

    def __init__(self):
        self.set_palette("ntsc")

    def set_palette(self, palette_type):
        """ palette_type needs to match the file name, expected:
            ntsc -> palette.ntsc.dat
            or 
            pal -> palette.pal.dat
        """

        palette_filename = "palette.%s.dat"%(palette_type)

        self.colors = []

        palette_file = pkg_resources.resource_stream(__name__, palette_filename)
        for line in palette_file:
            (r, g, b) = [int(x) for x in line.split()[0:3]]
            self.colors.append(self.set_color(r, g, b))

    def fade_color(self, color):
        color  = (int(color[0] * 0.9), 
                  int(color[1] * 0.9),
                  int(color[2] * 0.9),
                  int(color[3] * 0.9))
        return color # * (0.9,0.9,0.9)

    def set_color(self, r, g, b):
        pass

    def get_color(self, color):
        c = color >> 1
        return self.colors[c]

class VDP(object):

    FRAME_WIDTH  = 200
    FRAME_HEIGHT = 320
    PIXEL_WIDTH  = 2
    PIXEL_HEIGHT = 2

    START_DRAW_Y = 0
    END_DRAW_Y   = FRAME_HEIGHT 

    def __init__(self, clocks, inputs, AudioDriver):
        self.clocks = clocks
        self.inputs = inputs

        # Sound generation
        self.tiasound = AudioDriver(clocks)

        self._display_lines = []
        for y in range(self.END_DRAW_Y - self.START_DRAW_Y + 1):
          self._display_lines.append([self.default_color]*self.FRAME_WIDTH)

    def _draw_display(self):
        self.poll_events()
        self.driver_draw_display()


