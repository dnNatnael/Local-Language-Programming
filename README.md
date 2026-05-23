# Local Language Programming for Beginners — Amharic Programming Language (AML)

**አማርኛ ፕሮግራሚንግ ቋንቋ** — A small educational language with Amharic keywords, compiled to Python.

## Quick Start

```bash
# Translate an AML program to Python
python translator.py examples/01_variables.aml

# Run the generated Python
python examples/01_variables.py
```

Output of `01_variables.py`: **30**

## Project Structure

```
PL/
├── translator.py          # CLI: python translator.py program.aml
├── src/
│   ├── lexer.py           # Unicode-aware tokenizer
│   ├── parser.py          # Recursive descent parser
│   ├── ast_nodes.py       # AST dataclasses
│   ├── codegen.py         # AST → Python
│   └── errors.py          # Amharic error messages
├── examples/
│   ├── 01_variables.aml
│   ├── 02_conditionals.aml
│   ├── 03_while_loop.aml
│   ├── 04_functions.aml
│   └── expected/          # Expected run output notes
├── docs/
│   ├── LANGUAGE_SPECIFICATION.md
│   ├── DESIGN_REPORT.md
│   └── FUTURE_IMPROVEMENTS.md
└── README.md
```

## Requirements

- **Python 3.8+** (UTF-8 support)
- **Python 3.8+** (to run generated `.py` files)

On Windows, if Amharic messages fail to print, set:

```powershell
$env:PYTHONIOENCODING = "utf-8"
```

## Example programs

Beginner-friendly samples live in [`examples/`](examples/README.md):

| File | Topic |
|------|--------|
| `01_variables.aml` | Declaration and assignment |
| `02_expressions.aml` | Arithmetic and comparisons |
| `03_conditionals.aml` | If / else |
| `04_while_loop.aml` | While loop |
| `05_functions.aml` | Define, call, return |

In the editor: **እገዛ → ምሳሌ ፕሮግራሞች** opens each file.

## Example: Variables

**AML** (`examples/01_variables.aml`):

```aml
ቁጥር x = 10
ቁጥር y = 20
አትም x + y
```

**Generated Python:**

```python
x = 10
y = 20
print((x + y))
```

## Debug: Token Stream

```bash
python translator.py examples/01_variables.aml --tokens
```

## Documentation

| Document | Description |
|----------|-------------|
| [LANGUAGE_SPECIFICATION.md](docs/LANGUAGE_SPECIFICATION.md) | Keywords, grammar, examples |
| [DESIGN_REPORT.md](docs/DESIGN_REPORT.md) | Architecture and Unicode notes |
| [FUTURE_IMPROVEMENTS.md](docs/FUTURE_IMPROVEMENTS.md) | Roadmap |

## Compiler Pipeline

1. **Lexer** — Reads UTF-8 source, emits tokens (Amharic keywords, identifiers, operators).
2. **Parser** — Builds an AST (no text replacement).
3. **Codegen** — Emits formatted, executable Python.

## Desktop Editor (PyQt6)

A beginner-friendly IDE is included in `amharic_editor/`:

```bash
pip install -r amharic_editor/requirements.txt
python amharic_editor/main.py
```

See [amharic_editor/README.md](amharic_editor/README.md) for shortcuts, packaging, and deployment.

## License

Educational use — built for Ethiopian beginners learning programming in Amharic.
