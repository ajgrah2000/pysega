import ctypes
import struct
from . import soundchannel

class Sound(object):
    def __init__(self, clocks):
        print("Sound chip created")

        self.FREQMULTIPLIER = 125000
#        self.SAMPLERATE = 32050
        self.SAMPLERATE = 22050
        self.CHANNELS = 4
        self.BITS = 8

        self.clocks = clocks

        self.volume    = [0xF] * self.CHANNELS
        self.channels  = [soundchannel.SoundChannel(),
                          soundchannel.SoundChannel(),
                          soundchannel.SoundChannel(),
                          soundchannel.SoundChannel()]
        self.freq      = [0] * self.CHANNELS
        self._chanFreq = 0

    def get_save_state(self):
        # TODO
        state = {}
        return state

    def set_save_state(self, state):
        # TODO
        pass

    def getHertz(self, frequency):
        return self.FREQMULTIPLIER/(frequency + 1)

    def get_next_audio_chunk(self, length):

        stream = [0] * length
        for c in range(self.CHANNELS):
            self.channels[c].setVolume((0xF - self.volume[c]) << 4)
            self.channels[c].setFrequency(self.getHertz(self.freq[c]), self.SAMPLERATE)
            channel_wave = self.channels[c].getWave(length)

            for i in range(length):
                stream[i] += channel_wave[i]

        return stream

    def writePort(self, data):
        # Dispatch the data to perform the specified audio function (frequency,
        # channel frequency, volume).

        if (data & 0x90) == 0x90:
            self.volume[(data >> 5) & 0x3] = data & 0xF

        if (data & 0x90) == 0x80:
            self._chanFreq = data

        if (data & 0x80) == 0x00:
            self.freq[(self._chanFreq >> 5) & 0x3] = ((data & 0x3F) << 4) | (self._chanFreq & 0xF)

    def step(self):
        pass

    def pre_write_generate_sound(self):
        pass

    def post_write_generate_sound(self):
        pass

    def handle_events(self, event):
        pass
