""" 0 : (1/2)^0 = 1
    1 : (1/2)^1 = 1/2
    2 : (1/2)^2 = 1/4
    3 : (1/2)^3 = 1/8
    4 : (1/2)^4 = 1/16
"""
from .markov import Markov

# speed = 0
##
#
#

map_tempo = {0:'half', 1:'full', 2:'two_full', 3:'four_full'}
train = '00123311101'

tempo = Markov(4, train)
predictions = tempo.predict(0, 5)
print(predictions)
translation = [map_tempo[key] for key in predictions]
print (translation)