import numpy as np

PI = np.pi
TWO_PI = 2.0 * PI

class WaveShape:

    @classmethod
    def sine(cls, t: np.ndarray, f: float, df: float=0.0):
        return np.sin(np.multiply(np.multiply(TWO_PI, np.add(f, df)), t))

    @classmethod
    def saw(cls, t: np.ndarray, f: float, df: float=0.0):
        T = np.multiply(np.add(f, df), t)
        return np.multiply(2.0, np.subtract(T, np.floor(np.add(0.5, T))))

    @classmethod
    def square(cls, t: np.ndarray, f: float, df: float=0.0):
        w = np.sin(np.multiply(TWO_PI, np.add(f, df)))
        return np.piecewise(w, [w < 0.0, w == 0.0,  w > 0.0], [-1.0, 0.0, 1.0])

    @classmethod
    def noise(cls, n: int, a:float=0.001):
        return np.random.normal(loc=0.0, scale=a, size=n)

class WaveEnvelope:

    def __init__(self,
        attack_time: float,
        decay_time: float,
        release_time: float,
        sustain_amp: float
        ):
        self.attack_time = attack_time
        self.decay_time = decay_time
        self.release_time = release_time
        self.sustain_amp = sustain_amp

    def subframe(self, d: float, i: int, j: int, n: int):
        """ t : time frame
            d : duration
            i : frame start
            j : frame end
        """

        u = (j - i) / d ## frame rate, basically

        if d <= self.attack_time:
            k = int((self.attack_time + self.release_time) * u)
        elif d >= (self.attack_time + self.decay_time):
            k = j + int(self.release_time * u)
        else: ## attack_time < d < attack_time + decay_time
            k = j + int(max(self.decay_time - d + self.attack_time, self.release_time) * u)

        return (i, min(k, n))

    def envelope(self, tf: np.ndarray, d: float):
        t = tf - tf[0]
        if d <= self.attack_time:
            return (
                self.smooth_trans(
                    t,
                    0.0, ## a
                    self.attack_time, ## b
                    self.attack_time, ## c
                    self.release_time ## d
                )
            )
        elif d >= (self.attack_time + self.decay_time):
            return (
                self.sustain_amp * self.smooth_trans(
                    t,
                    0.0, ## a
                    self.attack_time, ## b
                    d, ## c
                    d + self.release_time ## d
                ) + 
                (1.0 - self.sustain_amp) * self.smooth_trans(
                    t,
                    0.0, ## a
                    self.attack_time, ## b
                    self.attack_time, ## c
                    self.attack_time + self.decay_time ## d
                )
            )
        else: ## attack_time < d < attack_time + decay_time
            return (
                self.smooth_trans(
                    t,
                    0.0, ## a
                    self.attack_time, ## b
                    self.attack_time, ## c
                    max(self.decay_time - d + self.attack_time, self.release_time) ## d
                )
            )
            

    @classmethod
    def smooth_trans(cls, x: np.ndarray, a: float, b: float, c: float, d: float):
        return np.multiply(
            cls._g(np.divide(np.subtract(x, a), b - a)),
            cls._g(np.divide(np.subtract(d, x), d - c))
        )

    @classmethod
    def _f(cls, x: np.ndarray):
        return np.piecewise(x, [x <= 0, x > 0], [0.0, lambda x: np.exp(np.divide(-1.0, x))])

    @classmethod
    def _g(cls, x: np.ndarray):
        return np.divide(cls._f(x), np.add(cls._f(x), cls._f(np.subtract(1.0, x))))
    
class MetaInstrument(type):

    __mcn__ = 'Instrument'
    __mcs__ = None
    __scs__ = {}

    def __new__(cls, name: str, bases: tuple, attrs: dict):
        if name == cls.__mcn__: ## Main class found
            cls.__mcs__ = type.__new__(cls, name, bases, attrs)
            cls.__mcs__.__scs__ = cls.__scs__
            return cls.__mcs__
        else:
            new_cls = type.__new__(cls, name, bases, attrs)
            cls.__scs__[new_cls.__key__] = new_cls
            return new_cls

