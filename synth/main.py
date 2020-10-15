#!/usr/bin/env python3

def main(argc: int, argv: list):
    from pathlib import Path
    import argparse
    from .compiler import Compiler
    from .parser import parser
    from .synth import Synth
    from .instructions import instructions

    argparser = argparse.ArgumentParser(description="Sound Compiler & Synth")

    argparser.add_argument('-o', '--output', type=str, default="music.wav", help="Sets output destination.")
    argparser.add_argument('-r', '--rate', type=int, default=44_100, help="Sets sample rate.")
    argparser.add_argument('-b', '--bits', type=int, default=16, choices=[8, 16, 24, 32], help="Sets encoding bits.")
    argparser.add_argument('source', nargs="+", help="Provides Input files")

    # parser.add_argument("source", help="Source files with .mus extension.")
    args = argparser.parse_args(argv[1:argc])

    synth_params = {
        ## These may come from CLI parsing
        ## Nothing else to do here right now

        ## sample rate
        'sample_rate' : args.rate,

        ## Violin D String response (db)
        'harmonics' : [1.00, 0.36, 0.30, 0.26, 0.28, 0.08, 0.28, 0.31],

        ## Bowed Strings pluck
        'pluck' : Synth.bow()
    }

    compiler = Compiler(parser, instructions)
    synth = Synth(**synth_params)
    audio_list = []
    for fname in args.source:
        with open(fname, 'r') as file:
            source = file.read()
        notes = compiler.compile(source)
        audio = synth.synth(notes)
        audio_list.append(audio)
    else:
        if len(audio_list) == 1:
            audio = audio_list[0]
        else:
            audio = synth.merge(audio_list)

        if args.output.endswith('.wav'):
            wname = args.output
        else:
            wname = f"{args.output}.wav"

        synth.wave(wname, audio)
        
if __name__ == '__main__':
    import sys
    main(len(sys.argv), sys.argv)