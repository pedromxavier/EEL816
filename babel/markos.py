from fractions import Fraction
import numpy as np

class Markos:

    def __init__ (self, n):
        self.n = n
        self.r = np.arange(0, n, dtype=int)
        self._p = np.zeros(shape=(self.n, self.n))
        self._p_normal = None
        self._p_dirty = True
        
        self.prev = None

    @property
    def p(self):
        if self._p_dirty:
            self._p_normal = self._p / (np.sum(self._p, axis=1)[:, np.newaxis] + (self._p == 0))
            self._p_dirty = False
        return self._p_normal

    def seed(self, x: int):
        self.prev = x

    def train(self, data):
        for (current, next) in zip(data, data[1:]): 
            self._p[int(current)][int(next)] += 1
        else:
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
        self.s = self.FZERO
        self.L = Fraction(C[0], C[1])
        Markos.__init__(self, 7)

    def __iter__(self):
        while True:
            t = self.__next__()
            r = Fraction(1, pow(2, t))
            while True:
                if r + self.s == self.L: ## fecha o compasso
                    self.s = self.FZERO
                    yield t
                    yield None
                    break
                elif r + self.s < self.L:
                    self.s = self.s + r
                    yield t
                    break
                else:
                    t += 1
                    r = Fraction(1, pow(2, t))
                    continue


class ChordMarkos(Markos):
    def __init__(self):
        self.n = 7


class NoteMarkos(Markos):
        