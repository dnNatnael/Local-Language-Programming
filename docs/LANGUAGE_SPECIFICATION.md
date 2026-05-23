# አማርኛ ፕሮግራሚንግ ቋንቋ (AML)
## Amharic Programming Language — Language Specification

**Version:** 1.0  
**Project:** Local Language Programming for Beginners  
**Target:** Python (via source-to-source translation)

---

## 1. Language Name

| Property | Value |
|----------|-------|
| **Name (Amharic)** | አማርኛ ፕሮግራሚንግ ቋንቋ |
| **Abbreviation** | AML |
| **File extension** | `.aml` |
| **Encoding** | UTF-8 (mandatory) |

AML is a small, educational language designed for Ethiopian beginners. All **keywords** are Amharic; **identifiers** may use Amharic, English, or mixed Unicode letters.

---

## 2. Keyword Table

### Core (implemented in v1.0)

| English | Amharic | Usage |
|---------|---------|-------|
| print | አትም | Output to console |
| input | ግቤት | Read user input |
| if | ከሆነ | Conditional |
| else | ካልሆነ | Else branch |
| while | እስከ | While loop |
| function | ተግባር | Function definition |
| return | መልስ | Return from function |
| end | መጨረሻ | End of block |
| true | እውነት | Boolean true |
| false | ሐሰት | Boolean false |
| and | እና | Logical AND |
| or | ወይም | Logical OR |
| not | አይደለም | Logical NOT |
| number | ቁጥር | Declare numeric variable |
| text | ጽሑፍ | Declare string variable |

### Extended (reserved for future versions)

| English | Amharic |
|---------|---------|
| for | ለ |
| list | ዝርዝር |
| break | አቁም |
| continue | ቀጥል |
| repeat | ድገም |
| try | ሞክር |
| catch | ያዝ |
| import | አስገባ |

---

## 3. Syntax Rules

### 3.1 General

- One **statement** per line (newline-separated).
- **Blocks** end with the keyword `መጨረሻ` (not braces).
- **Comments** start with `#` until end of line.
- **Minimal punctuation:** no semicolons required in source.
- **Indentation** is optional but recommended for readability.

### 3.2 Variables

```
ቁጥር <identifier> = <expression>
ጽሑፍ <identifier> = <expression>
<identifier> = <expression>    # reassignment
```

### 3.3 Output

```
አትም <expression>
```

### 3.4 Conditionals

```
ከሆነ <expression>
    <statements>
ካልሆነ
    <statements>    # optional
መጨረሻ
```

### 3.5 While Loop

```
እስከ <expression>
    <statements>
መጨረሻ
```

### 3.6 Functions

```
ተግባር <name>(<param>, ...)
    <statements>
    መልስ <expression>    # optional
መጨረሻ
```

### 3.7 Expressions

**Operators (same symbols as many languages):**

| Category | Operators |
|----------|-----------|
| Arithmetic | `+` `-` `*` `/` |
| Comparison | `==` `<` `>` |
| Logical | `እና` `ወይም` `አይደለም` |
| Grouping | `( )` |
| Call | `name(arg, ...)` |

**Precedence** (highest to lowest):

1. Unary: `አይደለም`, `-`
2. `*`, `/`
3. `+`, `-`
4. `<`, `>`, `==`
5. `እና`
6. `ወይም`

### 3.8 Literals

- **Numbers:** integers and decimals (`10`, `3.14`)
- **Strings:** double or single quotes (`"ሰላም"`, `'hello'`)
- **Booleans:** `እውነት`, `ሐሰት`

### 3.9 Identifiers

- Start with Unicode letter `_` or Amharic/English letter.
- Continue with letters, digits, underscore.
- Examples: `x`, `ድምር`, `ውጤት`

---

## 4. Grammar Overview (EBNF-style)

```ebnf
program       ::= statement*
statement     ::= var_decl | assign | print | input | if_stmt | while_stmt
                | fun_def | return_stmt | expr_stmt
var_decl      ::= ('ቁጥር' | 'ጽሑፍ') IDENT '=' expression
assign        ::= IDENT '=' expression
print_stmt    ::= 'አትም' expression
if_stmt       ::= 'ከሆነ' expression block ('ካልሆነ' block)? 'መጨረሻ'
while_stmt    ::= 'እስከ' expression block 'መጨረሻ'
fun_def       ::= 'ተግባር' IDENT '(' param_list? ')' block 'መጨረሻ'
return_stmt   ::= 'መልስ' expression?
block         ::= statement*   /* until ካልሆነ or መጨረሻ */
expression    ::= or_expr
or_expr       ::= and_expr ('ወይም' and_expr)*
and_expr      ::= eq_expr ('እና' eq_expr)*
eq_expr       ::= cmp_expr ('==' cmp_expr)*
cmp_expr      ::= add_expr (('<' | '>') add_expr)*
add_expr      ::= mul_expr (('+' | '-') mul_expr)*
mul_expr      ::= unary (('*' | '/') unary)*
unary         ::= 'አይደለም' unary | '-' unary | primary
primary       ::= NUMBER | STRING | BOOL | IDENT | call | '(' expression ')'
call          ::= IDENT '(' arg_list? ')'
```

---

## 5. Example Programs

See `examples/` directory:

| File | Topic |
|------|-------|
| `01_variables.aml` | Variables and arithmetic |
| `02_conditionals.aml` | if / else |
| `03_while_loop.aml` | while loop |
| `04_functions.aml` | Functions |

---

## 6. Beginner-Friendly Design

1. **Natural keywords** — `ከሆነ` (“if it is”) reads like Amharic prose.
2. **Explicit block endings** — `መጨረሻ` makes scope visible; no invisible brace matching.
3. **Familiar operators** — `+`, `==` reduce surprise for those who see math/code elsewhere.
4. **Type hints in Amharic** — `ቁጥር` / `ጽሑፍ` clarify intent without complex type systems.
5. **Amharic errors** — e.g. `ስህተት: መጨረሻ ተጠበቀ` (“Error: end expected”).
6. **No text-replacement** — real lexer/parser ensures correct structure.

---

## 7. Translation to Python

| AML | Python |
|-----|--------|
| `ቁጥር x = 10` | `x = 10` |
| `አትም expr` | `print(expr)` |
| `ከሆነ ... መጨረሻ` | `if ...:` (indented block) |
| `እስከ ... መጨረሻ` | `while ...:` (indented block) |
| `ተግባር f(a)` | `def f(a):` (indented block) |
| `መልስ expr` | `return expr` |

Identifiers and string literals are preserved in Unicode in the generated `.py` file.

---

## 8. Error Messages

| Situation | Message |
|-----------|---------|
| Missing `መጨረሻ` | `ስህተት: መጨረሻ ተጠበቀ` |
| Bad token | `ስህተት: ያልተጠበቀ ምልክት '...'` |
| Expected expression | `ስህተት: ገላጭ ተጠበቀ` |
| Unclosed string | `ስህተት: ያልተጠናቀቀ ጽሑፍ` |

All errors include **line** and **column** when available.
