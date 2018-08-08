
class SoundChannel(object):
    def __init__(self):
        self.MAXPATTERN = 512
        self.volume     = 0
        self.playlength = 0
        self.nextlength = 0
        self.playpos    = 0
        self.playbuf    = [0] * self.MAXPATTERN
        self.next       = [0] * self.MAXPATTERN

        self._rMin = 0

    def setVolume(self, volume):
        self.volume = volume/4

    def setFrequency(self, freq, sample_rate):
        """ Generate a particular frequency for the channel.
            Generates a square waves at the specified frequency, for the length
            'MAXPATTERN'.
        """
        vol = self.volume

        d = freq * 2
        R = self._rMin
        self._rMin = sample_rate
        rMinPos = self.MAXPATTERN

        for self.nextlength in range(0, self.MAXPATTERN):
            if R >= sample_rate:
                R = R % sample_rate
                vol = self.volume - vol
                if vol == self.volume:
                    if R < self._rMin:
                        self._rMin    = R
                        rMinPos = self.nextlength

            self.next[self.nextlength] = vol
            R += d
        self.nextlength = rMinPos

        self.updated = True

    def getWave(self, length):
        """ Generate the 'wave' output buffer.
            First copy what's left of the current 'play buffer', update to the
            new buffer, if it's changed and copy that until the wave buffer has
            been fully populated.
        """
        wave = [0] * length

        wave_pos = 0
        while (self.playpos <  self.playlength) and (wave_pos < length):
            wave[wave_pos] = self.playbuf[self.playpos]

            self.playpos += 1
            wave_pos += 1

        if self.playpos >= self.playlength:
            # Swap buffers if updated
            if True == self.updated:
                self.updated = False
    
                self.playbuf, self.next = self.next, self.playbuf 
                self.playlength, self.nextlength = self.nextlength, self.playlength
            if self.playlength == 0:
                while wave_pos < length:
                    wave[wave_pos] = 0
            else:
                self.playpos = 0
                while wave_pos < length:
                    self.playpos = 0
                    while (self.playpos < self.playlength) and (wave_pos < length):
                        wave[wave_pos] = self.playbuf[self.playpos]
                        wave_pos += 1
                        self.playpos += 1

        return wave
           

