from . import sound
import sounddevice

class SoundDeviceSound(sound.Sound):
    """ Capture sound (accurately), try to stretch sound to current speed.
    """

    def __init__(self, clocks):
        super(SoundDeviceSound, self).__init__(clocks)

        self.CHANNEL_CHUNK_SIZE = 2048
        self.next_buffer = [0] * self.CHANNEL_CHUNK_SIZE

        self.openSound()
        
    def fill_me(self, indata, outdata, frames, time, status):
        outdata[:,0] = self.next_buffer[:frames] 
        #outdata[:,0] = self.get_next_audio_chunk(frames)

    def finished_callback(self):
        print("Audio stream finished")

    def openSound(self):
        self.stream = sounddevice.Stream(channels=1, blocksize=0, samplerate=self.SAMPLERATE,callback=self.fill_me, finished_callback=self.finished_callback)

        self.stream.start()

        print("Freq: ", self.SAMPLERATE, "Hz")

    def step(self):
        self.next_buffer = self.get_next_audio_chunk(self.CHANNEL_CHUNK_SIZE)
