# -*- coding: utf-8 -*-
"""
Ethiopic/Unicode font configuration for the Amharic Code Editor.

Best practices:
- Use explicit font families (avoid QFont.StyleHint.Monospace on Windows — it can
  resolve to legacy bitmap fonts like "8514oem" and break Ethiopic glyphs).
- Prefer Noto Sans Ethiopic / Abyssinica SIL for UI; monospace stack for code.
- Apply fonts via QApplication.setFont() and per-widget setFont() for consistency.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List, Optional

from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtWidgets import QApplication, QWidget

_fonts_bootstrapped = False

# Preferred families (first installed match is used by Qt fallback chain)
ETHIOPIC_UI_FAMILIES = [
    "Noto Sans Ethiopic",
    "Abyssinica SIL",
    "Nyala",
    "Segoe UI",
    "Tahoma",
    "Arial Unicode MS",
    "sans-serif",
]

ETHIOPIC_MONO_FAMILIES = [
    "Cascadia Mono",
    "Cascadia Code",
    "Consolas",
    "Noto Sans Mono",
    "Noto Sans Ethiopic",
    "Abyssinica SIL",
    "DejaVu Sans Mono",
    "monospace",
]


def register_system_ethiopic_fonts() -> List[str]:
    """
    Load Ethiopic fonts from the OS fonts folder into Qt.
    Call once at startup so newly installed fonts work without reboot.
    """
    global _fonts_bootstrapped
    if _fonts_bootstrapped:
        return []
    _fonts_bootstrapped = True
    loaded: List[str] = []
    search_dirs: List[Path] = []
    if sys.platform == "win32":
        windir = os.environ.get("WINDIR", r"C:\Windows")
        search_dirs.append(Path(windir) / "Fonts")
        search_dirs.append(Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "Windows" / "Fonts")
    else:
        search_dirs.extend([
            Path("/usr/share/fonts"),
            Path("/usr/local/share/fonts"),
            Path.home() / ".fonts",
            Path.home() / ".local/share/fonts",
        ])
    patterns = (
        "NotoSansEthiopic*.ttf",
        "NotoSansEthiopic*.otf",
        "Noto*Ethiopic*.ttf",
        "AbyssinicaSIL*.ttf",
        "Nyala*.ttf",
    )
    seen = set()
    for directory in search_dirs:
        if not directory.is_dir():
            continue
        for pattern in patterns:
            for font_file in directory.glob(pattern):
                key = str(font_file.resolve()).lower()
                if key in seen:
                    continue
                seen.add(key)
                fid = QFontDatabase.addApplicationFont(str(font_file))
                if fid >= 0:
                    loaded.extend(QFontDatabase.applicationFontFamilies(fid))
    return loaded


def _installed_families() -> set:
    register_system_ethiopic_fonts()
    return set(QFontDatabase.families())


def _pick_first_available(candidates: List[str]) -> Optional[str]:
    installed = _installed_families()
    for name in candidates:
        if name in installed:
            return name
    return None


def get_ui_font(point_size: int = 10) -> QFont:
    """Font for menus, sidebars, tabs, labels — full Ethiopic coverage."""
    primary = _pick_first_available(ETHIOPIC_UI_FAMILIES) or "Segoe UI"
    font = QFont(primary, point_size)
    font.setFamilies(ETHIOPIC_UI_FAMILIES)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    return font


def get_editor_font(point_size: int = 11) -> QFont:
    """
    Font for the code editor and output panels.
    No Monospace style hint — explicit families only (prevents 8514oem on Windows).
    """
    primary = _pick_first_available(ETHIOPIC_MONO_FAMILIES) or "Consolas"
    font = QFont(primary, point_size)
    font.setFamilies(ETHIOPIC_MONO_FAMILIES)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    font.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
    return font


def apply_application_fonts(app: QApplication) -> None:
    """Set global UI font; editor widgets set monospace font explicitly."""
    register_system_ethiopic_fonts()
    app.setFont(get_ui_font())


def active_font_status() -> str:
    """Short status line: which Ethiopic font Qt is using."""
    register_system_ethiopic_fonts()
    ui = _pick_first_available(ETHIOPIC_UI_FAMILIES) or "Segoe UI"
    if ui in ("Noto Sans Ethiopic", "Abyssinica SIL", "Nyala"):
        return f"ፊደል: {ui} ✓"
    return f"ፊደል: {ui} (Noto Sans Ethiopic ይጫን ከሆነ ዳግም ይጀምሩ)"


def apply_widget_font(widget: QWidget, *, monospace: bool = False, point_size: Optional[int] = None) -> None:
    font = get_editor_font() if monospace else get_ui_font()
    if point_size is not None:
        font.setPointSize(point_size)
    widget.setFont(font)
    # Propagate to common child types that don't inherit stylesheet fonts
    for child in widget.findChildren(QWidget):
        if child.font().pointSize() <= 0 or child.font().family() in ("MS Shell Dlg 2", "8514oem"):
            child.setFont(font)


def recommended_fonts_message() -> str:
    """User-facing hint when Ethiopic fonts are missing."""
    installed = _installed_families()
    has_ethiopic = any(f in installed for f in ("Noto Sans Ethiopic", "Abyssinica SIL", "Nyala"))
    if has_ethiopic:
        return ""
    return (
        "ለአማርኛ ምልክት ይህን ይጫኑ: Noto Sans Ethiopic ወይም Abyssinica SIL\n"
        "Install: https://fonts.google.com/noto/specimen/NotoSansEthiopic"
    )
