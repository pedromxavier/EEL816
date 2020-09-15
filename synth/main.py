#!/usr/bin/env python3

def main(argc: int, argv: list):
    from pathlib import Path
    # import argparse
    from .compiler import Compiler
    from .parser import parser
    from .synth import Synth
    from .instructions import instructions

    # parser = argparse.ArgumentParser(description="Music Synthetizer")
    # parser.add_argument("source", help="Source files with .mus extension.")
    # parser.parse_args(argv[1:])

    synth_params = {
        ## These may come from CLI parsing
        ## Nothing else to do here right now

        ## Violin D String response (db)
        'harmonics' : [1.00, 0.36, 0.30, 0.26, 0.28, 0.08, 0.28, 0.31],

        ## Bowed Strings pluck
        'pluck' : Synth.bow()
    }

    compiler = Compiler(parser, instructions)
    synth = Synth(**synth_params)
    for fname in argv[1:]:
        with open(fname, 'r') as file:
            source = file.read()
        notes = compiler.compile(source)
        audio = synth.synth(notes)
        wname = f"{Path(fname).stem}.wav"
        synth.wave(wname, audio)

if __name__ == '__main__':
    import sys
    main(len(sys.argv), sys.argv)