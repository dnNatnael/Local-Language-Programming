# -*- coding: utf-8 -*-
"""Main application window — menus, tabs, integration, themes."""

import json
import tempfile
from pathlib import Path
from typing import Dict, Optional

from PyQt6.QtCore import Qt, QTimer, QSettings, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence, QFont
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QTabWidget,
    QFileDialog,
    QMessageBox,
    QStatusBar,
    QLabel,
    QApplication,
    QMenu,
)

from editor.editor_widget import CodeEditor, FindDialog
from editor.themes import get_theme, THEMES
from ui.sidebar import FileExplorerSidebar
from ui.terminal_panel import OutputPanel
from ui.toolbar import EditorToolBar
from ui.keywords_dialog import KeywordsDialog
from ui.user_guide_dialog import UserGuideDialog
from integration.translator_runner import translate_source, translate_file
from integration.python_runner import run_python, find_python

PL_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = PL_ROOT / "examples"
MAX_RECENT = 10


class WorkerThread(QThread):
    """Background thread for translate + run."""

    finished_ok = pyqtSignal(object)
    finished_err = pyqtSignal(str)

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self._fn = fn
        self._args = args
        self._kwargs = kwargs

    def run(self):
        try:
            result = self._fn(*self._args, **self._kwargs)
            self.finished_ok.emit(result)
        except Exception as e:
            self.finished_err.emit(str(e))


