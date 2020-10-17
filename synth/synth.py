import numpy as np
import wave
import simpleaudio as sa

from .instruments import Instrument

def gcd(a: int, b: int) -> int:
    while b: 
       a, b = b, a % b
    return a 

def lazy_mean(X: list, dtype: type):
    n = len(X)
    y = np.zeros(max(map(len, X)), dtype=dtype)
    for x in X:
        y[:len(x)] += (x / n).astype(dtype)
    else:
        return y

TWO_PI = 2.0 * np.pi

class Synth:

    instrument = 'synth'

    sample_rate = 44_100

    channels = 1

    shape = None

    gain = 1.0

    bits = 16

    type = np.int16

    def __init__(self, **kwargs):
        if 'sample_rate' in kwargs:
            self.sample_rate = max(min(int(kwargs['sample_rate']), 88200), 22050)

        if 'gain' in kwargs:
            self.gain = max(min(float(kwargs['gain']), 1.0), 0.0)

        if 'instrument' in kwargs:
            self.instrument = Instrument.get(kwargs['instrument'])

        if 'shape' in kwargs:
            self.shape = kwargs['shape']
            assert callable(self.shape)

        if 'channels' in kwargs:
            self.channels = max(1, int(kwargs['channels']))

        if 'bits' in kwargs:
            self.bits = int(kwargs['bits'])
            if self.bits not in {8, 16, 24, 32}:
                raise ValueError("Encoding bits must be 8, 16, 24 or 32.")

            self.type = {
                 8: np.int16,
                16: np.int16,
                24: np.int32,
                32: np.int32
            }[self.bits]

        self.amp = (1 << (self.bits - 1)) - 1

    def _synth(self, notes: list):
        """
        """
        total_duration = sum(duration for frequency, duration in notes)

        n = int(total_duration * self.sample_rate)

        t = np.linspace(0.0, total_duration, num=n, endpoint=False, dtype=float)
        w = np.zeros(n, dtype=float) ## wave vector

        i, j = 0, 0
        for frequency, duration in notes:
            i, j = j, (j + int(duration * self.sample_rate))
            if frequency is None: continue
            self.instrument.touch(frequency, t, w, i, j, n)
        else:
            w /= np.max(np.abs(w))
            return (w * self.amp * self.gain).astype(self.type)

    def synth(self, notes: list) -> bytearray:
        return self._encode(self._synth(notes))

    def _shape(self, w: np.ndarray, i: int, j: int):
        if self.shape is None:
            return None
        else:
            w[i:j] *= self.shape(i, j) # pylint: disable=not-callable

    def _decode(self, w: bytearray) -> np.ndarray:
        a = self.bits
        b = 8 * self.type(0).nbytes

        if a == b:
            buffer = w
        else:
            c = gcd(a, b)
            a //= c
            b //= c
            buffer = [(x + b'\x00') if ((i - b) % a) else x for i, x in enumerate(w)]
        
        return np.frombuffer(buffer, dtype=self.type)

    def _encode(self, w: np.ndarray) -> bytearray:
        a = self.bits
        b = 8 * self.type(0).nbytes

        if a == b:
            return bytearray(w.tobytes())
        else:
            c = gcd(a, b)
            a //= c
            b //= c
            return bytearray([x for i, x in enumerate(w.tobytes()) if ((i - a) % b)])

    def wave(self, fname: str, audio: bytearray) -> None:
        """ Writes sound to .wav file
        """
        if self.channels == 1:
            nframes = len(audio)
        else:
            nframes = len(audio[0])

        with wave.open(fname, 'wb') as wave_write:
            ## pylint: disable=no-member
            wave_write.setframerate(self.sample_rate)
            wave_write.setnchannels(self.channels)
            wave_write.setsampwidth(self.bits // 8)
            wave_write.setnframes(nframes)
            wave_write.writeframes(audio)

    def play(self, w: np.ndarray, sync: bool=True):
        # Play sound
        play = sa.play_buffer(w, self.channels, self.bits // 8, self.sample_rate)

        if sync:
            # Wait until finish
            play.wait_done()
        else:
            return play

    def merge(self, *channels: list) -> list:
        """ cls.merge([audio_1: bytearray, ...], [audio_k: bytearray, ...], ...)
        """
        audio = [self._encode(lazy_mean([self._decode(w) for w in channel], self.type)) for channel in channels]
        
        if len(audio) == 1:
            return audio[0]
        else:
            return audio