# Compilers: Lexer, Parser and Evaluator with PLY

Two stages of a compiler front-end built with [PLY](https://www.dabeaz.com/ply/) (Python Lex-Yacc).

**Context:** Compilers module, UCT Honours (2026). Individual.

| Folder | Contents |
|---|---|
| `1-lexer/` | Lexer for short messages: words, numbers, punctuation, `#hashtags`, `@names` and illegal characters, written to a `.tkn` token file |
| `2-parser-evaluator/` | A full front-end for **BLA**, a small language of variable assignments over binary literals with operators `A`/`S`/`M`/`D` (add/subtract/multiply/divide), parentheses and comments. `lex_bla.py` tokenises, `parse_bla.py` builds an abstract syntax tree (`.ast`), `eval_bla.py` evaluates programs, and `errors_bla.py` reports lexical and syntax errors with line numbers |

## Run
```bash
pip install ply
cd 2-parser-evaluator
python parse_bla.py exprs.bla     # writes exprs.ast
python eval_bla.py exprs.bla      # evaluates the assignments
```
The `.bla` files are test programs. The `.tkn` / `.ast` files are the expected outputs.
