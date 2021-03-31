from babel import Babel
from babel import Compiler, Synth, parser, instructions, cmd_rel_note, cmd_chord

## Lê arquivo fonte
with open(r"archive/tetris.mus", 'r') as file:
    source = file.read()

## Reproduz
print('Tocando')
synth = Synth(instrument='synth')
compiler = Compiler(parser, instructions)
data = compiler.compile(source)
wave = synth.synth(data)
synth.play(wave, True)

## Aprendizado
print('Compondo')
instructions['NOTE'] = cmd_rel_note
instructions['CHORD'] = cmd_chord
bb = Babel(instrument='synth')
compiler = Compiler(parser, instructions)
data = compiler.compile(source)
##bb.cm.basic_train()
bb.cm.seed(5)
bb.nm.basic_train()
bb.tm.basic_train()
bb.train(data, weight=100)
print('Tocando')
bb.play(10)