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
        checksLayout = QVBoxLayout()
        metadataLayout = QHBoxLayout()

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
        self.shapeFolder = PathSelector(label="Φάκελος Χωρικών",
                                        selectortype='folder_in',
                                        mapping=path_mapping,
                                        orientation=VERTICAL,
                                        combosize=(180, 24),
                                        labelsize=(None, 24),
                                        parent=self)

        self.mdbFolder = FolderInput(label="Φάκελος Βάσεων",
                                     orientation=VERTICAL,
                                     labelsize=(None, 24),
                                     parent=self)
        self.checkMdbOrganized = CheckInput(label="Οργανωμένες",
                                            checked=True,
                                            parent=self)

        self.checkMetadata = CheckInput(label="Metadata",
                                        checked=False,
                                        parent=self)
        self.dateMetadata = StrInput(label="Ημερομηνία",
                                     labelsize=(100, 24),
                                     editsize=(150, 24),
                                     parent=self)

        self.checkEmptyShapes = CheckInput(label="Δημιουργία κενών shapefile",
                                           checked=False,
                                           parent=self)

        self.folderOutput = PathSelector(label="Φάκελος που θα δημιουργηθεί η παράδοση",
                                         selectortype='folder_in',
                                         mapping=path_mapping,
                                         orientation=VERTICAL,
                                         combosize=(180, 24),
                                         labelsize=(None, 24),
                                         parent=self)

        self.dateMetadata.setPlaceholder("dd/mm/yyyy")

        labelLayout.addWidget(self.fullname)
        labelLayout.addWidget(self.username)
        labelLayout.addWidget(self.company, stretch=2, alignment=Qt.AlignLeft)
        labelLayout.addWidget(self.meleti)
        layout.addLayout(labelLayout)
        layout.addWidget(HLine())
        layout.addWidget(self.shapeFolder)
        layout.addWidget(self.mdbFolder)
        layout.addWidget(HLine())
        checksLayout.addWidget(self.checkMdbOrganized)
        checksLayout.addWidget(self.checkEmptyShapes)
        metadataLayout.addWidget(self.checkMetadata)
        metadataLayout.addWidget(self.dateMetadata, stretch=2, alignment=Qt.AlignLeft)
        layout.addLayout(checksLayout)
        layout.addLayout(metadataLayout)
        layout.addWidget(self.folderOutput)
        layout.addWidget(HLine(), stretch=2, alignment=Qt.AlignTop)

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
