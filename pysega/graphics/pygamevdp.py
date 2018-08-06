import pygame
from . import vdp

class PygameColors(vdp.Colors):
    def __init__(self):
        super(PygameColors, self).__init__()

class PygameVDP(vdp.VDP):
    """ GUI layer for vdp.
    """

    # Scaled 'blit' size.
    BLIT_WIDTH  = vdp.VDP.FRAME_WIDTH  * vdp.VDP.PIXEL_WIDTH 
    BLIT_HEIGHT = vdp.VDP.FRAME_HEIGHT * vdp.VDP.PIXEL_HEIGHT

    def __init__(self, *args):
        # 'default_color' is used by vdp init, need to set before super
        self.default_color = 0x0
        self._colors = PygameColors()
        super(PygameVDP, self).__init__(*args)

        # Test if 'PixelArray' is part of pygame
        # pygame_cffi, may not have PixelArray

        if vdp.has_numpy:
            # Use a faster blit with a numpy array, if available.      
            self.driver_draw_display = self._draw_using_numpy_array
        elif hasattr(pygame, 'PixelArray'):
            self.driver_draw_display = self._draw_using_pixel_array
        else:
            self.driver_draw_display = self._draw_using_set_at

        # Map input keys/events
        self._map_input_events()

    def set_palette(self, palette_type):
        self._colors.set_palette(palette_type)

    def poll_events(self):
        # Handle events on diplay draw
        for event in pygame.event.get():
          self.handle_events(event)
          #self.sound.handle_events(event)

    def driver_open_display(self):
      pygame.init()

      if vdp.has_numpy:
        # Replayce the 'display_lines' with a numpy array.
        #self._display_lines = numpy.zeros((self.END_DRAW_Y - self.START_DRAW_Y + 1, self.FRAME_WIDTH), dtype=numpy.int)
        self._display_lines = vdp.numpy.array(self._display_lines)

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

    def set_color(self, r, g, b):
      r = r & 0xFF
      g = g & 0xFF
      b = b & 0xFF
      color = r << 16 | g << 8 | b

      return color

    def _map_input_events(self):
        self.inputs.EVENT_KEYDOWN     = pygame.KEYDOWN
        self.inputs.EVENT_KEYUP       = pygame.KEYUP

        self.inputs.KEY_UP            = pygame.K_UP
        self.inputs.KEY_DOWN          = pygame.K_DOWN
        self.inputs.KEY_LEFT          = pygame.K_LEFT
        self.inputs.KEY_RIGHT         = pygame.K_RIGHT
        self.inputs.KEY_RESET         = pygame.K_r
        self.inputs.KEY_FIRE_A        = pygame.K_z
        self.inputs.KEY_FIRE_B        = pygame.K_x
        self.inputs.KEY_QUIT          = pygame.K_q

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP: 
            self.inputs.handle_events(event.type, event.key)
            ## TODO: find a better way to quit/stop pygame.
            #pygame.quit()
