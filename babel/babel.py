from markov import Markov

# speed = 0

map_tempo = {0:'half', 1:'full', 2:'two_full', 3:'four_full'}
train = '00123311101'

tempo = Markov(4, train)
predictions = tempo.predict(0, 5)
print(predictions)
translation = [map_tempo[key] for key in predictions]
print (translation)