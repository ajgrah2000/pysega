from . import sound
import pygame.mixer
import pygame.locals

class PygameSound(sound.Sound):
    """ Capture sound (accurately), try to stretch sound to current speed.
    """

    def __init__(self, clocks):
        super(PygameSound, self).__init__(clocks)

        # Chunk size is somewhat arbitrary, larger is likely to be less
        # choppy/poppy/noisy, but may lag/miss frequency changes.
        self.CHANNEL_CHUNK_SIZE = 512

        self.openSound()
        
        self._last_update_time = self.clocks.cycles

    def openSound(self):
        pygame.mixer.pre_init(self.SAMPLERATE, -self.BITS, 1, 128)
        pygame.mixer.init()
        pygame.mixer.set_num_channels(1)

        self.channel = pygame.mixer.Channel(0)
        self.channel.set_volume(0.3)
        
        print("Freq: ", self.SAMPLERATE, "Hz")

    def step(self):
        self.play_channel_buffers()

    def play_channel_buffers(self):
        if not self.channel.get_queue() or not self.channel.get_busy():
          channel_chunk = self.get_next_audio_chunk(self.CHANNEL_CHUNK_SIZE)

          sound = pygame.mixer.Sound(bytearray(channel_chunk))

          if not self.channel.get_queue():
              self.channel.queue(sound)
          else:
              self.channel.play(sound)
