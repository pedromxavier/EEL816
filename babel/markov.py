import numpy as np
import pandas as pd 

class Markov:

    def __init__ (self, n, data):
        self.n = n
        self.data = data
        self.probabilities = ''
        self.train()

    def train(self):
        
        aux = np.zeros(shape=(self.n, self.n))
        
        for (current, next) in zip(self.data, self.data[1:]): 
            try:
                aux[int(current)][int(next)] += 1
            except:
                raise Exception("Data has to be constrained to the given limit 'n'")
        #normalize
        sum_of_rows = aux.sum(axis=1)
        self.probabilities = aux / sum_of_rows[:, np.newaxis] 



teste = Markov(2, '001010111')
print(teste.probabilities)

