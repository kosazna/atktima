# -*- coding: utf-8 -*-
import sys
from pathlib import Path
from time import sleep
from typing import Any, Tuple, Union

from PyQt5 import QtWidgets
from at.gui.line import HLine
from at.auth.client import Authorize, AuthStatus, licensed
from at.gui.button import Button
from at.gui.check import CheckInput
from at.gui.combo import ComboInput
from at.gui.console import Console
from at.gui.filename import FileNameInput
from at.gui.icons import *
from at.gui.input import IntInput, StrInput
from at.gui.io import FileInput, FileOutput, FolderInput
from at.gui.label import Label
from at.gui.list import ListWidget
from at.gui.popup import Popup, show_popup
from at.gui.progress import ProgressBar
from at.gui.status import StatusButton, StatusLabel
from at.gui.utils import *
from at.gui.worker import run_thread
from at.io.copyfuncs import batch_copy_file, copy_file
from at.logger import log
from at.path import PathEngine
from PyQt5.QtCore import Qt, QThreadPool
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget

from atktima.path import paths
from atktima.state import state

# When setting fixed width to QLineEdit ->
# -> add alignment=Qt.AlignLeft when adding widget to layout


class SettingsTab(QWidget):
    def __init__(self,
                 size: Tuple[Optional[int]] = (None, None),
                 parent: Optional[QWidget] = None,
                 *args,
                 **kwargs) -> None:
        super().__init__(parent=parent, *args, **kwargs)
        self.setupUi(size)

    def setupUi(self, size):
        set_size(widget=self, size=size)
        widgetlayout = QVBoxLayout()
        labelLayout = QHBoxLayout()
        meletiLayout = QHBoxLayout()
        licLayout = QHBoxLayout()

        self.fullname = Label(icon='person-fill',
                              label=state['fullname'],
                              parent=self)
        self.username = Label(icon='person-badge-fill',
                              label=state['username'],
                              parent=self)
        self.company = Label(icon='house-fill',
                             label=state['company'],
                             parent=self)
        self.meleti = Label(icon='info-circle-fill',
                            label=state[state['meleti']],
                            parent=self)
        self.app = Label(icon='app',
                         label=state['appname'],
                         parent=self)
        self.version = Label(icon='hash',
                             label=state['version'],
                             parent=self)

        self.kthmatemp = FolderInput(label='kthmatemp',
                                     editsize=(100, 24),
                                     parent=self)

        self.kthmadata = FolderInput(label='kthmadata',
                                     editsize=(100, 24),
                                     parent=self)

        self.meletes = ComboInput(label="Μελέτη",
                                  combosize=(100, 24),
                                  items=state['meletes'],
                                  parent=self)
        self.meletes.setCurrentText(state['meleti'])
        self.meletes.subscribe(self.onMeletiChanged)

        self.kthmatemp.setText(state['kthmatemp'])
        self.kthmadata.setText(state['kthmadata'])

        self.lic = FileInput("Άδεια", parent=self)
        self.licButton = Button("Φόρτωση", icon='upload', size=(90, 22))

        labelLayout.addWidget(self.fullname)
        labelLayout.addWidget(self.username)
        labelLayout.addWidget(self.company,
                              stretch=2,
                              alignment=Qt.AlignLeft)
        labelLayout.addWidget(self.app)
        labelLayout.addWidget(self.version)

        widgetlayout.addLayout(labelLayout)
        widgetlayout.addWidget(HLine())

        meletiLayout.addWidget(self.meletes)
        meletiLayout.addWidget(self.meleti,
                               stretch=2,
                               alignment=Qt.AlignLeft)
        widgetlayout.addLayout(meletiLayout)
        widgetlayout.addWidget(self.kthmatemp,
                               alignment=(Qt.AlignLeft | Qt.AlignTop))
        widgetlayout.addWidget(self.kthmadata,
                               stretch=2,
                               alignment=(Qt.AlignLeft | Qt.AlignTop))

        widgetlayout.addWidget(HLine())

        licLayout.addWidget(self.lic)
        licLayout.addWidget(self.licButton)

        widgetlayout.addLayout(licLayout, stretch=2)

        self.parent().progress.hide()

        self.setLayout(widgetlayout)

    def onMeletiChanged(self):
        state['meleti'] = self.meletes.getCurrentText()
        self.meleti.setText(state[state['meleti']])


if __name__ == '__main__':
    cssGuide = paths.get_css(obj=True).joinpath("_style.css").read_text()
    SEGOE = QFont("Segoe UI", 9)

    app = QApplication(sys.argv)
    app.setFont(SEGOE)
    app.setStyle('Fusion')

    ui = SettingsTab(size=(600, None))
    ui.setStyleSheet(cssGuide)
    ui.show()

    sys.exit(app.exec_())
