from markov import Markov

# speed = 0

map_tempo = ['half', 'full', 'two_full', 'four_full']
train = '00123311101'

tempo = Markov(4, train, map_tempo)
print (tempo.dFrame)
predictions = tempo.predict('half', 5)
print(predictions)
