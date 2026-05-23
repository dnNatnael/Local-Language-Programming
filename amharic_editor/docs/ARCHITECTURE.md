# Architecture — Simple Amharic Code Editor

## Design Goals

1. **Lightweight** — single process, PyQt6 only (no Electron/web stack).
2. **Beginner-friendly** — clear toolbar, Amharic menu labels, obvious Run button.
3. **Unicode-first** — UTF-8 files, Ethiopic fonts, Amharic error passthrough.
4. **Separation** — editor UI never implements compiler logic.

## Layers

### Presentation (`ui/`)

- `MainWindow` orchestrates layout, menus, tabs, settings.
- `FileExplorerSidebar` — `QFileSystemModel` + `QTreeView`.
- `OutputPanel` — read-only `QPlainTextEdit` tabs.
- `EditorToolBar` — signals for New/Open/Save/Translate/Run.

### Editor (`editor/`)

- `CodeEditor` extends `QPlainTextEdit` with custom line number gutter.
- `AmharicSyntaxHighlighter` — regex rules aligned with AML keywords.
- `build_completer()` — keyword/snippet popup.
- `themes.py` — centralized colors for dark/light.

### Integration (`integration/`)

- `translate_source()` / `translate_file()` import `translator.translate` from `PL/`.
- `run_javascript()` spawns `node` with `subprocess.run`, 30s timeout, UTF-8.

### Compiler (external)

Located at repository root:

- `translator.py`, `src/lexer.py`, `src/parser.py`, `src/codegen.py`

## Threading Model

| Operation | Thread | Reason |
|-----------|--------|--------|
| UI edits | Main | Qt requirement |
| Translate + parse | `QThread` | Avoid UI freeze |
| Node run | `QThread` | Same worker pattern |

Workers emit results back to main thread via Qt signals.

## Settings (`QSettings`)

- `theme` — dark / light
- `recent_files` — JSON list
- `last_folder` — file dialog default

## Error Flow

1. **Translation** — `AmharicSyntaxError` → line/column parsed → red underline in editor + Errors tab.
2. **Runtime** — Node stderr → Errors tab + Output tab.
3. **Logs** — all steps appended to Logs tab.

## Security

- No `shell=True` in subprocess.
- `CREATE_NO_WINDOW` on Windows for Node child process.
- File paths validated with `Path.exists()` before run.
- Timeout prevents hung programs.

## Extension Points

- Add LSP bridge in `integration/`
- Plug `QSortFilterProxyModel` into sidebar search
- Optional split editor via second `CodeEditor` in splitter
- REPL tab calling translator REPL when added to AML
