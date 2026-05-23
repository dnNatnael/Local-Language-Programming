# -*- coding: utf-8 -*-
"""Custom code editor with line numbers, indentation, find, and zoom."""

from PyQt6.QtCore import Qt, QRect, QSize, pyqtSignal
from PyQt6.QtGui import QInputMethodEvent
from PyQt6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QTextCharFormat,
    QTextCursor,
    QTextDocument,
    QTextFormat,
)
from PyQt6.QtWidgets import (
    QPlainTextEdit,
    QWidget,
    QTextEdit,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QCheckBox,
)

from .syntax_highlighter import AmharicSyntaxHighlighter
from .autocomplete import build_completer, SNIPPET_MAP
from .themes import EditorTheme, get_theme, editor_stylesheet
from .fonts import get_editor_font

# PyQt6 / PySide6: ExtraSelection is on QTextEdit only; QPlainTextEdit still uses it.
ExtraSelection = getattr(QPlainTextEdit, "ExtraSelection", QTextEdit.ExtraSelection)


class LineNumberArea(QWidget):
    def __init__(self, editor: "CodeEditor"):
        super().__init__(editor)
        self._editor = editor

    def sizeHint(self) -> QSize:
        return QSize(self._editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self._editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    """Unicode-aware code editor for .aml files."""

    modification_changed = pyqtSignal(bool)
    cursor_line_changed = pyqtSignal(int, int)

    def __init__(self, parent=None, theme_name: str = "dark"):
        super().__init__(parent)
        self._theme = get_theme(theme_name)
        self._line_number_area = LineNumberArea(self)
        self._highlighter = AmharicSyntaxHighlighter(self.document(), theme_name)

        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setTabStopDistance(32)
        self.setFont(get_editor_font(11))
        # UTF-8 document; allow IME / Amharic keyboard (default, do not filter input)
        self.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled, True)
        self._apply_theme()

        self.blockCountChanged.connect(self._update_line_number_width)
        self.updateRequest.connect(self._update_line_number_area)
        self.cursorPositionChanged.connect(self._on_cursor_changed)
        self.textChanged.connect(self._on_text_changed)

        self._completer = build_completer(self)
        self._completer.setWidget(self)
        self._completer.activated.connect(self._insert_completion)
        self._ime_preedit = ""  # non-empty while Amharic IME is composing

        self._update_line_number_width(0)

    @property
    def highlighter(self) -> AmharicSyntaxHighlighter:
        return self._highlighter

    def set_theme(self, theme: EditorTheme):
        self._theme = theme
        self._highlighter.set_theme(theme)
        self._apply_theme()
        self._line_number_area.update()

    def _apply_theme(self):
        self.setStyleSheet(editor_stylesheet(self._theme))
        pal = self.palette()
        pal.setColor(self.backgroundRole(), QColor(self._theme.background))
        pal.setColor(self.foregroundRole(), QColor(self._theme.foreground))
        self.setPalette(pal)

    def line_number_area_width(self) -> int:
        digits = max(2, len(str(max(1, self.blockCount()))))
        return 12 + self.fontMetrics().horizontalAdvance("9") * digits

    def _update_line_number_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def _update_line_number_area(self, rect, dy):
        if dy:
            self._line_number_area.scroll(0, dy)
        else:
            self._line_number_area.update(
                0, rect.y(), self._line_number_area.width(), rect.height()
            )
        if rect.contains(self.viewport().rect()):
            self._update_line_number_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def line_number_area_paint_event(self, event):
        painter = QPainter(self._line_number_area)
        # fill background
        painter.fillRect(event.rect(), QColor(self._theme.line_number_bg))
        # draw a subtle right-border line
        line = QColor(self._theme.border)
        line.setAlphaF(0.45)
        painter.setPen(line)
        right = self._line_number_area.width() - 1
        painter.drawLine(right, event.rect().top(), right, event.rect().bottom())

        painter.setPen(QColor(self._theme.line_number_fg))
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(
            self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        )
        bottom = top + round(self.blockBoundingRect(block).height())
        height = self.fontMetrics().height()
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                # Highlight current line number
                if block_number == self.textCursor().blockNumber():
                    hl_bg = QColor(self._theme.accent)
                    hl_bg.setAlphaF(0.12)
                    painter.fillRect(
                        0, top, right, height, hl_bg
                    )
                    cur_fg = QColor(self._theme.accent)
                    painter.setPen(cur_fg)
                else:
                    painter.setPen(QColor(self._theme.line_number_fg))
                painter.drawText(
                    0,
                    top,
                    right - 3,
                    height,
                    int(Qt.AlignmentFlag.AlignRight),
                    str(block_number + 1),
                )
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1
        painter.end()

    def _on_cursor_changed(self):
        line = self.textCursor().blockNumber() + 1
        col = self.textCursor().columnNumber() + 1
        self.cursor_line_changed.emit(line, col)
        extra = []
        if not self.isReadOnly():
            sel = self.extraSelections()
            line_sel = ExtraSelection()
            line_color = QColor(self._theme.current_line)
            line_sel.format.setBackground(line_color)
            line_sel.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            line_sel.cursor = self.textCursor()
            line_sel.cursor.clearSelection()
            extra.append(line_sel)
            self.setExtraSelections(extra)

    def _on_text_changed(self):
        self.modification_changed.emit(self.document().isModified())

    def inputMethodEvent(self, event: QInputMethodEvent):
        """Allow Windows/macOS/Linux IME for Amharic composition."""
        self._ime_preedit = event.preeditString() or ""
        super().inputMethodEvent(event)
        if not self._ime_preedit:
            self._on_cursor_changed()

    def _ime_composing(self) -> bool:
        """True while an input method is composing (e.g. Amharic syllables)."""
        return bool(self._ime_preedit)

    def keyPressEvent(self, event):
        # Never interfere with IME composition (Amharic keyboard)
        if self._ime_composing():
            super().keyPressEvent(event)
            return

        if self._completer.popup().isVisible():
            if event.key() in (
                Qt.Key.Key_Enter,
                Qt.Key.Key_Return,
                Qt.Key.Key_Escape,
                Qt.Key.Key_Tab,
                Qt.Key.Key_Backtab,
            ):
                event.ignore()
                return

        # Auto-indent on Enter
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            cursor = self.textCursor()
            line_text = cursor.block().text()
            indent = len(line_text) - len(line_text.lstrip())
            if line_text.rstrip().endswith(":") or any(
                line_text.strip().startswith(k)
                for k in ("ከሆነ", "ካልሆነ", "እስከ", "ተግባር")
            ):
                indent += 4
            super().keyPressEvent(event)
            self.insertPlainText(" " * indent)
            return

        # Tab → 4 spaces
        if event.key() == Qt.Key.Key_Tab:
            self.insertPlainText("    ")
            return

        # Autocomplete for ASCII only (Amharic uses IME; avoids WordUnderCursor issues)
        if event.text() and event.text()[-1].isascii() and event.text()[-1].isalnum():
            super().keyPressEvent(event)
            self._update_completer()
            return

        super().keyPressEvent(event)

    def _prefix_under_cursor(self) -> str:
        """Unicode-safe prefix for autocomplete (Ethiopic + ASCII identifiers)."""
        tc = self.textCursor()
        block = tc.block()
        text = block.text()
        col = tc.positionInBlock()
        if col > len(text):
            col = len(text)
        start = col
        while start > 0 and self._is_word_char(text[start - 1]):
            start -= 1
        return text[start:col]

    @staticmethod
    def _is_word_char(ch: str) -> bool:
        return bool(ch) and (ch == "_" or ch.isalnum())

    def _update_completer(self):
        prefix = self._prefix_under_cursor()
        if len(prefix) < 1:
            self._completer.popup().hide()
            return
        self._completer.setCompletionPrefix(prefix)
        popup = self._completer.popup()
        popup.setCurrentIndex(self._completer.completionModel().index(0, 0))
        cr = self.cursorRect()
        cr.setWidth(
            popup.sizeHintForColumn(0) + popup.verticalScrollBar().sizeHint().width()
        )
        self._completer.complete(cr)

    def _insert_completion(self, completion: str):
        if completion in SNIPPET_MAP:
            text = SNIPPET_MAP[completion]
        else:
            text = completion
        tc = self.textCursor()
        extra = len(self._prefix_under_cursor())
        if extra > 0:
            tc.movePosition(
                QTextCursor.MoveOperation.Left,
                QTextCursor.MoveMode.KeepAnchor,
                extra,
            )
        tc.removeSelectedText()
        tc.insertText(text)
        self.setTextCursor(tc)

    def zoom_in_editor(self):
        font = self.font()
        font.setPointSize(min(24, font.pointSize() + 1))
        self.setFont(font)
        self._update_line_number_width(0)

    def zoom_out_editor(self):
        font = self.font()
        font.setPointSize(max(8, font.pointSize() - 1))
        self.setFont(font)
        self._update_line_number_width(0)

    def reset_zoom(self):
        self.setFont(get_editor_font(11))
        self._update_line_number_width(0)

    def highlight_error_line(self, line: int):
        """Mark a line with error background (1-based line number)."""
        extra = []
        if line > 0:
            sel = ExtraSelection()
            sel.format.setBackground(QColor("#5a1d1d"))
            sel.format.setUnderlineColor(QColor(self._theme.error))
            sel.format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.WaveUnderline)
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            cursor.movePosition(
                QTextCursor.MoveOperation.Down,
                QTextCursor.MoveMode.MoveAnchor,
                line - 1,
            )
            sel.cursor = cursor
            sel.cursor.clearSelection()
            extra.append(sel)
        self.setExtraSelections(extra)

    def clear_error_highlight(self):
        self._on_cursor_changed()


