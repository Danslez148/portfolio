#errors_bla.py

import sys
import ply.lex as lex
import ply.yacc as yacc

_errors = []
_lex_line = 1

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
    line = t.lexer.lineno
    _errors.append(('lexical', line))
    t.lexer.skip(1)

class Node:
    def __init__(self, label, children=None, lineno=None):
        self.label = label
        self.children = children if children is not None else []
        self.lineno = lineno

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
    p[0] = Node('=', [Node(f'ID,{p[1]}', lineno=p.lineno(1)), p[3]], lineno=p.lineno(1))

def p_expression_add(p):
    '''expression : expression A term'''
    p[0] = Node('A', [p[1], p[3]], lineno=p.lineno(2))

def p_expression_sub(p):
    '''expression : expression S term'''
    p[0] = Node('S', [p[1], p[3]], lineno=p.lineno(2))

def p_expression_term(p):
    '''expression : term'''
    p[0] = p[1]

def p_term_mul(p):
    '''term : term M factor'''
    p[0] = Node('M', [p[1], p[3]], lineno=p.lineno(2))

def p_term_div(p):
    '''term : term D factor'''
    p[0] = Node('D', [p[1], p[3]], lineno=p.lineno(2))

def p_term_factor(p):
    '''term : factor'''
    p[0] = p[1]

def p_factor_paren(p):
    '''factor : LPARENTHESIS expression RPARENTHESIS'''
    p[0] = p[2]

def p_factor_binary(p):
    '''factor : BINARY_LITERAL'''
    p[0] = Node(f'BINARY_LITERAL,{p[1]}', lineno=p.lineno(1))

def p_factor_id(p):
    '''factor : ID'''
    p[0] = Node(f'ID,{p[1]}', lineno=p.lineno(1))

def p_empty(p):
    '''empty :'''
    pass

def p_error(p):
    if p:
        _errors.append(('parse', p.lineno))
    else:
        _errors.append(('parse', _current_lexer.lineno if _current_lexer else 1))

def analyse(tree):
    """Walk the AST, maintaining a symbol table.  Appends to _errors."""
    symbol_table = {}

    def check_expr(node):
        """Check right-hand-side expression for undefined identifiers."""
        if node is None:
            return
        if node.label.startswith('ID,'):
            name = node.label[3:]
            if name not in symbol_table:
                _errors.append(('semantic', node.lineno))
        for child in node.children:
            check_expr(child)

    def check_statement(node):
        """Check a single assignment statement."""
        lhs = node.children[0]
        rhs = node.children[1]
        name = lhs.label[3:]
        line = node.lineno

        check_expr(rhs)

        if name in symbol_table:
            _errors.append(('semantic', line))
        else:
            symbol_table[name] = line

    if tree is None:
        return
    for stmt in tree.children:
        check_statement(stmt)

_current_lexer = None

def main():
    global _current_lexer

    if len(sys.argv) < 2:
        print("Usage: errors_bla.py <input.bla>")
        sys.exit(1)

    inputfile = sys.argv[1]
    errfile = inputfile[:-4] + '.err'

    try:
        with open(inputfile, 'r') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: file '{inputfile}' not found.")
        sys.exit(1)

    lexer = lex.lex()
    _current_lexer = lexer
    parser = yacc.yacc()

    tree = parser.parse(source, lexer=lexer, tracking=True)

    if not _errors and tree is not None:
        analyse(tree)

    if _errors:
        kind, line = _errors[0]
        msg = f"{kind} error on line {line}"
        print(msg)
        with open(errfile, 'w') as f:
            f.write(msg + '\n')
    else:
        print("No errors found.")

if __name__ == '__main__':
    main()