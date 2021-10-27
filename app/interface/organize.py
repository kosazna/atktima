# -*- coding: utf-8 -*-
import sys
from os import path
from pathlib import Path
from time import sleep
from typing import Any, Optional, Tuple, Union

import pandas as pd
from at.auth.client import Authorize, AuthStatus, licensed
from at.auth.utils import load_lic
from at.gui.components import *
from at.gui.utils import set_size
from at.gui.worker import run_thread
from at.io.copyfuncs import batch_copy_file, copy_file
from at.logger import log
from at.path import PathEngine
from at.result import Result
from atktima.app.utils import db, paths, state
from PyQt5.QtCore import Qt, QThreadPool, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget

# When setting fixed width to QLineEdit ->
# -> add alignment=Qt.AlignLeft when adding widget to layout


class OrganizeTab(QWidget):
    def __init__(self,
                 size: Tuple[Optional[int]] = (None, None),
                 parent: Optional[QWidget] = None,
                 *args,
                 **kwargs) -> None:
        super().__init__(parent=parent, *args, **kwargs)
        self.setupUi(size)
        self.pickedMeleti = state['meleti']
        self.threadpool = QThreadPool(parent=self)
        self.popup = Popup(state['appname'])

    def setupUi(self, size):
        set_size(widget=self, size=size)

        layout = QVBoxLayout()
        layout.setContentsMargins(2, 4, 2, 0)
        labelLayout = QHBoxLayout()
        inputLayout = QVBoxLayout()
        inputFilterLayout = QHBoxLayout()
        outputLayout = QVBoxLayout()
        buttonLayout = QHBoxLayout()

        self.fullname = Label(icon='person-fill',
                              label=state['fullname'],
                              parent=self)
        self.username = Label(icon='person-badge-fill',
                              label=state['username'],
                              parent=self)
        self.company = Label(icon='house-fill',
                             label=state['company'],
                             parent=self)
        self.meleti = Label(icon='layers-fill',
                            label=state['meleti'],
                            parent=self)

        self.inputFolder = FolderInput(label="Εύρεση σε",
                                       parent=self)
        self.inputPattern = StrSelector(label="Δομή",
                                        combosize=(200, 24),
                                        editsize=(300, 24),
                                        parent=self)
        self.inputFilters = StrInput("Φίλτρα")
        self.checkRecursive = CheckInput("Εύρεση σε υποφακέλους")

        self.ouputFolder = FolderInput(label="Απόθεση σε",
                                       parent=self)
        self.outputPattern = StrSelector(label="Δομή",
                                         combosize=(200, 24),
                                         editsize=(300, 24),
                                         parent=self)

        self.buttonCopy = Button(label='Αντιγραφή',
                                 size=(180, 30),
                                 parent=self)
        self.buttonMake = Button(label='Δημιουργία',
                                 size=(180, 30),
                                 parent=self)
        self.status = StatusButton(parent=self)

        labelLayout.addWidget(self.fullname)
        labelLayout.addWidget(self.username)
        labelLayout.addWidget(self.company, stretch=2, alignment=Qt.AlignLeft)
        labelLayout.addWidget(self.meleti)
        layout.addLayout(labelLayout)
        layout.addWidget(HLine())
        inputLayout.addWidget(self.inputFolder)
        inputLayout.addWidget(self.inputPattern)
        inputFilterLayout.addWidget(self.inputFilters)
        inputFilterLayout.addWidget(self.checkRecursive)
        inputLayout.addLayout(inputFilterLayout)
        layout.addLayout(inputLayout)
        layout.addWidget(HLine())
        outputLayout.addWidget(self.ouputFolder)
        outputLayout.addWidget(self.outputPattern)
        layout.addLayout(outputLayout)
        layout.addWidget(HLine())
        buttonLayout.addWidget(self.buttonCopy)
        buttonLayout.addWidget(self.buttonMake)
        layout.addLayout(buttonLayout)
        layout.addWidget(self.status, stretch=2, alignment=Qt.AlignBottom)

        self.setLayout(layout)


if __name__ == '__main__':
    cssGuide = paths.get_css(obj=True).joinpath("_style.css").read_text()
    SEGOE = QFont("Segoe UI", 9)

    app = QApplication(sys.argv)
    app.setFont(SEGOE)
    app.setStyle('Fusion')

    ui = OrganizeTab(size=(600, None))
    ui.setStyleSheet(cssGuide)
    ui.show()

    sys.exit(app.exec_())
