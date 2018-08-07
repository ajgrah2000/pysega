#include "soundchannel.h"
#include <iostream>
#include <math.h>

SoundChannel::SoundChannel()
{
    playBuf = new uint8[MAXPATTERN];
    for (int i = 0; i < MAXPATTERN; i++)
        playBuf[i] = 0;

    next = new uint8[MAXPATTERN];
    for (int i = 0; i < MAXPATTERN; i++)
        next[i] = 0;

    playPos = 0;
    playLength = 0;
    nextLength = 0;
    updated = false;
}

SoundChannel::~SoundChannel()
{
    delete [] playBuf;
    delete [] next;
}

void SoundChannel::getWave(uint8 *buf, int len)
{
    int i = 0;

    for (i = 0; (playPos < playLength) && (i < len); i++, playPos++)
        buf[i] = playBuf[playPos];

    if (playPos < playLength)
        return;

    // If a new pattern was written, which the pattern to play
    if (updated == true)
    {
        uint8 *tmp = playBuf;
        playBuf = next;
        next = tmp;
        updated = false;

        uint16 tmp16 = playLength;
        playLength = nextLength;
        nextLength = tmp16;
    }

    if (playLength == 0)
    {
        for(; i < len; i++)
            buf[i] = 0;
        return;
    }

    playPos = 0;
    while (i < len)
    {
        playPos = 0;
        for (; (playPos < playLength) && (i < len); i++, playPos++)
            buf[i] = playBuf[playPos];
    }
}

void SoundChannel::setVolume(uint8 volume)
{
    this->volume = volume/4;
}

void SoundChannel::setFrequency(int freq, uint16 sampleRate)
{
    static uint32 R, d;
    uint8 vol = volume;
    static uint32 rMin, rMinPos;

    d = freq*2;
    R = rMin;
    rMin = sampleRate;
    rMinPos = MAXPATTERN;
    for (nextLength = 0; (nextLength < MAXPATTERN); nextLength++)
    {
        if (R >= sampleRate)
        {
            R = R % sampleRate;
            vol = volume - vol;
            if (vol == volume)
            {
                if (R < rMin)
                {
                    rMin = R;
                    rMinPos = nextLength;
                }
            }
        }
        next[nextLength] = vol;
        R += d;
    }
    nextLength = rMinPos;

    updated = true;
}

void SoundChannel::setFrequency2(int freq, uint16 sampleRate)
{
    static float waveform[MAXPATTERN];

    float minError = 127;

    nextLength = 1;
    for (int i = 0; i < MAXPATTERN; i++)
    {
        waveform[i] = volume *4/3.1415926* sin(2*3.14159265*
                             ((float)i/(float)sampleRate)*(float)freq);
        waveform[i] += volume *4/(3.1415926*3.0)* sin(3.0*2*3.14159265*
                             ((float)i/(float)sampleRate)*(float)freq);
        waveform[i] += volume *4/(3.1415926*5.0)* sin(5.0*2*3.14159265*
                             ((float)i/(float)sampleRate)*(float)freq);
        waveform[i] += volume *4/(3.1415926*7.0)* sin(7.0*2*3.14159265*
                             ((float)i/(float)sampleRate)*(float)freq);
        waveform[i] += volume *4/(3.1415926*9.0)* sin(9.0*2*3.14159265*
                             ((float)i/(float)sampleRate)*(float)freq);
        waveform[i] += volume *4/(3.1415926*11.0)* sin(11.0*2*3.14159265*
                             ((float)i/(float)sampleRate)*(float)freq);
        waveform[i] += volume *4/(3.1415926*13.0)* sin(13.0*2*3.14159265*
                             ((float)i/(float)sampleRate)*(float)freq);

        if ((minError > waveform[i]) && (waveform[i] >= 0.0) && (waveform[i] >
        waveform[i-1]))
        {
            if (i != 0)
            {
                minError = waveform[i];
                nextLength = i;
            }
        }
    }

    for (int i = 0; i < MAXPATTERN;i++)
    {
        next[i] = (uint8) (waveform[i]+128);
    }

//    nextLength = MAXPATTERN;
    updated = true;
}
