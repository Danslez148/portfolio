#eval_bla.py

import sys
import ply.lex as lex
import ply.yacc as yacc

tokens = (
    'ID', 'BINARY_LITERAL', 'A', 'S', 'M', 'D',
    'EQUALS', 'LPARENTHESIS', 'RPARENTHESIS',
)

def t_COMMENT_BLOCK(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')

def t_COMMENT_LINE(t):
    r'//[^\n]*'
    pass

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_WHITESPACE(t):
    r'[ \t\r]+'
    pass

def t_A(t):
    r'A'
    return t

def t_S(t):
    r'S'
    return t

def t_M(t):
    r'M'
    return t

def t_D(t):
    r'D'
    return t

def t_ID(t):
    r'[a-z_][a-z0-9_]*'
    return t

def t_BINARY_LITERAL(t):
    r'[+\-]?[01]+'
    return t

def t_EQUALS(t):
    r'='
    return t

def t_LPARENTHESIS(t):
    r'\('
    return t

def t_RPARENTHESIS(t):
    r'\)'
    return t

def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)

class Node:
    def __init__(self, label, children=None):
        self.label = label
        self.children = children if children is not None else []

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
        print(f"Syntax error at token '{p.value}' on line {p.lineno}")
    else:
        print("Syntax error at end of input")

def binary_literal_to_int(text):
    """Convert a bla binary literal string to a Python int.

    Literals may have an optional leading '+' or '-'.
    The remaining digits are treated as a standard unsigned binary number,
    then the sign is applied.
    """
    text = text.strip()
    if text.startswith('-'):
        return -int(text[1:], 2)
    elif text.startswith('+'):
        return int(text[1:], 2)
    else:
        return int(text, 2)

def int_to_bla_binary(n):
    """Convert a Python int to the bla output format.

    Positive: plain binary  e.g. 29  -> '11101'
    Zero:     '0'
    Negative: '-' followed by binary absolute value  e.g. -5 -> '-101'
    """
    if n == 0:
        return '0'
    elif n > 0:
        return bin(n)[2:]
    else:
        return '-' + bin(-n)[2:]

def evaluate(node, env):
    """Recursively evaluate an AST node, returning a Python int."""
    label = node.label

    if label.startswith('BINARY_LITERAL,'):
        text = label[len('BINARY_LITERAL,'):]
        return binary_literal_to_int(text)

    if label.startswith('ID,'):
        name = label[3:]
        if name not in env:
            raise NameError(f"Undefined variable '{name}'")
        return env[name]

    if label == 'A':
        return evaluate(node.children[0], env) + evaluate(node.children[1], env)

    if label == 'S':
        return evaluate(node.children[0], env) - evaluate(node.children[1], env)

    if label == 'M':
        return evaluate(node.children[0], env) * evaluate(node.children[1], env)

    if label == 'D':
        left  = evaluate(node.children[0], env)
        right = evaluate(node.children[1], env)
        return int(left / right)

    raise ValueError(f"Unknown node label: {label}")

def main():
    if len(sys.argv) < 2:
        print("Usage: eval_bla.py <input.bla>")
        sys.exit(1)

    inputfile = sys.argv[1]
    evafile   = inputfile[:-4] + '.eva'

    try:
        with open(inputfile, 'r') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: file '{inputfile}' not found.")
        sys.exit(1)

    lexer  = lex.lex()
    parser = yacc.yacc()

    tree = parser.parse(source, lexer=lexer)

    if tree is None:
        print("Parsing failed – cannot evaluate.")
        sys.exit(1)

    env      = {}
    output   = []

    for stmt in tree.children:
        lhs  = stmt.children[0]
        rhs  = stmt.children[1] 
        name = lhs.label[3:]

        value = evaluate(rhs, env)
        env[name] = value

        bla_repr = int_to_bla_binary(value)
        line = f"{name}[{bla_repr}]"
        print(line)
        output.append(line)

    with open(evafile, 'w') as f:
        f.write('\n'.join(output) + '\n')

if __name__ == '__main__':
    main()