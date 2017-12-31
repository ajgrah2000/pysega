import ctypes
import time
import pkg_resources
import inspect
from .. import errors

class ScanLine(object):
    pass

class HorizontalScroll(object):
    pass

class PriorityScanLine(object):
    pass

class SpriteScanLine(object):
    pass

class PatternInfo(object):
    pass

class TileAttribute(object):
    pass

class Sprite(object):
    pass

class VdpConstants(object):
        RAMSIZE  = 0x4000;
        CRAMSIZE  = 0x20;
        # // 3Mhz CPU, 50Hz refresh ~= 60000 ticks
        VSYNCCYCLETIME = 65232;
        BLANKTIME      = (VSYNCCYCLETIME * 72)/262;
        VFRAMETIME     = (VSYNCCYCLETIME * 192)/262;
        HSYNCCYCLETIME = 216;

        REGISTERMASK  = 0x0F;
        REGISTERUPDATEMASK  = 0xF0;
        REGISTERUPDATEVALUE = 0x80;
        NUMVDPREGISTERS = 16;

        # VDP status register 
        VSYNCFLAG = 0x80;

        # VDP register 0
        MODE_CONTROL_NO_1 = 0x0;
        VDP0DISVSCROLL    = 0x80;
        VDP0DISHSCROLL    = 0x40;
        VDP0COL0OVERSCAN  = 0x20;
        VDP0LINEINTENABLE = 0x10;
        VDP0SHIFTSPRITES  = 0x08;
        VDP0M4            = 0x04;
        VDP0M2            = 0x02;
        VDP0NOSYNC        = 0x01;

        # VDP register 1 
        MODE_CONTROL_NO_2 = 0x1;
        VDP1BIT7          = 0x80;
        VDP1ENABLEDISPLAY = 0x40;
        VDP1VSYNC         = 0x20;
        VDP1M1            = 0x10;
        VDP1M3            = 0x08;
        VDP1BIGSPRITES    = 0x02;
        VDP1DOUBLESPRITES = 0x01;

        NAMETABLEPRIORITY = 0x10;
        NUMSPRITES = 64;

        DMM4 = 0x8;
        DMM3 = 0x4;
        DMM2 = 0x2;
        DMM1 = 0x1;

        PALETTE_ADDRESS  = 0xC000;

        SMS_WIDTH  = 256;
        SMS_HEIGHT = 192; # MAX HEIGHT
        SMS_COLOR_DEPTH = 16;

        MAXPATTERNS = 512;
        PATTERNWIDTH  = 8;
        PATTERNHEIGHT = 8;
        PATTERNSIZE = 64;

        MAXPALETTES = 2;

        NUMTILEATTRIBUTES = 0x700;
        TILEATTRIBUTEMASK     = 0x7FF;
        TILEATTRIBUTESADDRESSMASK = 0x3800; 
        TILEATTRIBUTESTILEMASK = 0x07FE; 
        TILESHIFT = 1; 
        TILEATTRIBUTESHMASK    = 0x0001; 
        TILEPRIORITYSHIFT = 4; 
        TILEPALETTESHIFT = 3; 
        TILEVFLIPSHIFT = 2; 
        TILEHFLIPSHIFT = 1; 

        YTILES = 28; 
        XTILES = 32; 
        NUMTILES = XTILES * YTILES; 

        SPRITEATTRIBUTESADDRESSMASK = 0x3F00; 
        SPRITEATTRIBUTESMASK = 0x00FF; 
        NUMSPRITEATTRIBUTES = 0x00FF; 

        SPRITETILEMASK = 0x0001; 

        LASTSPRITETOKEN = 0xD0;
        SPRITEXNMASK = 0x0080; 
        MAXSPRITES = 64;
        NOSPRITE = MAXSPRITES;
        MAXSPRITESPERSCANLINE = 8;

        PATTERNADDRESSLIMIT = 0x4000;

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

    FRAME_WIDTH  = VdpConstants.SMS_WIDTH
    FRAME_HEIGHT = VdpConstants.SMS_HEIGHT
    PIXEL_WIDTH  = 2
    PIXEL_HEIGHT = 2

    START_DRAW_Y = 0
    END_DRAW_Y   = FRAME_HEIGHT 

    # VDP status register

    def __init__(self, clocks, inputs, AudioDriver):
        self.clocks = clocks
        self.inputs = inputs

        # Sound generation
        self.tiasound = AudioDriver(clocks)

        self._display_lines = []
        for y in range(self.END_DRAW_Y - self.START_DRAW_Y):
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

        self._interupt = None


        # From original constructor
        self._vsyncInteruptEnable = False
        self._hsyncInteruptEnable = False
        self._horizontalScrollChanged = False
        self._verticalScroll = 0
        self._lineInterupt = 0
        #self._tileDefinitions = 0
        self._enableDisplay = False

        self._vdpRAM        = [0] * VdpConstants.RAMSIZE
        self._cRAM          = [0] * VdpConstants.CRAMSIZE
        self._screenPalette = [0] * VdpConstants.CRAMSIZE

        self._vdpStatusRegister = 0;
        self._hIntPending = False;
        self._vIntPending = False;

        self._addressLatch = False;
        self._isFullSpeed = False;

        self._codeRegister = 0
        self._readBELatch = 0
        self._lastSpriteAttributesAddress = 0;

#        self._interupt= NULL;

    # Initialise interupt counters */
#    self._vSync = 0;
#    self._lineIntTime = 0;
#    self._lastVSync = 0;

#        self._currentYpos = 0;
        self._hCounter = 0
#        self._vCounter = 0;
#        self._yEnd = 0;
        self._displayMode = 0;
