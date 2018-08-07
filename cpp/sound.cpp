#include "sound.h"
#include "SDL.h"

#include <iostream>
#include <assert.h>
#include <string>
#include <time.h>

Sound::WritePort Sound::writePortFunction;

Sound::Sound(const uint32 &cycles): cycles(cycles)
{
    desired = new SDL_AudioSpec;
    audioSpec = new SDL_AudioSpec;

    desired->freq = SAMPLERATE;
    desired->format = AUDIO_U8;
    desired->channels = 1;
    desired->samples = SAMPLE;
    desired->callback = audioCallback;
    desired->userdata = this;

    assert(SDL_Init(SDL_INIT_AUDIO) == 0);

    if(SDL_OpenAudio(desired, audioSpec) != 0)
    {
	std::cerr << "Couldn't open audio:" << SDL_GetError() << std::endl;
        exit(-1);
    }
    assert(audioSpec != NULL);
    delete desired;

    std::cout << "Freq: " << audioSpec->freq << "Hz" << std::endl;
    std::cout << "Sound Buffer (bytes): " << audioSpec->size << std::endl;
 

    volume = new uint8[CHANNELS];
    for (int i = 0; i < CHANNELS; i++)
        volume[i] = 0xF; // Silence

    freq = new uint16[CHANNELS];
    for (int i = 0; i < CHANNELS; i++)
        freq[i] = 0;

    SDL_PauseAudio(0);
    std::cout << "Sound initialised!" << std::endl;
}

Sound::~Sound()
{
    SDL_QuitSubSystem(SDL_INIT_AUDIO);

    delete [] freq;
    delete [] volume;
    delete desired;
    delete audioSpec;
}

Byte Sound::readPort(void *object)
{
    return ((Sound *) object)->realReadPort();
}

void Sound::writePort(void *object, Byte data)
{
    ((Sound *) object)->realWritePort(data);
}

void Sound::writePort(void *object, const Byte *data, uint16 length)
{
    ((Sound *) object)->realWritePort(data, length);
}

Byte Sound::realReadPort(void)
{
    return 0;
}

void Sound::realWritePort(Byte data)
{
    static uint8 chanFreq;
    SDL_PauseAudio(0);
    if ((data & 0x90) == 0x90)
        volume[(data >> 5) & 0x3] = data & 0xF;

    if ((data & 0x90) == 0x80)
        chanFreq = data;

    if ((data & 0x80) == 0x00)
    {
        freq[(chanFreq >> 5) & 0x3] = ((data & 0x3F) << 4) | (chanFreq & 0xF);
    }
}

void Sound::realWritePort(const Byte *data, uint16 length)
{
    for (int i = 0; i < length; i++)
        realWritePort(data[i]);
}

uint16 Sound::getHertz(uint16 freq)
{
    return FREQMULTIPLIER/(freq + 1);
}

void Sound::audioCallback(Uint8 *stream, int len)
{
    static uint16 bufSize = 0;
    static uint8 *tmp = NULL;

    if (bufSize < len)
    {
        delete tmp;
        bufSize = len;
        tmp = new uint8[bufSize];
    }

    memset(stream, 0, len);

    for (int c = 0; c < CHANNELS; c++)
//int c = 0;
    {
        channel[c].setVolume((0xF - volume[c]) << 4);
//        channel[c].setFrequency(getHertz(freq[c]), audioSpec->freq);
        channel[c].setFrequency(getHertz(freq[c]), audioSpec->freq);
        channel[c].getWave(tmp, len);

        for (int i = 0; i < len; i++)
        {
            stream[i] += tmp[i];
        }
    }
}

void Sound::audioCallback(void *userdata, Uint8 *stream, int len)
{
    ((Sound *) userdata)->audioCallback(stream, len);
}

