import ctypes
import time
import pkg_resources
import inspect
from .. import errors

class ScanLine(object):
    pass

class HorizontalScroll(object):
    def __init__(self):
        self.xOffset = 0

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
        RAMSIZE  = 0x4000
        CRAMSIZE  = 0x20
        # 3Mhz CPU, 50Hz refresh ~= 60000 ticks
        VSYNCCYCLETIME = 65232
        BLANKTIME      = (VSYNCCYCLETIME * 72)/262
        VFRAMETIME     = (VSYNCCYCLETIME * 192)/262
        HSYNCCYCLETIME = 216

        REGISTERMASK  = 0x0F
        REGISTERUPDATEMASK  = 0xF0
        REGISTERUPDATEVALUE = 0x80
        NUMVDPREGISTERS = 16

        # VDP status register 
        VSYNCFLAG   = 0x80

        # VDP register 0
        MODE_CONTROL_NO_1 = 0x0
        VDP0DISVSCROLL    = 0x80
        VDP0DISHSCROLL    = 0x40
        VDP0COL0OVERSCAN  = 0x20
        VDP0LINEINTENABLE = 0x10
        VDP0SHIFTSPRITES  = 0x08
        VDP0M4            = 0x04
        VDP0M2            = 0x02
        VDP0NOSYNC        = 0x01

        # VDP register 1 
        MODE_CONTROL_NO_2 = 0x1
        VDP1BIT7          = 0x80
        VDP1ENABLEDISPLAY = 0x40
        VDP1VSYNC         = 0x20
        VDP1M1            = 0x10
        VDP1M3            = 0x08
        VDP1BIGSPRITES    = 0x02
        VDP1DOUBLESPRITES = 0x01

        NAMETABLEPRIORITY = 0x10
        NUMSPRITES = 64

        DMM4 = 0x8
        DMM3 = 0x4
        DMM2 = 0x2
        DMM1 = 0x1

        PALETTE_ADDRESS  = 0xC000

        SMS_WIDTH  = 256
        SMS_HEIGHT = 192 # MAX HEIGHT
        SMS_COLOR_DEPTH = 16

        MAXPATTERNS = 512
        PATTERNWIDTH  = 8
        PATTERNHEIGHT = 8
        PATTERNSIZE = 64

        MAXPALETTES = 2

        NUMTILEATTRIBUTES = 0x700
        TILEATTRIBUTEMASK     = 0x7FF
        TILEATTRIBUTESADDRESSMASK = 0x3800 
        TILEATTRIBUTESTILEMASK = 0x07FE 
        TILESHIFT = 1 
        TILEATTRIBUTESHMASK    = 0x0001 
        TILEPRIORITYSHIFT = 4 
        TILEPALETTESHIFT = 3 
        TILEVFLIPSHIFT = 2 
        TILEHFLIPSHIFT = 1 

        YTILES = 28 
        XTILES = 32 
        NUMTILES = XTILES * YTILES 

        SPRITEATTRIBUTESADDRESSMASK = 0x3F00 
        SPRITEATTRIBUTESMASK = 0x00FF 
        NUMSPRITEATTRIBUTES = 0x00FF 

        SPRITETILEMASK = 0x0001 

        LASTSPRITETOKEN = 0xD0
        SPRITEXNMASK = 0x0080 
        MAXSPRITES = 64
        NOSPRITE = MAXSPRITES
        MAXSPRITESPERSCANLINE = 8

        PATTERNADDRESSLIMIT = 0x4000

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
          self._display_lines.append([self.default_color for x in range(self.FRAME_WIDTH)])

        self.driver_open_display()

        # Interrupt variables
        self._vSync = 0
        self._lineIntTime = 0
        self._lastVSync = 0

        self._lineInteruptLatch = 0
        self._frameUpdated = False
        self._update = False
        self._lastClock = 0

        self._lineInterupt = 0
        self._vsyncInteruptEnable = False
        self._vIntPending = False
        self._hsyncInteruptEnable = False
        self._hIntPending = False
        self._isFullSpeed = True
        self._videoChange = False
        self._vdpStatusRegister = 0
        self._vCounter = 0xD5
        self._currentYpos = 0
        self._yEnd = 0
        self._enableDisplay = True

        self._nextPossibleInterupt = 0
        self._interupt = None


        # From original constructor
        self._vsyncInteruptEnable = False
        self._hsyncInteruptEnable = False
        self._horizontalScrollChanged = False
        self._verticalScroll = 0
        self._lineInterupt = 0
        #self._tileDefinitions = 0
        self._enableDisplay = False

        self._tileAttributesAddress = 0
        self._spriteAttributesAddress = 0

        self._vdpRAM        = [0] * VdpConstants.RAMSIZE
        self._cRAM          = [0] * VdpConstants.CRAMSIZE
        self._screenPalette = [0] * VdpConstants.CRAMSIZE

        self._vdpStatusRegister = 0
        self._hIntPending = False
        self._vIntPending = False

        self._addressLatch = False
        self._lowaddress   = 0
        self._isFullSpeed = False

        self._codeRegister = 0
        self._readBELatch = 0
        self._lastSpriteAttributesAddress = 0

        self._spriteHeight = 8 
        self._spriteWidth = 8

        self._startX = 0
    
        self._vdpRegister = [0] *VdpConstants.NUMVDPREGISTERS
    
        self._displayMode = 0
    
        # Allocate memory for pattern tiles
        self._patternInfo = [PatternInfo() for x in range(VdpConstants.MAXPATTERNS)]
    
        self._patterns4 = [0] * VdpConstants.MAXPATTERNS*VdpConstants.PATTERNSIZE
    
        self._patterns16 = [[0 for i in range(VdpConstants.MAXPATTERNS*VdpConstants.PATTERNSIZE)] for j in range(VdpConstants.MAXPALETTES)]
    
        for pattern_info in self._patternInfo:
            pattern_info.references = 0
            pattern_info.changed = False
            pattern_info.colorCheck = False
            pattern_info.colors = False
            pattern_info.screenVersionCached = False
    
        self._tileAttributes = [TileAttribute() for x in range(VdpConstants.NUMTILEATTRIBUTES)]
        for tile_attribute in self._tileAttributes:
            tile_attribute.tileNumber = 0
            self._patternInfo[tile_attribute.tileNumber].references +=1
            # Assuming 'False' is the correct default.
            tile_attribute.changed = True
            tile_attribute.priority = False
            tile_attribute.priorityCleared = False
            tile_attribute.paletteSelect = False
            tile_attribute.verticalFlip = False
            tile_attribute.horizontalFlip = False
    
        self._spriteTileShift = 0
        self._totalSprites = VdpConstants.MAXSPRITES
        self._sprites = [Sprite() for x in range(VdpConstants.MAXSPRITES)]
        for sprite in self._sprites:
            sprite.y = 1
            sprite.x = 0
            sprite.tileNumber = 0
            self._patternInfo[sprite.tileNumber].references += 1
            sprite.changed = False
    
        self.openDisplay()

        self._horizontalScroll = 0

    def _draw_display(self):
        self.driver_draw_display()

    def setCycle(self, cycle):
        if (cycle >= self._nextPossibleInterupt):
                if (self.pollInterupts(cycle) == True):
                    self.poll_events()
                    self._interupt.interupt()
                self.getNextInterupt(cycle)

    def pollInterupts(self, cycle):

        self._vSync = cycle - self._lastVSync
    
        if ((self._lineIntTime < VdpConstants.VFRAMETIME) and
            (self._vSync >= (self._lineIntTime))):
            self._currentYpos = (self.clocks.cycles-self._lastVSync)/VdpConstants.HSYNCCYCLETIME+1
    
            self._lineInteruptLatch = self._lineInterupt + 1
    
            self._lineIntTime += self._lineInteruptLatch * VdpConstants.HSYNCCYCLETIME
    
            self._hIntPending = True
    
        if ((False == self._frameUpdated) and (self._vSync >= VdpConstants.VFRAMETIME)):
            if (self._enableDisplay == True):
                if (self._update == True):
                    self.updateDisplay()
                    self._update = False
            else:
                self.clearDisplay()
    
            self._frameUpdated = True
            self._vCounter = 0xD5
            self._currentYpos = self._yEnd
    
            self._vIntPending = True
            self._vdpStatusRegister |= VdpConstants.VSYNCFLAG
    
        if (self._vSync >= VdpConstants.VSYNCCYCLETIME):
            self._lastVSync = cycle
            self._vSync = 0
            self._currentYpos = 0
            self._vCounter = 0x00
            self.updateHorizontalScrollInfo()
            self.updateVerticalScrollInfo()
    
            self._lineInteruptLatch = self._lineInterupt
    
            self._lineIntTime = self._lineInteruptLatch * VdpConstants.HSYNCCYCLETIME
    
            if (self._videoChange == True):
                self.drawBuffer()
                self._update = True
                self._videoChange = False
    
            self._frameUpdated = False
    
        if ((self._vsyncInteruptEnable and self._vIntPending) or
            (self._hsyncInteruptEnable and self._hIntPending)):
            return True
        else:
            return False

    def readPort7E(self):
        self._addressLatch = False  # Address is unlatched during port read
    
        vCounter = (self.clocks.cycles-self._lastVSync)/VdpConstants.HSYNCCYCLETIME
        self._currentYpos = (self.clocks.cycles-self._lastVSync)/VdpConstants.HSYNCCYCLETIME+1
    
        # I can't think of an ellegant solution, so this is as good as it gets
        # for now (fudge factor and all)
        self.inputs.joystick.setYpos(vCounter+10)
        return vCounter

    def readPort7F(self):
        self._addressLatch = False  # Address is unlatched during port read
    
        # I can't think of an ellegant solution, so this is as good as it gets
        # for now (fudge factor and all)
        hCounter = ((self.inputs.joystick.getXpos() + 0x28)/2 & 0x7F)
        return hCounter

    def readPortBE(self):
        self._addressLatch = False  # Address is unlatched during port read
    
        data = self._readBELatch
    
        self._address = (self._address + 1) & 0x3FFF # Should be ok without this
        self._readBELatch = self._vdpRAM[self._address] 
    
        return data

    def readPortBF(self):
        self._addressLatch = False # Address is unlatched during port read
    
        original_value = self._vdpStatusRegister
        self._vdpStatusRegister = 0
        self._hIntPending = False
        self._vIntPending = False
    
        return original_value

    def writePortBF(self, data):

        if (False == self._addressLatch):
            self._lowaddress = data
            self._addressLatch = True
        else:
            # Set the register (as specified in the `hiaddress') to the
            # previous value written to this port
            if ((data & VdpConstants.REGISTERUPDATEMASK) == VdpConstants.REGISTERUPDATEVALUE):
                self.writeRegister(data & VdpConstants.REGISTERMASK, self._lowaddress)
    
            self._address = (self._lowaddress + (data << 8)) & 0x3FFF
            self._codeRegister = (self._lowaddress + (data << 8)) >> 14
            self._addressLatch = False
    
            self._readBELatch = self._vdpRAM[self._address] 

    def writePortBE(self, data):
        self._addressLatch = False  # Address is unlatched during port read
    
        if (self._codeRegister == 0x3): # Write to video ram
            self.setPalette(self._address, data)
        else: 
            if (((self._address & VdpConstants.TILEATTRIBUTESADDRESSMASK) == self._tileAttributesAddress) and
                 ((self._address & VdpConstants.TILEATTRIBUTEMASK) < VdpConstants.NUMTILEATTRIBUTES)):
                self.updateTileAttributes(self._address,self._vdpRAM[self._address], data)
            elif (((self._address & VdpConstants.SPRITEATTRIBUTESADDRESSMASK) == self._spriteAttributesAddress) and
                  ((self._address & VdpConstants.SPRITEATTRIBUTESMASK) < VdpConstants.NUMSPRITEATTRIBUTES)):
                self.updateSpriteAttributes(self._address,self._vdpRAM[self._address], data)
            if (self._address < VdpConstants.PATTERNADDRESSLIMIT):
                self.updatePattern(self._address, self._vdpRAM[self._address], data)
    
            self._vdpRAM[self._address] = data # Update after function call
            self._readBELatch = data 
    
        self._address = (self._address + 1) & 0x3FFF # Should be ok without this
    
    def setFullSpeed(self, isFullSpeed):
        self._isFullSpeed = isFullSpeed

    def updateSpriteAttributes(self, address, oldData, newData):
    
        # Only update if need be
        if (oldData != newData):
            spriteNum = address & VdpConstants.SPRITEATTRIBUTESMASK
    
            # See if it's an x, or tile number attributes
            if (spriteNum & VdpConstants.SPRITEXNMASK):
                spriteNum = (spriteNum >> 1) ^ VdpConstants.MAXSPRITES
                if (address & VdpConstants.SPRITETILEMASK): # Changing tile
                    self._patternInfo[self._sprites[spriteNum].tileNumber].references -= 1
                    self._sprites[spriteNum].tileNumber = newData | self._spriteTileShift
                    self._patternInfo[self._sprites[spriteNum].tileNumber].references += 1
                else: # Changing x position
                    self._sprites[spriteNum].x = newData
    
                self._sprites[spriteNum].changed = True
                self._videoChange = True
    
            elif (spriteNum < VdpConstants.MAXSPRITES): # Updating y attribute
                # The number of sprites has changed, do some work updating
                # the appropriate scanlines
    
                # If inserting a new token earlier then previous, remove tiles
                if (newData == VdpConstants.LASTSPRITETOKEN):
                    if (spriteNum < self._totalSprites):
                        for i in range(self._totalSprites - 1, spriteNum - 1, -1):
                            # Not the most efficient, but fairly robust
                            for y in range(self._sprites[i].y, self._sprites[i].y + self._spriteHeight):
                                self.removeSpriteFromScanlines(y, i)
                        self._totalSprites = spriteNum
    
                    self._sprites[spriteNum].y = newData + 1
                  # Removing token, so extend the number of sprites
                elif (((self._sprites[spriteNum].y-1) == VdpConstants.LASTSPRITETOKEN) and (spriteNum == self._totalSprites)):
    
                    self._totalSprites += 1
                    while((self._totalSprites < VdpConstants.MAXSPRITES) and
                          ((self._sprites[self._totalSprites].y -1) != VdpConstants.LASTSPRITETOKEN)):
                                self._totalSprites += 1
    
                    self._sprites[spriteNum].y = newData + 1
    
                    # Not the most efficient, but fairly robust
                    for i in range(spriteNum, self._totalSprites):
                        for y in range(self._sprites[i].y, self._sprites[i].y + self._spriteHeight):
                            self.addSpriteToScanlines(y, i)
                elif (spriteNum < self._totalSprites):
                    # Remove from previous scanlines, add to new scanlines
                    # Not the most efficient, but fairly robust
                    for y in range(self._sprites[spriteNum].y, self._sprites[spriteNum].y + self._spriteHeight):
                        self.removeSpriteFromScanlines(y, spriteNum)
    
                    self._sprites[spriteNum].y = newData + 1
    
                    for y in range(self._sprites[spriteNum].y, self._sprites[spriteNum].y + self._spriteHeight):
                        self.addSpriteToScanlines(y, spriteNum)
                else:
                    self._sprites[spriteNum].y = newData + 1
    
                self._sprites[spriteNum].changed = True
                self._videoChange = True
    
            # SpriteNum at this point may be invalid if using `unused space'

    def drawSprites(self):
        # Chech for any sprite alterations
        for i in range(self._totalSprites):
            if (self._patternInfo[self._sprites[i].tileNumber].changed):
                self._sprites[i].changed = True
    
            if(self._sprites[i].changed):
                y = self._sprites[i].y 
                while (y < self._sprites[i].y + self._spriteHeight) and (y < VdpConstants.SMS_HEIGHT):
                    self._spriteScanLines[y].lineChanged = True
                    y += 1
    
                self._sprites[i].changed = False # Sprite changes noted
    
        for y in range(self._yEnd):
            # Only need to draw lines that have changed
            if (self._spriteScanLines[y].lineChanged):
                for i in range(VdpConstants.SMS_WIDTH):
                    self._spriteScanLines[y].scanLine[i] = 0
    
                i = 0
                while ((i < self._spriteScanLines[y].numSprites) and (i < VdpConstants.MAXSPRITESPERSCANLINE)):
                    spriteNum = self._spriteScanLines[y].sprites[i]
    
                    # FIXME, loosing motivation, this is better but still
                    # not quite right
                    if (self._sprites[spriteNum].y > VdpConstants.SMS_HEIGHT):
                        tiley = y - self._sprites[spriteNum].y + VdpConstants.SMS_HEIGHT
                    else:
                        tiley = y - self._sprites[spriteNum].y
    
                    tileAddr = (self._sprites[spriteNum].tileNumber << 6) | ((tiley) << 3)
                    for x in range(self._spriteWidth):
                        # If the line is clear
                        if(((self._sprites[spriteNum].x + x) < VdpConstants.SMS_WIDTH) and 
                            (self._spriteScanLines[y].scanLine[self._sprites[spriteNum].x+x]==0)):
                            self._spriteScanLines[y].scanLine[self._sprites[spriteNum].x+x] = self._patterns4[tileAddr | x]
    
                    i += 1

    # Not the most efficient routine, but it should do the job
    def removeSpriteFromScanlines(self, scanlineNumber, spriteNumber):
        scanlineNumber = scanlineNumber & 0xFF

        shift = 0
    
        if (scanlineNumber < self._yEnd):
            numSprites = self._spriteScanLines[scanlineNumber].numSprites
    
            for i in range(numSprites - shift):
                if (self._spriteScanLines[scanlineNumber].sprites[i] == spriteNumber):
                    shift +=1
                    self._spriteScanLines[scanlineNumber].numSprites -=1
                    self._spriteScanLines[scanlineNumber].lineChanged = True
    
                if (i + shift < VdpConstants.MAXSPRITES):
                    self._spriteScanLines[scanlineNumber].sprites[i] = self._spriteScanLines[scanlineNumber].sprites[i + shift]
                else:
                    errors.warning("Index exceeds range of MAXSPRITES")

    # Not the most efficient routine, but it should do the job
    def addSpriteToScanlines(self, scanlineNumber, spriteNumber):
        scanlineNumber = scanlineNumber & 0xFF

        if (scanlineNumber < self._yEnd):
            #assert(self._spriteScanLines[scanlineNumber].numSprites != VdpConstants.MAXSPRITES)
    
            if(self._spriteScanLines[scanlineNumber].numSprites != VdpConstants.MAXSPRITES):
                i = self._spriteScanLines[scanlineNumber].numSprites
                self._spriteScanLines[scanlineNumber].numSprites += 1
                while(i > 0):
                    if (self._spriteScanLines[scanlineNumber].sprites[i-1] < spriteNumber):
                        self._spriteScanLines[scanlineNumber].lineChanged = True
                        self._spriteScanLines[scanlineNumber].sprites[i] = spriteNumber
                        return
    
                    self._spriteScanLines[scanlineNumber].sprites[i] = self._spriteScanLines[scanlineNumber].sprites[i - 1]
                    i -= 1
    
                self._spriteScanLines[scanlineNumber].sprites[0] = spriteNumber
                self._spriteScanLines[scanlineNumber].lineChanged = True
            else:
                errors.warning("Max sprite limit reached.")

    # Update a more convenient representation of the patterns
    def updatePattern(self, address, oldData, data):

        change = oldData ^ data # Flip only the bits that have changed
        if (change != 0):
            index = (address & 0x3FFC) << 1 # Base index (pattern + row)
    
            mask = 1 << (address & 0x3)  # Bit position to flip
    
            # Only update if the data has changed
            # From right to left
            x = 7
            while (change != 0):
                # Flip the bit position if required
                if (change & 0x1):
                    self._patterns4[index + x] ^= mask
    
                x -= 1
                change = change >> 1
    
            self._patternInfo[index >> 6].changed = True
            self._patternInfo[index >> 6].colorCheck = False
            if (self._patternInfo[index >> 6].references):
                self._videoChange = True
    
            self._patternInfo[index >> 6].screenVersionCached = False

    # `Cache' a screen palette version of the pattern
    def updateScreenPattern(self, patternNumber):

        index = patternNumber << 6
    
        for py in range(VdpConstants.PATTERNHEIGHT):
            for px in range(VdpConstants.PATTERNWIDTH):
                pixel4 = self._patterns4[index] 
    
                self._patterns16[0][index] = self._screenPalette[pixel4]
                self._patterns16[1][index] = self._screenPalette[pixel4 | (1 << 4)]
                index += 1

        self._patternInfo[patternNumber].screenVersionCached = True

    # Update the horizontal scroll offsets for each scanline
    def updateHorizontalScrollInfo(self):
        columnOffset = (0x20 - (self._horizontalScroll >> 3)) & 0x1F
        fineScroll = self._horizontalScroll & 0x7
        xOffset = (columnOffset*VdpConstants.PATTERNWIDTH - fineScroll) % VdpConstants.SMS_WIDTH
    
        for y in range(self._currentYpos, self._yEnd):
            self._horizontalScrollInfo[y].columnOffset = columnOffset
            self._horizontalScrollInfo[y].fineScroll = fineScroll
            self._horizontalScrollInfo[y].xOffset = xOffset

    # Update the vertical scroll offsets for each scanline
    def updateVerticalScrollInfo(self):
        for y in range(self._currentYpos, self._yEnd):
            self._verticalScrollInfo[y] = self._verticalScroll

    def updateTileAttributes(self, address, oldData, data):
        # Only update if altered
        if (oldData != data):
            tile = (address & VdpConstants.TILEATTRIBUTESTILEMASK) >> VdpConstants.TILESHIFT
    
            self._patternInfo[self._tileAttributes[tile].tileNumber].references -= 1
    
            # Alteration of the high byte 
            if (address & VdpConstants.TILEATTRIBUTESHMASK):
                if (self._tileAttributes[tile].priority):
                    if ((data >> VdpConstants.TILEPRIORITYSHIFT) == 0):
                        self._tileAttributes[tile].priorityCleared = True
    
                self._tileAttributes[tile].priority       =  data >> VdpConstants.TILEPRIORITYSHIFT
                self._tileAttributes[tile].paletteSelect  = (data >> VdpConstants.TILEPALETTESHIFT) & 0x1
                self._tileAttributes[tile].verticalFlip   = (data >> VdpConstants.TILEVFLIPSHIFT) & 0x1
                self._tileAttributes[tile].horizontalFlip = (data >> VdpConstants.TILEHFLIPSHIFT) & 0x1
                self._tileAttributes[tile].tileNumber     = (self._tileAttributes[tile].tileNumber & 0xFF) | ((data & 0x1) << 8)
            else:
                self._tileAttributes[tile].tileNumber     = (self._tileAttributes[tile].tileNumber & 0x100) | data
    
            # Flag that the tile referenced is displayed
            # This may `exceed value' (ie 511), but should have no adverse effect
            self._patternInfo[self._tileAttributes[tile].tileNumber].references += 1
    
            self._tileAttributes[tile].changed = True
            self._videoChange = True

    def writeRegister(self, registerNumber, data):

        self._vdpRegister[registerNumber] = data # Update register data
    
        # Only need to react immediately to some register changes
        if ((0 == registerNumber) or
            (1 == registerNumber)):
            self.updateModeControl()
        elif (2 == registerNumber):
            self._tileAttributesAddress = (data & 0xE) << 10
            #self._nameTable = &self._vdpRAM[self._tileAttributesAddress]
            self._nameTableOffset = self._tileAttributesAddress
    
        elif (5 == registerNumber):
            self._spriteAttributesAddress = ((data & 0x7E) << 7)
            if (self._lastSpriteAttributesAddress != self._spriteAttributesAddress):
                self._lastSpriteAttributesAddress = self._spriteAttributesAddress
