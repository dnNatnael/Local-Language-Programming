#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Amharic Code Editor — desktop IDE for AML (.aml) files.

Run:
    python main.py

From project root (PL/):
    python amharic_editor/main.py
"""

import sys
from pathlib import Path

# Ensure amharic_editor package and PL translator are importable
EDITOR_ROOT = Path(__file__).resolve().parent
PL_ROOT = EDITOR_ROOT.parent
for p in (str(EDITOR_ROOT), str(PL_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)


def _configure_encoding():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


def _apply_stylesheet(app):
    """Load and apply app.qss from the styles/ directory."""
    qss_path = EDITOR_ROOT / "styles" / "app.qss"
    if qss_path.exists():
        try:
            app.setStyleSheet(qss_path.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"[WARN] Could not load stylesheet: {exc}")


def main():
    _configure_encoding()

    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("Amharic Code Editor")
    app.setOrganizationName("AML")

    from editor.fonts import (
        apply_application_fonts,
        recommended_fonts_message,
        active_font_status,
    )

    apply_application_fonts(app)
    _apply_stylesheet(app)

    from ui.main_window import MainWindow

    window = MainWindow()
    hint = recommended_fonts_message() or active_font_status()
    window.statusBar().showMessage(hint, 12000)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
