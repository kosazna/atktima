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
        self.serverCombo.subscribe(self.serverComboChange)
        self.localCombo.subscribe(self.localComboChange)
        self.otas.assignLoadFunc(self.loadOtas)

    def setupUi(self, size):
        set_size(widget=self, size=size)

        layout = QVBoxLayout()
        labelLayout = QHBoxLayout()
        serverStruct = QHBoxLayout()
        localStruct = QHBoxLayout()
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

        self.serverLoad = Button("Φόρτωση απο Server",
                                 color='green',
                                 size=(180, 30),
                                 parent=self)

        self.serverCombo = ComboInput(label="Δομή Server",
                                      labelsize=(80, 24),
                                      items=['<ota>/SHP',
                                             '<ota>/SHP/<shape>',
                                             'Άλλο...'],
                                      combosize=(200, 24),
                                      parent=self)
        self.localCombo = ComboInput(label="Δομή Τοπικά",
                                     labelsize=(80, 24),
                                     items=['<ota>/SHAPE/<shape>',
                                            '<ota>/<shape>',
                                            'Άλλο...'],
                                     combosize=(200, 24),
                                     parent=self)
        self.companyOtaCombo = ComboInput(label="ΟΤΑ για εταιρία",
                                     labelsize=(100, 24),
                                     items=state[state['meleti']]['company'].keys(),
                                     combosize=(100, 24),
                                     parent=self)
        self.serverStructure = StrInput(completer=['<ota>/SHP',
                                                   '<ota>/SHP/<shape>'],
                                        editsize=(220, 24),
                                        parent=self)
        self.localStructure = StrInput(completer=['<ota>/SHAPE/<shape>',
                                                  '<ota>/<shape>'],
                                       editsize=(220, 24),
                                       parent=self)

        self.progress = ProgressBar(parent=self)

        if state['company'] == 'NAMA':
            self.serverCombo.setCurrentText('<ota>/SHP')
            self.serverStructure.setText('<ota>/SHP')
        else:
            self.serverCombo.setCurrentText('<ota>/SHP/<shape>')
            self.serverStructure.setText('<ota>/SHP/<shape>')
        
        self.serverStructure.disable()

        self.localCombo.setCurrentText('<ota>/<shape>')
        self.localStructure.setText('<ota>/<shape>')
        self.localStructure.disable()
        self.companyOtaCombo.setCurrentText(state['company'])

        self.checkServer()
        self.shape.addItems(db.get_shapes(state['meleti']))
        self.otas.addItems(state[state['meleti']]['company']['NAMA'])
        self.shape.hideButtons()

        labelLayout.addWidget(self.fullname)
        labelLayout.addWidget(self.username)
        labelLayout.addWidget(self.company, stretch=2, alignment=Qt.AlignLeft)
        labelLayout.addWidget(self.server)
        labelLayout.addWidget(self.meleti)
        layout.addLayout(labelLayout)
        layout.addWidget(HLine())
        layout.addWidget(self.info)
        serverStruct.addWidget(self.serverCombo)
        serverStruct.addWidget(self.serverStructure,
                               stretch=2,
                               alignment=Qt.AlignLeft)
        localStruct.addWidget(self.localCombo)
        localStruct.addWidget(self.localStructure,
                              stretch=2,
                              alignment=Qt.AlignLeft)

        layout.addLayout(serverStruct)
        layout.addLayout(localStruct)
        layout.addWidget(HLine())
        layout.addWidget(self.companyOtaCombo, alignment=Qt.AlignRight)
        listLayout.addWidget(self.shape)
        listLayout.addWidget(self.otas)
        layout.addLayout(listLayout)
        layout.addWidget(HLine(), stretch=2, alignment=Qt.AlignTop)
        buttonLayout.addWidget(self.serverLoad)
        layout.addLayout(buttonLayout)
        layout.addWidget(self.progress, stretch=2, alignment=Qt.AlignBottom)

        self.setLayout(layout)

    def serverComboChange(self):
        current_server = self.serverCombo.getCurrentText()

        if current_server == 'Άλλο...':
            self.serverStructure.enable()
            self.serverStructure.lineEdit.setPlaceholderText("Μοτίβο...")
            self.serverStructure.setText('')
        else:
            self.serverStructure.disable()
            self.serverStructure.lineEdit.setPlaceholderText("")
            self.serverStructure.setText(current_server)
    
    def localComboChange(self):
        current_local = self.localCombo.getCurrentText()

        if current_local == 'Άλλο...':
            self.localStructure.enable()
            self.localStructure.lineEdit.setPlaceholderText("Μοτίβο...")
            self.localStructure.setText('')
        else:
            self.localStructure.disable()
            self.localStructure.lineEdit.setPlaceholderText("")
            self.localStructure.setText(current_local)

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
                    self.popup.error(status.msg)
            elif isinstance(status, Result):
                if status.result == Result.ERROR:
                    self.popup.error(status.msg)
                elif status.result == Result.WARNING:
                    self.popup.warning(status.msg, **status.details)
                else:
                    self.popup.info(status.msg, **status.details)
            else:
                self.popup.info(status)

    def updateFinish(self):
        pass

    def loadOtas(self):
        company = self.companyOtaCombo.getCurrentText()
        return state[state['meleti']]['company'][company]

    def onGetFromServer(self):
        run_thread(threadpool=self.threadpool,
                   function=self.getFilesFromServer,
                   on_update=self.updateProgress,
                   on_result=self.updateResult,
                   on_finish=self.updateFinish)

    @licensed(state['appname'])
    def getFilesFromServer(self, _progress):
        server = paths.get_kthmadata(True)
        local = paths.get_localdata(True)

        server_structure = self.serverStructure.getText()
        local_structure = self.localStructure.getText()

        user_shapes = self.shape.getCheckState()
        user_otas = self.otas.getCheckState()

        if user_otas and user_shapes:
            _progress.emit({'pbar_max': len(user_otas)})
            ota_counter = 0
            file_counter = 0
            for ota in user_otas:
                ota_counter += 1
                for shape in user_shapes:
                    if shape == 'VSTEAS_REL':
                        pass
                    else:
                        sub_server = replace_all(server_structure,
                                                {'shape': shape, 'ota': ota})
                        sub_local = replace_all(local_structure,
                                                {'shape': shape, 'ota': ota})
                        _src = server.joinpath(f"{sub_server}/{shape}.shp")
                        _dst = local.joinpath(f"{sub_local}/{shape}.shp")

                        copied = copy_file(_src, _dst)
                        if copied:
                            file_counter += 1
                _progress.emit({'pbar': ota_counter})

            if file_counter:
                return Result.success("Η αντιγραφή αρχείων ολοκληρώθηκε",
                                details={'secondary': f"Σύνολο αρχείων: {file_counter}"})
            return Result.warning("Δεν έγινε αντιγραφή για κανένα αρχείο")
        else:
            return Result.warning('Δεν βρέθηκε επιλογή για κάποια κατηγορία')


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
