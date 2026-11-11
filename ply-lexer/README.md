# PLY Lexer

A lexical analyser built with [PLY](https://www.dabeaz.com/ply/) (Python Lex-Yacc). It splits short messages into tokens: words, numbers, punctuation, `#hashtags`, `@names`, whitespace and illegal characters. It writes the token stream to a `.tkn` file.

**Context:** Compilers module, UCT Honours (2026). Individual.

## Run
```bash
pip install ply
python lex_msg.py hashtag.msg      # writes hashtag.tkn
```
The `.msg` / `.tkn` pairs are the test inputs and their expected outputs.
