import pygame
from . import vdp

# Import numpy, if it exists.
try:
    import numpy
    has_numpy = True
except:
    has_numpy = False
finally:
    pass

class PygameColors(vdp.Colors):
    def __init__(self):
        super(PygameColors, self).__init__()

    def set_color(self, r, g, b):
      r = r & 0xFF
      g = g & 0xFF
      b = b & 0xFF
      color = r << 16 | g << 8 | b

      return color

class PygameVDP(vdp.VDP):
    """ GUI layer for vdp.
    """

    # Scaled 'blit' size.
    BLIT_WIDTH  = vdp.VDP.FRAME_WIDTH  * vdp.VDP.PIXEL_WIDTH 
    BLIT_HEIGHT = vdp.VDP.FRAME_HEIGHT * vdp.VDP.PIXEL_HEIGHT

    def __init__(self, *args):
        # 'default_color' is used by vdp init, need to set before super
        self.default_color = 0
        self._colors = PygameColors()
        super(PygameVDP, self).__init__(*args)

        # Test if 'PixelArray' is part of pygame
        # pygame_cffi, may not have PixelArray

        if has_numpy:
            # Use a faster blit with a numpy array, if available.      
            self.driver_draw_display = self._draw_using_numpy_array
        elif hasattr(pygame, 'PixelArray'):
            self.driver_draw_display = self._draw_using_pixel_array
        else:
            self.driver_draw_display = self._draw_using_set_at

    def set_palette(self, palette_type):
        self._colors.set_palette(palette_type)

    def poll_events(self):
        # Handle events on diplay draw
        for event in pygame.event.get():
          self.inputs.handle_events(event)
          #self.sound.handle_events(event)

    def driver_open_display(self):
      pygame.init()

      if has_numpy:
        # Replayce the 'display_lines' with a numpy array.
        #self._display_lines = numpy.zeros((self.END_DRAW_Y - self.START_DRAW_Y + 1, self.FRAME_WIDTH), dtype=numpy.int)
        self._display_lines = numpy.array(self._display_lines)

      self._screen = pygame.display.set_mode((
                            vdp.VDP.FRAME_WIDTH  * vdp.VDP.PIXEL_WIDTH, 
                            vdp.VDP.FRAME_HEIGHT * vdp.VDP.PIXEL_HEIGHT))

      pygame.display.set_caption('Pysega')
      pygame.mouse.set_visible(0)

      self._background = pygame.Surface((vdp.VDP.FRAME_WIDTH, vdp.VDP.FRAME_HEIGHT))
      self._background = self._background.convert()

    def driver_update_display(self):
      self._draw_display()
      self._screen.blit(pygame.transform.scale(self._background,(self.BLIT_WIDTH, self.BLIT_HEIGHT)), (0,0))
      pygame.display.flip()

    def _draw_using_numpy_array(self):
        pygame.surfarray.blit_array(self._background, self._display_lines.transpose())

    def _draw_using_pixel_array(self):
        pxarray = pygame.PixelArray(self._background)
        for y in range(min(self.END_DRAW_Y - self.START_DRAW_Y, self.FRAME_HEIGHT)):
            for x in range(self.FRAME_WIDTH):
                pxarray[x][y] = self._display_lines[y][x]
        del pxarray

    def _draw_using_set_at(self):
        for y in range(min(self.END_DRAW_Y - self.START_DRAW_Y, self.FRAME_HEIGHT)):
            for x in range(self.FRAME_WIDTH):
                self._background.set_at((x,y),  self._display_lines[y][x])