#        self._videoChange = False;

        self._spriteHeight = 8 
        self._spriteWidth = 8;

        self._startX = 0;
    
        self._vdpRegister = [0] *VdpConstants.NUMVDPREGISTERS
    
        self._displayMode = 0;
    
        # Allocate memory for pattern tiles
        self._patternInfo = [PatternInfo()] * VdpConstants.MAXPATTERNS
    
        self._patterns4 = [0] * VdpConstants.MAXPATTERNS*VdpConstants.PATTERNSIZE
    
        self._patterns16 = [[0 for i in range(VdpConstants.MAXPATTERNS*VdpConstants.PATTERNSIZE)] for j in range(VdpConstants.MAXPALETTES)]
    
        for pattern_info in self._patternInfo:
            pattern_info.references = 0;
            pattern_info.changed = False;
            pattern_info.colorCheck = False;
            pattern_info.colors = False;
            pattern_info.screenVersionCached = False;
    
        self._tileAttributes = [TileAttribute()] * VdpConstants.NUMTILEATTRIBUTES
        for tile_attribute in self._tileAttributes:
            tile_attribute.tileNumber = 0;
            self._patternInfo[tile_attribute.tileNumber].references +=1;
            # Assuming 'False' is the correct default.
            tile_attribute.changed = True;
            tile_attribute.priority = False;
            tile_attribute.priorityCleared = False;
            tile_attribute.paletteSelect = False;
            tile_attribute.verticalFlip = False;
            tile_attribute.horizontalFlip = False;
    
        self._spriteTileShift = 0;
        totalSprites = VdpConstants.MAXSPRITES;
        self._sprites = [Sprite()] * VdpConstants.MAXSPRITES
        for sprite in self._sprites:
            sprite.y = 1;
            sprite.x = 0;
            sprite.tileNumber = 0;
            self._patternInfo[sprite.tileNumber].references += 1;
            sprite.changed = False;
    
        self.openDisplay()

        self._horizontalScroll = 0

    def _draw_display(self):
        self.poll_events()
        self.driver_draw_display()

    def setCycle(self, cycle):
        if (cycle >= self.getNextInterupt(cycle)):
            if (self.pollInterupts(cycle) == True):
                self._interupt.interupt();

    def getNextInterupt(self, cycles):
        print("getNextInterupt Not implemented")
        return 0

    def pollInterupts(self, cycle):

        self._vSync = cycle - self._lastVSync;
    
        if ((self._lineIntTime < VdpConstants.VFRAMETIME) and
            (self._vSync >= (self._lineIntTime))):
            self._currentYpos = (self.clocks.cycles-self._lastVSync)/VdpConstants.HSYNCCYCLETIME+1;
    
            self._lineInteruptLatch = self._lineInterupt + 1;
    
            self._lineIntTime += self._lineInteruptLatch * VdpConstants.HSYNCCYCLETIME;
    
            self._hIntPending = True;
    
        if ((False == self._frameUpdated) and (self._vSync >= VdpConstants.VFRAMETIME)):
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
            self._vdpStatusRegister |= VdpConstants.VSYNCFLAG;
    
        if (self._vSync >= VdpConstants.VSYNCCYCLETIME):
            self._lastVSync = cycle;
            self._vSync = 0;
            self._currentYpos = 0;
            self._vCounter = 0x00;
            self.updateHorizontalScrollInfo();
            self.updateVerticalScrollInfo();
    
            self._lineInteruptLatch = self._lineInterupt;
    
            self._lineIntTime = self._lineInteruptLatch * VdpConstants.HSYNCCYCLETIME;
    
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

    def readPort7E(self):
        self._addressLatch = False;  # Address is unlatched during port read
    
        vCounter = (cycles-self._lastVSync)/VdpConstants.HSYNCCYCLETIME;
        self._currentYpos = (cycles-self._lastVSync)/VdpConstants.HSYNCCYCLETIME+1;
    
          # I can't think of an ellegant solution, so this is as good as it gets
          # for now (fudge factor and all)
        self.inputs.joystick.setYpos(vCounter+10);
        return vCounter;

    def readPort7F(self):
        print inspect.stack()[0][3]
        return 0
    """
{
    self._addressLatch = False;  // Address is unlatched during port read

      // I can't think of an ellegant solution, so this is as good as it gets
      // for now (fudge factor and all)
    hCounter = ((Joystick::getXpos() + 0x28)/2 & 0x7F);
    return hCounter;
}
    """

    def readPortBE(self):
        print inspect.stack()[0][3]
        return 0
    """
{
    uint8 data;
    self._addressLatch = False;  // Address is unlatched during port read

    data = self._readBELatch;

    self._address = (self._address + 1) & 0x3FFF; // Should be ok without this
    self._readBELatch = self._vdpRAM[self._address]; 

    return data;
}
    """

    def readPortBF(self):
        self._addressLatch = False; # Address is unlatched during port read
    
        original_value = self._vdpStatusRegister;
        self._vdpStatusRegister = 0;
        self._hIntPending = False;
        self._vIntPending = False;
    
        return original_value;

    def writePortBF(self, data):

        if (False == self._addressLatch):
            self._lowaddress = data
            self._addressLatch = True
        else:
              # Set the register (as specified in the `hiaddress') to the
              # previous value written to this port
            if ((data & VdpConstants.REGISTERUPDATEMASK) == VdpConstants.REGISTERUPDATEVALUE):
                self.writeRegister(data & VdpConstants.REGISTERMASK, self._lowaddress);
    
            self._address = (self._lowaddress + (data << 8)) & 0x3FFF;
            self._codeRegister = (self._lowaddress + (data << 8)) >> 14;
            self._addressLatch = False;
    
            self._readBELatch = self._vdpRAM[self._address]; 

    def writePortBE(self, data):
        self._addressLatch = False;  # Address is unlatched during port read
    
        if (self._codeRegister == 0x3): # Write to video ram
            self.setPalette(self._address, data);
        else: 
            if (((self._address & VdpConstants.TILEATTRIBUTESADDRESSMASK) == self._tileAttributesAddress) and
                 ((self._address & VdpConstants.TILEATTRIBUTEMASK) < VdpConstants.NUMTILEATTRIBUTES)):
                self.updateTileAttributes(self._address,self._vdpRAM[self._address], data);
            elif (((self._address & VdpConstants.SPRITEATTRIBUTESADDRESSMASK) == self._spriteAttributesAddress) and
                  ((self._address & VdpConstants.SPRITEATTRIBUTESMASK) < VdpConstants.NUMSPRITEATTRIBUTES)):
                self.updateSpriteAttributes(self._address,self._vdpRAM[self._address], data);
            if (self._address < VdpConstants.PATTERNADDRESSLIMIT):
                self.updatePattern(self._address, self._vdpRAM[self._address], data);
    
            self._vdpRAM[self._address] = data; # Update after function call
            self._readBELatch = data; 
    
        self._address = (self._address + 1) & 0x3FFF; # Should be ok without this
    
    def setFullSpeed(self, isFullSpeed):
        print inspect.stack()[0][3]
        self._isFullSpeed = isFullSpeed

    def updateSpriteAttributes(self, address, oldData, newData):
        print inspect.stack()[0][3]
    """
{
    uint8 spriteNum;

    // Only update if need be
    if (oldData != newData)
    {
        spriteNum = address & VdpConstants.SPRITEATTRIBUTESMASK;

        // See if it's an x, or tile number attributes
        if (spriteNum & VdpConstants.SPRITEXNMASK)
        {
            spriteNum = (spriteNum >> 1) ^ VdpConstants.MAXSPRITES;
            if (address & VdpConstants.SPRITETILEMASK) // Changing tile
            {
                self._patternInfo[sprites[spriteNum].tileNumber].references--;
                sprites[spriteNum].tileNumber = newData | self._spriteTileShift;
                self._patternInfo[sprites[spriteNum].tileNumber].references++;
            }
            else // Changing x position
            {
                sprites[spriteNum].x = newData;
            }

            sprites[spriteNum].changed = True;
            self._videoChange = True;

        }
        else if (spriteNum < VdpConstants.MAXSPRITES) // Updating y attribute
        {
            // The number of sprites has changed, do some work updating
            // the appropriate scanlines

            // If inserting a new token earlier then previous, remove tiles
            if (newData == VdpConstants.LASTSPRITETOKEN)
            {
                if (spriteNum < totalSprites)
                {
                    for (int i = totalSprites - 1; i >= spriteNum; i--)
                    {
                        // Not the most efficient, but fairly robust
                        for (int y = sprites[i].y; 
                                 y < sprites[i].y + spriteHeight; y++)
                        {
                            removeSpriteFromScanlines(y, i);
                        }
                    }
                    totalSprites = spriteNum;
                }

                sprites[spriteNum].y = newData + 1;
            }
              // Removing token, so extend the number of sprites
            else if (((sprites[spriteNum].y-1) == VdpConstants.LASTSPRITETOKEN) &&
                    (spriteNum == totalSprites))
            {

                totalSprites++;
                while((totalSprites < VdpConstants.MAXSPRITES) &&
                      ((sprites[totalSprites].y -1) != VdpConstants.LASTSPRITETOKEN))
                            totalSprites++;

                sprites[spriteNum].y = newData + 1;

                // Not the most efficient, but fairly robust
                for (int i = spriteNum; i < totalSprites; i++)
                {
                    for (int y = sprites[i].y; 
                                    y < sprites[i].y + spriteHeight; y++)
                    {
                        addSpriteToScanlines(y, i);
                    }
                }
            }
            else
            if (spriteNum < totalSprites)
            {
                // Remove from previous scanlines, add to new scanlines
                // Not the most efficient, but fairly robust
                for (int y = sprites[spriteNum].y; 
                                y < sprites[spriteNum].y + spriteHeight; y++)
                    removeSpriteFromScanlines(y, spriteNum);

                sprites[spriteNum].y = newData + 1;

                for (int y = sprites[spriteNum].y; 
                                y < sprites[spriteNum].y + spriteHeight; y++)
                    addSpriteToScanlines(y, spriteNum);
            }
            else
            {
                sprites[spriteNum].y = newData + 1;
            }

            sprites[spriteNum].changed = True;
            self._videoChange = True;
        }

        // SpriteNum at this point may be invalid if using `unused space'
    }
}
    """

    def drawSprites(self):
        print inspect.stack()[0][3]
    """
{
    /* Chech for any sprite alterations */
    for (int i = 0; i < totalSprites; i++)
    {
        if (self._patternInfo[sprites[i].tileNumber].changed)
            sprites[i].changed = True;

        if(sprites[i].changed)
        {
            for (unsigned int y = sprites[i].y; 
                  (y < (unsigned) sprites[i].y + spriteHeight) && 
                  (y < VdpConstants.SMS_HEIGHT); y++)
            {
                self._spriteScanLines[y].lineChanged = True;
            }

            sprites[i].changed = False; // Sprite changes noted
        }
    }

    for (int y = 0; y < self._yEnd; y++)
    {

        // Only need to draw lines that have changed
        if (self._spriteScanLines[y].lineChanged)
        {

            memset(self._spriteScanLines[y].scanLine, 0, VdpConstants.SMS_WIDTH*sizeof(uint8));

            uint8 spriteNum;
            uint16 tileAddr;
            uint8 tiley;

            for (int i = 0; (i < self._spriteScanLines[y].numSprites) &&
                            (i < VdpConstants.MAXSPRITESPERSCANLINE); i++)
            {
                spriteNum = self._spriteScanLines[y].sprites[i];

                /* FIXME, loosing motivation, this is better but still
                   not quite right
                   */
                if (sprites[spriteNum].y > VdpConstants.SMS_HEIGHT)
                    tiley = y - sprites[spriteNum].y + VdpConstants.SMS_HEIGHT;
                else
                    tiley = y - sprites[spriteNum].y;

                tileAddr = (sprites[spriteNum].tileNumber << 6) |
                           ((tiley) << 3);
                for (unsigned int x = 0; x < spriteWidth; x++)
                {
                      // If the line is clear
                    if(((sprites[spriteNum].x + x) < VdpConstants.SMS_WIDTH) && 
                      (self._spriteScanLines[y].scanLine[sprites[spriteNum].x+x]==0))
                        self._spriteScanLines[y].scanLine[sprites[spriteNum].x+x] = 
                               self._patterns4[tileAddr | x];

                }
            }
        }
    }
}
    """

    def printSpriteScanLineInfo(self):
        print inspect.stack()[0][3]
    """
{
    std::cout << "Total Sprites: " << (int) totalSprites << std::endl;
    std::cout << "End tokens: ";
    for (unsigned int i = 0; i < VdpConstants.MAXSPRITES; i++)
    {
        if ((sprites[i].y - 1) == VdpConstants.LASTSPRITETOKEN)
            std::cout << "(" << i << ")";
    }
    std::cout << std::endl;

    for (int y = 0; y < self._yEnd; y++)
    {
	std::cout << (self._spriteScanLines[y].lineChanged?"*":" ") << 
                "y: " << y << " sprites: " << 
                (int) self._spriteScanLines[y].numSprites;
        for (int i = 0; i < self._spriteScanLines[y].numSprites;i++)
            std::cout << " [" << (int) self._spriteScanLines[y].sprites[i] << "]";

	std::cout << std::endl;
    }
}
    """

