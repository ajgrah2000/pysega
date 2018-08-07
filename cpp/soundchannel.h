#ifndef SOUNDCHANNEL_H
#define SOUNDCHANNEL_H
#include "types.h"

class SoundChannel
{
    public:
        SoundChannel();
        ~SoundChannel();
        void setFrequency(int freq, uint16 sampleRate);
        void setFrequency2(int freq, uint16 sampleRate);
        void setVolume(uint8 volume);
        void getWave(uint8 *buf, int length);

    private:
        const static uint16 MAXPATTERN = 512;
        uint8 *playBuf;
        uint8 *next;
        uint16 playLength;
        uint16 nextLength;
        uint16 playPos;
        uint8 volume;
        bool updated;
};
#endif

