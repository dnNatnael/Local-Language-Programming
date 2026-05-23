# -*- coding: utf-8 -*-
"""Basic autocomplete for AML keywords and snippets."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QCompleter
from PyQt6.QtGui import QStandardItemModel, QStandardItem

from .keywords import AML_KEYWORDS

SNIPPETS = [
    ("if block", "ከሆነ \n    \nመጨረሻ"),
    ("if-else", "ከሆነ \n    \nካልሆነ\n    \nመጨረሻ"),
    ("while", "እስከ \n    \nመጨረሻ"),
    ("function", "ተግባር ())\n    መልስ \nመጨረሻ"),
    ("print", "አትም "),
    ("number var", "ቁጥር  = "),
    ("text var", "ጽሑፍ  = "),
]


def build_completer(parent=None) -> QCompleter:
    """Create a QCompleter with AML keywords and snippet labels."""
    items = list(AML_KEYWORDS)
    for label, _ in SNIPPETS:
        items.append(label)
    model = QStandardItemModel()
    for word in sorted(set(items), key=len, reverse=True):
        model.appendRow(QStandardItem(word))
    completer = QCompleter(model, parent)
    completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
    completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
    completer.setFilterMode(Qt.MatchFlag.MatchContains)
    return completer


SNIPPET_MAP = {label: text for label, text in SNIPPETS}
