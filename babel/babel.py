import numpy as np
import pandas as pd


class Babel:

    def __init__(self, data, n):
        self.data = data
        self.n = n
        self.chords
    
    #parsing function here.

    def get_ngrams (self):
        aux = zip(*[chords[i:] for i in range(self.n)])
        ngrams = [" ".join(ngram) for ngram in ngrams]




