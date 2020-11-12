import re
from math import log2

from .compiler import Compiler

CHORD_KEYS = {
    0 : 0,
    2 : 1,
    4 : 2,
    5 : 3,
    7 : 4,
    9 : 5,
    11: 6,
}

KEYS = {
    'A': 0,
    'B': 2,
    'C': 3,
    'D': 5,
    'E': 7,
    'F': 8,
    'G': 10
}

NOTE_RE = re.compile(r'^([A-G])([\#b\§]?)([0-9])$', flags=re.UNICODE)
CHORD_RE = re.compile(r'^([A-G])([\#b\§]?)([mº]?)$', flags=re.UNICODE)

MAJOR_RE = re.compile(r'^[A-G][\#b\§]?$', flags=re.UNICODE)
MINOR_RE = re.compile(r'^[A-G][\#b\§]?m$', flags=re.UNICODE)

MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]

ACCIDENTS = {
    r'b' : -1,
    r'§' :  0,
    r'#' :  1,
    r''  :  None,
}

CLEF_INDEX = {
    'C': {},
    'G': {'F': '#'},
    'D': {'C': '#', 'F': '#'},
    'A': {'C': '#', 'F': '#', 'G': '#'},
    'E': {'C': '#', 'D': '#', 'F': '#', 'G': '#'},
    'B': {'C': '#', 'D': '#', 'F': '#', 'G': '#', 'A': '#'},
}

def minor(tone):
    return MINOR_RE.match(tone)

def major(tone):
    return MAJOR_RE.match(tone)

def get_clef(tone):
    if minor(tone):
        tone_ = tone[:-1]
    if major(tone):
        tone_ = tone
    else:
        raise ValueError(f'Invalid Tone: {tone}')

    return CLEF_INDEX[tone_]

def cmd_init(compiler: Compiler):
    """
    """
    compiler.env['tone'] = 'C'
    compiler.env['time'] = (4, 4)
    compiler.env['freq'] = 440.0
    compiler.env['tempo'] = 120
    return None

def cmd_rel_note(compiler: Compiler, note: str, duration: int, dot: None) -> (int, int):
    """ note, duration, dot -> frequency(Hz), lenght(s)
    """
    if duration is None:
        duration = compiler.env['time'][1]
    n = get_note(compiler, note) - KEYS[compiler.env['tone']]
    t = int(log2(duration))
    return (n, t)

def get_duration(compiler: Compiler, duration: int) -> int:
    if duration is None:
        duration = compiler.env['time'][1]

    return (compiler.env['time'][1] / duration) * (60.0 / compiler.env['tempo'])

def get_note(compiler: Compiler, note: str) -> int:
    m = NOTE_RE.match(note)

    if m is None: return None ## Pause

    key = m.group(1)
    acc = m.group(2)
    ocv = m.group(3)

    clef = get_clef(compiler.env['tone'])

    c = KEYS[key]

    if acc == '':
        if key in clef:
            b = ACCIDENTS[clef[key]]
        else:
            b = 0
    else:
        b = ACCIDENTS[acc]

    a = (int(ocv) - 4)

    return (12 * a + b + c)

def cmd_note(compiler: Compiler, note: str, duration, dot):
    """ note, duration, dot -> frequency(Hz), lenght(s)
    """

    duration = get_duration(compiler, duration)

    if dot: duration += duration / 2

    n = get_note(compiler, note)

    if n is not None:
        frequency = compiler.env['freq'] * pow(2.0, n / 12.0)
    else:
        frequency = None

    return (frequency, duration)

def cmd_tone(compiler: Compiler, tone):
    """
    """
    compiler.env['tone'] = tone
    return None

def cmd_time(compiler: Compiler, a: int, b: int):
    """
    """
    compiler.env['time'] = (a, b)
    return None

def cmd_rept(compiler: Compiler, code: tuple):
    """
    """
    compiler.queue.extendleft(code + code)
    return None

def cmd_tempo(compiler: Compiler, tempo: int):
    """
    """
    compiler.env['tempo'] = tempo
    return None

def cmd_chord(compiler: Compiler, chord: str):
    m = CHORD_RE.match(chord)

    key = m.group(1)
    acc = m.group(2)
    qua = m.group(3)

    n = (KEYS[key] - KEYS[compiler.env['tone']]) % 12

    if n in CHORD_KEYS:
        return (CHORD_KEYS[n], None)
    else:
        return None

def cmd_no_chord(compiler, *args):
    return None
    
instructions = {
    'INIT' : cmd_init,
    'NOTE' : cmd_note,
    'CHORD' : cmd_no_chord,
    'TONE' : cmd_tone,
    'TIME' : cmd_time,
    'REPT' : cmd_rept,
    'TEMPO' : cmd_tempo
}