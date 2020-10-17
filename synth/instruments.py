import numpy as np

TWO_PI = 2.0 * np.pi

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

    __scs__ = {}

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def touch(self, f: float, t:np.ndarray, w: np.ndarray, i: int, j: int, n: int):
        for k, h in self.harmonics(f):
            w[i:j] += h * self.wave(t[i:j], f, k)
        else:
            w[i:j] += self.noise(j - i)

        self.shape(w, i, j, n)

    @classmethod
    def wave(self, t: np.ndarray, f: float, k: int):
        return np.sin(TWO_PI * f * k * t)

    @classmethod
    def shape(self, w: np.ndarray, i: int, j: int, n: int):
        raise NotImplementedError

    @classmethod
    def noise(self, n: int, a:float=0.01):
        return np.random.normal(loc=0.0, scale=a, size=n)

    @classmethod
    def harmonics(cls, f: float):
        raise NotImplementedError

    @classmethod
    def get_harmonics(cls, h: list):
        ## Harmonics in dB
        h = np.array(h, dtype=float)
        h = np.power(h, 10.0)
        h/= np.sum(h)
        return [(k, h) for k, h in enumerate(h, 1)]

    @classmethod
    def get(cls, key: str, **kwargs):
        return cls.__scs__[key](**kwargs)

class Violin(Instrument, metaclass=MetaInstrument):

    __key__ = 'violin'

    G_STRING = Instrument.get_harmonics([1.00, 0.42, 0.28, 0.32, 0.16, 0.02, 0.16, 0.08])
    D_STRING = Instrument.get_harmonics([1.00, 0.36, 0.30, 0.26, 0.28, 0.08, 0.28, 0.31])
    A_STRING = Instrument.get_harmonics([1.00, 0.32, 0.32, 0.24, 0.32, 0.16, 0.32, 0.36])
    E_STRING = Instrument.get_harmonics([1.00, 0.24, 0.36, 0.26, 0.38, 0.22, 0.28, 0.42])
    
    @classmethod
    def shape(cls, w, i, j, n):
        w[i:j] *= cls.bow_shape(i, j)

    @classmethod
    def bow_shape(cls, i, j, a: float=0.4):
        x = np.linspace(0.0, 1.0, j - i, endpoint=True, dtype=float) / (a * np.sqrt(np.pi / 8.0))
        y = 0.5 * np.power(x, 2.0)
        return y * np.exp(1.0 - y)

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

    VOICE = Instrument.get_harmonics([1.00, 0.5, 0.0, 0.25, 0.0, 0.0, 0.0, 0.125])

    @classmethod
    def wave(cls, t: np.ndarray, f: float, k: int):
        return t % (1.0 / ((f + cls.tremolo(t)) * k))

    @classmethod
    def tremolo(cls, t: np.ndarray):
        return 0.001 * np.sin(TWO_PI * 5.0 * t)

    @classmethod
    def noise(cls, n: int):
        return 0.0

    @classmethod
    def shape(cls, w, i, j, n):
        w[i:j] *= cls.synth_shape(i, j)

    @classmethod
    def synth_shape(cls, i, j):
        t = np.linspace(-1.0, 1.0, num = (j - i), endpoint = True)
        return np.exp(-np.power(1.2 * t, 12.0)) 

    @classmethod
    def harmonics(cls, f: float):
        return cls.VOICE














