import ply.lex
import sys

tokens = ("WORD", "NUMBER", "WHITESPACE", "PUNCTUATION", "HASHTAG", "NAME", "ILLEGAL")

t_WORD = r'[a-zA-Z]+'
t_NUMBER = r'[0-9]+'
t_WHITESPACE = r'[\s\t]+'
t_PUNCTUATION = r'[.,;!?]'
t_HASHTAG = r'#[a-zA-Z0-9]+'
t_NAME = r'@[a-zA-Z]+'
t_ILLEGAL = r'.'

def t_error(t):
    t.lexer.skip(1)

inputFile = sys.argv[1]
outputFile = inputFile[:-3:] + "tkn"
output = open(outputFile, 'w')
lexer = ply.lex.lex()
with open(inputFile, 'r') as f:
    data = f.read()
lexer.input(data)
while True:
    tok = lexer.token()
    if not tok:
        break
    print(f'{tok.type},{tok.value}\n')
    output.write(f'{tok.type},{tok.value}\n')

