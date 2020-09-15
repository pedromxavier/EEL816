from .compiler import Compiler

def cmd_init(compiler: Compiler):
    """
    """
    compiler.env['clef'] = {}
    compiler.env['time'] = (4, 4)
    compiler.env['freq'] = 440.0
    compiler.env['tempo'] = 120
    return None

KEYS = {k : v for k, v in zip('ABCDEFG', [0, 2, 3, 5, 7, 8, 10])}

ACCIDENTS = {
    'b' : -1,
    '#' : 1,
    '§' : 0
}

def cmd_note(compiler: Compiler, note, duration, dot):
    """ note, duration, dot -> frequency(Hz), lenght(s)
    """
    key, accident, octave = note

    tempo = compiler.env['tempo']

    time = compiler.env['time']
    clef = compiler.env['clef']

    if accident is None:
        if key in clef:
            accident = ACCIDENTS[clef[key]]
        else:
            accident = ACCIDENTS['§']
    else:
        accident = ACCIDENTS[accident]

    if duration is None:
        duration = time[1]

    duration = (time[1] / duration) * (60.0 / tempo)

    if dot:
        duration += duration / 2

    if key is not None:
        frequency = compiler.env['freq'] * pow(2.0, (12 * (octave - 4) + KEYS[key] + accident) / 12.0)
    else:
        frequency = None

    return (frequency, duration)

def get_clef(tone):
    if tone == 'C:':
        return {} ## C Major
    elif tone == 'G':
        return {'F': '#'}
    elif tone == 'D': ## D Major
        return {'C': '#', 'F': '#'}
    else:
        raise NotImplementedError

def cmd_clef(compiler: Compiler, tone):
    """
    """
    compiler.env['clef'] = get_clef(tone)
    return None

def cmd_time(compiler: Compiler, a: int, b: int):
    """
    """
    compiler.env['time'] = (a, b)
    return None

def cmd_rept(compiler: Compiler, code: tuple):
    """
    """
    compiler.queue.extend(code + code)
    return None

def cmd_tempo(compiler: Compiler, tempo: int):
    """
    """
    compiler.env['tempo'] = tempo
    return None
    
instructions = {
    'INIT' : cmd_init,
    'NOTE' : cmd_note,
    'CLEF' : cmd_clef,
    'TIME' : cmd_time,
    'REPT' : cmd_rept,
    'TEMPO' : cmd_tempo
}