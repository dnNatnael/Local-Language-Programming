# Future Improvements — AML

## Language Features

1. **Arrays and objects** — `ዝርዝር` lists, key/value structures for real projects.
2. **For loops** — `ለ i = 1 እስከ 10` with `እርምጃ` (step).
3. **Break / continue** — `አቁም`, `ቀጥል` for loop control.
4. **Exception handling** — `ሞክር` / `ያዝ` mapped to try/catch.
5. **Modules** — `አስገባ` / `ሞጁል` for multi-file programs.
6. **Richer types** — optional type checking for `ቁጥር` vs `ጽሑፍ`.

## Tooling

1. **VS Code extension**
   - Syntax highlighting for Amharic keywords.
   - Snippets for `ከሆነ` / `መጨረሻ` blocks.
   - “Run AML” command invoking `translator.py` + Node.

2. **Interactive REPL**
   - Read-eval-print loop in Amharic.
   - Immediate feedback for classroom use.

3. **Better debugging**
   - Source maps: JS errors point back to `.aml` line numbers.
   - Optional `--sourcemap` flag in translator.

4. **Standard library in Amharic**
   - Wrappers: `ርዝመት(ዝርዝር)`, math helpers with Amharic names.

5. **Online playground**
   - Web UI: editor + translate + run in iframe (like JSFiddle).

6. **Educational IDE integration**
   - Blockly-style blocks that emit AML text.
   - Curriculum aligned with Ethiopian schools.

## Compiler Quality

1. **Better error recovery** — continue parsing after one error; list multiple issues.
2. **Formatter** — auto-indent AML source.
3. **LSP server** — hover docs for keywords in Amharic.
4. **Unit test suite** — pytest over lexer/parser/codegen golden files.

## Community

1. **Localized documentation** — full Amharic tutorials and video scripts.
2. **Community keyword review** — native speakers refine natural phrasing.
3. **Bilingual mode** — optional English keyword aliases for transition.
