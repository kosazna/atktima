# -*- coding: utf-8 -*-
import sys
from typing import Any, Optional, Tuple
from at.gui.popup import Popup

from at.gui.worker import run_thread
from at.auth.client import AuthStatus
from at.gui.console import Console
from at.gui.progress import ProgressBar
from at.gui.status import StatusButton
from at.gui.list import ListWidget
from at.logger import log
from at.gui.utils import set_size
from atktima.path import paths
from PyQt5.QtCore import Qt, QThreadPool, pyqtSlot
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QTabWidget,
                             QVBoxLayout, QWidget)

from atktima.gui.settings import SettingsTab
from atktima.gui.files import FilesTab

from atktima.state import state

cssGuide = paths.get_css(obj=True).joinpath("_style.css").read_text()
log.set_mode("GUI")
paths.set_meleti(state['meleti'], state['kthmadata'], state['kthmatemp'])


class KtimaUI(QWidget):
    def __init__(self,
                 size: Tuple[Optional[int]] = (None, None),
                 parent: Optional[QWidget] = None,
                 *args,
                 **kwargs) -> None:
        super().__init__(parent=parent, *args, **kwargs)
        self.setupUi(size)
        self.threadpool = QThreadPool(parent=self)
        self.settingsTab.meletiChanged.connect(self.onMeletiUpdate)
        self.settingsTab.serverStatusChanged.connect(self.onServerStatusChanged)

    def setupUi(self, size):
        self.setObjectName("MainWidget")
        self.setStyleSheet(cssGuide)
        self.setWindowTitle(f"{state['appname']} - {state['version']}")

        set_size(widget=self, size=size)

        self.appLayout = QHBoxLayout()
        # self.tabLayout = QVBoxLayout()

        self.console = Console(size=(450, None), parent=self)

        self.tabs = QTabWidget(self)
        self.tabs.setDocumentMode(True)

        self.settingsTab = SettingsTab(size=(650, None), parent=self)
        self.tabs.addTab(self.settingsTab, "Ρυθμίσεις")
        self.filesTab = FilesTab(size=(650, None), parent=self)
        self.tabs.addTab(self.filesTab, "Αρχεία")

        self.appLayout.addWidget(self.tabs)
        self.appLayout.addWidget(self.console)

        self.tabs.setCurrentIndex(0)

        self.setLayout(self.appLayout)

    @pyqtSlot()
    def onMeletiUpdate(self):
        meleti_otas = state[state['meleti']]['company'][state['company']]
        self.filesTab.meleti.setText(state['meleti'])
        self.filesTab.otas.clearContent()
        self.filesTab.otas.addItems(meleti_otas)
        self.filesTab.otas.toggle()

    @pyqtSlot(tuple)
    def onServerStatusChanged(self, status):
        self.filesTab.server.changeStatus(*status)


if __name__ == '__main__':

    SEGOE = QFont("Segoe UI", 9)

    app = QApplication(sys.argv)
    app.setFont(SEGOE)
    app.setStyle('Fusion')

    ui = KtimaUI(size=(None, 600))
    ui.show()

    sys.exit(app.exec_())