class EditorTab(QWidget):
    """Single tab: CodeEditor + file path metadata."""

    def __init__(self, path: Optional[Path] = None, theme_name: str = "dark", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.editor = CodeEditor(theme_name=theme_name)
        layout.addWidget(self.editor)
        self.file_path: Optional[Path] = path
        if path and path.exists():
            self.editor.setPlainText(path.read_text(encoding="utf-8"))
            self.editor.document().setModified(False)

    def title(self) -> str:
        if self.file_path:
            name = self.file_path.name
            if self.editor.document().isModified():
                return f"● {name}"
            return name
        return "ያልተቀመጠ"

    def is_untitled(self) -> bool:
        return self.file_path is None


class MainWindow(QMainWindow):
    """Simple Amharic Code Editor — main IDE window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Amharic Code Editor")
        self.resize(1200, 800)
        self._settings = QSettings("AML", "AmharicEditor")
        self._theme_name = self._settings.value("theme", "dark", str)
        self._theme = get_theme(self._theme_name)
        self._find_dialog: Optional[FindDialog] = None
        self._keywords_dialog: Optional[KeywordsDialog] = None
        self._user_guide_dialog: Optional[UserGuideDialog] = None
        self._worker: Optional[WorkerThread] = None
        self._tabs: Dict[int, EditorTab] = {}

        self._build_ui()
        self._build_menus()
        self._setup_shortcuts()
        self._apply_window_theme()
        self._setup_autosave()

        # Default workspace
        root = self._settings.value("last_folder", str(EXAMPLES_DIR), str)
        if Path(root).exists():
            self._sidebar.set_root(root)
        elif EXAMPLES_DIR.exists():
            self._sidebar.set_root(str(EXAMPLES_DIR))

        self._open_tab()
        self._update_status("ዝግጁ")

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._sidebar = FileExplorerSidebar()
        self._sidebar.setMinimumWidth(180)
        self._sidebar.setMaximumWidth(320)
        self._sidebar.file_open_requested.connect(self._open_file_path)
        self._sidebar.new_file_requested.connect(self._handle_new_file_request)
        self._sidebar.file_renamed.connect(self._on_file_renamed)

        center_split = QSplitter(Qt.Orientation.Vertical)
        self._tab_widget = QTabWidget()
        self._tab_widget.setTabsClosable(True)
        self._tab_widget.setMovable(True)
        self._tab_widget.tabCloseRequested.connect(self._close_tab)
        self._tab_widget.currentChanged.connect(self._on_tab_changed)

        self._output = OutputPanel()
        self._output.setMinimumHeight(120)
        self._output.run_clicked.connect(self._run_current)
        self._output.translate_clicked.connect(self._translate_current)

        center_split.addWidget(self._tab_widget)
        center_split.addWidget(self._output)
        center_split.setStretchFactor(0, 4)
        center_split.setStretchFactor(1, 1)

        self._splitter.addWidget(self._sidebar)
        self._splitter.addWidget(center_split)
        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 1)

        main_layout.addWidget(self._splitter)

        self._toolbar = EditorToolBar(self)
        self.addToolBar(self._toolbar)
        self._toolbar.new_clicked.connect(self._new_file)
        self._toolbar.open_clicked.connect(self._open_file)
        self._toolbar.save_clicked.connect(self._save_file)
        self._toolbar.translate_clicked.connect(self._translate_current)
        self._toolbar.run_clicked.connect(self._run_current)
        self._toolbar.find_clicked.connect(self._show_find)
        self._toolbar.keywords_clicked.connect(self._show_keywords)
        self._toolbar.user_guide_clicked.connect(self._show_user_guide)

        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._status_label = QLabel()
        self._status_pos = QLabel()
        self._status_theme = QLabel(self._theme_name)
        self._status.addWidget(self._status_label, 1)
        self._status.addPermanentWidget(self._status_pos)
        self._status.addPermanentWidget(self._status_theme)

    def _add_menu_action(self, menu, text, slot, shortcut=None):
        """PyQt6-compatible menu action (text, shortcut, slot order)."""
        action = QAction(text, self)
        if shortcut is not None:
            action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(slot)
        menu.addAction(action)
        return action

    def _build_menus(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("ፋይል")
        self._add_menu_action(file_menu, "አዲስ", self._new_file, QKeySequence.StandardKey.New)
        self._add_menu_action(file_menu, "ክፈት...", self._open_file, QKeySequence.StandardKey.Open)
        self._add_menu_action(file_menu, "አስቀምጥ", self._save_file, QKeySequence.StandardKey.Save)
        self._add_menu_action(file_menu, "እንደ...", self._save_file_as, "Ctrl+Shift+S")
        file_menu.addSeparator()
        self._recent_menu = file_menu.addMenu("የቅርብ ጊዜ")
        self._refresh_recent_menu()
        file_menu.addSeparator()
        self._add_menu_action(file_menu, "ውጣ", self.close, QKeySequence.StandardKey.Quit)

        edit_menu = menubar.addMenu("አርትዕ")
        self._add_menu_action(edit_menu, "ፈልግ", self._show_find, QKeySequence.StandardKey.Find)
        self._add_menu_action(edit_menu, "ቁልፍ ቃላት", self._show_keywords)
        self._add_menu_action(edit_menu, "የተጠቃሚ መመሪያ ሰነድ", self._show_user_guide)
        self._add_menu_action(edit_menu, "ዱቄት+ ", self._zoom_in, QKeySequence.StandardKey.ZoomIn)
        self._add_menu_action(edit_menu, "ዱቄት- ", self._zoom_out, QKeySequence.StandardKey.ZoomOut)

        run_menu = menubar.addMenu("ፕሮግራም")
        self._add_menu_action(run_menu, "ተርጉም", self._translate_current, "Ctrl+T")
        self._add_menu_action(run_menu, "ጀምር (F5)", self._run_current, "F5")

        view_menu = menubar.addMenu("እይታ")
        theme_menu = view_menu.addMenu("ገጽታ")
        for name in THEMES:
            act = QAction(name.capitalize(), self)
            act.triggered.connect(lambda checked, n=name: self._set_theme(n))
            theme_menu.addAction(act)
        self._add_menu_action(
            view_menu,
            "አቃፊ መስታወት",
            lambda: self._sidebar.setVisible(not self._sidebar.isVisible()),
        )
        self._add_menu_action(
            view_menu,
            "ውጤት መስታወት",
            lambda: self._output.setVisible(not self._output.isVisible()),
        )

        help_menu = menubar.addMenu("እገዛ")
        examples_menu = help_menu.addMenu("ምሳሌ ፕሮግራሞች")
        example_files = [
            ("1. ቁጥሮች (Variables)", "01_variables.aml"),
            ("2. ገላጮች (Expressions)", "02_expressions.aml"),
            ("3. ከሆነ/ካልሆነ (If/Else)", "03_conditionals.aml"),
            ("4. እስከ (While)", "04_while_loop.aml"),
            ("5. ተግባር (Functions)", "05_functions.aml"),
        ]
        for label, filename in example_files:
            path = EXAMPLES_DIR / filename
            if path.exists():
                act = QAction(label, self)
                act.triggered.connect(
                    lambda checked, p=str(path): self._open_file_path(p)
                )
                examples_menu.addAction(act)
        help_menu.addSeparator()
        readme = EXAMPLES_DIR / "README.md"
        if readme.exists():
            act = QAction("ምሳሌ መመሪያ (README)", self)
            act.triggered.connect(
                lambda: self._open_file_path(str(readme))
            )
            help_menu.addAction(act)
        self._add_menu_action(help_menu, "ስለ", self._show_about)

    def _setup_shortcuts(self):
        pass  # bound in menu actions

    def _apply_window_theme(self):
        t = self._theme
        from editor.fonts import ETHIOPIC_UI_FAMILIES
        families = ", ".join(f"'{f}'" for f in ETHIOPIC_UI_FAMILIES[:6])
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {t.background};
                color: {t.foreground};
                font-family: {families};
            }}
            QMenuBar, QMenu, QToolBar, QTabBar, QTabWidget, QTreeView,
            QStatusBar, QLabel, QPushButton, QLineEdit, QPlainTextEdit {{
                font-family: {families};
            }}
            QMenuBar, QMenu {{
                background-color: {t.toolbar_bg};
                color: {t.foreground};
            }}
            QToolBar {{
                background-color: {t.toolbar_bg};
                border-bottom: 1px solid {t.border};
                spacing: 6px;
            }}
            QTabWidget::pane {{
                border: 1px solid {t.border};
            }}
            QTabBar::tab {{
                background: {t.sidebar_bg};
                padding: 6px 12px;
            }}
            QTabBar::tab:selected {{
                background: {t.background};
            }}
            QTreeView {{
                background-color: {t.sidebar_bg};
                color: {t.foreground};
            }}
            QStatusBar {{
                background-color: {t.status_bg};
                color: white;
            }}
            QSplitter::handle {{
                background: {t.border};
            }}
        """)

    def _setup_autosave(self):
        self._autosave_timer = QTimer(self)
        self._autosave_timer.timeout.connect(self._autosave)
        self._autosave_timer.start(60_000)  # every 60 seconds

    def _current_tab(self) -> Optional[EditorTab]:
        w = self._tab_widget.currentWidget()
        return w if isinstance(w, EditorTab) else None

    def _current_editor(self) -> Optional[CodeEditor]:
        tab = self._current_tab()
        return tab.editor if tab else None

    def _open_tab(self, path: Optional[Path] = None) -> EditorTab:
        tab = EditorTab(path, theme_name=self._theme_name)
        tab.editor.cursor_line_changed.connect(self._on_cursor_line)
        idx = self._tab_widget.addTab(tab, tab.title())
        self._tab_widget.setCurrentIndex(idx)
        return tab

    def _on_tab_changed(self, index: int):
        tab = self._tab_widget.widget(index)
        if isinstance(tab, EditorTab):
            self._tab_widget.setTabText(index, tab.title())

    def _on_cursor_line(self, line: int, col: int):
        self._status_pos.setText(f"ረድፍ {line}, አምድ {col}")

    def _update_status(self, msg: str):
        self._status_label.setText(msg)

    def _new_file(self):
        self._open_tab()

    def _handle_new_file_request(self, folder: str, default_name: str):
        new_path = self._sidebar.create_file_for_inline_rename(folder, default_name)
        if new_path:
            self._open_tab(Path(new_path))
            self._sidebar.set_root(str(Path(new_path).parent))
            self._update_status(f"አዲስ ፋይል: {Path(new_path).name}")
            QTimer.singleShot(200, lambda: self._start_renaming(Path(new_path)))

    def _start_renaming(self, file_path: Path):
        self._sidebar.start_rename_file(str(file_path))

    def _on_file_renamed(self, old_path: str, new_path: str):
        for i in range(self._tab_widget.count()):
            tab = self._tab_widget.widget(i)
            if isinstance(tab, EditorTab) and tab.file_path:
                if tab.file_path == Path(old_path):
                    tab.file_path = Path(new_path)
                    self._tab_widget.setTabText(i, tab.title())
                    break

    def _create_new_file_in_folder(self, folder: str):
        folder_path = Path(folder)
        if not folder_path.exists():
            return

        base_name = "አዲስ ፋይል"
        counter = 1
        new_path = folder_path / f"{base_name}.aml"
        while new_path.exists():
            counter += 1
            new_path = folder_path / f"{base_name} ({counter}).aml"

        self._open_tab(new_path)
        self._sidebar.set_root(str(folder_path))
        self._update_status(f"አዲስ ፋይል: {new_path.name}")

    def _open_file(self):
        start = self._settings.value("last_folder", str(PL_ROOT), str)
        path, _ = QFileDialog.getOpenFileName(
            self,
            "AML ፋይል ክፈት",
            start,
            "AML ፋይሎች (*.aml);;ሁሉም (*.*)",
        )
        if path:
            self._open_file_path(path)

    def _open_file_path(self, path: str):
        p = Path(path)
        # Already open?
        for i in range(self._tab_widget.count()):
            tab = self._tab_widget.widget(i)
            if isinstance(tab, EditorTab) and tab.file_path == p:
                self._tab_widget.setCurrentIndex(i)
                return
        self._add_recent(p)
        self._settings.setValue("last_folder", str(p.parent))
        tab = self._open_tab(p)
        self._sidebar.set_root(str(p.parent))
        self._update_status(f"ተከፈተ: {p.name}")

    def _save_file(self) -> bool:
        tab = self._current_tab()
        if not tab:
            return False
        if tab.is_untitled():
            return self._save_file_as()
        try:
            tab.file_path.write_text(tab.editor.toPlainText(), encoding="utf-8")
            tab.editor.document().setModified(False)
            self._tab_widget.setTabText(self._tab_widget.currentIndex(), tab.title())
            self._update_status("ተቀምጧል")
            return True
        except OSError as e:
            QMessageBox.critical(self, "ስህተት", f"ማስቀመጥ አልተሳካም: {e}")
            return False

    def _save_file_as(self) -> bool:
        tab = self._current_tab()
        if not tab:
            return False
        start = self._settings.value("last_folder", str(PL_ROOT), str)
        path, _ = QFileDialog.getSaveFileName(
            self, "እንደ...", start, "AML (*.aml)"
        )
        if not path:
            return False
        if not path.endswith(".aml"):
            path += ".aml"
        tab.file_path = Path(path)
        return self._save_file()

    def _autosave(self):
        tab = self._current_tab()
        if tab and tab.file_path and tab.editor.document().isModified():
            try:
                tab.file_path.write_text(tab.editor.toPlainText(), encoding="utf-8")
                self._output.append_log(f"[አውቶ] ተቀምጧል: {tab.file_path.name}")
            except OSError:
                pass

    def _close_tab(self, index: int):
        tab = self._tab_widget.widget(index)
        if isinstance(tab, EditorTab) and tab.editor.document().isModified():
            r = QMessageBox.question(
                self,
                "ማስቀመጥ",
                "ለውጦች ይቀመጡ?",
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
            )
            r_custom = (
                QMessageBox.Save
                if r == QMessageBox.StandardButton.Save
                else (
                    QMessageBox.Discard
                    if r == QMessageBox.StandardButton.Discard
                    else QMessageBox.Cancel
                )
            )
            if r_custom == QMessageBox.Save:
                self._tab_widget.setCurrentIndex(index)
                if not self._save_file():
                    return
            elif r == QMessageBox.StandardButton.Cancel:
                return
        self._tab_widget.removeTab(index)

    def _show_find(self):
        editor = self._current_editor()
        if not editor:
            return
        if self._find_dialog is None:
            self._find_dialog = FindDialog(editor, self)
        self._find_dialog._editor = editor
        self._find_dialog.show()
        self._find_dialog.raise_()

    def _show_keywords(self):
        if self._keywords_dialog is None:
            self._keywords_dialog = KeywordsDialog(self)
            self._keywords_dialog.keyword_selected.connect(self._insert_keyword)
        self._keywords_dialog.show()
        self._keywords_dialog.raise_()
        self._keywords_dialog.activateWindow()

    def _show_user_guide(self):
        if not UserGuideDialog.warn_if_unavailable(self):
            return
        if self._user_guide_dialog is None:
            self._user_guide_dialog = UserGuideDialog(self, theme_name=self._theme_name)
        else:
            self._user_guide_dialog.refresh_theme(self._theme_name)
        self._user_guide_dialog.show()
        self._user_guide_dialog.raise_()
        self._user_guide_dialog.activateWindow()

    def _insert_keyword(self, keyword: str):
        editor = self._current_editor()
        if not editor or not keyword:
            return
        editor.textCursor().insertText(keyword + " ")
        editor.setFocus()

    def _zoom_in(self):
        e = self._current_editor()
        if e:
            e.zoom_in_editor()

    def _zoom_out(self):
        e = self._current_editor()
        if e:
            e.zoom_out_editor()

    def _set_theme(self, name: str):
        self._theme_name = name
        self._theme = get_theme(name)
        self._settings.setValue("theme", name)
        self._status_theme.setText(name)
        self._apply_window_theme()
        for i in range(self._tab_widget.count()):
            tab = self._tab_widget.widget(i)
            if isinstance(tab, EditorTab):
                tab.editor.set_theme(self._theme)
        if self._user_guide_dialog is not None and self._user_guide_dialog.isVisible():
            self._user_guide_dialog.refresh_theme(name)

    def _translate_current(self):
        tab = self._current_tab()
        if not tab:
            return
        if tab.editor.document().isModified() and tab.file_path:
            self._save_file()
        source = tab.editor.toPlainText()
        aml_path = tab.file_path
        self._output.clear_all()
        self._output.append_log("በመተርጎም ላይ...")
        self._update_status("በመተርጎም...")

        def do_translate():
            if aml_path:
                return translate_file(aml_path)
            tmp = Path(tempfile.gettempdir()) / "aml_editor_preview.py"
            return translate_source(source, output_path=tmp)

        self._run_worker(do_translate, self._on_translate_done)

    def _on_translate_done(self, result):
        editor = self._current_editor()
        if editor:
            editor.clear_error_highlight()
        if result.success:
            self._output.show_python(result.python)
            self._output.set_log(result.log)
            self._output.show_output("ተርጉም ተሳካ። F5 ይጫኑ ለመፈጸም።")
            self._update_status("ተተርጉሟል")
        else:
            self._output.show_errors(result.error_message)
            self._output.set_log(result.log)
            if result.error_line and editor:
                editor.highlight_error_line(result.error_line)
            self._update_status("የተርጎም ስህተት")

    def _run_current(self):
        tab = self._current_tab()
        if not tab:
            return
        if not find_python():
            QMessageBox.warning(
                self,
                "Python",
                "Python አልተገኘም። እባክዎ Python ይጫኑ።\nhttps://python.org",
            )
            return

        source = tab.editor.toPlainText()
        aml_path = tab.file_path

        def do_run():
            if aml_path:
                tr = translate_file(aml_path)
            else:
                tmp = Path(tempfile.gettempdir()) / "aml_editor_run.py"
                tr = translate_source(source, output_path=tmp)
            if not tr.success:
                return ("translate_fail", tr)
            py_path = tr.output_path
            if not py_path:
                return ("translate_fail", tr)
            run = run_python(py_path)
            return ("run", tr, run)

        self._output.clear_all()
        self._output.append_log("በማሄድ ላይ...")
        self._update_status("በማሄድ...")
        self._run_worker(do_run, self._on_run_done)

    def _on_run_done(self, payload):
        editor = self._current_editor()
        if editor:
            editor.clear_error_highlight()

        kind = payload[0]
        if kind == "translate_fail":
            tr = payload[1]
            self._output.show_errors(tr.error_message)
            if tr.error_line and editor:
                editor.highlight_error_line(tr.error_line)
            self._update_status("ስህተት")
            return

        _, tr, run = payload
        self._output.show_python(tr.python)
        self._output.append_log(tr.log)
        self._output.append_log(run.log)

        out_parts = []
        if run.stdout:
            out_parts.append(run.stdout.rstrip())
        if run.stderr:
            out_parts.append("---\n" + run.stderr.rstrip())
        self._output.show_output("\n".join(out_parts) or "(ምንም ውጤት የለም)")

        if not run.success:
            self._output.show_errors(run.stderr or f"Exit code {run.exit_code}")
            self._update_status("የመፈጸሚያ ስህተት")
        else:
            self._update_status("ተጠናቀቀ")

    def _run_worker(self, fn, on_done):
        if self._worker and self._worker.isRunning():
            self._output.append_log("ቀዳሚ ስራ እየተሰራ ነው...")
            return

        self._output.set_running(True)

        def _finish_ok(result):
            self._output.set_running(False)
            on_done(result)

        def _finish_err(msg):
            self._output.set_running(False)
            self._output.show_errors(f"ስህተት: {msg}")

        self._worker = WorkerThread(fn)
        self._worker.finished_ok.connect(_finish_ok)
        self._worker.finished_err.connect(_finish_err)
        self._worker.start()

    def _add_recent(self, path: Path):
        recent = self._get_recent()
        s = str(path.resolve())
        if s in recent:
            recent.remove(s)
        recent.insert(0, s)
        recent = recent[:MAX_RECENT]
        self._settings.setValue("recent_files", json.dumps(recent))
        self._refresh_recent_menu()

    def _get_recent(self):
        raw = self._settings.value("recent_files", "[]", str)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return []

    def _refresh_recent_menu(self):
        self._recent_menu.clear()
        for p in self._get_recent():
            if Path(p).exists():
                act = QAction(Path(p).name, self)
                act.setToolTip(p)
                act.triggered.connect(lambda checked, path=p: self._open_file_path(path))
                self._recent_menu.addAction(act)
        if not self._recent_menu.actions():
            empty = QAction("(ባዶ)", self)
            empty.setEnabled(False)
            self._recent_menu.addAction(empty)

    def _show_about(self):
        QMessageBox.about(
            self,
            "Simple Amharic Code Editor",
            "<b>Simple Amharic Code Editor</b><br>"
            "አማርኛ ፕሮግራሚንግ ቋንቋ (AML) አርታዒ<br><br>"
            "PyQt6 • Unicode • AML → Python<br>"
            f"Translator: {PL_ROOT}",
        )

    def closeEvent(self, event):
        for i in range(self._tab_widget.count()):
            tab = self._tab_widget.widget(i)
            if isinstance(tab, EditorTab) and tab.editor.document().isModified():
                self._tab_widget.setCurrentIndex(i)
                w = QMessageBox(
                    QMessageBox.Icon.Question,
                    "ማስቀመጥ",
                    f"'{tab.title()}' ይቀመጥ?",
                    QMessageBox.StandardButton.NoButton,
                    self,
                )
                yes_btn = w.addButton("አዎ", QMessageBox.ButtonRole.YesRole)
                no_btn = w.addButton("አይ", QMessageBox.ButtonRole.NoRole)
                w.exec()
                if w.clickedButton() is yes_btn:
                    if not self._save_file():
                        event.ignore()
                        return

        event.accept()