#/* Not the most efficient routine, but it should do the job
# */
    def removeSpriteFromScanlines(self, scanlineNumber, spriteNumber):
        print inspect.stack()[0][3]
    """
{
    uint8 shift = 0;

    if (scanlineNumber < self._yEnd)
    {
        uint8 numSprites = self._spriteScanLines[scanlineNumber].numSprites;

        for (int i = 0; i < numSprites - shift; i++)
        {
            if (self._spriteScanLines[scanlineNumber].sprites[i] == spriteNumber) 
            {
                shift++;
                self._spriteScanLines[scanlineNumber].numSprites--;
                self._spriteScanLines[scanlineNumber].lineChanged = True;
            }

            self._spriteScanLines[scanlineNumber].sprites[i] = 
                    self._spriteScanLines[scanlineNumber].sprites[i + shift];
        }
    }
}
    """

#/* Not the most efficient routine, but it should do the job
# */
    def addSpriteToScanlines(scanlineNumber, spriteNumber):
        print inspect.stack()[0][3]
    """
{
    if (scanlineNumber < self._yEnd)
    {
        assert(self._spriteScanLines[scanlineNumber].numSprites != VdpConstants.MAXSPRITES);

        for (int i = self._spriteScanLines[scanlineNumber].numSprites++; i > 0; i--)
        {
            if (self._spriteScanLines[scanlineNumber].sprites[i-1] < spriteNumber) 
            {
                self._spriteScanLines[scanlineNumber].lineChanged = True;
                self._spriteScanLines[scanlineNumber].sprites[i] = spriteNumber;
                return;
            }

            self._spriteScanLines[scanlineNumber].sprites[i] = 
                    self._spriteScanLines[scanlineNumber].sprites[i - 1];
        }

        self._spriteScanLines[scanlineNumber].sprites[0] = spriteNumber;
        self._spriteScanLines[scanlineNumber].lineChanged = True;
    }
}
    """

