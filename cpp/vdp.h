#ifndef VDP_H
#define VDP_H

#include "SDL.h"
#include "types.h"
#include "interupt.h"
#include "interuptor.h"
#include "readInterface.h"
#include "writeInterface.h"

class Vdp:public Interuptor
{
    public:
        Vdp(const uint32 &cycles);
        virtual ~Vdp();
        static Byte readPort7E(void *object);
        static Byte readPort7F(void *object);
        static Byte readPortBE(void *object);
        static Byte readPortBF(void *object);
        class ReadPort7E : public ReadInterface
        {
                virtual Byte read(void *arg){return readPort7E(arg);};
        };
        static ReadPort7E readPort7EFunction;
        class ReadPort7F : public ReadInterface
        {
                virtual Byte read(void *arg){return readPort7F(arg);};
        };
        static ReadPort7F readPort7FFunction;
        class ReadPortBE : public ReadInterface
        {
                virtual Byte read(void *arg){return readPortBE(arg);};
        };
        static ReadPortBE readPortBEFunction;
        class ReadPortBF : public ReadInterface
        {
                virtual Byte read(void *arg){return readPortBF(arg);};
        };
        static ReadPortBF readPortBFFunction;
        static void writePortBF(void *object, Byte data);
        static void writePortBE(void *object, Byte data);
        static void writePortBF(void *object, const Byte *data, uint16 length);
        static void writePortBE(void *object, const Byte *data, uint16 length);
        class WritePortBE : public WriteInterface
        {
                virtual void write(void *object, const Byte data){writePortBE(object, data);};
                virtual void write(void *object, const Byte *data, uint16 length){writePortBE(object, data, length);};
        };
        static WritePortBE writePortBEFunction;
        class WritePortBF : public WriteInterface
        {
                virtual void write(void *object, const Byte data){writePortBF(object, data);};
                virtual void write(void *object, const Byte *data, uint16 length){writePortBF(object, data, length);};
        };
        static WritePortBF writePortBFFunction;

        void writeRegister(Byte vdpRegister, Byte data);
        unsigned int getNextInterupt(uint32 cycle);
        bool pollInterupts(uint32 cycle);
        void setCycle(uint32 cycle);
        void setInterupt(Interupt *interupt);
        void setFullSpeed(bool isFullSpeed);

    private:
        void openDisplay(void);
        void updateDisplay(void);
        void clearDisplay(void);
        void updateModeControl(void);
        void setPalette(uint16 addr, uint8 data);
        uint16 setColor(uint8 r, uint8 g, uint8 b);
        void checkPatternColors(uint16 pattern);
        void drawBuffer(void);
        void drawDisplay(void);
        void drawBackground(void);
        void drawSprites(void);
        void drawPatterns(void);
        void updatePattern(uint16 addr, uint8 oldData, uint8 newData);
        void updateScreenPattern(uint16 patternNumber);
        void updateHorizontalScrollInfo(void);
        void updateVerticalScrollInfo(void);
        void updateTileAttributes(uint16 addr, uint8 oldData, uint8 newData);
        void updateSpriteAttributes(uint16 addr, uint8 oldData, uint8 newData);

        void printNameTable(void);
        void printSpriteInformation(void);
        Byte realReadPort7E(void);
        Byte realReadPort7F(void);
        Byte realReadPortBE(void);
        Byte realReadPortBF(void);
        void realWritePortBF(Byte data);
        void realWritePortBE(Byte data);
        void realWritePortBF(const Byte *data, uint16 length);
        void realWritePortBE(const Byte *data, uint16 length);
        static const unsigned long RAMSIZE  = 0x4000;
        static const unsigned long CRAMSIZE  = 0x20;
        // 3Mhz CPU, 50Hz refresh ~= 60000 ticks
        static const unsigned int VSYNCCYCLETIME = 65232;
        static const unsigned int BLANKTIME      = (VSYNCCYCLETIME * 72)/262;
        static const unsigned int VFRAMETIME     = (VSYNCCYCLETIME * 192)/262;
        static const unsigned int HSYNCCYCLETIME = 216;
        uint16 vSync;
        uint32 lastVSync;
        bool hIntPending, vIntPending;
        unsigned int lineIntTime;
        uint8 vCounter, hCounter;
        const uint32 &cycles;

