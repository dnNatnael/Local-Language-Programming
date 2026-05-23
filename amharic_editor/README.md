# Simple Amharic Code Editor

A lightweight **PyQt6** desktop IDE for the Amharic Programming Language (AML). It integrates with the existing AML translator in the parent `PL/` project — it does **not** reimplement the lexer, parser, or compiler.

## Features

- Unicode Amharic code editing with syntax highlighting
- Line numbers, auto-indent, autocomplete, find
- Dark / light themes, multiple tabs
- File explorer sidebar, recent files
- Translate AML → Python (in-process API)
- Run programs via Python
- Output panel: stdout, errors, generated Python, logs
- User guide (`የተጠቃሚ መመሪያ ሰነድ`) from `docs/user_guide/*.yml`

## Requirements

- **Python 3.9+**
- **PyQt6**
- **Python 3.8+** (for Run / F5)
- AML translator at `../` (same repo)

## Install & Run

```bash
cd c:\Users\hp\Desktop\PL
pip install -r amharic_editor/requirements.txt
python amharic_editor/main.py
```

Or from the editor folder:

```bash
cd amharic_editor
pip install -r requirements.txt
python main.py
```

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| New | Ctrl+N |
| Open | Ctrl+O |
| Save | Ctrl+S |
| Save As | Ctrl+Shift+S |
| Find | Ctrl+F |
| Translate | Ctrl+T |
| Run | F5 |
| Zoom In/Out | Ctrl++ / Ctrl+- |

## Project Structure

```
amharic_editor/
├── main.py                 # Application entry
├── editor/
│   ├── editor_widget.py    # Code editor + line numbers
│   ├── syntax_highlighter.py
│   ├── autocomplete.py
│   └── themes.py
├── ui/
│   ├── main_window.py      # Main IDE window
│   ├── sidebar.py          # File explorer
│   ├── terminal_panel.py   # Output tabs
│   └── toolbar.py
├── integration/
│   ├── translator_runner.py  # Calls PL/translator.py
│   └── javascript_runner.py  # Node.js subprocess
├── build.spec              # PyInstaller
├── requirements.txt
└── README.md
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    MainWindow (PyQt6)                    │
├──────────┬──────────────────────────────┬───────────────┤
│ Sidebar  │  TabWidget → CodeEditor       │  Menu/Toolbar │
│ (files)  │  + SyntaxHighlighter          │               │
├──────────┴──────────────────────────────┴───────────────┤
│              OutputPanel (tabs)                          │
│   Output | Errors | JavaScript | Logs                    │
└─────────────────────────────────────────────────────────┘
         │ Translate              │ Run (F5)
         ▼                        ▼
  translator_runner.py    javascript_runner.py
  (import translate)      (subprocess: node file.js)
         │                        │
         ▼                        ▼
    PL/translator.py          Node.js
```

Translation runs in a **QThread** so the UI stays responsive. Node execution uses **subprocess** with timeout and UTF-8 encoding.

## Packaging

### Windows (.exe)

```bash
pip install pyinstaller
cd c:\Users\hp\Desktop\PL
pyinstaller amharic_editor/build.spec --distpath dist
# Output: dist/AmharicCodeEditor.exe
```

### Ubuntu (AppImage / binary)

```bash
pip install pyinstaller
cd ~/Desktop/PL
pyinstaller amharic_editor/build.spec --distpath dist
chmod +x dist/AmharicCodeEditor
```

### Debian package (outline)

1. Install binary to `/usr/bin/amharic-editor`
2. Add `.desktop` file under `/usr/share/applications/`
3. Depend on `python3-pyqt6` if shipping as script instead

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for full deployment notes.

## Amharic fonts & keyboard

Install **Noto Sans Ethiopic** or **Abyssinica SIL** for correct menus and editor glyphs.

- Windows: [Noto Sans Ethiopic](https://fonts.google.com/noto/specimen/NotoSansEthiopic) → Install → restart editor
- Enable **Amharic keyboard** in Windows language settings; type in the editor with IME

See [docs/UNICODE_FONTS.md](docs/UNICODE_FONTS.md) for details.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Amharic squares in UI | Install Noto Sans Ethiopic / Abyssinica SIL |
| `8514oem` font warnings | Fixed in v1 — update `editor/fonts.py` is used |
| Crash when typing | Fixed — PyQt6 `WordUnderCursor` + IME handling |
| Translator not found | Run from `PL/` root; keep `translator.py` and `src/` intact |
| Node not found | Install Node.js and ensure `node` is on PATH |
| PyQt6 missing | `pip install PyQt6` |

## License

Educational — part of the AML beginner programming project.
