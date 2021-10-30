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
from at.gui.utils import VERTICAL, set_size
from at.gui.worker import run_thread
from at.io.copyfuncs import copy_pattern
from at.logger import log
from at.path import PathEngine
from at.result import Result
from at.text import parse_filters
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
        self.buttonFilterTest.subscribe(self.onTestFilter)

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

        self.inputFolder = PathSelector(label="Εύρεση σε",
                                        labelsize=(180, 24),
                                        mapping={},
                                        orientation=VERTICAL,
                                        parent=self)
        self.inputPattern = StrSelector(label="Δομή",
                                        combosize=(200, 24),
                                        editsize=(300, 24),
                                        parent=self)
        # self.inputFilters = StrInput("Φίλτρα")
        # self.checkRecursive = CheckInput("Εύρεση σε υποφακέλους")

        self.filters = FilterFileSelector("Φίλτρα")

        self.ouputFolder = PathSelector(label="Απόθεση σε",
                                        labelsize=(180, 24),
                                        mapping={},
                                        orientation=VERTICAL,
                                        parent=self)
        self.outputPattern = StrSelector(label="Δομή",
                                         combosize=(200, 24),
                                         editsize=(300, 24),
                                         parent=self)
        self.outputName = StrInput(label="Με όνομα",
                                   parent=self)

        self.buttonCopy = Button(label='Αντιγραφή',
                                 size=(180, 30),
                                 parent=self)
        self.buttonFilterTest = Button(label='Δοκιμή Φίλτρου',
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
        # inputFilterLayout.addWidget(self.inputFilters)
        # inputFilterLayout.addWidget(self.checkRecursive)
        # inputLayout.addLayout(inputFilterLayout)
        inputLayout.addWidget(self.filters)
        inputLayout.addWidget(self.inputPattern)
        layout.addLayout(inputLayout)
        layout.addWidget(HLine())
        outputLayout.addWidget(self.ouputFolder)
        outputLayout.addWidget(self.outputName)
        outputLayout.addWidget(self.outputPattern)
        layout.addLayout(outputLayout)
        layout.addWidget(HLine())
        buttonLayout.addWidget(self.buttonCopy)
        buttonLayout.addWidget(self.buttonFilterTest)
        layout.addLayout(buttonLayout)
        layout.addWidget(self.status, stretch=2, alignment=Qt.AlignBottom)

        self.setLayout(layout)

    @licensed(appname=state['appname'], category=state['meleti'])
    def copyFiles(self, _progress):
        filters = parse_filters(self.inputFilters.getText())
        src = self.inputFolder.getText()
        read_pattern = self.inputPattern.getText()
        dst = self.outputPattern.getText()
        save_pattern = self.outputPattern.getText()
        save_name = self.outputName.getText()

        recursive = self.checkRecursive.isChecked()

        return copy_pattern(src=src,
                            dst=dst,
                            filters=filters,
                            read_pattern=read_pattern,
                            save_pattern=save_pattern,
                            save_name=save_name,
                            recursive=recursive,
                            verbose=True)

    def onTestFilter(self):
        file_filter = self.filters.getFilterObject()
        filter_str = self.filters.getText()
        folder = self.inputFolder.getText()
        keep = self.filters.getKeepValue()
        files = file_filter.search(folder, keep)

        if files:
            log.success(f"\nΑρχεία: {len(files)} | Αποτελέσματα φίλτρου: {filter_str}\n")
            for f in files:
                log.info(str(f))
        else:
            log.error(f"\nΑρχεία: {len(files)} | Αποτελέσματα φίλτρου: {filter_str}\n")

        


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
