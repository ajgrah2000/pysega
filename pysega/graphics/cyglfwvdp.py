import cyglfw3 as glfw
from OpenGL import GL as gl
from . import vdp

if not glfw.Init():
    exit()

# Not sure if this is the best spot for the window.
window = glfw.CreateWindow(vdp.VDP.FRAME_WIDTH  * vdp.VDP.PIXEL_WIDTH, vdp.VDP.FRAME_HEIGHT * vdp.VDP.PIXEL_HEIGHT, "Cyglfw Stella")

class CyglfwColors(vdp.Colors):
    def __init__(self):
        super(CyglfwColors, self).__init__()

class CyglfwVDP(vdp.VDP):
    """ GUI layer for vdp.
    """

    # Scaled 'blit' size.
    BLIT_WIDTH  = vdp.VDP.FRAME_WIDTH  * vdp.VDP.PIXEL_WIDTH 
    BLIT_HEIGHT = vdp.VDP.FRAME_HEIGHT * vdp.VDP.PIXEL_HEIGHT

    def __init__(self, *args):
        # 'default_color' is used by vdp init, need to set before super
        self.default_color = 0x0
        self._colors = CyglfwColors()
        super(CyglfwVDP, self).__init__(*args)

        # Map input keys/events
        self._map_input_events()

    def set_palette(self, palette_type):
        self._colors.set_palette(palette_type)

    def poll_events(self):
        pass

    def driver_open_display(self):
        if not window:
            glfw.Terminate()
            exit()

        glfw.MakeContextCurrent(window)

        glfw.SetKeyCallback(window, self.cyglfw_key_callback)

    def driver_update_display(self):
        self._draw_display()
        data = [x for line in reversed(self._display_lines[:vdp.VDP.FRAME_HEIGHT:]) for x in line]

        rawdata = (gl.GLuint * len(data))(*data)
        gl.glDrawPixels(vdp.VDP.FRAME_WIDTH, vdp.VDP.FRAME_HEIGHT, gl.GL_RGBA, gl.GL_UNSIGNED_INT_8_8_8_8, rawdata)
        gl.glPixelZoom(self.PIXEL_WIDTH, self.PIXEL_HEIGHT)

        if not glfw.WindowShouldClose(window):
            glfw.SwapBuffers(window)

            glfw.PollEvents()

    def set_color(self, r, g, b):
      return r << 24 | g << 16 | b << 8

    def driver_draw_display(self):
        pass

    def cyglfw_key_callback(self, window, key, scancode, action, mods):
        # TODO: Key callback with GLFW 3.2.1 appears to add extra 'press,
        # repeat and release' after a repeat event.
        self.inputs.handle_events(action, key)

        # TODO: find a better way to quit/stop pygame.
        #glfw.Terminate()
        #sys.exit()

    def _map_input_events(self):
        self.inputs.EVENT_KEYDOWN     = glfw.PRESS
        self.inputs.EVENT_KEYUP       = glfw.RELEASE
                                        
        self.inputs.KEY_UP            = glfw.KEY_UP
        self.inputs.KEY_DOWN          = glfw.KEY_DOWN
        self.inputs.KEY_LEFT          = glfw.KEY_LEFT
        self.inputs.KEY_RIGHT         = glfw.KEY_RIGHT
        self.inputs.KEY_RESET         = glfw.KEY_R
        self.inputs.KEY_FIRE_A        = glfw.KEY_Z
        self.inputs.KEY_FIRE_B        = glfw.KEY_X
        self.inputs.KEY_QUIT          = glfw.KEY_Q
