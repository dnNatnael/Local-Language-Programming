# -*- coding: utf-8 -*-
"""Dialog listing all AML keywords (ቁልፍ ቃላት)."""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHeaderView,
    QAbstractItemView,
)

from editor.keywords import AML_KEYWORD_ENTRIES


class KeywordsDialog(QDialog):
    """Shows Amharic keywords; double-click or Insert to add at cursor."""

    keyword_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ቁልፍ ቃላት")
        self.setMinimumSize(480, 420)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(
            QLabel(
                "አማርኛ ፕሮግራሚንግ ቋንቋ — ቁልፍ ቃላት\n"
                "ይጫኑ ለመጨመር ወይም ሁለት ጊዜ ይጫኑ"
            )
        )

        self._table = QTableWidget(len(AML_KEYWORD_ENTRIES), 3)
        self._table.setHorizontalHeaderLabels(["ቁልፍ ቃል", "English", "መግለጫ"])
        self._table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self._table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self._table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)

        for row, (amharic, english, desc) in enumerate(AML_KEYWORD_ENTRIES):
            self._table.setItem(row, 0, QTableWidgetItem(amharic))
            self._table.setItem(row, 1, QTableWidgetItem(english))
            self._table.setItem(row, 2, QTableWidgetItem(desc))

        self._table.cellDoubleClicked.connect(self._on_row_activated)
        layout.addWidget(self._table)

        btn_row = QHBoxLayout()
        insert_btn = QPushButton("ጨምር")
        insert_btn.setToolTip("የተመረጠውን ቁልፍ ቃል ወደ አርታዒ ጨምር")
        insert_btn.clicked.connect(self._insert_selected)
        close_btn = QPushButton("ዝጋ")
        close_btn.clicked.connect(self.close)
        btn_row.addWidget(insert_btn)
        btn_row.addStretch()
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    def _selected_keyword(self) -> str:
        row = self._table.currentRow()
        if row < 0:
            return ""
        item = self._table.item(row, 0)
        return item.text() if item else ""

    def _on_row_activated(self, row: int, _col: int):
        item = self._table.item(row, 0)
        if item:
            self.keyword_selected.emit(item.text())
            self.close()

    def _insert_selected(self):
        kw = self._selected_keyword()
        if kw:
            self.keyword_selected.emit(kw)