# Update a more convenient representation of the patterns
    def updatePattern(self, address, oldData, data):

        change = oldData ^ data; # Flip only the bits that have changed
        if (change != 0):
            index = (address & 0x3FFC) << 1; # Base index (pattern + row)
    
            mask = 1 << (address & 0x3);  # Bit position to flip
    
            # Only update if the data has changed
            # From right to left
            x = 7;
            while (change != 0):
                # Flip the bit position if required
                if (change & 0x1):
                    self._patterns4[index + x] ^= mask;
    
                x -= 1
                change = change >> 1;
    
            self._patternInfo[index >> 6].changed = True;
            self._patternInfo[index >> 6].colorCheck = False;
            if (self._patternInfo[index >> 6].references):
                self._videoChange = True;
    
            self._patternInfo[index >> 6].screenVersionCached = False;

# `Cache' a screen palette version of the pattern
    def updateScreenPattern(self, patternNumber):
        print inspect.stack()[0][3]
    """
{
    uint8 pixel4;
    uint16 index = patternNumber << 6;

    for (unsigned int py = 0; py < VdpConstants.PATTERNHEIGHT; py++)
    {
        for (unsigned int px = 0; px < VdpConstants.PATTERNWIDTH; px++)
        {
            pixel4 = self._patterns4[index]; 

            patterns16[0][index] = screenPalette[pixel4];
            patterns16[1][index++] = screenPalette[pixel4 | (1 << 4)];
        }
    }
    self._patternInfo[patternNumber].screenVersionCached = True;
}
    """

#/* Update the horizontal scroll offsets for each scanline */
    def updateHorizontalScrollInfo(self):
        columnOffset = (0x20 - (self._horizontalScroll >> 3)) & 0x1F;
        fineScroll = self._horizontalScroll & 0x7;
        xOffset = columnOffset*VdpConstants.PATTERNWIDTH - fineScroll;
    
        for y in range(self._currentYpos, self._yEnd):
            self._horizontalScrollInfo[y].columnOffset = columnOffset;
            self._horizontalScrollInfo[y].fineScroll = fineScroll;
            self._horizontalScrollInfo[y].xOffset = xOffset;
            self._horizontalScrollInfo[y].xOffset = xOffset;

