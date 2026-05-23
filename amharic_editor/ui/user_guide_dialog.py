# -*- coding: utf-8 -*-
"""Dialog showing user guide content from YAML documentation."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QTextBrowser,
    QVBoxLayout,
    QMessageBox,
)

from ui.user_guide_loader import (
    USER_GUIDE_DIR,
    load_user_guides,
    render_all_documents_html,
    render_document_html,
    theme_to_colors,
)

ALL_GUIDES_ROLE = -1


class UserGuideDialog(QDialog):
    """የተጠቃሚ መመሪያ ሰነድ — content from docs/user_guide/*.yml."""

    def __init__(self, parent=None, theme_name: str = "dark"):
        super().__init__(parent)
        self.setWindowTitle("የተጠቃሚ መመሪያ ሰነድ")
        self.resize(920, 680)
        self.setMinimumSize(720, 520)
        self._theme_name = theme_name
        if parent is not None and hasattr(parent, "_theme_name"):
            self._theme_name = parent._theme_name
        self._colors = theme_to_colors(self._theme_name)
        self._documents = load_user_guides()
        self._build_ui()
        if self._documents:
            self._list.setCurrentRow(0)
            self._show_row(0)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        header = QLabel(
            "የተጠቃሚ መመሪያ ሰነድ — ሁሉንም ርዕሶች ከታች ይመርጡ ወይም «ሙሉ መመሪያ» ይመልከቱ"
        )
        header.setWordWrap(True)
        layout.addWidget(header)

        if not self._documents:
            layout.addWidget(
                QLabel(
                    "ምንም .yml መመሪያ አልተገኘም።\n"
                    f"አቃፊ: {USER_GUIDE_DIR}\n\n"
                    "PyYAML ይጫኑ: pip install PyYAML"
                )
            )
            close_btn = QPushButton("ዝጋ")
            close_btn.clicked.connect(self.close)
            layout.addWidget(close_btn)
            return

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self._list = QListWidget()
        self._list.setMinimumWidth(200)
        self._list.setMaximumWidth(320)

        all_item = QListWidgetItem("📘 ሙሉ መመሪያ (ሁሉንም)")
        all_item.setData(Qt.ItemDataRole.UserRole, ALL_GUIDES_ROLE)
        all_item.setToolTip("ሁሉንም ርዕሶች በአንድ ገጽ")
        self._list.addItem(all_item)

        for i, doc in enumerate(self._documents):
            item = QListWidgetItem(doc.title)
            item.setData(Qt.ItemDataRole.UserRole, i)
            item.setToolTip(doc.path.name)
            self._list.addItem(item)

        self._list.currentRowChanged.connect(self._show_row)
        splitter.addWidget(self._list)

        self._browser = QTextBrowser()
        self._browser.setOpenExternalLinks(True)
        self._browser.setLineWrapMode(QTextBrowser.LineWrapMode.WidgetWidth)
        self._browser.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self._browser.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self._browser.document().setDocumentMargin(0)
        splitter.addWidget(self._browser)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([240, 680])

        layout.addWidget(splitter, stretch=1)

        btn_row = QHBoxLayout()
        close_btn = QPushButton("ዝጋ")
        close_btn.clicked.connect(self.close)
        btn_row.addStretch()
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        self._apply_widget_styles()

    def _apply_widget_styles(self):
        bg = self._colors["background"]
        fg = self._colors["foreground"]
        border = self._colors["border"]
        self.setStyleSheet(
            f"""
            QDialog, QListWidget, QTextBrowser, QLabel, QPushButton {{
                background-color: {bg};
                color: {fg};
            }}
            QListWidget {{
                border: 1px solid {border};
                border-radius: 4px;
                padding: 4px;
            }}
            QListWidget::item:selected {{
                background-color: #094771;
                color: #ffffff;
            }}
            QTextBrowser {{
                border: 1px solid {border};
                border-radius: 4px;
            }}
            QPushButton {{
                border: 1px solid {border};
                padding: 6px 14px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {self._colors['code_bg']};
            }}
            """
        )

    def _show_row(self, row: int):
        if row < 0:
            return
        item = self._list.item(row)
        if item is None:
            return
        role = item.data(Qt.ItemDataRole.UserRole)
        if role == ALL_GUIDES_ROLE:
            html = render_all_documents_html(self._documents, self._colors)
        else:
            idx = int(role)
            if idx < 0 or idx >= len(self._documents):
                return
            html = render_document_html(self._documents[idx], self._colors)
        self._browser.setHtml(html)
        self._browser.verticalScrollBar().setValue(0)

    def refresh_theme(self, theme_name: str):
        """Re-render visible content when the app theme changes."""
        self._theme_name = theme_name
        self._colors = theme_to_colors(theme_name)
        self._apply_widget_styles()
        row = self._list.currentRow()
        if row >= 0:
            self._show_row(row)

    @staticmethod
    def warn_if_unavailable(parent) -> bool:
        """Return True if guides can be shown; otherwise show warning."""
        try:
            import yaml  # noqa: F401
        except ImportError:
            QMessageBox.warning(
                parent,
                "የተጠቃሚ መመሪያ",
                "PyYAML አልተገኘም።\n\npip install PyYAML",
            )
            return False
        if not load_user_guides():
            QMessageBox.warning(
                parent,
                "የተጠቃሚ መመሪያ",
                f"ምንም .yml ፋይል በዚህ አቃፊ ውስጥ አልተገኘም:\n{USER_GUIDE_DIR}",
            )
            return False
        return True