        bool blitImage;

        Interupt *interupt;

        static const unsigned int REGISTERMASK  = 0x0F;
        static const unsigned int REGISTERUPDATEMASK  = 0xF0;
        static const unsigned int REGISTERUPDATEVALUE = 0x80;
        static const unsigned int NUMVDPREGISTERS = 16;

        /* VDP status register */
        static const unsigned char VSYNCFLAG = 0x80;

        /* VDP register 0 */
        static const uint8 MODE_CONTROL_NO_1 = 0x0;
        static const unsigned int VDP0DISVSCROLL    = 0x80;
        static const unsigned int VDP0DISHSCROLL    = 0x40;
        static const unsigned int VDP0COL0OVERSCAN  = 0x20;
        static const unsigned int VDP0LINEINTENABLE = 0x10;
        static const unsigned int VDP0SHIFTSPRITES  = 0x08;
        static const unsigned int VDP0M4            = 0x04;
        static const unsigned int VDP0M2            = 0x02;
        static const unsigned int VDP0NOSYNC        = 0x01;

        /* VDP register 1 */
        static const uint8 MODE_CONTROL_NO_2 = 0x1;
        static const unsigned int VDP1BIT7          = 0x80;
        static const unsigned int VDP1ENABLEDISPLAY = 0x40;
        static const unsigned int VDP1VSYNC         = 0x20;
        static const unsigned int VDP1M1            = 0x10;
        static const unsigned int VDP1M3            = 0x08;
        static const unsigned int VDP1BIGSPRITES    = 0x02;
        static const unsigned int VDP1DOUBLESPRITES = 0x01;

        bool vsyncInteruptEnable;
        bool hsyncInteruptEnable;
        uint8 startX;
        uint8 lowaddress;
        uint16 address;
        bool addressLatch;
        uint8 readBELatch;

        uint8 codeRegister;
        uint8 vdpStatusRegister;
        // VDP register 2 = name table address
        uint8 borderColor;
        uint8 horizontalScroll;

        typedef struct
        {
            uint8 fineScroll;
            uint8 columnOffset;
            uint8 xOffset;
        } HorizontalScroll;
        HorizontalScroll *horizontalScrollInfo;
        HorizontalScroll *lastHorizontalScrollInfo;
        uint8 *verticalScrollInfo;
        uint8 *lastVerticalScrollInfo;
        bool verticalScrollChanged;

        bool horizontalScrollChanged;
        uint8 verticalScroll;
        uint8 lineInterupt;
        uint8 *tileDefinitions;

        static const uint8 NAMETABLEPRIORITY = 0x10;
        uint8 *nameTable;
        static const uint8 NUMSPRITES = 64;
        uint8 spriteHeight;
        uint8 spriteWidth;
        uint8 *spriteInformationTable;
        uint16 vdpRegister[NUMVDPREGISTERS];
        uint8 *vdpRAM;
        uint8 *cRAM;

        uint16 *screenPalette;

        bool videoChange;
        bool enableDisplay;

        uint8 displayMode;
        static const uint8 DMM4 = 0x8;
        static const uint8 DMM3 = 0x4;
        static const uint8 DMM2 = 0x2;
        static const uint8 DMM1 = 0x1;
        uint8  currentYpos;
        uint8  yEnd;
        uint16 yScroll;
        uint16 xScroll;

        static const unsigned int PALETTE_ADDRESS  = 0xC000;

