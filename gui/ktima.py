# -*- coding: utf-8 -*-
import sys
from typing import Any, Optional, Tuple

from at.gui.worker import run_thread
from at.auth.client import AuthStatus
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
        self.threadpool = QThreadPool(parent=self)

    def setupUi(self, size):
        self.setObjectName("MainWidget")
        self.setStyleSheet(cssGuide)

        set_size(widget=self, size=size)

        self.appLayout = QHBoxLayout()
        self.tabLayout = QVBoxLayout()

        self.console = Console(size=(500, None), parent=self)

        self.tabs = QTabWidget(self)
        self.tabs.setDocumentMode(True)
        self.tabs.addTab(SettingsTab(
            size=(600, None), parent=self), "Ρυθμίσεις")
        self.tabs.addTab(ListWidget(), "Αρχεία")

        self.appLayout.addWidget(self.tabs)
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
