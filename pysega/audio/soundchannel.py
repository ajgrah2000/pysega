
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
        self._rMinPos = 0
        self._R = 0
        self._d = 0

    def setVolume(self, volume):
        self.volume = volume/4

    def setFrequency(self, freq, sample_rate):
        vol = self.volume

        self._d = freq * 2
        self._R = self._rMin
        self._rMin = sample_rate
        self._rMinPos = self.MAXPATTERN
        for self.nextlength in range(0, self.MAXPATTERN):
            if self._R >= sample_rate:
                self._R = self._R % sample_rate
                vol = self.volume - vol
                if vol == self.volume:
                    if self._R < self._rMin:
                        self._rMin    = self._R
                        self._rMinPos = self.nextlength

            self.next[self.nextlength] = vol
            self._R += self._d
        self.nextlength = self._rMinPos
        self.updated = True

    def getWave(self, length):
        wave = [0] * length

        i = 0
        while (self.playpos <  self.playlength) and (i < length):
            wave[i] = self.playbuf[self.playpos]

            self.playpos += 1
            i += 1

        if self.playpos < self.playlength:
            return wave

        
        # Swap buffers if updated
        if True == self.updated:
            self.updated = False

            tmp = self.playbuf
            self.playbuf = self.next
            self.next = tmp

            tmp = self.playlength
            self.playlength = self.nextlength
            self.nextlength = tmp

        if self.playlength == 0:
            while i < length:
                wave[i] = 0

            return wave

        self.playpos = 0
        while i < length:
            self.playpos = 0
            while (self.playpos < self.playlength) and (i < length):
                wave[i] = self.playbuf[self.playpos]
                i += 1
                self.playpos += 1

        return wave
           

