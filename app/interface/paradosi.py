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
from at.gui.utils import HORIZONTAL, VERTICAL, set_size
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


class ParadosiTab(QWidget):
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
        mdbLayout = QHBoxLayout()
        checksLayout = QHBoxLayout()
        metadataLayout = QHBoxLayout()
        listLayout = QHBoxLayout()
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

        path_mapping = {'LocalData': paths.get_localdata(),
                        'ParadosiData': paths.get_paradosidata()}

        self.mdbFolder = FolderInput(label="Βάσεις",
                                     parent=self)
        self.checkMdbOrganized = CheckInput(label="Οργανωμένες",
                                            checked=False,
                                            parent=self)
        self.checkMetadata = CheckInput(label="Metadata",
                                        checked=False,
                                        parent=self)
        self.dateMetadata = StrInput(labelsize=(100, 24),
                                     editsize=(150, 24),
                                     parent=self)

        self.checkEmptyShapes = CheckInput(label="Δημιουργία κενών shapefile",
                                           checked=False,
                                           parent=self)

        path_mapping = {'ParadosiData': paths.get_paradosidata()}
        self.folderOutput = PathSelector(label="Φάκελος που θα δημιουργηθεί η παράδοση",
                                         selectortype='folder_in',
                                         mapping=path_mapping,
                                         orientation=VERTICAL,
                                         combosize=(180, 24),
                                         labelsize=(None, 24),
                                         parent=self)

        self.shape = ListWidget(label="Επιλογή αρχείων",
                                parent=self)
        self.otas = ListWidget(label="Επιλογή ΟΤΑ",
                               parent=self)

        self.makeAll = Button("Δημιουργία Παράδοσης",
                                 color='blue',
                                 size=(150, 30),
                                 parent=self)

        self.progress = ProgressBar(parent=self)

        self.dateMetadata.setPlaceholder("dd/mm/yyyy")
        self.folderOutput.setCurrentText("ParadosiData")
        self.shape.addItems(db.get_shapes(state['meleti']))
        self.otas.addItems(db.get_ota_per_meleti_company(
            state['meleti'], state['company']))
        self.shape.hideButtons()
        self.otas.hideButtons()

        labelLayout.addWidget(self.fullname)
        labelLayout.addWidget(self.username)
        labelLayout.addWidget(self.company, stretch=2, alignment=Qt.AlignLeft)
        labelLayout.addWidget(self.meleti)
        layout.addLayout(labelLayout)
        layout.addWidget(HLine())
        mdbLayout.addWidget(self.mdbFolder)
        mdbLayout.addWidget(self.checkMdbOrganized)
        layout.addLayout(mdbLayout)
        layout.addWidget(HLine())

        listLayout.addWidget(self.shape)
        listLayout.addWidget(self.otas)
        layout.addLayout(listLayout)
        layout.addWidget(HLine())
        checksLayout.addWidget(self.checkEmptyShapes)
        metadataLayout.addWidget(self.checkMetadata)
        metadataLayout.addWidget(
            self.dateMetadata, stretch=2, alignment=Qt.AlignLeft)
        checksLayout.addLayout(metadataLayout)
        layout.addLayout(checksLayout)
        layout.addWidget(self.folderOutput)
        layout.addWidget(HLine())
        buttonLayout.addWidget(self.makeAll)
        layout.addLayout(buttonLayout)
        layout.addWidget(HLine(), stretch=2, alignment=Qt.AlignTop)
        layout.addWidget(self.progress)

        self.setLayout(layout)


if __name__ == '__main__':
    cssGuide = paths.get_css(obj=True).joinpath("_style.css").read_text()
    SEGOE = QFont("Segoe UI", 9)

    app = QApplication(sys.argv)
    app.setFont(SEGOE)
    app.setStyle('Fusion')

    ui = ParadosiTab(size=(None, 600))
    ui.setStyleSheet(cssGuide)
    ui.show()

    sys.exit(app.exec_())