class Instrument(metaclass=MetaInstrument):

    VOICE = [(1, 1.0)]

    __scs__ = {}

    def __init__(self, envelope: WaveEnvelope, **kwargs):
        self.env = envelope

    def touch(self, f: float, d: float, t:np.ndarray, w: np.ndarray, i: int, j: int, n: int):
        """ f : frequency
            d : duration
            t : time frame 
            w : wave frame
            i : subframe start
            j : subframe end
            n : frame end
        """
        ## get frame boundaries
        i, j = self.env.subframe(d, i, j, n)

        ## get time frame
        tf = t[i:j]
        for k, h in self.harmonics(f):
            w[i:j] += h * self.shape(tf, f, k)
        else:
            w[i:j] *= self.env.envelope(tf, d)

    @classmethod
    def effects(cls, w: np.ndarray, i: int, j: int, n: int):
        ...

    @classmethod
    def tremolo(cls, t: np.ndarray, a: float=0.0, b: float=4.0):
        if a == 0.0:
            return 0.0
        else:
            return a * np.sin(TWO_PI * b * t)

    @classmethod
    def shape(cls, t: np.ndarray, f: float, k: int):
        raise NotImplementedError

    @classmethod
    def harmonics(cls, f: float):
        return cls.VOICE

    @classmethod
    def get_harmonics(cls, h: list):
        ## Harmonics in dB
        h = np.array(h, dtype=float)
        h = np.power(h, 10.0)
        h/= np.sum(h)
        return [kh for kh in enumerate(h, 1)]

    @classmethod
    def get(cls, key: str):
        subcls = cls.__scs__[key]
        return subcls(**subcls.kwargs)

class Violin(Instrument, metaclass=MetaInstrument):

    __key__ = 'violin'

    G_STRING = Instrument.get_harmonics([1.00, 0.42, 0.28, 0.32, 0.16, 0.02, 0.16, 0.08])
    D_STRING = Instrument.get_harmonics([1.00, 0.36, 0.30, 0.26, 0.28, 0.08, 0.28, 0.31])
    A_STRING = Instrument.get_harmonics([1.00, 0.32, 0.32, 0.24, 0.32, 0.16, 0.32, 0.36])
    E_STRING = Instrument.get_harmonics([1.00, 0.24, 0.36, 0.26, 0.38, 0.22, 0.28, 0.42])

    ENVELOPE = WaveEnvelope(
        attack_time=0.05,
        decay_time=0.025,
        release_time=0.025,
        sustain_amp=0.9
        )

    kwargs = {
        'envelope' : ENVELOPE
    }

    @classmethod
    def shape(cls, t: np.ndarray, f: float, k: int):
        return WaveShape.saw(t, f * k, cls.tremolo(t, 0.001))

    @classmethod
    def harmonics(cls, f: float):
        if f < 293.6647679174076:
            return cls.G_STRING
        elif f < 440.0:
            return cls.D_STRING
        elif f < 659.2551138257398:
            return cls.A_STRING
        else:
            return cls.E_STRING

class Synth(Instrument, metaclass=MetaInstrument):

    __key__ = 'synth'

    VOICE = Instrument.get_harmonics([1.00, 0.5, 0.25, 0.125])

    ENVELOPE = WaveEnvelope(
        attack_time=0.01,
        decay_time=0.01,
        release_time=0,
        sustain_amp=0.95
        )

    kwargs = {
        'envelope' : ENVELOPE
    }

    @classmethod
    def shape(cls, t: np.ndarray, f: float, k: int):
        return WaveShape.saw(t, f * k, cls.tremolo(t, a=0.025))

    @classmethod
    def harmonics(cls, f: float):
        return cls.VOICE














