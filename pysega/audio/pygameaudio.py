from . import sound
import pygame.mixer
import pygame.locals

class PygameSound(sound.Sound):
    """ Capture sound (accurately), try to stretch sound to current speed.
    """

    def __init__(self, clocks):
        super(PygameSound, self).__init__(clocks)

        self._sound_chunk_size        =   1024*4

        self.openSound()
        
        self._last_update_time = self.clocks.system_clock

    def openSound(self):
        pygame.mixer.pre_init(self.SAMPLERATE, -self.BITS, self.CHANNELS, 1024*8)
        pygame.mixer.init()
        pygame.mixer.set_num_channels(2)

        self.channel = pygame.mixer.Channel(0)
        self.channel.set_volume(0.3)
        
        print("Freq: ", self.SAMPLERATE, "Hz")

    def step(self):
        self.play_channel_buffers()

    def play_channel_buffers(self):

         if len(self._stretched[0]) > self._sound_chunk_size and len(self._stretched[1]) > self._sound_chunk_size:
             if not self.channel.get_queue() or not self.channel.get_busy():
                  # Set left and right data for the channel.
                  channel_chunk = [0] * 2 * self._sound_chunk_size

                  sound = pygame.mixer.Sound(bytearray(channel_chunk))

                  if not self.channel.get_queue():
                      self.channel.queue(sound)
                  else:
                      self.channel.play(sound)

    def handle_events(self, event):
        print("handle", event.type, event)
