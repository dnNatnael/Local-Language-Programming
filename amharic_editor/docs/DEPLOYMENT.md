# Deployment Guide

## Development Setup

### Windows 10/11

```powershell
cd C:\Users\hp\Desktop\PL
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r amharic_editor\requirements.txt
pip install pyinstaller   # optional, for packaging
python amharic_editor\main.py
```

Install [Node.js LTS](https://nodejs.org/) for the Run feature.

Recommended fonts: **Segoe UI**, **Noto Sans Ethiopic**, **Nyala**.

### Ubuntu 22.04+

```bash
cd ~/Desktop/PL
python3 -m venv .venv
source .venv/bin/activate
pip install -r amharic_editor/requirements.txt
sudo apt install nodejs   # or nvm install --lts
python3 amharic_editor/main.py
```

PyQt6 system package (optional):

```bash
sudo apt install python3-pyqt6
```

Fonts:

```bash
sudo apt install fonts-noto-core fonts-noto-ui-core
```

## PyInstaller (Windows .exe)

```bash
cd PL
pip install pyinstaller PyQt6
pyinstaller amharic_editor/build.spec --noconfirm
```

Output: `dist/AmharicCodeEditor.exe`

**Note:** Ship the whole `PL` folder next to the exe OR bundle `src/` and `translator.py` via `datas` in `build.spec` if you need a standalone folder:

```python
datas=[
    (str(pl_root / 'src'), 'src'),
    (str(pl_root / 'translator.py'), '.'),
],
```

## PyInstaller (Linux)

```bash
pyinstaller amharic_editor/build.spec --noconfirm
./dist/AmharicCodeEditor
```

For AppImage, use `appimage-builder` or `linuxdeploy` wrapping the PyInstaller output.

## cx_Freeze (alternative)

```python
# setup_freeze.py (create if needed)
from cx_Freeze import setup, Executable
setup(
    name="AmharicCodeEditor",
    executables=[Executable("amharic_editor/main.py", base="Win32GUI")],
    options={"build_exe": {"packages": ["PyQt6", "src"], "include_files": ["translator.py", "src"]}},
)
```

## Debian .deb (outline)

1. Install files to `/opt/aml-editor/`
2. Wrapper script `/usr/bin/amharic-editor`:

```bash
#!/bin/sh
cd /opt/aml-editor/PL && exec /opt/aml-editor/venv/bin/python amharic_editor/main.py "$@"
```

3. Desktop entry:

```ini
[Desktop Entry]
Name=Amharic Code Editor
Exec=amharic-editor
Icon=aml-editor
Type=Application
Categories=Development;Education;
```

## Post-install Checklist

- [ ] `python amharic_editor/main.py` launches
- [ ] Open `examples/01_variables.aml`
- [ ] Ctrl+T translates
- [ ] F5 runs and shows `30` in output
- [ ] Amharic keywords highlight correctly
- [ ] Syntax error shows Amharic message in Errors tab

## Environment Variables

| Variable | Effect |
|----------|--------|
| `PYTHONIOENCODING=utf-8` | Safer console on Windows |
| `QT_SCALE_FACTOR` | HiDPI scaling if needed |

## Known Platform Notes

- **Windows:** PyInstaller `--console=False` for GUI-only exe.
- **Linux:** May need `libxcb-cursor0` for Qt6 on minimal installs.
- **Wayland:** Qt6 generally works; set `QT_QPA_PLATFORM=xcb` if issues occur.
