import pyglet
from pyglet.gl import *
from . import vdp

window = pyglet.window.Window(visible=False, resizable=True)

class PygletColors(vdp.Colors):
    def __init__(self):
        super(PygletColors, self).__init__()

class PygletVDP(vdp.VDP):
    """ GUI layer for vdp.
    """

    # Scaled 'blit' size.
    BLIT_WIDTH  = vdp.VDP.FRAME_WIDTH  * vdp.VDP.PIXEL_WIDTH 
    BLIT_HEIGHT = vdp.VDP.FRAME_HEIGHT * vdp.VDP.PIXEL_HEIGHT

    def __init__(self, *args):
        # 'default_color' is used by vdp init, need to set before super
        self.default_color = 0x0
        self._colors = PygletColors()
        super(PygletVDP, self).__init__(*args)

        self.KEY_PRESS_ENUM = 0
        self.KEY_RELEASE_ENUM = 1

        # Map input keys/events
        self._map_input_events()

    def set_palette(self, palette_type):
        self._colors.set_palette(palette_type)

    def poll_events(self):
        pass

    def driver_open_display(self):
        # Enable alpha blending, required for image.blit.
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        window.width  = self.BLIT_WIDTH 
        window.height = self.BLIT_HEIGHT
        window.set_visible()
        pyglet.gl.glScalef(vdp.VDP.PIXEL_WIDTH, vdp.VDP.PIXEL_HEIGHT, 1.0)

        window.push_handlers(self.on_key_press)
        window.push_handlers(self.on_key_release)

    def driver_update_display(self):
        self._draw_display()

        data = [x for line in reversed(self._display_lines[:vdp.VDP.FRAME_HEIGHT:]) for x in line]

        rawdata = (gl.GLuint * len(data))(*data)

        rawimage = pyglet.image.ImageData(self.FRAME_WIDTH, self.FRAME_HEIGHT, 'RGBA', rawdata)
        pyglet.gl.glTexParameteri(rawimage.get_texture().target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        rawimage.blit(0,0,0)

        window.switch_to()
        window.dispatch_events()
        window.dispatch_event('on_draw')
        window.flip()

    def set_color(self, r, g, b):
      r = r & 0xFF
      g = g & 0xFF
      b = b & 0xFF
      return b << 16 | g << 8 | r

    def driver_draw_display(self):
        pass

    def on_key_press(self, symbol, modifiers):
        self.inputs.handle_events(self.KEY_PRESS_ENUM, symbol)

    def on_key_release(self, symbol, modifiers):
        self.inputs.handle_events(self.KEY_RELEASE_ENUM, symbol)

    def _map_input_events(self):
        self.inputs.EVENT_KEYDOWN     = self.KEY_PRESS_ENUM
        self.inputs.EVENT_KEYUP       = self.KEY_RELEASE_ENUM
                                        
        self.inputs.KEY_UP            = pyglet.window.key.UP
        self.inputs.KEY_DOWN          = pyglet.window.key.DOWN
        self.inputs.KEY_LEFT          = pyglet.window.key.LEFT
        self.inputs.KEY_RIGHT         = pyglet.window.key.RIGHT
        self.inputs.KEY_RESET         = pyglet.window.key.R
        self.inputs.KEY_FIRE_A        = pyglet.window.key.Z
        self.inputs.KEY_FIRE_B        = pyglet.window.key.X
        self.inputs.KEY_QUIT          = pyglet.window.key.Q