        static const unsigned int SMS_WIDTH  = 256;
        static const unsigned int SMS_HEIGHT = 192; // MAX HEIGHT
        static const unsigned int SMS_COLOR_DEPTH = 16;
        SDL_Surface *screen;
        SDL_Surface *image;
        Uint16 *raw_pixels;

        static const unsigned int MAXPATTERNS = 512;
        static const unsigned int PATTERNWIDTH  = 8;
        static const unsigned int PATTERNHEIGHT = 8;
        static const unsigned int PATTERNSIZE = 64;

        static const unsigned int MAXPALETTES = 2;

        uint16 tileAttributesAddress;
        static const uint16 NUMTILEATTRIBUTES = 0x700;
        static const uint16 TILEATTRIBUTEMASK     = 0x7FF;
        static const uint16 TILEATTRIBUTESADDRESSMASK = 0x3800; 
        static const uint16 TILEATTRIBUTESTILEMASK = 0x07FE; 
        static const uint16 TILESHIFT = 1; 
        static const uint16 TILEATTRIBUTESHMASK    = 0x0001; 
        static const uint16 TILEPRIORITYSHIFT = 4; 
        static const uint16 TILEPALETTESHIFT = 3; 
        static const uint16 TILEVFLIPSHIFT = 2; 
        static const uint16 TILEHFLIPSHIFT = 1; 

        static const uint16 YTILES = 28; 
        static const uint16 XTILES = 32; 
        static const uint16 NUMTILES = XTILES * YTILES; 
        typedef struct
        {
            bool changed;
            bool priority;
            bool priorityCleared;
            bool paletteSelect;
            bool verticalFlip;
            bool horizontalFlip;
            uint16 tileNumber;
        } TileAttribute;

        TileAttribute *tileAttributes;

        void removeSpriteFromScanlines(uint8 scanLine, uint8 sprite);
        void addSpriteToScanlines(uint8 scanLine, uint8 sprite);
        void printSpriteScanLineInfo(void);
        uint16 spriteAttributesAddress;
        static const uint16 SPRITEATTRIBUTESADDRESSMASK = 0x3F00; 
        static const uint16 SPRITEATTRIBUTESMASK = 0x00FF; 
        static const uint16 NUMSPRITEATTRIBUTES = 0x00FF; 

        static const uint16 SPRITETILEMASK = 0x0001; 

        static const uint8  LASTSPRITETOKEN = 0xD0;
        static const uint8  SPRITEXNMASK = 0x0080; 
        static const uint8  MAXSPRITES = 64;
        static const uint8  NOSPRITE = MAXSPRITES;
        static const uint8  MAXSPRITESPERSCANLINE = 8;

        uint16 spriteTileShift;
        uint8 totalSprites;
        typedef struct
        {
            uint8 y;
            uint8 x;
            uint16 tileNumber;
            bool changed;
        } Sprite;
        Sprite *sprites;

        typedef struct
        {
            uint8 numSprites;
            uint8 *sprites;
            uint8 *scanLine;
            bool lineChanged;
        } SpriteScanLine;
        SpriteScanLine *spriteScanLines;

        typedef struct
        {
            uint16 *scanLine;
            bool lineChanged;
        } ScanLine;

        typedef struct
        {
            bool *scanLine;
            uint16 hasPriority;
        } PriorityScanLine;

        uint16 **backgroundBuffers;
        ScanLine *backgroundScanLines;
        bool **forgroundBuffers;
        PriorityScanLine *forgroundScanLines;
        ScanLine *scanLines;

        typedef struct
        {
            bool colorCheck;
            uint32 colors;
            bool changed;
            uint16 references;
            uint16 screenVersionCached;
        } PatternInfo;
        uint16 patternAddress;
        static const unsigned int PATTERNADDRESSLIMIT = 0x4000;

        PatternInfo *patternInfo;
        uint8 *patterns4;
        uint16 **patterns16;

        bool isFullSpeed;
};

#endif
