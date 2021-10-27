# -*- coding: utf-8 -*-
import sys
from pathlib import Path
from typing import Any, Optional, Tuple

from at.auth.client import AuthStatus, licensed
from at.gui.components import *
from at.gui.utils import set_size
from at.gui.worker import run_thread
from at.io.copyfuncs import copy_file
from at.io.utils import load_json, write_json
from at.logger import log
from at.result import Result
from at.text import replace_all
from atktima.app.core import get_shapes
from atktima.app.settings import *
from atktima.app.utils import db, paths, state
from PyQt5.QtCore import Qt, QThreadPool
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget

# When setting fixed width to QLineEdit ->
# -> add alignment=Qt.AlignLeft when adding widget to layout

infostr = "Μόνο για τα αρχεία που θα βρεθούν θα γίνει αντιγραφή στο LocalData της μελέτης"


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

        self.filesCopied = False

        self.serverLoad.subscribe(self.onGetFromServer)
        self.localLoad.subscribe(self.onGetFromLocal)
        self.deleteButton.subscribe(self.onDelete)
        self.localFolder.lineEdit.textChanged.connect(self.checkLocalFolder)

    def setupUi(self, size):
        set_size(widget=self, size=size)

        layout = QVBoxLayout()
        layout.setContentsMargins(2, 4, 2, 0)
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
        self.shape = ListWidget(label="Επιλογή Χωρικών",
                                parent=self)
        self.otas = ListWidget(label="Επιλογή ΟΤΑ",
                               parent=self)
        self.serverLoad = Button("Φόρτωση από Server",
                                 color='green',
                                 size=(180, 30),
                                 parent=self)
        # self.serverCombo = ComboInput(label="Δομή Server",
        #                               labelsize=(80, 24),
        #                               items=['<ota>/SHP',
        #                                      '<ota>/SHP/<shape>',
        #                                      'Άλλο...'],
        #                               combosize=(200, 24),
        #                               parent=self)
        self.serverWidget = StrSelector(label="Δομή Εισαγωγής",
                                        mapping=server_mapping,
                                        labelsize=(100, 24),
                                        combosize=(180, 24),
                                        parent=self)
        self.localWidget = StrSelector(label="Δομή Τοπικά",
                                       mapping=local_mapping,
                                       labelsize=(100, 24),
                                       combosize=(180, 24),
                                       parent=self)
        self.localFolder = FolderInput(label="Φάκελος", parent=self)
        self.localLoad = Button("Φόρτωση από Φάκελο",
                                size=(180, 30),
                                parent=self)
        self.deleteButton = Button("Διαγραφή αρχείων",
                                   color='red',
                                   size=(200, 30),
                                   parent=self)

        self.progress = ProgressBar(parent=self)

        serverWidgetKey = f"{state['company']} Server"
        self.serverWidget.setCurrentText(serverWidgetKey)
        localWidgetKey = state[state['meleti']]['type']
        self.localWidget.setCurrentText(localWidgetKey)
        self.localLoad.disable()
        self.checkServer()
        self.shape.addItems(db.get_shapes(state['meleti']))
        self.otas.addItems(db.get_ota_per_meleti_company(
            state['meleti'], state['company']))
        self.shape.hideButtons()
        self.otas.hideButtons()

        labelLayout.addWidget(self.fullname)
        labelLayout.addWidget(self.username)
        labelLayout.addWidget(self.company, stretch=2, alignment=Qt.AlignLeft)
        labelLayout.addWidget(self.server)
        labelLayout.addWidget(self.meleti)
        layout.addLayout(labelLayout)
        layout.addWidget(HLine())
        layout.addWidget(self.info)

        layout.addWidget(self.serverWidget)
        layout.addWidget(self.localWidget)
        layout.addWidget(HLine())
        listLayout.addWidget(self.shape)
        listLayout.addWidget(self.otas)
        layout.addLayout(listLayout)
        layout.addWidget(HLine())
        layout.addWidget(self.localFolder)
        buttonLayout.addWidget(self.serverLoad)
        buttonLayout.addWidget(self.localLoad)
        layout.addLayout(buttonLayout)
        layout.addWidget(self.deleteButton, alignment=Qt.AlignCenter)
        layout.addWidget(self.progress, stretch=2, alignment=Qt.AlignBottom)

        self.setLayout(layout)

    def checkLocalFolder(self):
        if self.localFolder.getText():
            if Path(self.localFolder.getText()).exists():
                self.localLoad.enable()
            else:
                self.localLoad.disable()
        else:
            self.localLoad.disable()

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
                    self.filesCopied = True
            else:
                self.popup.info(status)

    def updateFinish(self):
        if self.filesCopied:
            user_shapes = self.shape.getCheckState()
            status = load_json(paths.get_json_status())

            for shape in user_shapes:
                if shape in status['ktima']['SHAPE']:
                    status['ktima']['SHAPE'][shape] = False

            write_json(paths.get_json_status(), status)

    def onGetFromServer(self):
        run_thread(threadpool=self.threadpool,
                   function=self.getFilesFromServer,
                   on_update=self.updateProgress,
                   on_result=self.updateResult,
                   on_finish=self.updateFinish)

    def onGetFromLocal(self):
        result = self.popup.info("Η δομή server είναι σωστή?",
                                 buttons=['yes', 'no'])
        if result == 'yes':
            return run_thread(threadpool=self.threadpool,
                              function=self.getFilesFromLocal,
                              on_update=self.updateProgress,
                              on_result=self.updateResult,
                              on_finish=self.updateFinish)
        else:
            log.error("Η φόρτωση ακυρώθηκε")

    def onDelete(self):
        folder = self.localFolder.getText()

        if folder:
            _folder = folder
        else:
            _folder = paths.get_localdata()

        result = self.popup.warning("Διαγραφή επιλεγμένων αρχείων απο φάκελο:",
                                    secondary=_folder,
                                    buttons=['yes', 'no'])

        if result == 'yes':
            return run_thread(threadpool=self.threadpool,
                              function=self.getFilesFromLocal,
                              on_update=self.updateProgress,
                              on_result=self.updateResult,
                              on_finish=self.updateFinish)
        else:
            log.error("Η διαγραφή ακυρώθηκε")

    @licensed(appname=state['appname'], category=state['meleti'])
    def getFilesFromServer(self, _progress):
        server = paths.get_kthmadata(True)
        local = paths.get_localdata(True)

        server_structure = self.serverWidget.getText()
        local_structure = self.localWidget.getText()

        user_shapes = self.shape.getCheckState()
        user_otas = self.otas.getCheckState()

        if user_otas and user_shapes:
            return get_shapes(src=server,
                              dst=local,
                              otas=user_otas,
                              shapes=user_shapes,
                              server_schema=server_structure,
                              local_schema=local_structure,
                              _progress=_progress)
        else:
            return Result.warning('Δεν βρέθηκε επιλογή για κάποια κατηγορία')

    @licensed(appname=state['appname'], category=state['meleti'])
    def getFilesFromLocal(self, _progress):
        server = Path(self.localFolder.getText())
        local = paths.get_localdata(True)

        if not server.exists():
            return Result.error("Ο φάκελος δεν υπάρχει")

        server_structure = self.serverWidget.getText()
        local_structure = self.localWidget.getText()

        user_shapes = self.shape.getCheckState()
        user_otas = self.otas.getCheckState()

        if user_otas and user_shapes:
            return get_shapes(src=server,
                              dst=local,
                              otas=user_otas,
                              shapes=user_shapes,
                              server_schema=server_structure,
                              local_schema=local_structure,
                              _progress=_progress)
        else:
            return Result.warning('Δεν βρέθηκε επιλογή για κάποια κατηγορία')

    @licensed(appname=state['appname'], category=state['meleti'])
    def deleteFiles(self, _progress):
        user_shapes = self.shape.getCheckState()

        folder = self.localFolder.getText()

        if folder:
            _folder = Path(folder)
        else:
            _folder = paths.get_localdata(True)

        for shape in user_shapes:
            for p in _folder.glob(shape):
                p.unlink(missing_ok=True)


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