class FindDialog(QDialog):
    """Simple find bar for the editor."""

    def __init__(self, editor: CodeEditor, parent=None):
        super().__init__(parent)
        self._editor = editor
        self.setWindowTitle("ፈልግ")
        layout = QVBoxLayout(self)
        row = QHBoxLayout()
        self._input = QLineEdit()
        self._input.setPlaceholderText("ፈልግ...")
        row.addWidget(self._input)
        self._case = QCheckBox("ትክክለኛ")
        row.addWidget(self._case)
        layout.addLayout(row)
        btn_row = QHBoxLayout()
        find_btn = QPushButton("ቀጣይ")
        find_btn.clicked.connect(self._find_next)
        prev_btn = QPushButton("ቀዳሚ")
        prev_btn.clicked.connect(self._find_prev)
        close_btn = QPushButton("ዝጋ")
        close_btn.clicked.connect(self.close)
        btn_row.addWidget(find_btn)
        btn_row.addWidget(prev_btn)
        btn_row.addStretch()
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)
        self._input.returnPressed.connect(self._find_next)

    def _flags(self):
        flags = QTextDocument.FindFlag(0)
        if self._case.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        return flags

    def _find_next(self):
        text = self._input.text()
        if not text:
            return
        found = self._editor.find(text, self._flags())
        if not found:
            cursor = self._editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self._editor.setTextCursor(cursor)
            self._editor.find(text, self._flags())

    def _find_prev(self):
        text = self._input.text()
        if not text:
            return
        flags = self._flags() | QTextDocument.FindFlag.FindBackward
        self._editor.find(text, flags)
