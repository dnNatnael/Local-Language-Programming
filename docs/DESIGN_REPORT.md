# Design Report — Amharic Programming Language (AML)

## 1. Overview

AML is a **source-to-source translator** (transpiler) that compiles a beginner-oriented Amharic syntax into executable JavaScript. The implementation follows classic compiler phases: **lexical analysis → parsing → code generation**.

## 2. Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌──────────────┐
│  .aml file  │───▶│   Lexer     │───▶│   Parser    │───▶│  Codegen     │
│  (UTF-8)    │    │  (tokens)   │    │  (AST)      │    │  (.js file)  │
└─────────────┘    └─────────────┘    └─────────────┘    └──────────────┘
```

### Module layout

| Module | Responsibility |
|--------|----------------|
| `src/lexer.py` | Unicode tokenization, keyword table |
| `src/parser.py` | Recursive descent, AST construction |
| `src/ast_nodes.py` | Dataclass AST nodes |
| `src/codegen.py` | AST → JavaScript with indentation |
| `src/errors.py` | Amharic error messages |
| `translator.py` | CLI entry point |

## 3. Design Choices

### 3.1 Why recursive descent?

- Easy to teach and read alongside beginner courses.
- Maps directly to grammar rules in the specification.
- Sufficient for a small statement/expression language.

### 3.2 Why `መጨረሻ` instead of braces?

- Aligns with “readable block endings” goal.
- Mirrors spoken structure (“… until end”).
- Parser uses **stop tokens** (`ካልሆነ`, `መጨረሻ`) rather than indentation enforcement.

### 3.3 Why translate to JavaScript?

- Runs everywhere (browser, Node.js) without a custom VM.
- Beginners can use familiar DevTools later.
- Unicode identifiers are valid in modern JS.

### 3.4 Why not text replacement?

String substitution cannot handle nested blocks, expressions, or strings containing keywords. A real parser prevents false matches and enables precise errors.

## 4. Unicode Challenges

| Challenge | Solution |
|-----------|----------|
| Amharic letters in keywords | UTF-8 source; Python 3 `str`; keyword dict keyed by Amharic strings |
| Identifiers in Ethiopic script | `str.isalpha()` / `isalnum()` (Unicode-aware in Python 3) |
| Mixed Amharic/ASCII identifiers | Same identifier rules for all scripts |
| Console/display | Terminal and editor must use UTF-8; README documents this |
| Generated JS | Preserve Unicode in output; escape only `"` and `\` in strings |

**Lesson:** Local-language compilers must treat source as **Unicode text end-to-end**, not bytes with ASCII assumptions.

## 5. Lexer Highlights

- Explicit `TokenType` enum for every keyword and symbol.
- Two-character operators (`==`) handled before single `=`.
- Comments (`#`) and whitespace skipped.
- Newlines are tokens (statement boundaries in practice).

## 6. Parser Highlights

- `Program` → list of `Statement` nodes.
- `block_until(*stop)` parses nested control flow without consuming the closing keyword.
- Expression precedence via layered `_parse_*` methods.

## 7. Code Generator Highlights

- Emits `let` for declarations, `console.log` for `አትም`.
- Indentation with 4 spaces for readable JS.
- Parentheses in binary expressions for correct precedence in output.

## 8. Testing Strategy

1. Translate each `examples/*.aml` file.
2. Run with `node output.js` and verify stdout.
3. Use `--tokens` flag to inspect lexer output during development.

## 9. Limitations (v1.0)

- No `ለ` (for) loop yet.
- No lists (`ዝርዝር`) or modules.
- `ግቤት` maps to `prompt()` (browser-oriented).
- No type checking beyond declaration keywords.

## 10. Educational Value

Students see the full pipeline: tokens → tree → JavaScript. This demystifies “how programming languages work” while lowering the language barrier for Amharic speakers.
