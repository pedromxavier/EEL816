from fractions import Fraction
import numpy as np

class Markos:

    def __init__ (self, n):
        self.n = n
        self.r = np.arange(0, n, dtype=int)
        self._p = np.zeros((self.n, self.n), dtype=int)
        self._p_normal = np.empty((self.n, self.n), dtype=float)
        self._p_dirty = True
        
        self.prev = None

    @property
    def p(self):
        if self._p_dirty:
            self._p_normal[:] = np.divide(self._p, np.add(np.sum(self._p, axis=1)[:, np.newaxis], (self._p == 0)))
            self._p_dirty = False
        return self._p_normal

    def seed(self, x: int):
        self.prev = x

    def train(self, data, weight=1):
        for i in zip(data[:-1], data[1:]):
            self._p[i] += weight
        self._p_dirty = True

    def __next__(self):
        self.prev = np.random.choice(self.r, p=self.p[self.prev])
        return self.prev

    def __iter__(self):
        while True:
            yield self.__next__()

class TimeMarkos(Markos):

    FZERO = Fraction(0)

    def __init__(self, C: tuple):
        self.s = None
        self.L = Fraction(C[0], C[1])
        Markos.__init__(self, 7)

    def __next__(self) -> int:
        if self.s is None: ## reiniciou o compasso
            self.s: Fraction = self.FZERO
            return None
        else:
            t: int = Markos.__next__(self)
            r: Fraction = Fraction(1, pow(2, t))

            while True:
                if r + self.s == self.L: ## fecha o compasso
                    self.s = None
                    return t
                elif r + self.s < self.L: ## no meio do compasso
                    self.s = self.s + r
                    return t
                else: ## buscando completar o compasso
                    t += 1
                    r = Fraction(1, pow(2, t))
                    continue

    def __iter__(self) -> int:
        while True: yield next(self)

    def basic_train(self):
        for i in range(4):
            self.train([i, 2])
        self.train([2, 3])
        self.train([2, 1])
        self.seed(0)

class ChordMarkos(Markos):
    """
    """
    def __init__(self):
        Markos.__init__(self, 7)

    def basic_train(self):
        self.train([0, 3, 4, 3])
        self.train([0, 4, 5, 3])
        self.train([5, 1, 2, 1])
        self.train([5, 3, 0, 4])
        self.seed(0)

class _NoteMarkos(Markos):

    def __init__(self, octaves=8):
        self.octaves = octaves
        Markos.__init__(self, 12 * self.octaves)

class NoteMarkos:
    """ >>> notes = NoteMarkos()
        >>> notes[chord].train(data)
        >>> notes[chord].seed(0)
    """
    
    MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]

    def __init__(self):
        self._m = [_NoteMarkos(8) for _ in range(7)]
        
    def __getitem__(self, key: int):
        return self._m[key]

    def basic_train(self):
        ## return-to-key
        for i in range(7):
            for j in range(self[i].octaves):
                self[i]._p[12*j:12*(j+1), 12*j + self.MAJOR_SCALE[i]] += 1
                self[i]._p[12*j:12*(j+1), 12*j + self.MAJOR_SCALE[(i + 2) % 7]] += 1
                self[i]._p[12*j:12*(j+1), 12*j + self.MAJOR_SCALE[(i + 4) % 7]] += 1
            self[i].seed(0)