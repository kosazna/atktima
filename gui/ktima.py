# -*- coding: utf-8 -*-
import sys
from typing import Optional, Tuple

from at.gui.console import Console
from at.gui.progress import ProgressBar
from at.gui.status import StatusButton
from at.gui.list import ListWidget
from at.logger import log
from at.gui.utils import set_size
from atktima.path import paths
from PyQt5.QtCore import Qt, QThreadPool
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QTabWidget,
                             QVBoxLayout, QWidget)

from atktima.gui.settings import SettingsTab

cssGuide = paths.get_css(obj=True).joinpath("_style.css").read_text()
log.set_mode("GUI")


class KtimaUI(QWidget):
    def __init__(self,
                 size: Tuple[Optional[int]] = (None, None),
                 parent: Optional[QWidget] = None,
                 *args,
                 **kwargs) -> None:
        super().__init__(parent=parent, *args, **kwargs)
        self.setupUi(size)

    def setupUi(self, size):
        self.setObjectName("MainWidget")
        self.setStyleSheet(cssGuide)

        set_size(widget=self, size=size)

        self.appLayout = QHBoxLayout()
        self.tabLayout = QVBoxLayout()

        self.console = Console(size=(500, None), parent=self)
        self.progress = ProgressBar(parent=self)
        self.status = StatusButton(parent=self)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.addTab(SettingsTab(size=(600, None), parent=self), "Ρυθμίσεις")
        self.tabs.addTab(ListWidget(), "Αρχεία")

        self.tabLayout.addWidget(self.tabs)
        self.tabLayout.addWidget(self.progress, stretch=2, alignment=Qt.AlignBottom)
        self.tabLayout.addWidget(self.status, stretch=2, alignment=Qt.AlignBottom)

        self.appLayout.addLayout(self.tabLayout)
        self.appLayout.addWidget(self.console)

        self.tabs.setCurrentIndex(0)

        self.setLayout(self.appLayout)


if __name__ == '__main__':

    SEGOE = QFont("Segoe UI", 9)

    app = QApplication(sys.argv)
    app.setFont(SEGOE)
    app.setStyle('Fusion')

    ui = KtimaUI(size=(None, 600))
    ui.show()

    sys.exit(app.exec_())
