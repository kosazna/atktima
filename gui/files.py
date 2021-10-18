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

# When setting fixed width to QLineEdit ->
# -> add alignment=Qt.AlignLeft when adding widget to layout

infostr = "Μόνο για τα αρχεία που θα βρεθούν θα γίνει αντιγραφή στο προορισμό"


class FilesTab(QWidget):
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
        self.serverLoad.clicked.connect(self.onGetFromServer)

    def setupUi(self, size):
        set_size(widget=self, size=size)

        layout = QVBoxLayout()
        labelLayout = QHBoxLayout()
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
        self.server = StatusLabel(icon='hdd-network-fill',
                                  statussize=(110, 22),
                                  parent=self)
        self.meleti = Label(icon='layers-fill',
                            label=state['meleti'],
                            parent=self)
        self.info = Label(icon='info-square-fill',
                          label=infostr,
                          fontsize=10,
                          italic=True,
                          parent=self)
        self.shape = ListWidget(label="Επιλογή αρχείων",
                                parent=self)

        self.otas = ListWidget(label="Επιλογή ΟΤΑ",
                               parent=self)

        self.serverLoad = Button("Server -> LocalData",
                                 color='blue',
                                 size=(180, 30),
                                 parent=self)

        self.localLoad = Button("LocalData -> ParadosiData",
                                color='blue',
                                size=(180, 30),
                                parent=self)
        self.structure = StrInput(label="Δομή server",
                                  completer=['<ota>/SHP/',
                                             '<ota>/SHP/<shape>/'],
                                  editsize=(200, 24),
                                  parent=self)

        self.progress = ProgressBar(parent=self)

        if state['company'] == 'NAMA':
            self.structure.setText('<ota>/SHP/')
        else:
            self.structure.setText('<ota>/SHP/<shape>/')

        self.checkServer()
        self.shape.addItems(db.get_shapes(state['meleti']))
        self.otas.addItems(state[state['meleti']]['company'][state['company']])
        self.shape.hideButtons()
        self.otas.hideButtons()
        self.shape.toggle()
        self.otas.toggle()

        labelLayout.addWidget(self.fullname)
        labelLayout.addWidget(self.username)
        labelLayout.addWidget(self.company, stretch=2, alignment=Qt.AlignLeft)
        labelLayout.addWidget(self.server)
        labelLayout.addWidget(self.meleti)
        layout.addLayout(labelLayout)
        layout.addWidget(HLine())
        layout.addWidget(self.info)
        layout.addWidget(self.structure, alignment=Qt.AlignLeft)
        listLayout.addWidget(self.shape)
        listLayout.addWidget(self.otas)
        layout.addLayout(listLayout)
        layout.addWidget(HLine(), stretch=2, alignment=Qt.AlignTop)
        buttonLayout.addWidget(self.serverLoad)
        buttonLayout.addWidget(self.localLoad)
        layout.addLayout(buttonLayout)
        layout.addWidget(self.progress, stretch=2, alignment=Qt.AlignBottom)

        self.setLayout(layout)

    def checkServer(self):
        if Path(state['kthmadata']).exists():
            self.server.changeStatus("Προσβάσιμο", 'statusOk')
            state['kthmadata_status'] = "Προσβάσιμο"
        else:
            self.server.changeStatus("Μη Προσβάσιμο", 'statusError')
            state['kthmadata_status'] = "Μη Προσβάσιμο"

    def updateProgress(self, metadata: dict):
        if metadata:
            progress_now = metadata.get('pbar', None)
            progress_max = metadata.get('pbar_max', None)
            status = metadata.get('status', None)

            if progress_now is not None:
                self.progress.setValue(progress_now)
            if progress_max is not None:
                self.progress.setMaximum(progress_max)
            if status is not None:
                self.status.disable(str(status))

    def updateResult(self, status: Any):
        if status is not None:
            if isinstance(status, AuthStatus):
                if not status.authorised:
                    self.popup.error(status.info)
            elif isinstance(status, Result):
                if status.result == Result.ERROR:
                    self.popup.error(status.info)
                elif status.result == Result.WARNING:
                    self.popup.warning(status.info, **status.details)
                else:
                    self.popup.info(status.info, **status.details)
            else:
                self.status.disable(status)

    def updateFinish(self):
        pass

    def onGetFromServer(self):
        run_thread(threadpool=self.threadpool,
                   function=self.getFilesFromServer,
                   on_update=self.updateProgress,
                   on_result=self.updateResult,
                   on_finish=self.updateFinish)

    def getFilesFromServer(self, _progress):
        server = paths.get_kthmadata(True)
        structure = self.structure.getText()
        user_shapes = self.shape.getCheckState()
        user_otas = self.otas.getCheckState()

        _progress.emit({'pbar_max': len(user_otas)})

        counter = 0

        for ota in user_otas:
            counter += 1
            for shape in user_shapes:
                if shape == 'VSTEAS_REL':
                    pass
                else:
                    sub = replace_all(structure, {'shape': shape, 'ota': ota})
                    filepath = server.joinpath(f"{sub}{shape}.shp")
                    log.info(str(filepath))
                    _progress.emit({'pbar': counter})


if __name__ == '__main__':
    cssGuide = paths.get_css(obj=True).joinpath("_style.css").read_text()
    SEGOE = QFont("Segoe UI", 9)

    app = QApplication(sys.argv)
    app.setFont(SEGOE)
    app.setStyle('Fusion')

    ui = FilesTab(size=(600, None))
    ui.setStyleSheet(cssGuide)
    ui.show()

    sys.exit(app.exec_())
