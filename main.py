from babel import Babel
from babel import Compiler, parser, instructions, cmd_note_

bb = Babel()

fname = r"archive/beethoven.mus"

with open(fname, 'r') as file:
    source = file.read()

instructions['NOTE'] = cmd_note_

cp = Compiler(parser, instructions)
print(*[(u%12, v) for u, v in cp.compile(source)], end="\n\n")