#/* Update the vertical scroll offsets for each scanline */
    def updateVerticalScrollInfo(self):
        for y in range(self._currentYpos, self._yEnd):
            self._verticalScrollInfo[y] = self._verticalScroll;

    def updateTileAttributes(self, address, oldData, data):
        print inspect.stack()[0][3]
    """
{

    // Only update if altered
    if (oldData != data)
    {
        int tile = (address & VdpConstants.TILEATTRIBUTESTILEMASK) >> VdpConstants.TILESHIFT;

        self._patternInfo[tileAttributes[tile].tileNumber].references--;

        // Alteration of the high byte 
        if (address & VdpConstants.TILEATTRIBUTESHMASK)
        {
            if (tileAttributes[tile].priority)
                if ((data >> VdpConstants.TILEPRIORITYSHIFT) == 0)
                    tileAttributes[tile].priorityCleared = True;

            tileAttributes[tile].priority = data >> VdpConstants.TILEPRIORITYSHIFT;
            tileAttributes[tile].paletteSelect = 
                        (data >> VdpConstants.TILEPALETTESHIFT) & 0x1;
            tileAttributes[tile].verticalFlip = 
                        (data >> VdpConstants.TILEVFLIPSHIFT) & 0x1;
            tileAttributes[tile].horizontalFlip = 
                        (data >> VdpConstants.TILEHFLIPSHIFT) & 0x1;
            tileAttributes[tile].tileNumber = 
                    (unsigned) (tileAttributes[tile].tileNumber & 0xFF) | 
                    ((data & 0x1) << 8);
        }
        else
        {
            tileAttributes[tile].tileNumber = 
                    (tileAttributes[tile].tileNumber & 0x100) | data;
        }

        // Flag that the tile referenced is displayed
        // This may `exceed value' (ie 511), but should have no adverse effect
        self._patternInfo[tileAttributes[tile].tileNumber].references++;

        tileAttributes[tile].changed = True;
        self._videoChange = True;
    }
}
    """

    def writeRegister(self, registerNumber, data):

        self._vdpRegister[registerNumber] = data; # Update register data
    
        # Only need to react immediately to some register changes
        if ((0 == registerNumber) or
            (1 == registerNumber)):
            self.updateModeControl();
        elif (2 == registerNumber):
            self._tileAttributesAddress = (data & 0xE) << 10;
            #self._nameTable = &self._vdpRAM[self._tileAttributesAddress];
            self._nameTableOffset = self._tileAttributesAddress;
    
        elif (5 == registerNumber):
            self._spriteAttributesAddress = ((data & 0x7E) << 7);
            if (self._lastSpriteAttributesAddress != self._spriteAttributesAddress):
                self._lastSpriteAttributesAddress = self._spriteAttributesAddress;
#            self._spriteInformationTable = &self._vdpRAM[self._spriteAttributesAddress];
            self._spriteInformationTableOffset = self._spriteAttributesAddress
    
        elif (6 == registerNumber):
            #self._tileDefinitions = &self._vdpRAM[(data & 0x4) << 11];
            # Probably should do more when this changes, as all the 
            # sprite tile numbers should change... maybe later
            self._spriteTileShift = (data & 0x4) << 6;
    
        elif (7 == registerNumber):
    	    print("Using border color: %x"%(data))
            self._borderColor = data & 0xf;
    
        elif (8 == registerNumber):
            self._horizontalScroll = data;
            self.updateHorizontalScrollInfo();
            self._videoChange = True;
    
        elif (9 == registerNumber):
            self._verticalScroll = data;
            self.updateVerticalScrollInfo();
            self._videoChange = True;
    
        elif (10 == registerNumber):
            self._lineInterupt = data;
    
    def updateModeControl(self):
    
        # Set first scrolling line
        if(self._vdpRegister[VdpConstants.MODE_CONTROL_NO_1] & VdpConstants.VDP0DISHSCROLL):
            self._yScroll = 16
        else:
            self._yScroll = 0
    
        # Set last scrolling position
        if(self._vdpRegister[VdpConstants.MODE_CONTROL_NO_1] & VdpConstants.VDP0DISHSCROLL):
            self._xScroll = 192
        else:
            self._xScroll = VdpConstants.SMS_WIDTH
    
        if (self._vdpRegister[VdpConstants.MODE_CONTROL_NO_2] & VdpConstants.VDP1VSYNC):
            self._vsyncInteruptEnable = True
        else:
            self._vsyncInteruptEnable = False
    
        if (self._vdpRegister[VdpConstants.MODE_CONTROL_NO_1] & VdpConstants.VDP0LINEINTENABLE):
            self._hsyncInteruptEnable = True
        else:
            self._hsyncInteruptEnable = False
    
        if (self._vdpRegister[VdpConstants.MODE_CONTROL_NO_1] & VdpConstants.VDP0COL0OVERSCAN):
            self._startX = VdpConstants.PATTERNWIDTH
        else:
            self._startX = 0
    
        if (self._vdpRegister[VdpConstants.MODE_CONTROL_NO_1] & VdpConstants.VDP0SHIFTSPRITES):
            errors.warning("Sprite shift not implemented")
    
        if (self._vdpRegister[VdpConstants.MODE_CONTROL_NO_1] & VdpConstants.VDP0NOSYNC):
            errors.warning("No sync, not implemented");
    
        if (self._vdpRegister[VdpConstants.MODE_CONTROL_NO_2] & VdpConstants.VDP1ENABLEDISPLAY):
            enableDisplay = True;
        else:
            enableDisplay = False;
    
        if (self._vdpRegister[VdpConstants.MODE_CONTROL_NO_2] & VdpConstants.VDP1BIGSPRITES):
            spriteHeight = 16;
        else:
            spriteHeight = 8;
    
        if (self._vdpRegister[VdpConstants.MODE_CONTROL_NO_2] & VdpConstants.VDP1DOUBLESPRITES):
            errors.warning("Double sprites not implemented");
    
        self._displayMode = 0
        if (0 != (self._vdpRegister[VdpConstants.MODE_CONTROL_NO_1] & VdpConstants.VDP0M4)):
            self._displayMode |= 8
        if (0 != (self._vdpRegister[VdpConstants.MODE_CONTROL_NO_2] & VdpConstants.VDP1M3)):
            self._displayMode |= 4
        if (0 != (self._vdpRegister[VdpConstants.MODE_CONTROL_NO_1] & VdpConstants.VDP0M2)):
            self._displayMode |= 2
        if (0 != (self._vdpRegister[VdpConstants.MODE_CONTROL_NO_2] & VdpConstants.VDP1M1)):
            self._displayMode |= 1

        # Need to see what the modes do/mean.
        if ((self._displayMode == 0x8) or (self._displayMode == 0xA)):
            self._yEnd = 192;
        else:
            self._yEnd = 0;
            errors.warning("Mode not supported");

    def setInterupt(self, interupt):
        self._interupt = interupt;

    def getNextInterupt(self, cycle):
        # Check conditions to see if a line interupt is next 
        if ((self._lineIntTime < VdpConstants.VFRAMETIME) and
            (self._vSync < self._lineIntTime)):
            # Next interupt will be a line interupt
            return self._lastVSync + self._lineIntTime;
        elif (self._vSync < VdpConstants.VFRAMETIME):  # Check for a frame interupt
            return self._lastVSync + VdpConstants.VFRAMETIME;
        else:
            return self._lastVSync + VdpConstants.VSYNCCYCLETIME;

    def openDisplay(self):
        # // Initialise the scanlines
        self._scanLines = [ScanLine()] * VdpConstants.SMS_HEIGHT
        for i in range(VdpConstants.SMS_HEIGHT):
            self._scanLines[i].scanLine = self._display_lines
            self._scanLines[i].lineChanged = True;
    
        # Scanlines for the background image
        self._backgroundScanLines = [ScanLine()] * VdpConstants.YTILES*VdpConstants.PATTERNHEIGHT
        for i in range(VdpConstants.YTILES*VdpConstants.PATTERNHEIGHT):
            self._backgroundScanLines[i].scanLine = [0] * VdpConstants.PATTERNWIDTH*VdpConstants.XTILES*VdpConstants.YTILES
            self._backgroundScanLines[i].lineChanged = True;
    
        # Scanlines for the forground image
        self._forgroundScanLines = [PriorityScanLine()] * VdpConstants.YTILES*VdpConstants.PATTERNHEIGHT
        for i in range(VdpConstants.YTILES*VdpConstants.PATTERNHEIGHT):
            self._forgroundScanLines[i].scanLine = [False] * VdpConstants.PATTERNWIDTH*VdpConstants.XTILES*VdpConstants.YTILES
            self._forgroundScanLines[i].hasPriority = False;
    
        # Initialise the Sprite scanlines
        self._spriteScanLines = [SpriteScanLine()] * VdpConstants.SMS_HEIGHT
        for i in range(VdpConstants.SMS_HEIGHT):
            self._spriteScanLines[i].scanLine = [0] * VdpConstants.SMS_WIDTH
            self._spriteScanLines[i].lineChanged = True;
            self._spriteScanLines[i].numSprites = 0;
            self._spriteScanLines[i].sprites = [VdpConstants.NOSPRITE] * VdpConstants.MAXSPRITES
    
        self._lastHorizontalScrollInfo = [HorizontalScroll()] * VdpConstants.SMS_HEIGHT
        self._horizontalScrollInfo     = [HorizontalScroll()] * VdpConstants.SMS_HEIGHT
        self._verticalScrollInfo       = [0] * VdpConstants.SMS_HEIGHT;
        self._lastVerticalScrollInfo   = [0] * VdpConstants.SMS_HEIGHT;

