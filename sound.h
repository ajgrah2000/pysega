#ifndef SOUND_H
#define SOUND_H

#include "types.h"
#include "SDL.h"
#include "soundchannel.h"
#include "writeInterface.h"

class Sound
{
    public:
        Sound(const uint32 &cycles);
        virtual ~Sound();
        static Byte readPort(void *object);
        static void writePort(void *object, Byte data);
        static void writePort(void *object, const Byte *data, uint16 length);

        class WritePort : public WriteInterface
        {
                virtual void write(void *object, const Byte data){writePort(object, data);};
                virtual void write(void *object, const Byte *data, uint16 length){writePort(object, data, length);};
        };
        static WritePort writePortFunction;

    private:
        Byte realReadPort(void);
        void realWritePort(Byte data);
        void realWritePort(const Byte *data, uint16 length);

        SDL_AudioSpec *desired;
        SDL_AudioSpec *audioSpec;

        static void audioCallback(void *userdata, Uint8 *stream, int len);
        void audioCallback(Uint8 *stream, int len);

        const static uint32 FREQMULTIPLIER = 125000;
        uint16 getHertz(uint16 freq);

        const static uint16 SAMPLE = 512;
        const static uint16 SAMPLERATE = 22050;
        const static uint8 CHANNELS = 4;
        uint8 *volume;
        uint16 *freq;

        SoundChannel channel[CHANNELS];

        const uint32 &cycles;
};

#endif

