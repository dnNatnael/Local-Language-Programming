# Lexer — Token Definitions and Example Streams

## Token Types

| Category | TokenType | Example value |
|----------|-----------|-----------------|
| Keyword | `KW_PRINT` | `አትም` |
| Keyword | `KW_IF` | `ከሆነ` |
| Keyword | `KW_END` | `መጨረሻ` |
| Identifier | `IDENTIFIER` | `x`, `ድምር` |
| Literal | `NUMBER` | `10`, `3.14` |
| Literal | `STRING` | `ሰላም` |
| Operator | `PLUS`, `MINUS`, `STAR`, `SLASH` | `+` `-` `*` `/` |
| Operator | `EQ`, `EQEQ`, `LT`, `GT` | `=` `==` `<` `>` |
| Punctuation | `LPAREN`, `RPAREN`, `COMMA` | `( ) ,` |
| Structure | `NEWLINE` | line break |
| Structure | `EOF` | end of file |

## Example 1 — Variables (`01_variables.aml`)

Source:

```aml
ቁጥር x = 10
ቁጥር y = 20
አትም x + y
```

Token stream (abbreviated):

```
KW_NUMBER_TYPE       'ቁጥር'           @ 1:1
IDENTIFIER           'x'              @ 1:6
EQ                   '='              @ 1:8
NUMBER               '10'             @ 1:10
NEWLINE              '\n'             @ 1:12
KW_NUMBER_TYPE       'ቁጥር'           @ 2:1
IDENTIFIER           'y'              @ 2:6
...
KW_PRINT             'አትም'           @ 4:1
IDENTIFIER           'x'              @ 4:5
PLUS                 '+'              @ 4:7
IDENTIFIER           'y'              @ 4:9
EOF
```

Generate with:

```bash
python translator.py examples/01_variables.aml --tokens
```

## Unicode Notes

- Keywords are matched **exactly** as full Amharic words after identifier scanning.
- `str.isalpha()` allows Ethiopic letters in identifiers.
- Source files must be saved as **UTF-8**.