# Translate colors to screen color depth when the palette is altered
#
    def setPalette(self, addr, data):
        print inspect.stack()[0][3]
    """
{
    uint16 color;
    uint8 r, g, b;

    addr = addr % VdpConstants.CRAMSIZE;

    if (cRAM[addr] != data)
    {
        cRAM[addr] = data;

        // Generate 8-bit RGB components, just to be generic
        r = ((int)(data&0x3)*0xFF)/0x3;
        g = ((int)((data>>2)&0x3)*0xFF)/0x3;
        b = ((int)((data>>4)&0x3)*0xFF)/0x3;

        color = setColor(r, g, b);

        screenPalette[addr] = color;

        // Rough optimisation for palette `rotate' graphics 

        for (unsigned int i = 0; i < VdpConstants.MAXPATTERNS; i++)
        {
            if (self._patternInfo[i].colorCheck == False)
                checkPatternColors(i);

            if (self._patternInfo[i].colors & (1<<(addr & 0xF)))
            {
                self._patternInfo[i].changed = True;
                self._patternInfo[i].screenVersionCached = False;
            }
        }
        self._videoChange = True;
    }
}
    """

# This changes 8-bit r, g, b values into a 16-bit encoded color
    def setColor(self, r, g, b):
        print inspect.stack()[0][3]
    """
{
    uint16 color;

    color = ((((int) 0x1F*r)/0xFF) << 11) |
            ((((int) 0x3F*g)/0xFF) << 5) |
            (((0x1F*b)/0xFF));

    return color;
}
    """

    def checkPatternColors(self, pattern):
        print inspect.stack()[0][3]
    """
{
    self._patternInfo[pattern].colors = 0; 
    for (uint8 i = 0; i < 64;i++)
        self._patternInfo[pattern].colors |= 1 << self._patterns4[pattern << 6 | i]; 

    self._patternInfo[pattern].colorCheck = True;
}
    """

    def drawBuffer(self):
        self.drawBackground();
        self.drawSprites();
    
        # Reset any change indicators for the patterns
        for i in range(VdpConstants.MAXPATTERNS):
            self._patternInfo[i].changed = False;

    """
void Vdp::drawDisplay(void)
{
    drawBuffer();
    updateDisplay();
}
    """

