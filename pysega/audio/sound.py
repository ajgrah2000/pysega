import ctypes
import struct

class Sound(object):
    def __init__(self, clocks):
        print("Sound chip created")

        self.SAMPLERATE = 32050
        self.CHANNELS = 2
        self.BITS = 8

        self.clocks = clocks

        self.volume     = [0] * 2
        self.freq       = [0] * 2

    def get_save_state(self):
        # TODO
        state = {}
        return state

    def set_save_state(self, state):
        # TODO
        pass

    def get_channel_data(self, channel, length):
        length = int(length)
        stream = [0] * length
        return stream

    def step(self):
        pass

    def pre_write_generate_sound(self):
        pass

    def post_write_generate_sound(self):
        pass

    def handle_events(self, event):
        pass
