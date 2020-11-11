""" 0 : (1/2)^0 = 1
    1 : (1/2)^1 = 1/2
    2 : (1/2)^2 = 1/4
    3 : (1/2)^3 = 1/8
    4 : (1/2)^4 = 1/16
    5 : (1/2)^5 = 1/32
    6 : (1/2)^6 = 1/64

    4 : 4 notas de referência
    4 : nota de referência é a 1/4 (índice 2)

"""
from .markos import Markos, TimeMarkos, ChordMarkos, NoteMarkos, Fraction
from .synth import Synth

class Babel:

    FREQ = 440.0 #Hz
    TEMPO = 120.0 # bpm

    def __init__(self, **kwargs):
        if 'C' in kwargs:
            self.C: tuple = kwargs['C']
        else:
            self.C: tuple = (4, 4)

        if 'tempo' in kwargs:
            self.tempo: float = kwargs['tempo']
        else:
            self.tempo: float = self.TEMPO

        self.t: int = None
        self.c: int = 0
        self.n: int = 0

        self.k: int = 0 ## contador de compassos

        self.cm = ChordMarkos()
        self.nm = NoteMarkos()
        self.tm = TimeMarkos(self.C)

        self.cm.basic_train()
        self.nm.basic_train()
        self.tm.basic_train()

        self.synth = Synth(instrument='harmonica')

    def __next__(self):
        ## solicita tempo
        self.t : int = next(self.tm)

        if self.t is None: ## vira o compasso
            ## solicita acorde
            self.c: int = next(self.cm)
            ## solicita tempo
            self.t: int = next(self.tm)

            ## incrementa contador de compasso
            self.k: int = self.k + 1

        ## solicita nota
        self.n: int = next(self.nm[self.c])

        return (self.FREQ * pow(2.0, self.n / 12.0), (self.C[1] / float(self.t)) * (60.0 / self.tempo))

    def __iter__(self):
        while True: yield next(self)

    def compose(self, k: int):
        """ k: int (nº de compassos)
        """
        notes = []
        ## reinicia a contagem
        self.k = 0
        while self.k < k:
            notes.append(next(self))
        else:
            return notes

    def play(self, k: int):
        notes = self.compose(k)
        wave = self.synth.synth(notes)
        self.synth.play(wave, sync=True)

