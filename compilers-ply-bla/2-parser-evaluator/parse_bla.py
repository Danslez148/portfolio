import sys
import os
import ply.lex as lex
import ply.yacc as yacc

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
    pass

def t_COMMENT_BLOCK(t):
    r'/\*(.|\n)*?\*/'
    t.type = 'COMMENT'
    pass

def t_COMMENT_LINE(t):
    r'//[^\n]*'
    t.type = 'COMMENT'
    pass

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

class Node:
    def __init__(self, label, children=None):
        self.label = label
        self.children = children if children is not None else []
    def depth_first(self, depth=0):
        yield '\t' * depth + self.label
        for child in self.children:
            yield from child.depth_first(depth + 1)

precedence = (
    ('left', 'A', 'S'),
    ('left', 'M', 'D'),
)

def p_program(p):
    '''program : statement_list'''
    p[0] = Node('Program', p[1])

def p_statement_list_nonempty(p):
    '''statement_list : statement_list statement'''
    p[0] = p[1] + [p[2]]

def p_statement_list_empty(p):
    '''statement_list : empty'''
    p[0] = []

def p_statement(p):
    '''statement : ID EQUALS expression'''
    p[0] = Node('=', [Node(f'ID,{p[1]}'), p[3]])

def p_expression_add(p):
    '''expression : expression A term'''
    p[0] = Node('A', [p[1], p[3]])
 
 
def p_expression_sub(p):
    '''expression : expression S term'''
    p[0] = Node('S', [p[1], p[3]])
 
 
def p_expression_term(p):
    '''expression : term'''
    p[0] = p[1]

def p_term_mul(p):
    '''term : term M factor'''
    p[0] = Node('M', [p[1], p[3]])
 
 
def p_term_div(p):
    '''term : term D factor'''
    p[0] = Node('D', [p[1], p[3]])
 
 
def p_term_factor(p):
    '''term : factor'''
    p[0] = p[1]

def p_factor_paren(p):
    '''factor : LPARENTHESIS expression RPARENTHESIS'''
    p[0] = p[2]
 
 
def p_factor_binary(p):
    '''factor : BINARY_LITERAL'''
    p[0] = Node(f'BINARY_LITERAL,{p[1]}')
 
 
def p_factor_id(p):
    '''factor : ID'''
    p[0] = Node(f'ID,{p[1]}')

def p_empty(p):
    '''empty :'''
    pass
 
 
def p_error(p):
    if p:
        print(f"Syntax error at token '{p.value}' (type={p.type}, pos={p.lexpos})")
    else:
        print("Syntax error at end of input")

def main():
    inputfile = sys.argv[1]
    outputfile = inputfile[:-4:] + '.ast'

    try:
        with open(inputfile, 'r') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: file '{inputfile}' not found.")
        sys.exit(1)

    lexer = lex.lex()
    parser = yacc.yacc()

    tree = parser.parse(source, lexer=lexer)

    if tree is None:
        print("Parsing failed")
        sys.exit(1)
    
    lines = list(tree.depth_first())

    for line in lines:
        print(line)
    
    with open(outputfile, 'w') as f:
        f.write('\n'.join(lines) + '\n')

if __name__ == '__main__':
    main()