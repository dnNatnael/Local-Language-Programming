# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec — run from PL/ directory:
#   pyinstaller amharic_editor/build.spec

from pathlib import Path

block_cipher = None
pl_root = Path(SPECPATH).resolve().parent.parent
editor_root = pl_root / "amharic_editor"

a = Analysis(
    [str(editor_root / "main.py")],
    pathex=[str(pl_root), str(editor_root)],
    binaries=[],
    datas=[
        (str(pl_root / "src"), "src"),
        (str(pl_root / "translator.py"), "."),
    ],
    hiddenimports=[
        "src.lexer",
        "src.parser",
        "src.codegen",
        "src.errors",
        "src.ast_nodes",
        "translator",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="AmharicCodeEditor",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
