# -*- coding: utf-8 -*-
"""File explorer sidebar using QFileSystemModel."""

from pathlib import Path

from PyQt6.QtCore import QDir, QModelIndex, pyqtSignal, Qt, QTimer
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTreeView,
    QLabel,
    QLineEdit,
    QFileDialog,
    QPushButton,
    QHBoxLayout,
)
from PyQt6.QtGui import QFileSystemModel


class InlineEditDelegate:
    """Manages inline file creation and editing."""

    def __init__(self, tree, model, parent_path, default_name):
        self.tree = tree
        self.model = model
        self.parent_path = parent_path
        self.default_name = default_name
        self.new_path = None
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._start_edit)

    def create_and_edit(self):
        parent_path = Path(self.parent_path)
        if not parent_path.exists():
            return None

        base_stem = Path(self.default_name).stem
        base_ext = Path(self.default_name).suffix
        new_path = parent_path / self.default_name

        counter = 1
        while new_path.exists():
            new_path = parent_path / f"{base_stem} ({counter}){base_ext}"
            counter += 1

        new_path.touch()
        self.new_path = str(new_path)

        self.timer.start(100)
        return str(new_path)

    def _start_edit(self):
        if self.new_path:
            idx = self.model.index(self.new_path)
            if idx.isValid():
                self.tree.setCurrentIndex(idx)
                self.tree.edit(idx)


class FileExplorerSidebar(QWidget):
    """Project folder tree for .aml and related files."""

    file_open_requested = pyqtSignal(str)
    new_file_requested = pyqtSignal(str, str)
    file_renamed = pyqtSignal(str, str)  # old_path, new_path

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # Header row with "ፋይሎች" label
        header_row = QHBoxLayout()
        header_row.addWidget(QLabel("ፋይሎች"))
        header_row.addStretch()
        layout.addLayout(header_row)

        # Search row with filter input
        search_row = QHBoxLayout()
        self._filter = QLineEdit()
        self._filter.setPlaceholderText("ፈልግ...")
        self._filter.textChanged.connect(self._apply_filter)
        search_row.addWidget(self._filter)
        search_row.addStretch()
        layout.addLayout(search_row)

        # Middle row with folder name and open folder button
        middle_row = QHBoxLayout()
        self._name_label = QLabel("")
        self._name_label.setStyleSheet("font-weight: bold; color: #4fc3f7;")
        middle_row.addWidget(self._name_label)
        
        open_folder_btn = QPushButton("📁")
        open_folder_btn.setToolTip("አቃፊ ክፈት")
        open_folder_btn.setFixedWidth(36)
        open_folder_btn.clicked.connect(self._choose_root)
        middle_row.addWidget(open_folder_btn)
        
        middle_row.addStretch()
        layout.addLayout(middle_row)

        # New file button row
        self._new_file_btn = QPushButton("＋")
        self._new_file_btn.setToolTip("አዲስ ፋይል ፍጠር")
        self._new_file_btn.setFixedSize(32, 32)
        self._new_file_btn.setStyleSheet("""
            QPushButton {
                background-color: #4fc3f7;
                color: #000;
                border: none;
                border-radius: 16px;
                font-weight: bold;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #63d4f7;
            }
        """)
        self._new_file_btn.clicked.connect(self._on_new_file_clicked)
        new_file_row = QHBoxLayout()
        new_file_row.addWidget(self._new_file_btn)
        new_file_row.addStretch()
        layout.addLayout(new_file_row)

        # Initialize model and tree
        self._model = QFileSystemModel()
        self._model.setRootPath("")
        self._model.setFilter(
            QDir.Filter.AllDirs
            | QDir.Filter.Files
            | QDir.Filter.NoDotAndDotDot
        )
        self._model.setNameFilters(["*.aml", "*.js", "*.md", "*.py", "*.yml", "*.yaml"])
        self._model.setNameFilterDisables(False)

        self._tree = QTreeView()
        self._tree.setModel(self._model)
        self._tree.setAnimated(True)
        self._tree.setIndentation(16)
        self._tree.doubleClicked.connect(self._on_double_click)
        for col in range(1, 4):
            self._tree.hideColumn(col)
        layout.addWidget(self._tree)

        self._root_path = str(Path.home())

    def set_root(self, path: str):
        if Path(path).exists():
            self._root_path = path
            idx = self._model.index(path)
            self._tree.setRootIndex(idx)
            self._update_name_label(path)

    def _update_name_label(self, path: str):
        folder_name = Path(path).name or path
        self._name_label.setText(folder_name)

    def _choose_root(self):
        folder = QFileDialog.getExistingDirectory(self, "አቃፊ ይምረጡ", self._root_path)
        if folder:
            self.set_root(folder)

    def _apply_filter(self, text: str):
        pass

    def _on_double_click(self, index: QModelIndex):
        path = self._model.filePath(index)
        if Path(path).is_file():
            self.file_open_requested.emit(path)

    def _on_new_file_clicked(self):
        default_name = "አዲስ ፋይል.yml"
        self.new_file_requested.emit(self._root_path, default_name)

    def create_file_for_inline_rename(self, parent_path: str, default_name: str):
        editor = InlineEditDelegate(self._tree, self._model, parent_path, default_name)
        return editor.create_and_edit()

    def start_rename_file(self, file_path: str):
        idx = self._model.index(file_path)
        if idx.isValid():
            self._tree.setCurrentIndex(idx)
            QTimer.singleShot(50, lambda: self._start_editing(idx))

    def _start_editing(self, index: QModelIndex):
        if index.isValid():
            self._tree.edit(index)

    def get_selected_folder(self) -> str:
        index = self._tree.currentIndex()
        if index.isValid():
            path = self._model.filePath(index)
            if Path(path).is_dir():
                return path
        return self._root_path

    def refresh(self):
        self._model.refresh()