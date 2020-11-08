import numpy as np
import pandas as pd 

class Markov:

    def __init__ (self, n, data, mapping=None):
        self.n = n
        self.data = data
        self.probabilities = None
        self.dFrame = None
        self.mapping = mapping
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

        #building the dataframe
        try:
            self.dFrame = pd.DataFrame(self.probabilities, index=self.mapping, columns=self.mapping)
        except:
            self.dFrame = pd.DataFrame(self.probabilities, index=range(self.n), columns=range(self.n))
        return

    def choose_next(self, base_name):
        return self.dFrame.idxmax(axis=1)[base_name]


    def predict(self, base_name, num_predictions):
        result_list = [base_name]
        aux = base_name
        for _ in range(num_predictions):
            aux = self.choose_next(aux)
            result_list.append(aux)
        return result_list



# teste = Markov(2, '001010111')
# print(teste.probabilities)
# print (teste.dFrame)
