#include "SDL.h"
#include "vdp.h"
#include "errors.h"
#include "joystick.h"

#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <time.h>
#include <stdexcept>

Vdp::WritePortBE Vdp::writePortBEFunction;
Vdp::WritePortBF Vdp::writePortBFFunction;

Vdp::ReadPort7E Vdp::readPort7EFunction;
Vdp::ReadPort7F Vdp::readPort7FFunction;
Vdp::ReadPortBE Vdp::readPortBEFunction;
Vdp::ReadPortBF Vdp::readPortBFFunction;

Vdp::Vdp(const uint32 &cycles):
        cycles(cycles),
        vsyncInteruptEnable(false),
        hsyncInteruptEnable(false),
        horizontalScrollChanged(false),
        verticalScroll(0),
        lineInterupt(0),
        tileDefinitions(0),
        enableDisplay(false)
{
    assert((vdpRAM = new uint8[RAMSIZE]) != 0);
    assert((cRAM = new uint8[CRAMSIZE]) != 0);
    assert((screenPalette = new uint16[CRAMSIZE]) != 0);
    memset(vdpRAM, 0, RAMSIZE);
    memset(cRAM, 0, CRAMSIZE);
    memset(screenPalette, 0, CRAMSIZE);

    vdpStatusRegister = 0;
    hIntPending = false;
    vIntPending = false;

    addressLatch = false;
    isFullSpeed = false;

    interupt= NULL;

    /* Initialise interupt counters */
    vSync = 0;
    lineIntTime = 0;
    lastVSync = 0;

    currentYpos = 0;
    hCounter = vCounter = 0;
    yEnd = 0;
    displayMode = 0;
    videoChange = false;

    spriteHeight = spriteWidth = 8;
    startX = 0;

    for (unsigned int i = 0; i < NUMVDPREGISTERS;i++)
        vdpRegister[i] = 0;

    displayMode = 0;

    // Allocate memory for pattern tiles
    assert((patternInfo = new PatternInfo[MAXPATTERNS]) != 0);

    assert((patterns4 = new uint8 [MAXPATTERNS*PATTERNSIZE]) != 0);
    for (unsigned int i = 0; i < MAXPATTERNS*PATTERNSIZE;i++)
        patterns4[i] = 0;

    assert((patterns16 = new uint16 *[MAXPALETTES]) != 0);
    for (unsigned int i = 0; i < MAXPALETTES;i++)
        assert((patterns16[i] = new uint16 [MAXPATTERNS*PATTERNSIZE]) != 0);

    for (unsigned int i = 0; i < MAXPATTERNS; i++)
    {
        patternInfo[i].references = 0;
        patternInfo[i].changed = false;
        patternInfo[i].colorCheck = false;
        patternInfo[i].colors = false;
        patternInfo[i].screenVersionCached = false;
    }

    assert((tileAttributes = new TileAttribute[NUMTILEATTRIBUTES]) != 0);
    for (int i = 0; i < NUMTILEATTRIBUTES; i++)
    {
        tileAttributes[i].tileNumber = 0;
        patternInfo[tileAttributes[i].tileNumber].references++;
        // Assuming 'false' is the correct default.
        tileAttributes[i].changed = true;
        tileAttributes[i].priority = false;
        tileAttributes[i].priorityCleared = false;
        tileAttributes[i].paletteSelect = false;
        tileAttributes[i].verticalFlip = false;
        tileAttributes[i].horizontalFlip = false;
    }

    spriteTileShift = 0;
    totalSprites = MAXSPRITES;
    assert((sprites = new Sprite[MAXSPRITES]) != 0);
    for (int i = 0; i < MAXSPRITES; i++)
    {
        sprites[i].y = 1;
        sprites[i].x = 0;
        sprites[i].tileNumber = 0;
        patternInfo[sprites[i].tileNumber].references++;
        sprites[i].changed = false;
    }

    openDisplay();
}

Vdp::~Vdp()
{
    // Quit SDL
    SDL_VideoQuit();

    std::cout << "Destroying Vdp object" << std::endl;
  delete [] vdpRAM;
  delete [] cRAM;
  delete [] screenPalette;
  delete [] patterns4;
}

/******************* Public Port IO functions ********************/

Byte Vdp::readPort7E(void *object)
{
    return ((Vdp *)object)->realReadPort7E();
}

Byte Vdp::readPort7F(void *object)
{
    return ((Vdp *)object)->realReadPort7F();
}

Byte Vdp::readPortBE(void *object)
{
    return ((Vdp *)object)->realReadPortBE();
}

Byte Vdp::readPortBF(void *object)
{
    return ((Vdp *)object)->realReadPortBF();
}

void Vdp::writePortBF(void *object, Byte data)
{
    ((Vdp *)object)->realWritePortBF(data);
}

void Vdp::writePortBF(void *object, const Byte *data, uint16 length)
{
    ((Vdp *)object)->realWritePortBF(data, length);
}

void Vdp::writePortBE(void *object, Byte data)
{
    ((Vdp *)object)->realWritePortBE(data);
}

void Vdp::writePortBE(void *object, const Byte *data, uint16 length)
{
    ((Vdp *)object)->realWritePortBE(data, length);
}

/***************** Private Port IO functions *********************/