#            self._spriteInformationTable = &self._vdpRAM[self._spriteAttributesAddress]
            self._spriteInformationTableOffset = self._spriteAttributesAddress
    
        elif (6 == registerNumber):
            #self._tileDefinitions = &self._vdpRAM[(data & 0x4) << 11]
            # Probably should do more when this changes, as all the 
            # sprite tile numbers should change... maybe later
            self._spriteTileShift = (data & 0x4) << 6
    
        elif (7 == registerNumber):
    	    print("Using border color: %x"%(data))
            self._borderColor = data & 0xf
    
        elif (8 == registerNumber):
            self._horizontalScroll = data
            self.updateHorizontalScrollInfo()
            self._videoChange = True
    
        elif (9 == registerNumber):
            self._verticalScroll = data
            self.updateVerticalScrollInfo()
            self._videoChange = True
    
        elif (10 == registerNumber):
            self._lineInterupt = data
    
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
            errors.warning("No sync, not implemented")
    
        if (self._vdpRegister[VdpConstants.MODE_CONTROL_NO_2] & VdpConstants.VDP1ENABLEDISPLAY):
            self._enableDisplay = True
        else:
            self._enableDisplay = False
    
        if (self._vdpRegister[VdpConstants.MODE_CONTROL_NO_2] & VdpConstants.VDP1BIGSPRITES):
            self._spriteHeight = 16
        else:
            self._spriteHeight = 8
    
        if (self._vdpRegister[VdpConstants.MODE_CONTROL_NO_2] & VdpConstants.VDP1DOUBLESPRITES):
            errors.warning("Double sprites not implemented")
    
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
            self._yEnd = 192
        else:
            self._yEnd = 0
            errors.warning("Mode not supported")

    def setInterupt(self, interupt):
        self._interupt = interupt

    def getNextInterupt(self, cycle):
        # Check conditions to see if a line interupt is next 
        if (self.clocks.cycles >= self._nextPossibleInterupt):
          if ((self._lineIntTime < VdpConstants.VFRAMETIME) and
              (self._vSync < self._lineIntTime)):
              # Next interupt will be a line interupt
              self._nextPossibleInterupt = self._lastVSync + self._lineIntTime
          elif (self._vSync < VdpConstants.VFRAMETIME):  # Check for a frame interupt
              self._nextPossibleInterupt = self._lastVSync + VdpConstants.VFRAMETIME
          else:
              self._nextPossibleInterupt = self._lastVSync + VdpConstants.VSYNCCYCLETIME

        return self._nextPossibleInterupt

    def openDisplay(self):
        # Initialise the scanlines
        self._scanLines = [ScanLine() for x in range(VdpConstants.SMS_HEIGHT)]
        for i in range(VdpConstants.SMS_HEIGHT):
            self._scanLines[i].scanLine = self._display_lines[i]
            self._scanLines[i].lineChanged = True

        # Scanlines for the background image
        self._backgroundScanLines = [ScanLine() for x in range(VdpConstants.YTILES*VdpConstants.PATTERNHEIGHT)]
        for i in range(VdpConstants.YTILES*VdpConstants.PATTERNHEIGHT):
            self._backgroundScanLines[i].scanLine = [0] * VdpConstants.PATTERNWIDTH*VdpConstants.XTILES*VdpConstants.YTILES
            self._backgroundScanLines[i].lineChanged = True
    
        # Scanlines for the forground image
        self._forgroundScanLines = [PriorityScanLine() for x in range(VdpConstants.YTILES*VdpConstants.PATTERNHEIGHT)]
        for i in range(VdpConstants.YTILES*VdpConstants.PATTERNHEIGHT):
            self._forgroundScanLines[i].scanLine = [False] * VdpConstants.PATTERNWIDTH*VdpConstants.XTILES*VdpConstants.YTILES
            self._forgroundScanLines[i].hasPriority = False
    
        # Initialise the Sprite scanlines
        self._spriteScanLines = [SpriteScanLine() for x in range(VdpConstants.SMS_HEIGHT)]
        for i in range(VdpConstants.SMS_HEIGHT):
            self._spriteScanLines[i].scanLine = [0] * VdpConstants.SMS_WIDTH
            self._spriteScanLines[i].lineChanged = True
            self._spriteScanLines[i].numSprites = 0
            self._spriteScanLines[i].sprites = [VdpConstants.NOSPRITE for x in range(VdpConstants.MAXSPRITES)]
    
        self._lastHorizontalScrollInfo = [HorizontalScroll() for x in range(VdpConstants.SMS_HEIGHT)]
        self._horizontalScrollInfo     = [HorizontalScroll() for x in range(VdpConstants.SMS_HEIGHT)]
        self._verticalScrollInfo       = [0] * VdpConstants.SMS_HEIGHT
        self._lastVerticalScrollInfo   = [0] * VdpConstants.SMS_HEIGHT

    # Translate colors to screen color depth when the palette is altered
    def setPalette(self, addr, data):
        #uint16 color
        #uint8 r, g, b
    
        addr = addr % VdpConstants.CRAMSIZE
    
        if (self._cRAM[addr] != data):
            self._cRAM[addr] = data
    
            # Generate 8-bit RGB components, just to be generic
            r = ((data&0x3)*0xFF)/0x3
            g = (((data>>2)&0x3)*0xFF)/0x3
            b = (((data>>4)&0x3)*0xFF)/0x3
    
            color = self.set_color(r, g, b)
    
            self._screenPalette[addr] = color
    
            # Rough optimisation for palette `rotate' graphics 
    
            for i in range(VdpConstants.MAXPATTERNS):
                if (self._patternInfo[i].colorCheck == False):
                    self.checkPatternColors(i)
    
                if (self._patternInfo[i].colors & (1<<(addr & 0xF))):
                    self._patternInfo[i].changed = True
                    self._patternInfo[i].screenVersionCached = False

            self._videoChange = True

    def checkPatternColors(self, pattern):
        self._patternInfo[pattern].colors = 0 
        for i in range(64):
            self._patternInfo[pattern].colors |= 1 << self._patterns4[pattern << 6 | i] 
    
        self._patternInfo[pattern].colorCheck = True

    def drawBuffer(self):

        self.drawBackground()
        self.drawSprites()

