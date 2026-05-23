# Unicode & Amharic Fonts Guide

## UTF-8 everywhere

- All `.aml` files are read/written with `encoding="utf-8"`.
- Python 3 `str` is Unicode; no `ascii` encoding in the editor pipeline.
- Node.js subprocess uses `encoding="utf-8"`.

## Recommended fonts (Windows & Ubuntu)

| Font | Use |
|------|-----|
| **Noto Sans Ethiopic** | Best all-round Ethiopic UI + editor |
| **Abyssinica SIL** | Excellent for Amharic script |
| **Nyala** | Often preinstalled on Windows Amharic setups |
| **Cascadia Mono** | Latin/code glyphs in editor |

### Windows install

1. Download [Noto Sans Ethiopic](https://fonts.google.com/noto/specimen/NotoSansEthiopic)
2. Right-click `.ttf` → Install
3. Restart the editor

### Ubuntu install

```bash
sudo apt install fonts-noto-core fonts-noto-ui-core
fc-cache -fv
```

## Qt font pitfalls (fixed in this project)

1. **`QFont.StyleHint.Monospace`** on Windows can resolve to legacy **8514oem** and break Ethiopic → we use explicit `setFamilies()` only.
2. **PyQt6 `WordUnderCursor`** moved to `QTextCursor.SelectionType.WordUnderCursor` → we use Unicode-safe `_prefix_under_cursor()` instead.
3. **Autocomplete on `isalnum()`** triggers for Ethiopic letters → restricted to **ASCII** so IME typing is not interrupted.

## Amharic keyboard

- Enable **Windows**: Settings → Time & language → Language → Amharic keyboard
- The editor enables `WA_InputMethodEnabled` and forwards `inputMethodEvent` for IME composition.
- Do not use `Key_Escape` handlers that steal focus during composition.

## Optional: keyword palette

Use the **እይታ** menu or type AML keywords from autocomplete (Ctrl+Space can be added). Snippets in `editor/autocomplete.py` include `if block`, `while`, etc.
