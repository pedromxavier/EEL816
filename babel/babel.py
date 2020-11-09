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
from fractions import Fraction
from markos import Markos, TimeMarkos

class Babel:

    def __init__(self, **kwargs):
        ...

C = (4, 4)

data = '0 0 1233 11 11 11'

tempo = TimeMarkos(C)
tempo.seed(0)
tempo.train([x for x in data if x != ' '])
k = 0
for t in tempo:
    if k >= 12: break
    if t is None:
        k += 1
        print(' ', end='')
    else:
        print(t, end='')
print()