Byte Vdp::realReadPort7E()
{
    addressLatch = false;  // Address is unlatched during port read

    vCounter = (cycles-lastVSync)/HSYNCCYCLETIME;
    currentYpos = (cycles-lastVSync)/HSYNCCYCLETIME+1;

      // I can't think of an ellegant solution, so this is as good as it gets
      // for now (fudge factor and all)
    Joystick::setYpos(vCounter+10);
    return vCounter;
}

Byte Vdp::realReadPort7F()
{
    addressLatch = false;  // Address is unlatched during port read

      // I can't think of an ellegant solution, so this is as good as it gets
      // for now (fudge factor and all)
    hCounter = ((Joystick::getXpos() + 0x28)/2 & 0x7F);
    return hCounter;
}

Byte Vdp::realReadPortBE()
{
    uint8 data;
    addressLatch = false;  // Address is unlatched during port read

    data = readBELatch;

    address = (address + 1) & 0x3FFF; // Should be ok without this
    readBELatch = vdpRAM[address]; 

    return data;
}

Byte Vdp::realReadPortBF()
{
    static Byte vdpStatusRegistertmp;
    addressLatch = false;  // Address is unlatched during port read

    vdpStatusRegistertmp = vdpStatusRegister;
    vdpStatusRegister = 0;
    hIntPending = false;
    vIntPending = false;

    return vdpStatusRegistertmp;
}

void Vdp::realWritePortBF(const Byte *data, uint16 length)
{
    for (int i = 0; i < length; i++)
        realWritePortBF(data[i]);
}

void Vdp::realWritePortBF(Byte data)
{
    if (!addressLatch)
    {
        lowaddress = data; 
        addressLatch = true;
    }
    else
    {
          /* Set the register (as specified in the `hiaddress') to the
           * previous value written to this port
           */
        if ((data & REGISTERUPDATEMASK) == REGISTERUPDATEVALUE)
            writeRegister(data & REGISTERMASK, lowaddress);

        address = (lowaddress + ((uint16) data << 8)) & 0x3FFF;
        codeRegister = (lowaddress + ((uint16) data << 8)) >> 14;
        addressLatch = false;

        readBELatch = vdpRAM[address]; 
    }
}

void Vdp::realWritePortBE(const Byte *data, uint16 length)
{
    for (int i = 0; i < length; i++)
        realWritePortBE(data[i]);
}

void Vdp::realWritePortBE(Byte data)
{
    addressLatch = false;  // Address is unlatched during port read

    if (codeRegister == 0x3) // Write to video ram
        setPalette(address, data);
    else 
    {
        if (((address & TILEATTRIBUTESADDRESSMASK) == 
                                tileAttributesAddress) &&
              ((address & TILEATTRIBUTEMASK) < NUMTILEATTRIBUTES))
            updateTileAttributes(address,vdpRAM[address], data);
        else if (((address & SPRITEATTRIBUTESADDRESSMASK) == 
                                spriteAttributesAddress) &&
              ((address & SPRITEATTRIBUTESMASK) < NUMSPRITEATTRIBUTES))
            updateSpriteAttributes(address,vdpRAM[address], data);
        if (address < PATTERNADDRESSLIMIT)
            updatePattern(address, vdpRAM[address], data);

        vdpRAM[address] = data; // Update after function call
        readBELatch = data; 
    }

    address = (address + 1) & 0x3FFF; // Should be ok without this

}

void Vdp::setFullSpeed(bool isFullSpeed)
{
    this->isFullSpeed = isFullSpeed;
}

