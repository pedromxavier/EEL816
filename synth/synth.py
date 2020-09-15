import numpy as np
import wave
import simpleaudio as sa

def gcd(a: int, b: int) -> int:
    while b: 
       a, b = b, a % b
    return a 

TWO_PI = 2.0 * np.pi

class Synth:

    harmonics = [(1, 1.0)]

    sample_rate = 44_100

    channels = 1

    pluck = None

    gain = 1.0

    bits = 16

    type = np.int16

    def __init__(self, **kwargs):
        if 'sample_rate' in kwargs:
            self.sample_rate = max(min(int(kwargs['sample_rate']), 88200), 22050)

        if 'gain' in kwargs:
            self.gain = max(min(float(kwargs['gain']), 1.0), 0.0)

        if 'harmonics' in kwargs:
            self.harmonics = [(k, pow(h, 10.0)) for k,h in enumerate(kwargs['harmonics'], start=1)]
            s = sum(h for k,h in self.harmonics)
            self.harmonics = [(k, h/s) for k, h in self.harmonics]

        if 'pluck' in kwargs:
            self.pluck = kwargs['pluck']
            assert callable(self.pluck)

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

            x = t[i:j]
            for k, h in self.harmonics:
                w[i:j] += h * np.sin(TWO_PI * frequency * k * x)
            
            ## envelope wave
            self._pluck(w, i, j)
        else:
            return (w * self.amp * self.gain).astype(self.type)

    def synth(self, notes: list) -> bytearray:
        return self._encode(self._synth(notes))

    def _pluck(self, w: np.ndarray, i: int, j: int):
        if self.pluck is None:
            return None
        else:
            w[i:j] *= self.pluck(i, j) # pylint: disable=not-callable

    def _encode(self, w: np.ndarray) -> bytearray:
        a = self.bits
        b = 8 * self.type(0).nbytes

        if a == b:
            return bytearray(w.tobytes())
        else:
            c = gcd(a, b)
            a //= c
            b //= c
            return bytearray([b for i, b in enumerate(w.tobytes()) if ((i - a) % b)])

    def wave(self, fname: str, audio: bytearray) -> None:
        with wave.open(fname, 'wb') as wave_write:
            ## pylint: disable=no-member
            wave_write.setframerate(self.sample_rate)
            wave_write.setnchannels(self.channels)
            wave_write.setsampwidth(self.bits // 8)
            wave_write.setnframes(len(audio))
            wave_write.writeframes(audio)

    def play(self, w: np.ndarray, sync: bool=True):
        # Play sound
        play = sa.play_buffer(w, self.channels, self.bits // 8, self.sample_rate)

        if sync:
            # Wait until finish
            play.wait_done()
        else:
            return play

    ## Plucks:
    ## Wave envelopers that vary according to playing style
    @staticmethod
    def bow(a: float = 10.0):
        r""" Bowed Strings
        """
        def bow_pluck(i, j):
            x = np.linspace(-1.0, 1.0, j - i, endpoint=True, dtype=float)
            y = 1.0 / (1.0 + np.exp(-a * (x - 0.5)))
            z = 1.0 / (1.0 + np.exp(-a * (x + 0.5)))
            return (y - z)
        return bow_pluck

    @staticmethod
    def key(a: float=0.40):
        r""" a \in (0, 1)
            Piano key
        """
        b = a * np.sqrt(np.pi / 8.0)
        def key_pluck(i, j):
            x = np.linspace(0.0, 1.0, j - i, endpoint=True, dtype=float)
            y = 0.5 * np.power(x / b, 2.0)
            return y * np.exp(1.0 - y)
        return key_pluck
            
