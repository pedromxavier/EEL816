import re
from ply import lex, yacc

tokens = (
    'TEMPO',
    'CLEF',
    'KEY',
    'TONE',
    'BAR',
    'LREP',
    'RREP',
    'LPAR',
    'RPAR',
    'LBRA',
    'RBRA',
    'PAUSE',
    'SEGNO',
    'CODA',
    'NUMBER',
    'SHARP',
    'FLAT',
    'NATURAL',
    'DOT'
)

t_DOT = r'\.'
t_BAR = r'\/'
t_SEGNO = r'\%'
t_CODA = r'\@'
t_SHARP = r'\#'
t_NATURAL = r'\§'
t_FLAT = r'b'
t_TEMPO = r'\!'
t_LREP = r'\|\:'
t_RREP = r'\:\|'
t_LBRA = r'\['
t_RBRA = r'\]'
t_LPAR = r'\('
t_RPAR = r'\)'
t_PAUSE = r'\-'
t_CLEF = r'\$'


t_KEY = r"[A-G]"

t_TONE = r'm'

t_ignore = ' \t'
t_ignore_COMMENT = r'\/\*[\s\S]*?\*\/'

def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)
    return None

def t_NUMBER(t):
    r"[1-9][0-9]*"
    t.value = int(t.value)
    return t

def t_error(t):
    raise SyntaxError(f'Invalid Token: {t}')

lexer = lex.lex(reflags=re.UNICODE)

def p_start(p):
    ''' start : code
    '''
    p[0] = list(p[1])

def p_code(p):
    ''' code : code expr
             | expr
    '''
    if len(p) == 3:
        p[0] = (*p[1], p[2])
    else:
        p[0] = (p[1],)

def p_expr(p):
    ''' expr : note
             | clef
             | time
             | rept
             | sign
             | tempo
    '''
    p[0] = p[1]

def p_note(p):
    ''' note : notehead DOT
             | notehead
    '''
    if len(p) == 3:
        p[0] = (*p[1], True)
    else:
        p[0] = (*p[1], False)

def p_notehead(p):
    ''' notehead : pitch duration
                 | pitch
    '''
    if len(p) == 3:
        p[0] = ('NOTE', p[1], p[2])
    else:
        p[0] = ('NOTE', p[1], None)

def p_pitch(p):
    ''' pitch : KEY accident NUMBER
              | KEY NUMBER
              | PAUSE
    '''
    if len(p) == 4:
        p[0] = (p[1], p[2], p[3])
    elif len(p) == 3:
        p[0] = (p[1], None, p[2])
    else: ## Pause
        p[0] = (None, None, None)

def p_accident(p):
    ''' accident : NATURAL
                 | SHARP
                 | FLAT
    '''
    p[0] = p[1]

def p_duration(p):
    ''' duration : LBRA NUMBER RBRA
    '''
    p[0] = p[2]

def p_clef(p):
    ''' clef : CLEF KEY TONE
             | CLEF KEY
    '''
    if len(p) == 4:
        p[0] = ('CLEF', p[2] + p[3])
    else:
        p[0] = ('CLEF', p[2])

def p_time(p):
    ''' time : LPAR NUMBER BAR NUMBER RPAR
    '''
    p[0] = ('TIME', p[2], p[4])

def p_rept(p):
    ''' rept : LREP code RREP
    '''
    p[0] = ('REPT', p[2])

def p_sign(p):
    ''' sign : SEGNO
             | CODA
    '''
    p[0] = ('SIGN', p[1])

def p_tempo(p):
    ''' tempo : TEMPO NUMBER
    '''
    p[0] = ('TEMPO', p[2])

def p_error(p):
    print('lineno=', lexer.lineno)
    print("lexpos=", lexer.lexpos)
    raise SyntaxError(f'Syntax Error:\n{p}')

parser = yacc.yacc()

if __name__ == '__main__':
    print(parser.parse(__doc__))