void Vdp::updateSpriteAttributes(uint16 address, uint8 oldData, uint8 newData)
{
    uint8 spriteNum;

    // Only update if need be
    if (oldData != newData)
    {
        spriteNum = address & SPRITEATTRIBUTESMASK;

        // See if it's an x, or tile number attributes
        if (spriteNum & SPRITEXNMASK)
        {
            spriteNum = (spriteNum >> 1) ^ MAXSPRITES;
            if (address & SPRITETILEMASK) // Changing tile
            {
                patternInfo[sprites[spriteNum].tileNumber].references--;
                sprites[spriteNum].tileNumber = newData | spriteTileShift;
                patternInfo[sprites[spriteNum].tileNumber].references++;
            }
            else // Changing x position
            {
                sprites[spriteNum].x = newData;
            }

            sprites[spriteNum].changed = true;
            videoChange = true;

        }
        else if (spriteNum < MAXSPRITES) // Updating y attribute
        {
            // The number of sprites has changed, do some work updating
            // the appropriate scanlines

            // If inserting a new token earlier then previous, remove tiles
            if (newData == LASTSPRITETOKEN)
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
            else if (((sprites[spriteNum].y-1) == LASTSPRITETOKEN) &&
                    (spriteNum == totalSprites))
            {

                totalSprites++;
                while((totalSprites < MAXSPRITES) &&
                      ((sprites[totalSprites].y -1) != LASTSPRITETOKEN))
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

            sprites[spriteNum].changed = true;
            videoChange = true;
        }

        // SpriteNum at this point may be invalid if using `unused space'
    }
}

void Vdp::drawSprites(void)
{
    /* Chech for any sprite alterations */
    for (int i = 0; i < totalSprites; i++)
    {
        if (patternInfo[sprites[i].tileNumber].changed)
            sprites[i].changed = true;

        if(sprites[i].changed)
        {
            for (unsigned int y = sprites[i].y; 
                  (y < (unsigned) sprites[i].y + spriteHeight) && 
                  (y < SMS_HEIGHT); y++)
            {
                spriteScanLines[y].lineChanged = true;
            }

            sprites[i].changed = false; // Sprite changes noted
        }
    }

    for (int y = 0; y < yEnd; y++)
    {

        // Only need to draw lines that have changed
        if (spriteScanLines[y].lineChanged)
        {

            memset(spriteScanLines[y].scanLine, 0, SMS_WIDTH*sizeof(uint8));

            uint8 spriteNum;
            uint16 tileAddr;
            uint8 tiley;

            for (int i = 0; (i < spriteScanLines[y].numSprites) &&
                            (i < MAXSPRITESPERSCANLINE); i++)
            {
                spriteNum = spriteScanLines[y].sprites[i];

                /* FIXME, loosing motivation, this is better but still
                   not quite right
                   */
                if (sprites[spriteNum].y > SMS_HEIGHT)
                    tiley = y - sprites[spriteNum].y + SMS_HEIGHT;
                else
                    tiley = y - sprites[spriteNum].y;

                tileAddr = (sprites[spriteNum].tileNumber << 6) |
                           ((tiley) << 3);
                for (unsigned int x = 0; x < spriteWidth; x++)
                {
                      // If the line is clear
                    if(((sprites[spriteNum].x + x) < SMS_WIDTH) && 
                      (spriteScanLines[y].scanLine[sprites[spriteNum].x+x]==0))
                        spriteScanLines[y].scanLine[sprites[spriteNum].x+x] = 
                               patterns4[tileAddr | x];

                }
            }
        }
    }
}

void Vdp::printSpriteScanLineInfo(void)
{
    std::cout << "Total Sprites: " << (int) totalSprites << std::endl;
    std::cout << "End tokens: ";
    for (unsigned int i = 0; i < MAXSPRITES; i++)
    {
        if ((sprites[i].y - 1) == LASTSPRITETOKEN)
            std::cout << "(" << i << ")";
    }
    std::cout << std::endl;

    for (int y = 0; y < yEnd; y++)
    {
	std::cout << (spriteScanLines[y].lineChanged?"*":" ") << 
                "y: " << y << " sprites: " << 
                (int) spriteScanLines[y].numSprites;
        for (int i = 0; i < spriteScanLines[y].numSprites;i++)
            std::cout << " [" << (int) spriteScanLines[y].sprites[i] << "]";

	std::cout << std::endl;
    }
}

/* Not the most efficient routine, but it should do the job
 */
void Vdp::removeSpriteFromScanlines(uint8 scanlineNumber, uint8 spriteNumber)
{
    uint8 shift = 0;

    if (scanlineNumber < yEnd)
    {
        uint8 numSprites = spriteScanLines[scanlineNumber].numSprites;

        for (int i = 0; i < numSprites - shift; i++)
        {
            if (spriteScanLines[scanlineNumber].sprites[i] == spriteNumber) 
            {
                shift++;
                spriteScanLines[scanlineNumber].numSprites--;
                spriteScanLines[scanlineNumber].lineChanged = true;
            }

            spriteScanLines[scanlineNumber].sprites[i] = 
                    spriteScanLines[scanlineNumber].sprites[i + shift];
        }
    }
}

/* Not the most efficient routine, but it should do the job
 */
void Vdp::addSpriteToScanlines(uint8 scanlineNumber, uint8 spriteNumber)
{
    if (scanlineNumber < yEnd)
    {
        assert(spriteScanLines[scanlineNumber].numSprites != MAXSPRITES);

        for (int i = spriteScanLines[scanlineNumber].numSprites++; i > 0; i--)
        {
            if (spriteScanLines[scanlineNumber].sprites[i-1] < spriteNumber) 
            {
                spriteScanLines[scanlineNumber].lineChanged = true;
                spriteScanLines[scanlineNumber].sprites[i] = spriteNumber;
                return;
            }

            spriteScanLines[scanlineNumber].sprites[i] = 
                    spriteScanLines[scanlineNumber].sprites[i - 1];
        }

        spriteScanLines[scanlineNumber].sprites[0] = spriteNumber;
        spriteScanLines[scanlineNumber].lineChanged = true;
    }
}

// Update a more convenient representation of the patterns
void Vdp::updatePattern(uint16 address, uint8 oldData, uint8 data)
{
    uint16 index;
    uint8 mask;
    uint8 change;

    change = oldData ^ data; // Flip only the bits that have changed
    if (change != 0)
    {
        index = (address & 0x3FFC) << 1; // Base index (pattern + row)

        mask = 1 << (address & 0x3);  // Bit position to flip

        // Only update if the data has changed
        // From right to left
        int x = 7;
        while (change != 0)
        {
            // Flip the bit position if required
            if (change & 0x1)
                patterns4[index + x] ^= mask;

            x--;
            change = change >> 1;
        }

        patternInfo[index >> 6].changed = true;
        patternInfo[index >> 6].colorCheck = false;
        if (patternInfo[index >> 6].references)
            videoChange = true;

        patternInfo[index >> 6].screenVersionCached = false;
    }
}

// `Cache' a screen palette version of the pattern
void Vdp::updateScreenPattern(uint16 patternNumber)
{
    uint8 pixel4;
    uint16 index = patternNumber << 6;

    for (unsigned int py = 0; py < PATTERNHEIGHT; py++)
    {
        for (unsigned int px = 0; px < PATTERNWIDTH; px++)
        {
            pixel4 = patterns4[index]; 

            patterns16[0][index] = screenPalette[pixel4];
            patterns16[1][index++] = screenPalette[pixel4 | (1 << 4)];
        }
    }
    patternInfo[patternNumber].screenVersionCached = true;
}

/* Update the horizontal scroll offsets for each scanline */
void Vdp::updateHorizontalScrollInfo(void)
{
    uint8 columnOffset;
    uint8 fineScroll;
    uint8 xOffset;

    columnOffset = (0x20 - (horizontalScroll >> 3)) & 0x1F;
    fineScroll = horizontalScroll & 0x7;
    xOffset = columnOffset*PATTERNWIDTH - fineScroll;

    for (int y = currentYpos; y < yEnd; y++)
    {
        horizontalScrollInfo[y].columnOffset = columnOffset;
        horizontalScrollInfo[y].fineScroll = fineScroll;
        horizontalScrollInfo[y].xOffset = xOffset;
        horizontalScrollInfo[y].xOffset = xOffset;
    }
}

/* Update the vertical scroll offsets for each scanline */
void Vdp::updateVerticalScrollInfo(void)
{
    for (int y = currentYpos; y < yEnd; y++)
        verticalScrollInfo[y] = verticalScroll;
}

void Vdp::updateTileAttributes(uint16 address, uint8 oldData, uint8 data)
{

    // Only update if altered
    if (oldData != data)
    {
        int tile = (address & TILEATTRIBUTESTILEMASK) >> TILESHIFT;

        patternInfo[tileAttributes[tile].tileNumber].references--;

        // Alteration of the high byte 
        if (address & TILEATTRIBUTESHMASK)
        {
            if (tileAttributes[tile].priority)
                if ((data >> TILEPRIORITYSHIFT) == 0)
                    tileAttributes[tile].priorityCleared = true;

            tileAttributes[tile].priority = data >> TILEPRIORITYSHIFT;
            tileAttributes[tile].paletteSelect = 
                        (data >> TILEPALETTESHIFT) & 0x1;
            tileAttributes[tile].verticalFlip = 
                        (data >> TILEVFLIPSHIFT) & 0x1;
            tileAttributes[tile].horizontalFlip = 
                        (data >> TILEHFLIPSHIFT) & 0x1;
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
        patternInfo[tileAttributes[tile].tileNumber].references++;

        tileAttributes[tile].changed = true;
        videoChange = true;
    }
}

void Vdp::writeRegister(Byte registerNumber, Byte data)
{
    static unsigned int lastSpriteAttributesAddress;
    vdpRegister[registerNumber] = data; // Update register data

    /* Only need to react immediately to some register changes */
    switch(registerNumber)
    {
        case 0:
        case 1:
            updateModeControl();
            break;

        case 2:
            tileAttributesAddress = (data & 0xE) << 10;
            nameTable = &vdpRAM[tileAttributesAddress];
            break;

        case 5:
            spriteAttributesAddress = ((data & 0x7E) << 7);
            if (lastSpriteAttributesAddress != spriteAttributesAddress)
                lastSpriteAttributesAddress = spriteAttributesAddress;
            spriteInformationTable = &vdpRAM[spriteAttributesAddress];
            break;

        case 6:
            tileDefinitions = &vdpRAM[(data & 0x4) << 11];
            // Probably should do more when this changes, as all the 
            // sprite tile numbers should change... maybe later
            spriteTileShift = (data & 0x4) << 6;
            break;

        case 7:
	    std::cout << "Using border color: " << std::hex << (int) data << std::endl;
            borderColor = data & 0xf;
            break;

        case 8:
            horizontalScroll = data;
            updateHorizontalScrollInfo();
            videoChange = true;
            break;

        case 9:
            verticalScroll = data;
            updateVerticalScrollInfo();
            videoChange = true;
            break;

        case 10:
            lineInterupt = data;
            break;

        default:
            ;
    }
}

void Vdp::updateModeControl(void)
{

      // Set first scrolling line
    yScroll = (vdpRegister[MODE_CONTROL_NO_1] & VDP0DISHSCROLL) ?  16:0;

      // Set last scrolling position
    xScroll = (vdpRegister[MODE_CONTROL_NO_1] & VDP0DISHSCROLL) ?  
              192:SMS_WIDTH;

    vsyncInteruptEnable = (vdpRegister[MODE_CONTROL_NO_2] & VDP1VSYNC) ?
                          true:false;

    hsyncInteruptEnable = (vdpRegister[MODE_CONTROL_NO_1] & VDP0LINEINTENABLE) ?
                          true:false;

    startX = (vdpRegister[MODE_CONTROL_NO_1] & VDP0COL0OVERSCAN) ?
                          PATTERNWIDTH:0;

    if (vdpRegister[MODE_CONTROL_NO_1] & VDP0SHIFTSPRITES)
        errors::warning("Sprite shift not implemented");

    if (vdpRegister[MODE_CONTROL_NO_1] & VDP0NOSYNC)
        errors::warning("No sync, not implemented");

    if (vdpRegister[MODE_CONTROL_NO_2] & VDP1ENABLEDISPLAY)
        enableDisplay = true;
    else
        enableDisplay = false;

    if (vdpRegister[MODE_CONTROL_NO_2] & VDP1BIGSPRITES)
        spriteHeight = 16;
    else
        spriteHeight = 8;

    if (vdpRegister[MODE_CONTROL_NO_2] & VDP1DOUBLESPRITES)
        errors::warning("Double sprites not implemented");

    displayMode = (vdpRegister[MODE_CONTROL_NO_1] & VDP0M4) ? 8:0 |
                  (vdpRegister[MODE_CONTROL_NO_2] & VDP1M3) ? 4:0 |
                  (vdpRegister[MODE_CONTROL_NO_1] & VDP0M2) ? 2:0 |
                  (vdpRegister[MODE_CONTROL_NO_2] & VDP1M1) ? 1:0;

    if (displayMode == 0x8)
    {
        yEnd = 192;
    }
    else
    {
        yEnd = 0;
        errors::warning("Mode not supported");
    }

}

void Vdp::setInterupt(Interupt *interupt)
{
    this->interupt = interupt;
}

void Vdp::setCycle(uint32 cycle)
{
    if (cycle >= getNextInterupt(cycle))
    {
        if (pollInterupts(cycle) == true)
            interupt->interupt();
    }
}

unsigned int Vdp::getNextInterupt(uint32 cycle)
{
    // Check conditions to see if a line interupt is next 
    if ((lineIntTime < VFRAMETIME) &&
        (vSync < lineIntTime)) 
    {
        // Next interupt will be a line interupt
        return lastVSync + lineIntTime;
    }
    else if (vSync < VFRAMETIME)  // Check for a frame interupt
    {
        return lastVSync + VFRAMETIME;
    }
    else
        return lastVSync + VSYNCCYCLETIME;
}

bool Vdp::pollInterupts(uint32 cycle)
{
    static unsigned int lineInteruptLatch;
    static bool frameUpdated;
    static bool update = false;
    static unsigned int lastClock;

    vSync = cycle - lastVSync;

    if ((lineIntTime < VFRAMETIME) &&
        (vSync >= (lineIntTime)))
    {
        currentYpos = (cycles-lastVSync)/HSYNCCYCLETIME+1;

        lineInteruptLatch = lineInterupt + 1;

        lineIntTime += lineInteruptLatch * HSYNCCYCLETIME;

        hIntPending = true;
    }

    if (!frameUpdated && (vSync >= VFRAMETIME))
    {
        if (enableDisplay == true)
        {
            if (update == true)
            {
                updateDisplay();
                update = false;
            }
        }
        else 
            clearDisplay();

        frameUpdated = true;
        vCounter = 0xD5;
        currentYpos = yEnd;

        vIntPending = true;
        vdpStatusRegister |= VSYNCFLAG;
    }

    if (vSync >= VSYNCCYCLETIME)
    {
        lastVSync = cycle;
        vSync = 0;
        currentYpos = 0;
        vCounter = 0x00;
        updateHorizontalScrollInfo();
        updateVerticalScrollInfo();

        lineInteruptLatch = lineInterupt;

        lineIntTime = lineInteruptLatch * HSYNCCYCLETIME;

        if (videoChange == true)
        {
            drawBuffer();
            update = true;
            videoChange = false;
        }

        if (!isFullSpeed)
        {
            while ((clock() - lastClock) < CLOCKS_PER_SEC/60)
                ;
            lastClock = clock();
        }

        frameUpdated = false;
    }

    if ((vsyncInteruptEnable && vIntPending) ||
        (hsyncInteruptEnable && hIntPending))
    {
        return true;
    }
    else
        return false;
}

void Vdp::openDisplay(void)
{
    if (SDL_Init(SDL_INIT_VIDEO) != 0)
    {
        fprintf(stderr,"Unable to initialize SDL: %s\n", SDL_GetError());
        exit (1);
    }

    atexit(SDL_Quit);
    screen = SDL_SetVideoMode(SMS_WIDTH, SMS_HEIGHT, SMS_COLOR_DEPTH,
                              SDL_HWSURFACE/*|SDL_FULLSCREEN*/);


    if (screen == NULL)
    {
       fprintf(stderr,"Unable to set video mode: %s\n", SDL_GetError());
        exit (1);
    }

    /* If the screen needs to be locked, blit the image otherwise draw to the
     * screen pixels directly */
    if (SDL_MUSTLOCK(screen))
    {
        blitImage = true;
        image = SDL_CreateRGBSurface(SDL_HWSURFACE, SMS_WIDTH, SMS_HEIGHT,
                        SMS_COLOR_DEPTH, 0, 0, 0, 0);

    }
    else
    {
        blitImage = false;
        /* Fastest display method so far, using framebuffer pixel pointer */
        /* Probably not as robust and/or portable as could be */
        image = SDL_CreateRGBSurfaceFrom(screen->pixels,
                        SMS_WIDTH, SMS_HEIGHT,
                        SMS_COLOR_DEPTH, screen->pitch,
                        0, 0, 0, 0);
    }

    assert(SDL_MUSTLOCK(image) == 0);

    raw_pixels = (Uint16 *)image->pixels;

    // Initialise the scanlines
    assert((scanLines = new ScanLine[SMS_HEIGHT]) != 0);
    for (unsigned int i = 0; i < SMS_HEIGHT; i++)
    {
        scanLines[i].scanLine = 
                (uint16 *)&((uint8 *)raw_pixels)[i*image->pitch];
        scanLines[i].lineChanged = true;
    }

    // Buffer for all background tiles, allocated in an interlaced fashion to
    // allow tile scrolling.  Oops, scrolling doesn't work like that, but it
    // doesn't matter anyhoo.
    backgroundBuffers = new uint16*[PATTERNHEIGHT];
    for (unsigned int i = 0; i < PATTERNHEIGHT; i++)
    {
        backgroundBuffers[i] = new uint16[PATTERNWIDTH*XTILES*YTILES];
        assert(backgroundBuffers != 0);
    }

    // Scanlines for the background image
    assert((backgroundScanLines = new ScanLine[YTILES*PATTERNHEIGHT]) != 0);
    for (unsigned int i = 0; i < YTILES*PATTERNHEIGHT; i++)
    {
        backgroundScanLines[i].scanLine = 
                &backgroundBuffers[i % PATTERNHEIGHT]
                                  [(i/PATTERNHEIGHT)*XTILES*PATTERNWIDTH];
        backgroundScanLines[i].lineChanged = true;
    }

    // Buffer for all forground tiles, allocated in an interlaced fashion to
    // allow tile scrolling
    forgroundBuffers = new bool*[PATTERNHEIGHT];
    for (unsigned int i = 0; i < PATTERNHEIGHT; i++)
    {
        forgroundBuffers[i] = new bool[PATTERNWIDTH*XTILES*YTILES];
        assert(forgroundBuffers != 0);
    }

    // Scanlines for the forground image
    assert((forgroundScanLines = new PriorityScanLine[YTILES*PATTERNHEIGHT]) 
                    != 0);
    for (unsigned int i = 0; i < YTILES*PATTERNHEIGHT; i++)
    {
        forgroundScanLines[i].scanLine = 
                &forgroundBuffers[i % PATTERNHEIGHT]
                                  [(i/PATTERNHEIGHT)*XTILES*PATTERNWIDTH];
        forgroundScanLines[i].hasPriority = false;
    }

    // Initialise the Sprite scanlines
    assert((spriteScanLines = new SpriteScanLine[SMS_HEIGHT]) != 0);
    for (unsigned int i = 0; i < SMS_HEIGHT; i++)
    {
        assert((spriteScanLines[i].scanLine = new uint8[SMS_WIDTH]) != 0);
        spriteScanLines[i].lineChanged = true;
        spriteScanLines[i].numSprites = 0;

        assert((spriteScanLines[i].sprites = new uint8[MAXSPRITES]) != 0);
        for (int j =0; j < MAXSPRITES; j++)
            spriteScanLines[i].sprites[j] = NOSPRITE;
    }

    lastHorizontalScrollInfo = new HorizontalScroll[SMS_HEIGHT];
    horizontalScrollInfo = new HorizontalScroll[SMS_HEIGHT];
    verticalScrollInfo = new uint8 [SMS_HEIGHT];
    lastVerticalScrollInfo = new uint8 [SMS_HEIGHT];
}

/* Translate colors to screen color depth when the palette is altered
 */
void Vdp::setPalette(uint16 addr, uint8 data)
{
    uint16 color;
    uint8 r, g, b;

    addr = addr % CRAMSIZE;

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

        for (unsigned int i = 0; i < MAXPATTERNS; i++)
        {
            if (patternInfo[i].colorCheck == false)
                checkPatternColors(i);

            if (patternInfo[i].colors & (1<<(addr & 0xF)))
            {
                patternInfo[i].changed = true;
                patternInfo[i].screenVersionCached = false;
            }
        }
        videoChange = true;
    }
}

// This changes 8-bit r, g, b values into a 16-bit encoded color
uint16 Vdp::setColor(uint8 r, uint8 g, uint8 b)
{
    uint16 color;

    color = ((((int) 0x1F*r)/0xFF) << 11) |
            ((((int) 0x3F*g)/0xFF) << 5) |
            (((0x1F*b)/0xFF));

    return color;
}

void Vdp::checkPatternColors(uint16 pattern)
{
    patternInfo[pattern].colors = 0; 
    for (uint8 i = 0; i < 64;i++)
        patternInfo[pattern].colors |= 1 << patterns4[pattern << 6 | i]; 

    patternInfo[pattern].colorCheck = true;
}

void Vdp::drawBuffer(void)
{
    drawBackground();
    drawSprites();
//printSpriteScanLineInfo();
//    drawPatterns(); // For debuging purposes

    // Reset any change indicators for the patterns
    for (unsigned int i = 0; i < MAXPATTERNS; i++)
        patternInfo[i].changed = false;
}

void Vdp::drawDisplay(void)
{
    drawBuffer();
    updateDisplay();
}

/* Draw the background tiles */
void Vdp::drawBackground(void)
{
    int tile = 0;
    bool priority;
    uint16 *patternPtr;
    uint8 *pattern4Ptr;
    int8 patternYdelta, patternXdelta;

    for (unsigned int y = 0; y < YTILES*PATTERNHEIGHT; y++)
        forgroundScanLines[y].hasPriority = false;

    for (unsigned int y = 0; y < YTILES*PATTERNHEIGHT; y += PATTERNHEIGHT)
    {
        for (unsigned int x = 0; x < XTILES*PATTERNWIDTH; x += PATTERNWIDTH)
        {

            if ((forgroundScanLines[y].hasPriority == false) &&
                (tileAttributes[tile].priority == true))
            {
                for (unsigned int py = 0; py < PATTERNHEIGHT; py++)
                    forgroundScanLines[y+py].hasPriority = true;
            }

            if(tileAttributes[tile].changed ||
               patternInfo[tileAttributes[tile].tileNumber].changed)
            {
                if(!patternInfo[tileAttributes[tile].tileNumber].
                       screenVersionCached)
                    updateScreenPattern(tileAttributes[tile].tileNumber);

                priority = tileAttributes[tile].priority;

                patternPtr = &patterns16[tileAttributes[tile].paletteSelect]
                                [(tileAttributes[tile].tileNumber << 6)];
                patternYdelta = 0;
                patternXdelta = 1;

                if (tileAttributes[tile].horizontalFlip != 0)
                {
                    patternPtr += PATTERNWIDTH-1;
                    patternXdelta = -1;
                    patternYdelta = PATTERNWIDTH * 2;
                }

                if (tileAttributes[tile].verticalFlip != 0) 
                {
                    patternPtr += ((PATTERNHEIGHT-1) << 3);
                    patternYdelta -= 2 * PATTERNWIDTH;
                }

                if (priority)
                {
                    pattern4Ptr = &patterns4[(tileAttributes[tile].tileNumber 
                                            << 6)];

                    if (tileAttributes[tile].horizontalFlip != 0)
                        pattern4Ptr += PATTERNWIDTH-1;

                    if (tileAttributes[tile].verticalFlip != 0) 
                        pattern4Ptr += ((PATTERNHEIGHT-1) << 3);

                    for (unsigned int py = 0; py < PATTERNHEIGHT; py++)
                    {
                        for (unsigned int px = 0; px < PATTERNWIDTH; px++)
                        {

                            backgroundScanLines[y+py].scanLine[x+px] =
                                    *patternPtr;

                            // Indicate a forground pixel if the value is
                            // non-zero and it is set as a forground pixel...
                            // well tile
                            forgroundScanLines[y+py].scanLine[x+px] = false;

                            if (priority && (*pattern4Ptr != 0x0))
                            {
                                forgroundScanLines[y+py].scanLine[x+px] = true;
                            }

                            patternPtr += patternXdelta;
                            pattern4Ptr += patternXdelta;
                        }
                        patternPtr += patternYdelta;
                        pattern4Ptr += patternYdelta;

                        backgroundScanLines[y+py].lineChanged = true;
                    }
                }
                else
                {
                    if (tileAttributes[tile].priorityCleared)
                    {
                        for (unsigned int py = 0; py < PATTERNHEIGHT; py++)
                            for (unsigned int px = 0; px < PATTERNWIDTH; px++)
                                forgroundScanLines[y+py].scanLine[x+px] =
                                false;
                        tileAttributes[tile].priorityCleared = false;
                    }

                    for (unsigned int py = 0; py < PATTERNHEIGHT; py++)
                    {

                        if (patternXdelta == 1)
                        {
                            memcpy(&backgroundScanLines[y+py].scanLine[x],
                                   patternPtr, PATTERNWIDTH*sizeof(uint16));
                            patternPtr += PATTERNWIDTH;
                        }
                        else
                        {
                            for (unsigned int px = 0; px < PATTERNWIDTH; px++)
                            {
                                backgroundScanLines[y+py].scanLine[x+px] =
                                        *patternPtr;

                                patternPtr += patternXdelta;
                            }
                        }
                        patternPtr += patternYdelta;

                        backgroundScanLines[y+py].lineChanged = true;
                    }
                }
                tileAttributes[tile].changed = false;
            }
            tile++;
        }
    }
}

/* Draw the background tiles */
void Vdp::drawPatterns(void)
{
    int pattern = 0;
    int pixel4;
    int paletteSelect = 1;

    for (unsigned int y = 0; y < 16*PATTERNHEIGHT; y += PATTERNHEIGHT)
    {
        for (unsigned int x = 0; x < XTILES*PATTERNWIDTH; x += PATTERNWIDTH)
        {

            for (unsigned int py = 0; py < PATTERNHEIGHT; py++)
            {
                for (unsigned int px = 0; px < PATTERNWIDTH; px++)
                {
                        pixel4 =
                            patterns4[(pattern << 6) | (py << 3 )| px] |
                                         (paletteSelect << 4);
                        backgroundScanLines[y+py].scanLine[x+px] =
                             screenPalette[pixel4];

                }
            }
            pattern++;
        }
    }
}

void Vdp::printSpriteInformation(void)
{
    for (int i = 0; i < NUMSPRITES; i++)
    {
	std::cout << "Sprite " << i;
	std::cout << " x: " << (int) spriteInformationTable[128 + i*2];
	std::cout << " y: " << (int) spriteInformationTable[i];
	std::cout << " tile: " << (int) spriteInformationTable[129 + i*2];
	std::cout << std::endl;
    }
}

void Vdp::printNameTable(void)
{
    int offset = 0;
    uint8 h, l;
    uint16 tmp;
    for (int y = 0; y < 28; y++)
    {
        for (int x = 0; x < 32; x++)
        {
            l = nameTable[offset++];
            h = nameTable[offset++];

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

void Vdp::clearDisplay(void)
{
//    SDL_FillRect(image, NULL, 0);
    SDL_Flip(screen);
}

void Vdp::updateDisplay(void)
{
    uint8 fineScroll = 0;
    uint16 firstBlock;
    uint16 secondBlock;
    int16 xOffset = 0;
    uint16 *src, *dst;
    unsigned int x;
    uint8 verticalOffset;

    for (int y = 0; y < yEnd; y++)
    {
        verticalOffset = verticalScrollInfo[y];
        if ((horizontalScrollInfo[y].xOffset !=
             lastHorizontalScrollInfo[y].xOffset)||
            (verticalScrollInfo[y] != lastVerticalScrollInfo[y])||
             (spriteScanLines[y].lineChanged)||
           (backgroundScanLines[(y+verticalOffset)%(YTILES*PATTERNHEIGHT)].
                     lineChanged))
        {
            lastHorizontalScrollInfo[y].xOffset = 
                    horizontalScrollInfo[y].xOffset;
            lastVerticalScrollInfo[y] = verticalScrollInfo[y];

            if (y >= yScroll)
            {
                fineScroll = horizontalScrollInfo[y].fineScroll;
                xOffset = horizontalScrollInfo[y].xOffset;
            }

            if (startX > fineScroll)
                x = startX;
            else 
                x = fineScroll;

            verticalOffset = verticalScrollInfo[y];

            /* Copy the source to the destination */
            dst = &(scanLines[y].scanLine[x]);
            src = &(backgroundScanLines[(y + verticalOffset) % 
                   (YTILES*PATTERNHEIGHT)].scanLine[(x+xOffset) % SMS_WIDTH]); 
            firstBlock = SMS_WIDTH - ((x+xOffset) % SMS_WIDTH);
            if (firstBlock > (SMS_WIDTH - x))
                firstBlock = SMS_WIDTH - x;

            if (firstBlock != 0)
                memcpy(dst, src, firstBlock*sizeof(uint16));

            dst = &(scanLines[y].scanLine[x + firstBlock]);
            src = &(backgroundScanLines[(y + verticalOffset) %
                            (YTILES * PATTERNHEIGHT)].scanLine[0]); 
            secondBlock = SMS_WIDTH - firstBlock - x;

            if (secondBlock != 0)
                memcpy(dst, src, secondBlock*sizeof(uint16));

            if (spriteScanLines[y].numSprites > 0)
            {
                  // If there is a transparent forground on this line
                if (forgroundScanLines[(y+verticalOffset) % 
                 (YTILES*PATTERNHEIGHT)].hasPriority)
                {
                for (int i = 0; i < spriteScanLines[y].numSprites; i++)
                {
                    uint8 spriteNumber = spriteScanLines[y].sprites[i];
                    for (x = sprites[spriteNumber].x; 
                         (x < (unsigned) sprites[spriteNumber].x +
                          spriteWidth) && (x < SMS_WIDTH);
                         x++)
                    {
                        if ((spriteScanLines[y].scanLine[x] != 0) &&
                            (forgroundScanLines[(y+verticalOffset) % 
                            (YTILES*PATTERNHEIGHT)].scanLine[(x+xOffset) % 
                            SMS_WIDTH] == false))
                        {
                            scanLines[y].scanLine[x] = 
                               screenPalette[spriteScanLines[y].scanLine[x] |
                               0x10]; 
                        }
                    }

                }
                }
                else{
                for (int i = 0; i < spriteScanLines[y].numSprites; i++)
                {
                    uint8 spriteNumber = spriteScanLines[y].sprites[i];
                    for (x = sprites[spriteNumber].x; 
                         (x < (unsigned) sprites[spriteNumber].x +
                         spriteWidth) && (x < SMS_WIDTH);
                         x++)
                    {
                        if (spriteScanLines[y].scanLine[x] != 0)
                        {
                            scanLines[y].scanLine[x] = 
                               screenPalette[spriteScanLines[y].scanLine[x] |
                               0x10]; 
                        }
                    }

                }
                }
                memset(&scanLines[y].scanLine[0], 0, startX*sizeof(uint16));
            }
        }
        spriteScanLines[y].lineChanged = false;
        backgroundScanLines[(y+verticalOffset)%(YTILES*PATTERNHEIGHT)].
                     lineChanged = false;
    }

    if (blitImage)
        SDL_BlitSurface(image, NULL, screen, NULL);
    SDL_Flip(screen);
}
