# -*- coding: utf-8 -*-
"""Bottom output panel: program output, errors, generated Python, logs."""

from PyQt6.QtCore import pyqtSignal
from editor.fonts import get_editor_font
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QPlainTextEdit,
    QLabel,
    QHBoxLayout,
    QPushButton,
)


class OutputPanel(QWidget):
    """Tabbed terminal/output area with Run / Translate controls."""

    run_clicked = pyqtSignal()
    translate_clicked = pyqtSignal()
    clear_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QHBoxLayout()
        header.setContentsMargins(6, 5, 6, 4)
        header.setSpacing(6)

        header.addWidget(QLabel("ውጤት"))

        self._translate_btn = QPushButton("ተርጉም")
        self._translate_btn.setToolTip("ወደ Python ተርጉም (Ctrl+T)")
        self._translate_btn.clicked.connect(self.translate_clicked.emit)
        header.addWidget(self._translate_btn)

        self._clear_btn = QPushButton("አጽዳ")
        self._clear_btn.setToolTip("የውጤት መስኮቶችን አጽዳ")
        self._clear_btn.clicked.connect(self._on_clear)
        header.addWidget(self._clear_btn)

        header.addStretch()

        self._run_btn = QPushButton("▶  ጀምር")
        self._run_btn.setToolTip("ፕሮግራሙን ተርጉም እና አስፈር (F5)")
        self._run_btn.setMinimumWidth(90)
        self._run_btn.clicked.connect(self.run_clicked.emit)
        self._run_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #1a8a3c, stop:1 #157030);
                border: 1px solid rgba(60,220,120,60);
                color: #ffffff;
                font-weight: 600;
                padding: 6px 16px;
                border-radius: 7px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #1ea044, stop:1 #1a8a3c);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #157030, stop:1 #105024);
            }
            QPushButton:disabled {
                background: rgba(30, 110, 60, 80);
                border-color: rgba(60, 180, 100, 30);
                color: rgba(180,210,190, 150);
            }
        """)
        header.addWidget(self._run_btn)
        layout.addLayout(header)

        self.tabs = QTabWidget()
        font = get_editor_font(10)

        self.output = self._make_view(font)
        self.errors = self._make_view(font)
        self.generated_py = self._make_view(font)
        self.logs = self._make_view(font)

        self.tabs.addTab(self.output, "ውጤት")
        self.tabs.addTab(self.errors, "ስህተቶች")
        self.tabs.addTab(self.generated_py, "Python")
        self.tabs.addTab(self.logs, "መዝገብ")
        layout.addWidget(self.tabs)

    def _make_view(self, font) -> QPlainTextEdit:
        view = QPlainTextEdit()
        view.setReadOnly(True)
        view.setFont(font)
        view.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        return view

    def clear_all(self):
        for w in (self.output, self.errors, self.generated_py, self.logs):
            w.clear()

    def show_output(self, text: str):
        self.output.setPlainText(text)
        self.tabs.setCurrentWidget(self.output)

    def show_errors(self, text: str):
        self.errors.setPlainText(text)
        self.tabs.setCurrentWidget(self.errors)

    def show_python(self, text: str):
        self.generated_py.setPlainText(text)
        self.tabs.setCurrentWidget(self.generated_py)

    def append_log(self, text: str):
        self.logs.appendPlainText(text)

    def set_log(self, text: str):
        self.logs.setPlainText(text)

    def _on_clear(self):
        self.clear_all()
        self.clear_clicked.emit()

    def set_running(self, running: bool):
        """Disable run controls while a job is in progress."""
        self._run_btn.setEnabled(not running)
        self._translate_btn.setEnabled(not running)