#        self.drawPatterns()# For debuging purposes
    
        # Reset any change indicators for the patterns
        for i in range(VdpConstants.MAXPATTERNS):
            self._patternInfo[i].changed = False

    """
void Vdp::drawDisplay(void)
{
    drawBuffer()
    updateDisplay()
}
    """

    # Draw the background tiles 
    def drawBackground(self):
        tile = 0

        for y in range(VdpConstants.YTILES*VdpConstants.PATTERNHEIGHT):
            self._forgroundScanLines[y].hasPriority = False
    
        for y in range(0, VdpConstants.YTILES*VdpConstants.PATTERNHEIGHT, VdpConstants.PATTERNHEIGHT):
            for x in range(0, VdpConstants.XTILES*VdpConstants.PATTERNWIDTH, VdpConstants.PATTERNWIDTH):

                _tile_attribute = self._tileAttributes[tile]
                _patterns16_palette = self._patterns16[_tile_attribute.paletteSelect]

                if ((self._forgroundScanLines[y].hasPriority == False) and (_tile_attribute.priority == True)):
                    for py in range(y, y+ VdpConstants.PATTERNHEIGHT):
                        self._forgroundScanLines[py].hasPriority = True
    
                if(_tile_attribute.changed or self._patternInfo[_tile_attribute.tileNumber].changed):
                    if(False == self._patternInfo[_tile_attribute.tileNumber].screenVersionCached):
                        self.updateScreenPattern(_tile_attribute.tileNumber)
    
                    patterns16_offset = (_tile_attribute.tileNumber << 6)
                    patternYdelta = 0
                    patternXdelta = 1
    
                    if (_tile_attribute.horizontalFlip != 0):
                        patterns16_offset += VdpConstants.PATTERNWIDTH-1
                        patternXdelta = -1
                        patternYdelta = VdpConstants.PATTERNWIDTH * 2
    
                    if (_tile_attribute.verticalFlip != 0):
                        patterns16_offset += ((VdpConstants.PATTERNHEIGHT-1) << 3)
                        patternYdelta -= 2 * VdpConstants.PATTERNWIDTH
    
                    if (_tile_attribute.priority):
                        pattern4_offset = (_tile_attribute.tileNumber << 6)
    
                        if (_tile_attribute.horizontalFlip != 0):
                            pattern4_offset += VdpConstants.PATTERNWIDTH-1
    
                        if (_tile_attribute.verticalFlip != 0):
                            pattern4_offset += ((VdpConstants.PATTERNHEIGHT-1) << 3)
    
                        for py in range(y, y + VdpConstants.PATTERNHEIGHT):
                            _background_y_line = self._backgroundScanLines[py]
                            _forground_y_line = self._forgroundScanLines[py]
                            for px in range(x, x + VdpConstants.PATTERNWIDTH):
                                _background_y_line.scanLine[px] = _patterns16_palette[patterns16_offset]
    
                                # Indicate a forground pixel if the value is
                                # non-zero and it is set as a forground pixel...
                                # well tile
                                _forground_y_line.scanLine[px] = False
    
                                # 'priority' is always true in this branch
                                if (self._patterns4[pattern4_offset] != 0x0):
                                    _forground_y_line.scanLine[px] = True
    
                                patterns16_offset += patternXdelta
                                pattern4_offset += patternXdelta
                            patterns16_offset += patternYdelta
                            pattern4_offset += patternYdelta
    
                            _background_y_line.lineChanged = True
                    else:
                        if (_tile_attribute.priorityCleared):
                            for py in range(y, y + VdpConstants.PATTERNHEIGHT):
                                _forground_y_line = self._forgroundScanLines[py]
                                for px in range(x, x + VdpConstants.PATTERNWIDTH):
                                    _forground_y_line.scanLine[px] = False
                            _tile_attribute.priorityCleared = False
    
                        for py in range(y, y + VdpConstants.PATTERNHEIGHT):
                            _background_y_line = self._backgroundScanLines[py]
                            if (patternXdelta == 1):
                                for i in range(VdpConstants.PATTERNWIDTH):
                                    _background_y_line.scanLine[x + i] = _patterns16_palette[patterns16_offset + i]
                                patterns16_offset += VdpConstants.PATTERNWIDTH
                            else:
                                for px in range(VdpConstants.PATTERNWIDTH):
                                    _background_y_line.scanLine[x+px]  = _patterns16_palette[patterns16_offset]
                                    patterns16_offset += patternXdelta
                            patterns16_offset += patternYdelta
    
                            _background_y_line.lineChanged = True
                    _tile_attribute.changed = False

                tile += 1

    def clearDisplay(self):
        # SDL_Flip(screen)
        self.driver_update_display()

    def updateDisplay(self):
        for y in range(self._yEnd):
            self.single_scan(y)

        self.driver_update_display()

    def single_scan(self, y):
            """ Could split this into the forst '_yScroll' rows, to reduce some computation.
            """

            fineScroll = 0
            xOffset = 0
    
            sprite_scan_y = self._spriteScanLines[y]
            verticalOffset = self._verticalScrollInfo[y]
            v_y = verticalOffset + y
            tile_offset = v_y % (VdpConstants.YTILES*VdpConstants.PATTERNHEIGHT)
            horizontal_info_y = self._horizontalScrollInfo[y]
            background_scan_y = self._backgroundScanLines[tile_offset]
            background_scan_y_line = background_scan_y.scanLine

            # This check helps if not much changes, but not so much during scrolls.
            if (horizontal_info_y.xOffset != self._lastHorizontalScrollInfo[y].xOffset) or (self._verticalScrollInfo[y] != self._lastVerticalScrollInfo[y]) or (sprite_scan_y.lineChanged) or (background_scan_y.lineChanged):

                self._lastHorizontalScrollInfo[y].xOffset = horizontal_info_y.xOffset
                self._lastVerticalScrollInfo[y] = self._verticalScrollInfo[y]

                scan_y_lines = self._scanLines[y].scanLine
                forground_scan_y  = self._forgroundScanLines[tile_offset]
    
                if (y >= self._yScroll):
                    fineScroll = horizontal_info_y.fineScroll
                    xOffset = horizontal_info_y.xOffset
    
                if (self._startX > fineScroll):
                    x = self._startX
                else:
                    x = fineScroll

                # Copy background,  'x' is either [0, 8].  Split into 2 loops to avoid modulus
                # Copying the brackground appears to be the slowest sections of this function.
                x_wrap_around = VdpConstants.SMS_WIDTH - xOffset
                for i in range(x, x_wrap_around):
                    scan_y_lines[i] = background_scan_y_line[xOffset + i] 

                _offset = xOffset - VdpConstants.SMS_WIDTH
                for i in range(max(x, x_wrap_around), VdpConstants.SMS_WIDTH):
                    scan_y_lines[i] = background_scan_y_line[i + _offset] 

                if (sprite_scan_y.numSprites > 0):
                    # If there is a transparent forground on this line
                    if (forground_scan_y.hasPriority):
                        for i in range(sprite_scan_y.numSprites):
                            spriteNumber = sprite_scan_y.sprites[i]

                            x_start = self._sprites[spriteNumber].x
                            x_end   = min(((self._sprites[spriteNumber].x & 0xFFFF)+ self._spriteWidth), VdpConstants.SMS_WIDTH)
                            x_wrap_around = VdpConstants.SMS_WIDTH - xOffset

                            for x in range(x_start, x_wrap_around):
                               if (sprite_scan_y.scanLine[x] != 0) and (forground_scan_y.scanLine[x+xOffset] == False):
                                    scan_y_lines[x] = self._screenPalette[sprite_scan_y.scanLine[x] | 0x10] 

                            for x in range(max(x_start, x_wrap_around), x_end):
                                if (sprite_scan_y.scanLine[x] != 0) and (forground_scan_y.scanLine[x+xOffset - VdpConstants.SMS_WIDTH] == False):
                                    scan_y_lines[x] = self._screenPalette[sprite_scan_y.scanLine[x] | 0x10] 

                    else:
                        for i in range(sprite_scan_y.numSprites):
                            spriteNumber = sprite_scan_y.sprites[i]
                            for x in range(self._sprites[spriteNumber].x, min(((self._sprites[spriteNumber].x + self._spriteWidth) & 0xFFFF, VdpConstants.SMS_WIDTH))):
                                if (sprite_scan_y.scanLine[x] != 0):
                                    scan_y_lines[x] = self._screenPalette[sprite_scan_y.scanLine[x] | 0x10] 

                    for i in range(self._startX):
                        scan_y_lines[i] = 0

            sprite_scan_y.lineChanged = False
            background_scan_y.lineChanged = False
    
    # Draw the background tiles
    def drawPatterns(self):

        pattern = 0
        paletteSelect = 1
    
        for y in range(0, 16*VdpConstants.PATTERNHEIGHT, VdpConstants.PATTERNHEIGHT):
            for x in range(0, VdpConstants.XTILES*VdpConstants.PATTERNWIDTH, VdpConstants.PATTERNWIDTH):
                for py in range(VdpConstants.PATTERNHEIGHT):
                    for px in range(VdpConstants.PATTERNWIDTH):
                        pixel4 = self._patterns4[(pattern << 6) | (py << 3 )| px] | (paletteSelect << 4)
                        self._backgroundScanLines[y+py].scanLine[x+px] = self._screenPalette[pixel4]
                        self._scanLines[y+py].scanLine[x+px] = self._screenPalette[pixel4]
                        self._scanLines[y+py].lineChanged = True
                pattern += 1

    def printSpriteInformation(self):
        print inspect.stack()[0][3]
    """
{
    for (int i = 0 i < VdpConstants.NUMSPRITES i++)
    {
	std::cout << "Sprite " << i
	std::cout << " x: " << (int) self._vdpRAM[self._spriteInformationTableOffset + 128 + i*2]
	std::cout << " y: " << (int) self._vdpRAM[self._spriteInformationTableOffset + i]
	std::cout << " tile: " << (int) self._vdpRAM[self._spriteInformationTableOffset + 129 + i*2]
	std::cout << std::endl
    }
}
    """

    def printNameTable(self):
        print inspect.stack()[0][3]
    """
{
    int offset = 0
    uint8 h, l
    uint16 tmp
    for (int y = 0 y < 28 y++)
    {
        for (int x = 0 x < 32 x++)
        {
            l = self.self._vdpRAM[self._nameTableOffset + offset++]
            h = self.self._vdpRAM[self._nameTableOffset + offset++]
            #l = self._nameTable[offset++]
            #h = self._nameTable[offset++]

            tmp = l + ((h & 0x1) << 8)
	    std::cout << "Name table " << tmp << " "
	    std::cout << (((h >> 4) & 0x1) ? 'F':'B')
	    std::cout << (((h >> 3) & 0x1) ? 'S':'T')
	    std::cout << (((h >> 2) & 0x1) ? 'V':'.')
	    std::cout << (((h >> 1) & 0x1) ? 'H':'.')
	    std::cout << std::endl
        }
    }
  
}
    """

    def printSpriteScanLineInfo(self):
        print inspect.stack()[0][3]
    """
{
    std::cout << "Total Sprites: " << (int) self._totalSprites << std::endl
    std::cout << "End tokens: "
    for (unsigned int i = 0 i < VdpConstants.MAXSPRITES i++)
    {
        if ((self._sprites[i].y - 1) == VdpConstants.LASTSPRITETOKEN)
            std::cout << "(" << i << ")"
    }
    std::cout << std::endl

    for (int y = 0 y < self._yEnd y++)
    {
	std::cout << (self._spriteScanLines[y].lineChanged?"*":" ") << 
                "y: " << y << " self._sprites: " << 
                (int) self._spriteScanLines[y].numSprites
        for (int i = 0 i < self._spriteScanLines[y].numSpritesi++)
            std::cout << " [" << (int) self._spriteScanLines[y].sprites[i] << "]"

	std::cout << std::endl
    }
}
    """