# Draw the background tiles 
    def drawBackground(self):
        print inspect.stack()[0][3]
    """
{
    int tile = 0;
    bool priority;
    uint16 *patternPtr;
    uint8 *pattern4Ptr;
    int8 patternYdelta, patternXdelta;

    for (unsigned int y = 0; y < VdpConstants.YTILES*VdpConstants.PATTERNHEIGHT; y++)
        self._forgroundScanLines[y].hasPriority = False;

    for (unsigned int y = 0; y < VdpConstants.YTILES*VdpConstants.PATTERNHEIGHT; y += VdpConstants.PATTERNHEIGHT)
    {
        for (unsigned int x = 0; x < VdpConstants.XTILES*VdpConstants.PATTERNWIDTH; x += VdpConstants.PATTERNWIDTH)
        {

            if ((self._forgroundScanLines[y].hasPriority == False) &&
                (tileAttributes[tile].priority == True))
            {
                for (unsigned int py = 0; py < VdpConstants.PATTERNHEIGHT; py++)
                    self._forgroundScanLines[y+py].hasPriority = True;
            }

            if(tileAttributes[tile].changed ||
               self._patternInfo[tileAttributes[tile].tileNumber].changed)
            {
                if(!self._patternInfo[tileAttributes[tile].tileNumber].
                       screenVersionCached)
                    updateScreenPattern(tileAttributes[tile].tileNumber);

                priority = tileAttributes[tile].priority;

                patternPtr = &patterns16[tileAttributes[tile].paletteSelect]
                                [(tileAttributes[tile].tileNumber << 6)];
                patternYdelta = 0;
                patternXdelta = 1;

                if (tileAttributes[tile].horizontalFlip != 0)
                {
                    patternPtr += VdpConstants.PATTERNWIDTH-1;
                    patternXdelta = -1;
                    patternYdelta = VdpConstants.PATTERNWIDTH * 2;
                }

                if (tileAttributes[tile].verticalFlip != 0) 
                {
                    patternPtr += ((VdpConstants.PATTERNHEIGHT-1) << 3);
                    patternYdelta -= 2 * VdpConstants.PATTERNWIDTH;
                }

                if (priority)
                {
                    pattern4Ptr = &self._patterns4[(tileAttributes[tile].tileNumber 
                                            << 6)];

                    if (tileAttributes[tile].horizontalFlip != 0)
                        pattern4Ptr += VdpConstants.PATTERNWIDTH-1;

                    if (tileAttributes[tile].verticalFlip != 0) 
                        pattern4Ptr += ((VdpConstants.PATTERNHEIGHT-1) << 3);

                    for (unsigned int py = 0; py < VdpConstants.PATTERNHEIGHT; py++)
                    {
                        for (unsigned int px = 0; px < VdpConstants.PATTERNWIDTH; px++)
                        {

                            self._backgroundScanLines[y+py].scanLine[x+px] =
                                    *patternPtr;

                            // Indicate a forground pixel if the value is
                            // non-zero and it is set as a forground pixel...
                            // well tile
                            self._forgroundScanLines[y+py].scanLine[x+px] = False;

                            if (priority && (*pattern4Ptr != 0x0))
                            {
                                self._forgroundScanLines[y+py].scanLine[x+px] = True;
                            }

                            patternPtr += patternXdelta;
                            pattern4Ptr += patternXdelta;
                        }
                        patternPtr += patternYdelta;
                        pattern4Ptr += patternYdelta;

                        self._backgroundScanLines[y+py].lineChanged = True;
                    }
                }
                else
                {
                    if (tileAttributes[tile].priorityCleared)
                    {
                        for (unsigned int py = 0; py < VdpConstants.PATTERNHEIGHT; py++)
                            for (unsigned int px = 0; px < VdpConstants.PATTERNWIDTH; px++)
                                self._forgroundScanLines[y+py].scanLine[x+px] =
                                False;
                        tileAttributes[tile].priorityCleared = False;
                    }

                    for (unsigned int py = 0; py < VdpConstants.PATTERNHEIGHT; py++)
                    {

                        if (patternXdelta == 1)
                        {
                            memcpy(&self._backgroundScanLines[y+py].scanLine[x],
                                   patternPtr, VdpConstants.PATTERNWIDTH*sizeof(uint16));
                            patternPtr += VdpConstants.PATTERNWIDTH;
                        }
                        else
                        {
                            for (unsigned int px = 0; px < VdpConstants.PATTERNWIDTH; px++)
                            {
                                self._backgroundScanLines[y+py].scanLine[x+px] =
                                        *patternPtr;

                                patternPtr += patternXdelta;
                            }
                        }
                        patternPtr += patternYdelta;

                        self._backgroundScanLines[y+py].lineChanged = True;
                    }
                }
                tileAttributes[tile].changed = False;
            }
            tile++;
        }
    }
}
    """

    # Draw the background tiles
    def drawPatterns(self):
        print inspect.stack()[0][3]
    """
{
    int pattern = 0;
    int pixel4;
    int paletteSelect = 1;

    for (unsigned int y = 0; y < 16*VdpConstants.PATTERNHEIGHT; y += VdpConstants.PATTERNHEIGHT)
    {
        for (unsigned int x = 0; x < VdpConstants.XTILES*VdpConstants.PATTERNWIDTH; x += VdpConstants.PATTERNWIDTH)
        {

            for (unsigned int py = 0; py < VdpConstants.PATTERNHEIGHT; py++)
            {
                for (unsigned int px = 0; px < VdpConstants.PATTERNWIDTH; px++)
                {
                        pixel4 =
                            self._patterns4[(pattern << 6) | (py << 3 )| px] |
                                         (paletteSelect << 4);
                        self._backgroundScanLines[y+py].scanLine[x+px] =
                             screenPalette[pixel4];

                }
            }
            pattern++;
        }
    }
}
    """

    def printSpriteInformation(self):
        print inspect.stack()[0][3]
    """
{
    for (int i = 0; i < VdpConstants.NUMSPRITES; i++)
    {
	std::cout << "Sprite " << i;
	std::cout << " x: " << (int) self._vdpRAM[self._spriteInformationTableOffset + 128 + i*2];
	std::cout << " y: " << (int) self._vdpRAM[self._spriteInformationTableOffset + i];
	std::cout << " tile: " << (int) self._vdpRAM[self._spriteInformationTableOffset + 129 + i*2];
	std::cout << std::endl;
    }
}
    """

    def printNameTable(self):
        print inspect.stack()[0][3]
    """
{
    int offset = 0;
    uint8 h, l;
    uint16 tmp;
    for (int y = 0; y < 28; y++)
    {
        for (int x = 0; x < 32; x++)
        {
            l = self.self._vdpRAM[self._nameTableOffset + offset++];
            h = self.self._vdpRAM[self._nameTableOffset + offset++];
            #l = self._nameTable[offset++];
            #h = self._nameTable[offset++];

            tmp = l + ((h & 0x1) << 8);
	    std::cout << "Name table " << tmp << " ";
	    std::cout << (((h >> 4) & 0x1) ? 'F':'B');
	    std::cout << (((h >> 3) & 0x1) ? 'S':'T');
	    std::cout << (((h >> 2) & 0x1) ? 'V':'.');
	    std::cout << (((h >> 1) & 0x1) ? 'H':'.');
	    std::cout << std::endl;
        }
    }
  
}
    """

    def clearDisplay(self):
        # SDL_Flip(screen);
        self.driver_update_display()

    def updateDisplay(self):
        print inspect.stack()[0][3]
    """
{
    uint8 fineScroll = 0;
    uint16 firstBlock;
    uint16 secondBlock;
    int16 xOffset = 0;
    uint16 *src, *dst;
    unsigned int x;
    uint8 verticalOffset;

    for (int y = 0; y < self._yEnd; y++)
    {
        verticalOffset = self._verticalScrollInfo[y];
        if ((self._horizontalScrollInfo[y].xOffset !=
             self._lastHorizontalScrollInfo[y].xOffset)||
            (self._verticalScrollInfo[y] != self._lastVerticalScrollInfo[y])||
             (self._spriteScanLines[y].lineChanged)||
           (self._backgroundScanLines[(y+verticalOffset)%(VdpConstants.YTILES*VdpConstants.PATTERNHEIGHT)].
                     lineChanged))
        {
            self._lastHorizontalScrollInfo[y].xOffset = 
                    self._horizontalScrollInfo[y].xOffset;
            self._lastVerticalScrollInfo[y] = self._verticalScrollInfo[y];

            if (y >= self._yScroll)
            {
                fineScroll = self._horizontalScrollInfo[y].fineScroll;
                xOffset = self._horizontalScrollInfo[y].xOffset;
            }

            if (self._startX > fineScroll)
                x = self._startX;
            else 
                x = fineScroll;

            verticalOffset = self._verticalScrollInfo[y];

            /* Copy the source to the destination */
            dst = &(self._scanLines[y].scanLine[x]);
            src = &(self._backgroundScanLines[(y + verticalOffset) % 
                   (VdpConstants.YTILES*VdpConstants.PATTERNHEIGHT)].scanLine[(x+xOffset) % VdpConstants.SMS_WIDTH]); 
            firstBlock = VdpConstants.SMS_WIDTH - ((x+xOffset) % VdpConstants.SMS_WIDTH);
            if (firstBlock > (VdpConstants.SMS_WIDTH - x))
                firstBlock = VdpConstants.SMS_WIDTH - x;

            if (firstBlock != 0)
                memcpy(dst, src, firstBlock*sizeof(uint16));

            dst = &(self._scanLines[y].scanLine[x + firstBlock]);
            src = &(self._backgroundScanLines[(y + verticalOffset) %
                            (VdpConstants.YTILES * VdpConstants.PATTERNHEIGHT)].scanLine[0]); 
            secondBlock = VdpConstants.SMS_WIDTH - firstBlock - x;

            if (secondBlock != 0)
                memcpy(dst, src, secondBlock*sizeof(uint16));

            if (self._spriteScanLines[y].numSprites > 0)
            {
                  // If there is a transparent forground on this line
                if (self._forgroundScanLines[(y+verticalOffset) % 
                 (VdpConstants.YTILES*VdpConstants.PATTERNHEIGHT)].hasPriority)
                {
                for (int i = 0; i < self._spriteScanLines[y].numSprites; i++)
                {
                    uint8 spriteNumber = self._spriteScanLines[y].sprites[i];
                    for (x = sprites[spriteNumber].x; 
                         (x < (unsigned) sprites[spriteNumber].x +
                          spriteWidth) && (x < VdpConstants.SMS_WIDTH);
                         x++)
                    {
                        if ((self._spriteScanLines[y].scanLine[x] != 0) &&
                            (self._forgroundScanLines[(y+verticalOffset) % 
                            (VdpConstants.YTILES*VdpConstants.PATTERNHEIGHT)].scanLine[(x+xOffset) % 
                            VdpConstants.SMS_WIDTH] == False))
                        {
                            self._scanLines[y].scanLine[x] = 
                               screenPalette[self._spriteScanLines[y].scanLine[x] |
                               0x10]; 
                        }
                    }

                }
                }
                else{
                for (int i = 0; i < self._spriteScanLines[y].numSprites; i++)
                {
                    uint8 spriteNumber = self._spriteScanLines[y].sprites[i];
                    for (x = sprites[spriteNumber].x; 
                         (x < (unsigned) sprites[spriteNumber].x +
                         spriteWidth) && (x < VdpConstants.SMS_WIDTH);
                         x++)
                    {
                        if (self._spriteScanLines[y].scanLine[x] != 0)
                        {
                            self._scanLines[y].scanLine[x] = 
                               screenPalette[self._spriteScanLines[y].scanLine[x] |
                               0x10]; 
                        }
                    }

                }
                }
                memset(&self._scanLines[y].scanLine[0], 0, self._startX*sizeof(uint16));
            }
        }
        self._spriteScanLines[y].lineChanged = False;
        self._backgroundScanLines[(y+verticalOffset)%(VdpConstants.YTILES*VdpConstants.PATTERNHEIGHT)].
                     lineChanged = False;
    }

    if (blitImage)
        SDL_BlitSurface(image, NULL, screen, NULL);
    SDL_Flip(screen);
}
    """
