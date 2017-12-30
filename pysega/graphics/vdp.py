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

    # VDP status register
    VSYNCFLAG = 0x80;

    HSYNCCYCLETIME = 216;
    VSYNCCYCLETIME = 65232
    VFRAMETIME = (VSYNCCYCLETIME * 192)/262

    def __init__(self, clocks, inputs, AudioDriver):
        self.clocks = clocks
        self.inputs = inputs

        # Sound generation
        self.tiasound = AudioDriver(clocks)

        self._display_lines = []
        for y in range(self.END_DRAW_Y - self.START_DRAW_Y + 1):
          self._display_lines.append([self.default_color]*self.FRAME_WIDTH)

        self.driver_open_display()

        # Interrupt variables
        self._vSync = 0;
        self._lineIntTime = 0;
        self._lastVSync = 0;

        self._lineInteruptLatch = 0;
        self._frameUpdated = False;
        self._update = False;
        self._lastClock = 0;

        self._lineInterupt = 0;
        self._vsyncInteruptEnable = False
        self._vIntPending = False
        self._hsyncInteruptEnable = False
        self._hIntPending = False
        self._isFullSpeed = True
        self._videoChange = False
        self._vdpStatusRegister = 0
        self._vCounter = 0xD5;
        self._currentYpos = 0;
        self._yEnd = 0;
        self._enableDisplay = True

        self.interupt = None

    def _draw_display(self):
        self.poll_events()
        self.driver_draw_display()

    def setCycle(self, cycle):
        if (cycle >= self.getNextInterupt(cycle)):
            if (self.pollInterupts(cycle) == True):
                self.interupt.interupt();

    def getNextInterupt(self, cycles):
        print("getNextInterupt Not implemented")
        return 0

    def pollInterupts(self, cycle):
        print("pollInteruptsNot fully implemented")

        self._vSync = cycle - self._lastVSync;
    
        if ((self._lineIntTime < self.VFRAMETIME) and
            (self._vSync >= (self._lineIntTime))):
            self._currentYpos = (self.clocks.cycles-self._lastVSync)/self.HSYNCCYCLETIME+1;
    
            self._lineInteruptLatch = self._lineInterupt + 1;
    
            self._lineIntTime += self._lineInteruptLatch * self.HSYNCCYCLETIME;
    
            self._hIntPending = True;
    
        if ((False == self._frameUpdated) and (self._vSync >= self.VFRAMETIME)):
            if (self._enableDisplay == True):
                if (self._update == True):
                    self.updateDisplay();
                    self._update = False;
            else:
                self.clearDisplay();
    
            self._frameUpdated = True;
            self._vCounter = 0xD5;
            self._currentYpos = self._yEnd;
    
            self._vIntPending = True;
            self._vdpStatusRegister |= self.VSYNCFLAG;
    
        if (self._vSync >= self.VSYNCCYCLETIME):
            self._lastVSync = cycle;
            self._vSync = 0;
            self._currentYpos = 0;
            self._vCounter = 0x00;
            self.updateHorizontalScrollInfo();
            self.updateVerticalScrollInfo();
    
            self._lineInteruptLatch = self._lineInterupt;
    
            self._lineIntTime = self._lineInteruptLatch * self.HSYNCCYCLETIME;
    
            if (self._videoChange == True):
                self.drawBuffer();
                self._update = True;
                self._videoChange = False;
    
#            if (!self._isFullSpeed):
#                while ((clock() - self._lastClock) < self.CLOCKS_PER_SEC/60)
#                    ;
#                self._lastClock = clock();
    
            self._frameUpdated = False;
    
        if ((self._vsyncInteruptEnable and self._vIntPending) or
            (self._hsyncInteruptEnable and self._hIntPending)):
            return True;
        else:
            return False;

    def updateDisplay(self):
        pass

    def clearDisplay(self):
        pass

    def updateHorizontalScrollInfo(self):
        pass

    def updateVerticalScrollInfo(self):
        pass

    def drawBuffer(self):
        pass


