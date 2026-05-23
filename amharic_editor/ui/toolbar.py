# -*- coding: utf-8 -*-
"""Main toolbar with Run, Translate, and common actions."""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QToolBar, QWidget, QSizePolicy


class EditorToolBar(QToolBar):
    run_clicked = pyqtSignal()
    translate_clicked = pyqtSignal()
    new_clicked = pyqtSignal()
    open_clicked = pyqtSignal()
    save_clicked = pyqtSignal()
    find_clicked = pyqtSignal()
    keywords_clicked = pyqtSignal()
    user_guide_clicked = pyqtSignal()

    def __init__(self, parent: QWidget = None):
        super().__init__("መሳሪያ አሞሌ", parent)
        self.setMovable(False)

        self._act_new = QAction("አዲስ", self)
        self._act_open = QAction("ክፈት", self)
        self._act_save = QAction("አስቀምጥ", self)
        self._act_translate = QAction("ተርጉም", self)
        self._act_run = QAction("▶ ጀምር", self)
        self._act_find = QAction("ፈልግ", self)
        self._act_keywords = QAction("ቁልፍ ቃላት", self)
        self._act_user_guide = QAction("የተጠቃሚ መመሪያ ሰነድ", self)

        self._act_new.triggered.connect(self.new_clicked.emit)
        self._act_open.triggered.connect(self.open_clicked.emit)
        self._act_save.triggered.connect(self.save_clicked.emit)
        self._act_translate.triggered.connect(self.translate_clicked.emit)
        self._act_run.triggered.connect(self.run_clicked.emit)
        self._act_find.triggered.connect(self.find_clicked.emit)
        self._act_keywords.triggered.connect(self.keywords_clicked.emit)
        self._act_user_guide.triggered.connect(self.user_guide_clicked.emit)

        self._act_run.setToolTip("ተርጉም እና ፕሮግራሙን አስፈር (F5)")
        self._act_translate.setToolTip("ወደ Python ተርጉም (Ctrl+T)")
        self._act_keywords.setToolTip("ሁሉንም አማርኛ ቁልፍ ቃላት አሳይ")
        self._act_user_guide.setToolTip("የተጠቃሚ መመሪያ ሰነድ (.yml) አሳይ")

        for act in (
            self._act_new,
            self._act_open,
            self._act_save,
        ):
            self.addAction(act)

        self.addSeparator()

        for act in (
            self._act_translate,
            self._act_find,
            self._act_keywords,
            self._act_user_guide,
        ):
            self.addAction(act)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.addWidget(spacer)

        self._act_run.setText("▶  ጀምር")
        self.addAction(self._act_run)
