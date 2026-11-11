import sys
import os
import ply.lex as lex

tokens = ('ID', 'BINARY_LITERAL', 'WHITESPACE', 'COMMENT', 'A', 'S' , 'M', 'D', 'EQUALS', 'LPARENTHESIS', 'RPARENTHESIS')

def t_ID(t):
    r'[a-z_][a-z0-9_]*'
    t.type = 'ID'
    return t

def t_BINARY_LITERAL(t):
    r'[+\-][01]+|[01]+'
    t.type = 'BINARY_LITERAL'
    return t

def t_WHITESPACE(t):
    r'[ \t\n\r]+'
    t.type = 'WHITESPACE'
    return t

def t_COMMENT_BLOCK(t):
    r'/\*(.|\n)*?\*/'
    t.type = 'COMMENT'
    return t

def t_COMMENT_LINE(t):
    r'//[^\n]*'
    t.type = 'COMMENT'
    return t

def t_A(t):
    r'A'
    t.type = 'A'
    return t

def t_S(t):
    r'S'
    t.type = 'S'
    return t

def t_M(t):
    r'M'
    t.type = 'M'
    return t

def t_D(t):
    r'D'
    t.type = 'D'
    return t

def t_EQUALS(t):
    r'='
    t.type = 'EQUALS'
    return t

def t_LPARENTHESIS(t):
    r'\('
    t.type = 'LPARENTHESIS'
    return t

def t_RPARENTHESIS(t):
    r'\)'
    t.type = 'RPARENTHESIS'
    return t

def t_error(t):
    print(f"Illegal character '{t.value[0]}' at position {t.lexpos}")
    t.lexer.skip(1)

_OPERATOR_OUTPUT = {
    'A':      'A',
    'S':      'S',
    'M':      'M',
    'D':      'D',
    'EQUALS': '=',
    'LPARENTHESIS': '(',
    'RPARENTHESIS': ')',
}

def format_token(tok):
    if tok.type == 'ID':
        return f'ID,{tok.value}'
    elif tok.type == 'BINARY_LITERAL':
        return f'BINARY_LITERAL,{tok.value}'
    elif tok.type == 'WHITESPACE':
        return 'WHITESPACE'
    elif tok.type == 'COMMENT':
        return 'COMMENT'
    elif tok.type in _OPERATOR_OUTPUT:
        return _OPERATOR_OUTPUT[tok.type]
    else:
        return tok.value

def main():
    inputfile = sys.argv[1]
    outputfile = inputfile[:-4:] + '.tkn'

    try:
        with open(inputfile, 'r') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: file '{inputfile}' not found")
        sys.exit(1)

    lexer = lex.lex()
    lexer.input(source)

    lines = []
    for tok in lexer:
        line = format_token(tok)
        print(line)
        lines.append(line)

    with open(outputfile, 'w') as f:
        f.write('\n'.join(lines) + '\n')

if __name__ == '__main__':
    main()