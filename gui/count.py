# -*- coding: utf-8 -*-
import sys
from pathlib import Path
from time import sleep
from typing import Any, Tuple, Union

from at.text import replace_all
from at.auth.utils import load_lic
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
from at.result import Result
from at.path import PathEngine
from PyQt5.QtCore import Qt, QThreadPool
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget

from atktima.path import paths
from atktima.state import state
from atktima.sql import db
from atktima.auth import auth, licensed
from at.utils import file_counter

# When setting fixed width to QLineEdit ->
# -> add alignment=Qt.AlignLeft when adding widget to layout

xmls = ('BLOCK_PNT_METADATA', 'GEO_METADATA', 'ROADS_METADATA')


class CountTab(QWidget):
    def __init__(self,
                 size: Tuple[Optional[int]] = (None, None),
                 parent: Optional[QWidget] = None,
                 *args,
                 **kwargs) -> None:
        super().__init__(parent=parent, *args, **kwargs)
        self.widgetMap = {}
        self.setupUi(size)
        self.pickedMeleti = state['meleti']
        self.threadpool = QThreadPool(parent=self)
        self.popup = Popup(state['appname'])
        self.buttonCount.subscribe(self.countFiles)
        self.buttonMissing.subscribe(self.findMissing)
        self.missingShapes = []

    def setupUi(self, size):
        set_size(widget=self, size=size)

        layout = QVBoxLayout()
        labelLayout = QHBoxLayout()
        countLayout = QHBoxLayout()
        shapeLayout = QVBoxLayout()
        shapeLayout.setContentsMargins(4, 2, 4, 2)
        shapeLayout.setSpacing(0)
        restLayout = QVBoxLayout()
        restLayout.setContentsMargins(4, 2, 4, 2)
        restLayout.setSpacing(0)

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

        self.folder = FolderInput(label="Φάκελος αρχείων",
                                  labelsize=(110, 24),
                                  parent=self)

        self.buttonCount = Button(label='Καταμέτρηση',
                                  size=(180, 30),
                                  parent=self)
        self.buttonMissing = Button(label='Εύρεση κενών',
                                    size=(180, 30),
                                    parent=self)

        for shape in db.get_shapes(state['meleti']):
            if shape != 'VSTEAS_REL':
                _widget = StatusLabel(label=shape, status='0',
                                      labelsize=(100, 18),
                                      statussize=(50, 18), parent=self)
                self.widgetMap[shape] = _widget
                shapeLayout.addWidget(_widget)
            else:
                _widget = StatusLabel(label=shape, status='0',
                                      labelsize=(140, 18),
                                      statussize=(50, 18), parent=self)
                self.widgetMap[shape] = _widget
                restLayout.addWidget(_widget)

        for xml in xmls:
            _widget = StatusLabel(label=xml, status='0',
                                  labelsize=(140, 18),
                                  statussize=(50, 18), parent=self)
            self.widgetMap[xml] = _widget
            restLayout.addWidget(_widget)
        restLayout.addStretch(2)

        self.buttonMissing.disable()

        labelLayout.addWidget(self.fullname)
        labelLayout.addWidget(self.username)
        labelLayout.addWidget(self.company, stretch=2, alignment=Qt.AlignLeft)
        labelLayout.addWidget(self.meleti)
        layout.addLayout(labelLayout)
        layout.addWidget(HLine())
        layout.addWidget(self.folder)
        countLayout.addLayout(shapeLayout)
        countLayout.addLayout(restLayout, stretch=1)
        layout.addLayout(countLayout)
        buttonLayout.addWidget(self.buttonCount)
        buttonLayout.addWidget(self.buttonMissing)
        layout.addWidget(HLine(), stretch=2, alignment=Qt.AlignTop)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)

    def countFiles(self):
        folder = self.folder.getText()

        all_folders = [p for p in Path(folder).iterdir() if p.is_dir()]

        folders_count = len(all_folders)

        if folder and Path(folder).exists():
            filters = ('*.shp', '*.mdb', '*.xml')
            ext_access_names = ('.shp', '.mdb', '.xml')
            counter = file_counter(src=folder, filters=filters)

            for ext in ext_access_names:
                if ext in counter:
                    shapecount = counter[ext]
                    for shape in shapecount:
                        if shape in self.widgetMap:
                            num = str(shapecount[shape])
                            self.widgetMap[shape].setText(num)

                            if shapecount[shape] == folders_count:
                                self.widgetMap[shape].setStyle('statusOk')
                            elif num == 0:
                                self.widgetMap[shape].setStyle('statusError')
                            else:
                                self.widgetMap[shape].setStyle('statusWarning')
                                self.missingShapes.append(shape)
            if self.missingShapes:
                self.buttonMissing.enable()
        else:
            self.popup.error("Δώσε φάκελο για καταμέτρηση")

    def findMissing(self):
        if self.missingShapes:
            pass
        else:
            self.popup.warning("Δεν έχει γίνει ακόμα καταμέτρηση")


if __name__ == '__main__':
    cssGuide = paths.get_css(obj=True).joinpath("_style.css").read_text()
    SEGOE = QFont("Segoe UI", 9)

    app = QApplication(sys.argv)
    app.setFont(SEGOE)
    app.setStyle('Fusion')

    ui = CountTab(size=(600, None))
    ui.setStyleSheet(cssGuide)
    ui.show()

    sys.exit(app.exec_())
