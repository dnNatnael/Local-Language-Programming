# -*- coding: utf-8 -*-
"""QSyntaxHighlighter for Amharic Programming Language (.aml) source."""

from typing import List, Optional, Tuple

from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat

from .themes import EditorTheme, get_theme
from .keywords import AML_KEYWORDS

FUNCTION_DEF_KW = "ተግባር"


def _safe_regex(pattern: str) -> Optional[QRegularExpression]:
    """Build QRegularExpression only if valid (Qt has limited Unicode lookbehind)."""
    rx = QRegularExpression(pattern)
    if not rx.isValid():
        return None
    return rx


def _is_identifier_char(ch: str) -> bool:
    return bool(ch) and (ch == "_" or ch.isalnum())


class AmharicSyntaxHighlighter(QSyntaxHighlighter):
    """Highlight AML keywords, strings, numbers, comments, and operators."""

    def __init__(self, document, theme_name: str = "dark"):
        super().__init__(document)
        self._theme = get_theme(theme_name)
        self._rules: List[Tuple[QRegularExpression, QTextCharFormat]] = []
        self._function_fmt: Optional[QTextCharFormat] = None
        self._build_rules()

    def set_theme(self, theme: EditorTheme):
        self._theme = theme
        self._rules.clear()
        self._build_rules()
        self.rehighlight()

    def _fmt(self, color: str, bold: bool = False, italic: bool = False) -> QTextCharFormat:
        f = QTextCharFormat()
        f.setForeground(QColor(color))
        if bold:
            f.setFontWeight(QFont.Weight.Bold)
        if italic:
            f.setFontItalic(True)
        return f

    def _build_rules(self):
        t = self._theme
        self._function_fmt = self._fmt(t.function)

        for pattern, fmt in (
            (r"#[^\n]*", self._fmt(t.comment, italic=True)),
            (r'"[^"\\]*(\\.[^"\\]*)*"', self._fmt(t.string)),
            (r"'[^'\\]*(\\.[^'\\]*)*'", self._fmt(t.string)),
            (r"\d+(\.\d+)?", self._fmt(t.number)),
            (r"==|<=|>=|[+\-*/=<>(),]", self._fmt(t.operator)),
        ):
            rx = _safe_regex(pattern)
            if rx:
                self._rules.append((rx, fmt))

    def _highlight_keywords(self, text: str, keyword_fmt: QTextCharFormat):
        """Literal keyword search — reliable for Amharic (Qt \\b is ASCII-centric)."""
        for kw in AML_KEYWORDS:
            start = 0
            while True:
                idx = text.find(kw, start)
                if idx == -1:
                    break
                before = text[idx - 1] if idx > 0 else ""
                after_idx = idx + len(kw)
                after = text[after_idx] if after_idx < len(text) else ""
                if not _is_identifier_char(before) and not _is_identifier_char(after):
                    self.setFormat(idx, len(kw), keyword_fmt)
                start = idx + len(kw)

    def _highlight_function_names(self, text: str):
        """Highlight name after ተግባር without regex lookbehind."""
        if not self._function_fmt:
            return
        kw = FUNCTION_DEF_KW
        start = 0
        while True:
            idx = text.find(kw, start)
            if idx == -1:
                break
            pos = idx + len(kw)
            while pos < len(text) and text[pos].isspace():
                pos += 1
            name_start = pos
            while pos < len(text) and not text[pos].isspace() and text[pos] not in "(,":
                pos += 1
            if pos > name_start:
                self.setFormat(name_start, pos - name_start, self._function_fmt)
            start = idx + len(kw)

    def highlightBlock(self, text: str):
        if not text:
            return

        for pattern, fmt in self._rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), fmt)

        self._highlight_keywords(text, self._fmt(self._theme.keyword, bold=True))
        self._highlight_function_names(text)
